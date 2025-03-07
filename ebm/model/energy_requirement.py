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
        return 1.0 - x.improvement_at_period_end
    return np.linspace(1.0, 1.0 - x.improvement_at_period_end, int(x.period_end_year - x.period_start_year + 1.0))[
        x.year_no]  # x.year_no.astype(int)



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
        return merged[['building_category', 'TEK', 'building_condition','year', 'purpose',
                       'original_kwh_m2', 'reduction_yearly', 'reduction_policy', 'reduction_condition',
                       'reduced_kwh_m2', 'behavior_factor', 'kwh_m2']]

    def calculate_energy_requirement(self, all_building_categories, all_purpose, all_teks, energy_requirement_original_condition, model_years,
                                     most_conditions, database_manager) -> pd.DataFrame:
        df_bc = pd.DataFrame(all_building_categories, columns=['building_category'])
        df_tek = pd.merge(df_bc, pd.DataFrame({'TEK': all_teks}), how='cross')
        df_purpose = pd.merge(df_tek, pd.DataFrame(all_purpose, columns=['purpose']), how='cross')
        df_condition = pd.merge(df_purpose, pd.DataFrame({'building_condition': most_conditions}), how='cross')
        df_years = pd.merge(df_condition, pd.DataFrame({'year': model_years}), how='cross')

        energy_requirement_original_condition = energy_requirement_original_condition.copy()
        energy_requirement_original_condition = energy_requirement_original_condition[
            energy_requirement_original_condition['TEK'] != 'TEK21']

        erq_all_years = pd.merge(left=df_years, right=energy_requirement_original_condition, how='left')
        energy_requirements = erq_all_years.drop(columns=['index', 'level_0'], errors='ignore')

        reduction_per_condition = database_manager.get_energy_req_reduction_per_condition()
        policy_improvement = database_manager.get_energy_req_policy_improvements()
        yearly_improvement = database_manager.get_energy_req_yearly_improvements()

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
        reduction_per_condition = self.calculate_reduction_condition(reduction_per_condition)
        condition_factor = pd.merge(left=energy_requirements, right=reduction_per_condition,
                                    on=['building_category', 'TEK', 'building_condition', 'purpose'],
                                    how='left')

        policy_improvement = pd.merge(right=pd.DataFrame({'year': model_years}), left=policy_improvement, how='cross')
        policy_improvement_factor = self.calculate_reduction_policy(policy_improvement)

        yearly_improvement.loc[:, 'efficiency_start_year'] = model_years.start
        yearly_improvement = pd.merge(yearly_improvement, pd.DataFrame({'year': model_years}), how='cross')
        yearly_reduction_factor = self.calculate_reduction_yearly(policy_improvement_factor, yearly_improvement)

        merged = self.merge_energy_requirement_reductions(condition_factor, yearly_reduction_factor)
        return merged

    def merge_energy_requirement_reductions(self, condition_factor, yearly_improvements):
        m_nrg_yi = pd.merge(left=condition_factor, right=yearly_improvements.copy(), how='left')
        merged = m_nrg_yi.copy()
        merged.loc[:, 'reduction_yearly'] = merged.loc[:, 'reduction_yearly'].fillna(1.0)
        merged.loc[:, 'reduction_policy'] = merged.loc[:, 'reduction_policy'].fillna(1.0)
        merged['reduction_condition'] = merged['reduction_condition'].fillna(1.0)
        merged['reduced_kwh_m2'] = (merged['kwh_m2'] * merged['reduction_condition'].fillna(1.0) *
                                    merged['reduction_yearly'].fillna(1.0) * merged['reduction_policy'].fillna(1.0))
        merged['behavior_kwh_m2'] = merged['reduced_kwh_m2'] * merged['behavior_factor'].fillna(1.0)
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
        yearly_improvements = pd.merge(yearly_improvement, policy_improvement, how='left')
        period_end_gt_start_year = (
            yearly_improvements[yearly_improvements.period_end_year > yearly_improvements.efficiency_start_year]).index
        yearly_improvements.loc[period_end_gt_start_year, 'efficiency_start_year'] = yearly_improvements.loc[
            period_end_gt_start_year, 'period_end_year']
        yearly_improvements.loc[:, 'reduce_efficiency_improvement'] = 1.0 - yearly_improvements.loc[:,
                                                                            'yearly_efficiency_improvement']
        yearly_improvements.loc[:, 'year_efficiency'] = yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:,
                                                                                             'efficiency_start_year']
        yearly_improvements.loc[:, 'year_efficiency'] = (
                yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:, 'efficiency_start_year']).clip(0)
        yearly_improvements.loc[:, 'reduction_yearly'] = (1.0 - yearly_improvements.loc[:,
                                                                'yearly_efficiency_improvement']) ** yearly_improvements.loc[
                                                                                                     :,
                                                                                                     'year_efficiency']
        yearly_improvements.loc[:, 'year_efficiency'] = yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:,
                                                                                             'efficiency_start_year']
        return yearly_improvements

    def calculate_reduction_policy(self, policy_improvement: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the reduction policy for each entry in the DataFrame.

        This method computes the reduction policy by first calculating the number of years since the
        start of the period. It then applies the `yearly_reduction` function to each relevant entry
        to determine the reduction policy.

        Parameters
        ----------
        policy_improvement : pd.DataFrame
            DataFrame containing policy improvement information. Must include columns 'year' and 'period_start_year'.

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_policy' column and updated entries.
        """
        policy_improvement.loc[:, 'year_no'] = policy_improvement.loc[:, 'year'] - policy_improvement.loc[:,
                                                                                   'period_start_year']
        policy_improvement.loc[:, 'year_no'] = policy_improvement.loc[:, 'year_no'].fillna(0)
        policy_improvement_slice = policy_improvement[~policy_improvement.year_no.isna()].index
        policy_improvement.loc[policy_improvement_slice, 'reduction_policy'] = policy_improvement.loc[
            policy_improvement_slice].apply(
            yearly_reduction, axis=1)
        return policy_improvement

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
        reduction_per_condition = reduction_per_condition[reduction_per_condition['TEK'] != 'TEK21']
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
