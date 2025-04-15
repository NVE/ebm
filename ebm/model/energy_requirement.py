import typing

from loguru import logger
import numpy as np
import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.file_handler import FileHandler
from ebm.services.files import make_unique_path


def yearly_reduction(x):
    if x.year < x.period_start_year:
        return 1.0
    if x.year > x.period_end_year:
        return round(1.0 - x.improvement_at_period_end, 15)
    ls = np.linspace(1.0, 1.0 - x.improvement_at_period_end, int(x.period_end_year - x.period_start_year + 1.0))[
        x.year_no]
    return round(ls, 15)  # x.year_no.astype(int)



class EnergyRequirement:
    def __init__(self,
                 tek_list: typing.List[str],
                 period: YearRange = YearRange(2010, 2050),
                 calibration_year: int = 1999,
                 database_manager = None):
        self.tek_list = tek_list
        self.period = period
        self.calibration_year = calibration_year
        if calibration_year == period.start:
            logger.trace(f'Calibration year {calibration_year} is same as start year {period.start}')
        elif calibration_year not in period.subset(1):
            logger.debug(f'Calibration year {calibration_year} is outside period {period.start}-{period.end}')

        self.database_manager = database_manager


    def calculate_for_building_category(self, database_manager: DatabaseManager = None) -> pd.DataFrame:
        """
        Calculates energy requirements for a single building category

        Parameters
        ----------
        database_manager: DatabaseManager
            optional database_manager used to load input parameters

        Returns
        -------
        Iterable of pd.Series
            indexed by year, building_category, TEK, purpose, building_condition
            column kwh_m2 representing energy requirement

        """
        database_manager = database_manager if database_manager else self.database_manager

        all_teks = database_manager.get_tek_list().tolist()
        all_building_categories = list(BuildingCategory)
        all_purpose = list(EnergyPurpose)
        most_conditions = list(BuildingCondition.existing_conditions())
        model_years = YearRange(2020, 2050)
        erq_oc = database_manager.get_energy_req_original_condition()

        merged = self.calculate_energy_requirement(all_building_categories, all_purpose, all_teks, erq_oc, model_years,
                                                   most_conditions, database_manager)
        
        merged = merged.drop_duplicates('building_category,TEK,building_condition,year,purpose'.split(','), keep='first')
        return merged[['building_category', 'TEK', 'building_condition','year', 'purpose',
                       'original_kwh_m2', 'reduction_yearly', 'reduction_policy', 'reduction_condition',
                       'reduced_kwh_m2', 'behaviour_factor', 'kwh_m2']]

    def calculate_energy_requirement(self, all_building_categories, all_purpose, all_teks, energy_requirement_original_condition, model_years,
                                     most_conditions, database_manager) -> pd.DataFrame:
        df_bc = pd.DataFrame(all_building_categories, columns=['building_category'])
        df_tek = pd.merge(df_bc, pd.DataFrame({'TEK': all_teks}), how='cross')
        df_purpose = pd.merge(df_tek, pd.DataFrame(all_purpose, columns=['purpose']), how='cross')
        df_condition = pd.merge(df_purpose, pd.DataFrame({'building_condition': most_conditions}), how='cross')
        df_years = pd.merge(df_condition, pd.DataFrame({'year': model_years}), how='cross')

        energy_requirement_original_condition = energy_requirement_original_condition.copy()

        energy_requirement_original_condition = energy_requirement_original_condition.join(
            pd.DataFrame({'building_condition_r': most_conditions}),
            how='cross',
        )
        energy_requirement_original_condition['building_condition'] = energy_requirement_original_condition.building_condition_r
        energy_requirement_original_condition = energy_requirement_original_condition.drop(columns=['building_condition_r'])

        erq_all_years = pd.merge(left=df_years, right=energy_requirement_original_condition, how='left')
        energy_requirements = erq_all_years.drop(columns=['index', 'level_0'], errors='ignore')

        reduction_per_condition = database_manager.get_energy_req_reduction_per_condition()
        policy_improvement = database_manager.get_energy_need_policy_improvement()
        yearly_improvement = database_manager.get_energy_need_yearly_improvements()

        return self.calculate_energy_reduction(energy_requirements, model_years, policy_improvement,
                                               reduction_per_condition, yearly_improvement)

    def calculate_energy_reduction(self, energy_requirements: pd.DataFrame,
                                   model_years: YearRange,
                                   policy_improvement: pd.DataFrame,
                                   reduction_per_condition: pd.DataFrame,
                                   yearly_improvement: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate and combine all reduction factors for energy needs into a single Dataframe.

        Parameters
        ----------
        energy_requirements : pd.DataFrame
        model_years : YearRange
        policy_improvement : pd.DataFrame
        reduction_per_condition : pd.DataFrame
        yearly_improvement : pd.DataFrame

        Returns
        -------
        pd.DataFrame
        """
        reduction_condition = self.calculate_reduction_condition(reduction_per_condition)
        condition_factor = pd.merge(left=energy_requirements, right=reduction_condition,
                                    on=['building_category', 'TEK', 'building_condition', 'purpose'],
                                    how='left')

        reduction_policy = self.calculate_reduction_policy(policy_improvement, energy_requirements)
        reduction_yearly = self.calculate_reduction_yearly(energy_requirements, yearly_improvement)

        merged = self.merge_energy_requirement_reductions(condition_factor, reduction_yearly, reduction_policy)

        return merged

    def merge_energy_requirement_reductions(self, condition_factor, yearly_improvements, reduction_policy):
        m_nrg_yi = pd.merge(left=condition_factor,
                            right=yearly_improvements.copy(),
                            on=['building_category', 'TEK', 'purpose', 'year'],
                            how='left')
        m_nrg_yi = pd.merge(left=m_nrg_yi,
                            right=reduction_policy.copy(),
                            on=['building_category', 'TEK', 'purpose', 'year'],
                            how='left')
        merged = m_nrg_yi.copy()
        merged.loc[:, 'reduction_yearly'] = merged.loc[:, 'reduction_yearly'].fillna(1.0)

        merged.loc[:, 'reduction_policy'] = merged.loc[:, 'reduction_policy'].fillna(1.0)
        merged['reduction_condition'] = merged['reduction_condition'].fillna(1.0)
        merged['reduced_kwh_m2'] = (merged['kwh_m2'] * merged['reduction_condition'].fillna(1.0) *
                                    merged['reduction_yearly'].fillna(1.0) * merged['reduction_policy'].fillna(1.0))
        merged['behavior_kwh_m2'] = merged['reduced_kwh_m2'] * merged['behaviour_factor'].fillna(1.0)
        merged = merged.rename(columns={'kwh_m2': 'original_kwh_m2'})
        merged['kwh_m2'] = merged['behavior_kwh_m2']
        return merged

    def calculate_reduction_yearly(self,
                                   policy_improvement: pd.DataFrame, yearly_improvement: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the yearly reduction for each entry in the DataFrame.

        This method merges the yearly improvement data with the policy improvement data, adjusts the
        efficiency start year if the period end year is greater, and calculates the yearly reduction
        based on the yearly efficiency improvement.

        Parameters
        ----------
        policy_improvement : pd.DataFrame
            DataFrame containing policy improvement information. Must include columns 'period_end_year' and 'efficiency_start_year'.
        yearly_improvement : pd.DataFrame
            DataFrame containing yearly improvement information. Must include columns 'year', 'yearly_efficiency_improvement', and 'efficiency_start_year'.

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_yearly' column and updated entries.
        """


        df = pd.merge(left=policy_improvement[['building_category', 'TEK', 'purpose', 'year']],
                      right=yearly_improvement,
                      on=['building_category', 'TEK', 'purpose'])
        ys = df[df.year >= df.start_year].index
        df.loc[ys, 'reduction_yearly'] = (1.0 - df.loc[ys,
                                                                'yearly_efficiency_improvement']) ** (df.loc[ys
                                                                                                     ,
                                                                                                     'year'] - df.loc[
                                                                                                     ys,
                                                                                                     'start_year'])
        df = df.drop_duplicates(['building_category', 'TEK', 'purpose', 'year'])
        return df


    def calculate_reduction_policy(self, policy_improvement: pd.DataFrame, all_things) -> pd.DataFrame:
        """
        Calculate the reduction policy for each entry in the DataFrame.

        This method computes the reduction policy by first calculating the number of years since the
        start of the period. It then applies the `yearly_reduction` function to each relevant entry
        to determine the reduction policy.

        Parameters
        ----------
        policy_improvement : pd.DataFrame
            DataFrame containing policy improvement information. Must include columns 'year' and 'period_start_year'.
        all_things: pd.DataFrame
            DataFrame containing every combination of building_category, TEK, purpose, year

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_policy' column and updated entries.
        """
        policy_improvement = policy_improvement.sort_values(
            by=['building_category', 'TEK', 'purpose', 'start_year', 'end_year'])

        policy_improvement[['building_category_s', 'TEK_s', 'purpose_s', 'start_year_s', 'end_year_s']] = \
        policy_improvement[
            ['building_category', 'TEK', 'purpose', 'start_year', 'end_year']]

        policy_improvement = policy_improvement.set_index(
            ['building_category', 'TEK', 'purpose', 'start_year', 'end_year'], drop=True)

        shifted = policy_improvement.shift(1).reset_index()

        shifted = shifted.query('building_category==building_category_s & TEK==TEK_s & purpose==purpose_s')
        shifted['improvement_at_start_year'] = shifted['improvement_at_end_year']
        shifted = shifted[['building_category', 'TEK', 'purpose', 'start_year', 'end_year', 'improvement_at_start_year']]

        start_year_from_previous = shifted

        policy_improvement = pd.merge(left=policy_improvement,
                                      right=start_year_from_previous,
                                      left_on=['building_category', 'TEK', 'purpose', 'start_year', 'end_year'],
                                      right_on=['building_category', 'TEK', 'purpose', 'start_year', 'end_year'],
                                      how='left'
                                      )

        policy_improvement[['start_year', 'end_year']] = policy_improvement[['start_year', 'end_year']].astype(int)
        policy_improvement = policy_improvement.set_index(
            ['building_category', 'TEK', 'purpose', 'start_year', 'end_year'], drop=True)
        policy_improvement['improvement_at_start_year'] = 1.0-policy_improvement['improvement_at_start_year'].fillna(0.0)

        policy_improvement = policy_improvement[['improvement_at_start_year', 'improvement_at_end_year']].reset_index()

        df = pd.merge(left=all_things[['building_category', 'TEK', 'purpose', 'year']],
                      right=policy_improvement,
                      on=['building_category', 'TEK', 'purpose'], how='left')

        df['num_values'] = df['end_year'] - df['start_year'] + 1.0
        df['n'] = (df.year - df.start_year).clip(upper=df.num_values-1, lower=0)

        df['step'] = ((1.0-df['improvement_at_end_year']) - df['improvement_at_start_year']) / (df['num_values']-1.0)

        df['reduction_policy'] = df['improvement_at_start_year'] + (df['n']) * df['step']
        df['reduction_policy'] = df['reduction_policy'].fillna(1.0)
        df['_col_to_filter'] = (df['year'] < df['start_year']) | (df['year'] > df['end_year'])
        df = df.sort_values(by=['building_category', 'TEK', 'purpose', 'year', '_col_to_filter'])
        df = df.drop_duplicates(['building_category', 'TEK', 'purpose', 'year'])

        return df[['building_category', 'TEK', 'purpose', 'year', 'reduction_policy']]


    def calculate_reduction_condition(self, reduction_per_condition: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the reduction condition for each entry in the DataFrame.

        This method computes the reduction condition by subtracting the reduction share from 1.0.
        It also fills any NaN values in the 'reduction_condition' column with 1.0.

        Parameters
        ----------
        reduction_per_condition : pd.DataFrame
            DataFrame containing the reduction share information. Must include columns 'reduction_share' and 'TEK'.

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_condition' column and filtered entries.
        """
        reduction_per_condition['reduction_condition'] = 1.0 - reduction_per_condition['reduction_share']
        reduction_per_condition.loc[:, 'reduction_condition'] = reduction_per_condition.loc[:,
                                                                'reduction_condition'].fillna(1.0)
        return reduction_per_condition

    def calculate_energy_requirements(
            self,
            building_categories: typing.Iterable[BuildingCategory] = None) -> pd.DataFrame:
        """
        Calculates energy requirements for building categories

        Parameters
        ----------
        building_categories : Iterable[BuildingCategory]
            Iterable containing building categories on which to calculate energy requirements.

        Returns
        -------
        Iterable of pd.Series
            indexed by year, building_category, TEK, purpose, building_condition
            column kwh_m2 representing energy requirement

        """
        building_categories = building_categories if building_categories else iter(BuildingCategory)

        return self.calculate_for_building_category(self.database_manager)

    @staticmethod
    def new_instance(period, calibration_year, database_manager=None):
        if period.start != 2010 and calibration_year != calibration_year:
            logger.warning(f'EnergyRequirements {period.start=} {calibration_year=}')
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        instance = EnergyRequirement(tek_list=dm.get_tek_list(), period=period, calibration_year=calibration_year,
                                     database_manager=dm)
        return instance


def main():
    import os
    import sys
    import pathlib
    log_format = """
    <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
    """.strip()
    logger.remove()
    logger.add(sys.stderr, format=log_format, level='WARNING')

    dm = DatabaseManager(FileHandler(directory='kalibrering'))
    er = EnergyRequirement.new_instance(YearRange(2020, 2050), calibration_year=2020, database_manager=dm)

    logger.error('Calculating')
    df =  er.calculate_energy_requirements()
    logger.error('Writing to file')

    xlsx_filename = make_unique_path(pathlib.Path('output/er.xlsx'))
    df.to_excel(xlsx_filename)

    logger.error('DONE')
    os.startfile(xlsx_filename, 'open')


if __name__ == '__main__':
    main()
