import typing

import numpy as np
import pandas as pd
from loguru import logger

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
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
                 building_code_list: typing.List[str],
                 period: YearRange = YearRange(2010, 2050),
                 calibration_year: int = 1999,
                 database_manager = None):
        self.building_code_list = building_code_list
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

        all_building_codes = database_manager.get_building_code_list().tolist()
        all_building_categories = list(BuildingCategory)
        all_purpose = list(EnergyPurpose)
        most_conditions = list(BuildingCondition.existing_conditions())
        model_years = YearRange(2020, 2050)
        erq_oc = database_manager.get_energy_req_original_condition()

        df = make_df_building_category_code_purpose_yearly(model_years, all_building_categories, all_building_codes,
                                                           all_purpose, most_conditions)

        merged = self.calculate_energy_requirement(erq_oc, model_years, database_manager,
                                                   make_df_building_category_code_purpose_yearly(model_years,
                                                                                                 all_building_categories,
                                                                                                 all_building_codes,
                                                                                                 all_purpose,
                                                                                                 most_conditions))
        
        merged = merged.drop_duplicates('building_category,building_code,building_condition,year,purpose'.split(','), keep='first')

        return merged

    def calculate_energy_requirement(self, energy_requirement_original_condition, model_years, database_manager,
                                     df_years) -> pd.DataFrame:

        energy_requirement_original_condition = energy_requirement_original_condition.copy()

        energy_requirement_original_condition = energy_requirement_original_condition.join(
            pd.DataFrame({'building_condition_r': df_years.building_condition.unique()}),
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
                                    on=['building_category', 'building_code', 'building_condition', 'purpose'],
                                    how='left')

        reduction_policy = self.calculate_reduction_policy(policy_improvement, energy_requirements)
        reduction_yearly = self.calculate_reduction_yearly(energy_requirements, yearly_improvement)

        merged = self.merge_energy_requirement_reductions(condition_factor, reduction_yearly, reduction_policy)

        return merged

    def merge_energy_requirement_reductions(self, condition_factor, yearly_improvements, reduction_policy):
        m_nrg_yi = pd.merge(left=condition_factor,
                            right=yearly_improvements.copy(),
                            on=['building_category', 'building_code', 'purpose', 'year'],
                            how='left')
        m_nrg_yi = pd.merge(left=m_nrg_yi,
                            right=reduction_policy.copy(),
                            on=['building_category', 'building_code', 'purpose', 'year'],
                            how='left')
        merged = m_nrg_yi.copy()
        merged = merged.rename(columns={'kwh_m2': 'original_kwh_m2'})
        merged.loc[:, 'reduction_yearly'] = merged.loc[:, 'reduction_yearly'].fillna(1.0)

        merged.loc[:, 'reduction_policy'] = merged.loc[:, 'reduction_policy'].fillna(1.0)
        merged['reduction_condition'] = merged['reduction_condition'].fillna(1.0)
        merged['behavior_kwh_m2'] = merged['original_kwh_m2'] * merged['behaviour_factor'].fillna(1.0)
        merged['reduced_kwh_m2'] = (merged['behavior_kwh_m2'] * merged['reduction_condition'].fillna(1.0) *
                                    merged['reduction_yearly'].fillna(1.0) * merged['reduction_policy'].fillna(1.0))



        merged['kwh_m2'] = merged['reduced_kwh_m2']

        # Removed  column name filter
        # [['building_category', 'building_code', 'building_condition','year', 'purpose',
        #                        'original'_kwh_m2', 'reduction_yearly', 'reduction_policy', 'reduction_condition',
        #                        'reduced_kwh_m2', 'behaviour_factor', 'kwh_m2']]

        return merged

    def calculate_reduction_yearly(self, df_years: pd.DataFrame, yearly_improvement: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate factor for yearly reduction for each entry in the DataFrame yearly_improvement.

        This method merges the yearly improvement data with the policy improvement data, adjusts the
        efficiency start year if the period end year is greater, and calculates the yearly reduction
        based on the yearly efficiency improvement.

        Parameters
        ----------
        df_years : pd.DataFrame
            DataFrame containing all years for which to calculate factors. Must include column 'year'.
        yearly_improvement : pd.DataFrame
            DataFrame containing yearly improvement information. Must include columns 'yearly_efficiency_improvement', and 'efficiency_start_year'.

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_yearly' column and updated entries.
        """
        required_in_yearly_improvement = {'yearly_efficiency_improvement', 'start_year', 'end_year'}
        if not required_in_yearly_improvement.issubset(yearly_improvement.columns):
            logger.debug(f'Got columns {", ".join(yearly_improvement.columns)}')
            missing = required_in_yearly_improvement.difference(yearly_improvement.columns)
            raise ValueError('Required column{} not found in yearly_improvement: {}'.format(
                's' if len(missing) != 1 else '', missing
            ))
        if 'year' not in df_years:
            logger.debug(f'Got columns {", ".join(df_years.columns)}')
            raise ValueError('df_years does not contain column year')

        years = pd.DataFrame(data=[y for y in df_years.year.unique()], columns=['year'])

        df = pd.merge(left=yearly_improvement, right=years, how='cross')
        rows_in_range = df[(df.year >= df.start_year) & (df.year <= df.end_year)].index

        df.loc[rows_in_range, 'yearly_change'] = (1.0 - df.loc[rows_in_range, 'yearly_efficiency_improvement'])
        df.loc[rows_in_range, 'pow'] = (df.loc[rows_in_range, 'year'] - df.loc[rows_in_range, 'start_year']) + 1
        df.loc[rows_in_range, 'reduction_yearly'] =  df.loc[rows_in_range, 'yearly_change'] ** df.loc[rows_in_range, 'pow']

        df.loc[df[df.start_year > df.year].index, 'reduction_yearly'] = df.loc[
            df[df.start_year > df.year].index, 'reduction_yearly'].fillna(1.0)
        df.loc[:, 'reduction_yearly'] = df.loc[:, 'reduction_yearly'].ffill()

        return df[['building_category', 'building_code', 'purpose', 'year', 'reduction_yearly']]


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
            by=['building_category', 'building_code', 'purpose', 'start_year', 'end_year'])

        policy_improvement[['building_category_s', 'TEK_s', 'purpose_s', 'start_year_s', 'end_year_s']] = \
        policy_improvement[
            ['building_category', 'building_code', 'purpose', 'start_year', 'end_year']]

        policy_improvement = policy_improvement.set_index(
            ['building_category', 'building_code', 'purpose', 'start_year', 'end_year'], drop=True)

        shifted = policy_improvement.shift(1).reset_index()

        shifted = shifted.query('building_category==building_category_s & building_code==TEK_s & purpose==purpose_s')
        shifted['improvement_at_start_year'] = shifted['improvement_at_end_year']
        shifted = shifted[['building_category', 'building_code', 'purpose', 'start_year', 'end_year', 'improvement_at_start_year']]

        start_year_from_previous = shifted

        policy_improvement = pd.merge(left=policy_improvement,
                                      right=start_year_from_previous,
                                      left_on=['building_category', 'building_code', 'purpose', 'start_year', 'end_year'],
                                      right_on=['building_category', 'building_code', 'purpose', 'start_year', 'end_year'],
                                      how='left'
                                      )

        policy_improvement[['start_year', 'end_year']] = policy_improvement[['start_year', 'end_year']].astype(int)
        policy_improvement = policy_improvement.set_index(
            ['building_category', 'building_code', 'purpose', 'start_year', 'end_year'], drop=True)
        policy_improvement['improvement_at_start_year'] = 1.0-policy_improvement['improvement_at_start_year'].fillna(0.0)

        policy_improvement = policy_improvement[['improvement_at_start_year', 'improvement_at_end_year']].reset_index()

        df = pd.merge(left=all_things[['building_category', 'building_code', 'purpose', 'year']],
                      right=policy_improvement,
                      on=['building_category', 'building_code', 'purpose'], how='left')

        df['num_values'] = df['end_year'] - df['start_year'] + 1.0
        df['n'] = (df.year - df.start_year).clip(upper=df.num_values-1, lower=0)

        df['step'] = ((1.0-df['improvement_at_end_year']) - df['improvement_at_start_year']) / (df['num_values']-1.0)

        df['reduction_policy'] = df['improvement_at_start_year'] + (df['n']) * df['step']
        df['reduction_policy'] = df['reduction_policy'].fillna(1.0)
        df['_col_to_filter'] = (df['year'] < df['start_year']) | (df['year'] > df['end_year'])
        df = df.sort_values(by=['building_category', 'building_code', 'purpose', 'year', '_col_to_filter'])
        df = df.drop_duplicates(['building_category', 'building_code', 'purpose', 'year'])

        return df[['building_category', 'building_code', 'purpose', 'year', 'reduction_policy']]


    def calculate_reduction_condition(self, reduction_per_condition: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the reduction condition for each entry in the DataFrame.

        This method computes the reduction condition by subtracting the reduction share from 1.0.
        It also fills any NaN values in the 'reduction_condition' column with 1.0.

        Parameters
        ----------
        reduction_per_condition : pd.DataFrame
            DataFrame containing the reduction share information. Must include columns 'reduction_share' and 'building_code'.

        Returns
        -------
        pd.DataFrame
            DataFrame with the calculated 'reduction_condition' column and filtered entries.
        """
        reduction_per_condition['reduction_condition'] = 1.0 - reduction_per_condition['reduction_share']
        reduction_per_condition.loc[:, 'reduction_condition'] = reduction_per_condition.loc[:,
                                                                'reduction_condition'].fillna(1.0)
        return reduction_per_condition


    @staticmethod
    def new_instance(period, calibration_year, database_manager=None):
        if period.start != 2010 and calibration_year != calibration_year:
            logger.warning(f'EnergyRequirements {period.start=} {calibration_year=}')
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        instance = EnergyRequirement(building_code_list=dm.get_building_code_list(), period=period, calibration_year=calibration_year,
                                     database_manager=dm)
        return instance

def make_df_building_category_code_purpose_yearly(period: YearRange | None,
                                                  building_category: pd.DataFrame | list[str] | None = None,
                                                  building_code: pd.DataFrame | list[str] | None = None,
                                                  purpose: pd.DataFrame | list[str] | None = None,
                                                  building_condition: pd.DataFrame | list[str] | None = None) -> pd.DataFrame:
    """
    Generate a cross-joined dataframe of building category, building code, purpose, building condition, and year.

    This function normalizes all input arguments to single-column
    DataFrames and performs a series of cross merges to produce the full
    combinatorial dataset. It is typically used to prepare a structured
    index for energy modeling or building analytics.

    Parameters
    ----------
    period : YearRange or None
        A YearRange iterable providing the sequence of years to include.
        If None, defaults to ``YearRange(2020, 2050)``.
    building_category : DataFrame, list of str, or None, optional
        Building categories to include. May be a DataFrame with a
        ``"building_category"`` column, a list of category strings, or None.
        If None, defaults to ``list(BuildingCategory)``.
    building_code : DataFrame, list of str, or None, optional
        Building codes to include. May be a DataFrame with a
        ``"building_code"`` column, a list of code strings, or None.
        If None, defaults to the predefined TEK code list.
    purpose : DataFrame, list of str, or None, optional
        Energy purposes to include. May be a DataFrame with a ``"purpose"``
        column, a list of purpose strings, or None.
        If None, defaults to ``list(EnergyPurpose)``.
    building_condition : DataFrame, list of str, or None, optional
        Building condition categories. May be a DataFrame with a
        ``"building_condition"`` column, a list of condition strings, or None.
        If None, defaults to ``BuildingCondition.existing_conditions()``.

    Returns
    -------
    DataFrame
        A DataFrame containing the full Cartesian product of all input
        dimensions, with columns:

        - ``building_category``
        - ``building_code``
        - ``purpose``
        - ``building_condition``
        - ``year``

    Notes
    -----
    - All non-DataFrame inputs are converted to single-column DataFrames.
    - Cross joins are implemented using ``pandas.DataFrame.merge(..., how="cross")``.
    - The output is guaranteed to contain one row per unique combination
      of the input dimensions.

    Examples
    --------
    Generate a table using default categories and years:

    >>> make_df_building_category_code_purpose_yearly(None).head()

    Provide custom building codes and a custom year range:

    >>> make_df_building_category_code_purpose_yearly(
    ...     period=YearRange(2025, 2030),
    ...     building_code=["TEK97", "TEK07"]
    ... )
    """

    def ensure_df(value, default: list[str], column_name) -> pd.DataFrame:
        """Normalize lists/enums/defaults to a single-column DataFrame."""
        if isinstance(value, pd.DataFrame):
            return value
        if value is None:
            return pd.DataFrame(default, columns=[column_name])
        return pd.DataFrame(value, columns=[column_name])

    period = period if period is not None else YearRange(2020, 2050)
    building_category = ensure_df(building_category, list(BuildingCategory), 'building_category')
    building_code = ensure_df(building_code, ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17'], 'building_code')
    purpose = ensure_df(purpose, list(EnergyPurpose), 'purpose')
    building_condition = ensure_df(building_condition, list(BuildingCondition.existing_conditions()), 'building_condition')

    df = building_category.merge(building_code, how="cross")
    df = df.merge(purpose, how="cross")
    df = df.merge(building_condition, how="cross")
    df = df.merge(pd.DataFrame({'year': period}), how="cross")

    return df


def main():
    import os
    import pathlib
    import sys
    log_format = """
    <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
    """.strip()
    logger.remove()
    logger.add(sys.stderr, format=log_format, level='WARNING')

    dm = DatabaseManager(FileHandler(directory='kalibrering'))
    er = EnergyRequirement.new_instance(YearRange(2020, 2050), calibration_year=2020, database_manager=dm)

    logger.error('Calculating')
    df = er.calculate_for_building_category(dm)
    logger.error('Writing to file')

    xlsx_filename = make_unique_path(pathlib.Path('output/er.xlsx'))
    df.to_excel(xlsx_filename)

    logger.error('DONE')
    os.startfile(xlsx_filename, 'open')


if __name__ == '__main__':
    main()
