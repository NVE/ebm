import itertools
import typing

from loguru import logger
import numpy as np
import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement_filter import EnergyRequirementFilter
from ebm.model.file_handler import FileHandler
from ebm.model.filter_tek import FilterTek
from ebm.services.files import make_unique_path


class EnergyRequirement:
    """
    """

    # TODO: add input params for yearly efficiency improvements and policy measure improvements
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


    def calculate_for_building_category(self,
                                        building_category: BuildingCategory,
                                        database_manager: DatabaseManager = None) -> pd.DataFrame:
        """
        Calculates energy requirements for a single building category

        Parameters
        ----------
        building_category : BuildingCategory
        database_manager: DatabaseManager
            optional database_manager used to load input parameters

        Returns
        -------
        Iterable of pd.Series
            indexed by year, building_category, TEK, purpose, building_condition
            column kwh_m2 representing energy requirement

        """
        database_manager = database_manager if database_manager else self.database_manager

        # %%
        def explode_column_alias(df, column, values=None, alias='default', de_dup_by=None):
            values = values if values else [c for c in df[column].unique().tolist() if c != alias]
            df['_explode_column_alias_default'] = df[column] == alias
            df.loc[df[df[column] == alias].index, column] = '+'.join(values)
            df = df.assign(**{column: df[column].str.split('+')}).explode(column)
            if de_dup_by:
                df = df.sort_values(by='_explode_column_alias_default', ascending=True)
                df = df.drop_duplicates(de_dup_by)
            return df.drop(columns=['_explode_column_alias_default'], errors='ignore')

        def yearly_reduction(x):
            if x.year < x.period_start_year:
                return 1.0
            if x.year > x.period_end_year:
                return 1.0 - x.improvement_at_period_end
            # year = int()
            return np.linspace(1.0, 1.0 - x.improvement_at_period_end, int(x.period_end_year - x.period_start_year + 1.0))[
                x.year_no]  # x.year_no.astype(int)

        all_teks = pd.read_csv('kalibrering/TEK_ID.csv').TEK.tolist()
        all_building_categories = list(BuildingCategory)
        all_purpose = list(EnergyPurpose)
        most_conditions = list(BuildingCondition.existing_conditions())
        model_years = YearRange(2020, 2050)

        df_bc = pd.DataFrame(all_building_categories, columns=['building_category'])
        df_tek = pd.merge(df_bc, pd.DataFrame({'TEK': all_teks}), how='cross')
        df_purpose = pd.merge(df_tek, pd.DataFrame(all_purpose, columns=['purpose']), how='cross')
        df_condition = pd.merge(df_purpose, pd.DataFrame({'building_condition': most_conditions}), how='cross')
        df_years = pd.merge(df_condition, pd.DataFrame({'year': model_years}), how='cross')
        df_years['_df_y_src'] = 'src'

        # erq_oc = database_manager.get_energy_req_original_condition()
        erq_oc = pd.read_csv('kalibrering/energy_requirement_original_condition.csv')

        erq_oc = erq_oc[erq_oc['TEK'] != 'TEK21']
        erq_oc['_src_erq_oc'] = 'src'
        erq_oc = explode_column_alias(erq_oc, 'TEK', all_teks, 'default')
        erq_all_conditions = pd.merge(left=df_condition, right=erq_oc, how='left')
        erq_all_conditions['_src_erq_a_c'] = 'src'

        erq_all_years = pd.merge(left=df_years, right=erq_oc, how='left')
        erq_all_years['_erq_al_yrs'] = 'src'

        energy_requirements = erq_all_years.drop(columns=['index', 'level_0'], errors='ignore')

        r_s = pd.read_csv('kalibrering/energy_requirement_reduction_per_condition.csv')
        r_s['reduction_condition'] = 1.0 - r_s['reduction_share']
        r_s = explode_column_alias(r_s, 'building_category', all_building_categories, 'default')
        r_s = explode_column_alias(df=r_s, column='TEK', values=all_teks, alias='default',
                                   de_dup_by=['building_category', 'TEK', 'purpose', 'building_condition'])
        r_s = r_s[r_s['TEK'] != 'TEK21']
        r_s.loc[:, 'reduction_condition'] = r_s.loc[:, 'reduction_condition'].fillna(1.0)
        r_s['_src_r_s'] = 'src'

        r_s[r_s.duplicated(['building_category', 'TEK', 'purpose', 'building_condition'])]

        reduction_condition = pd.merge(left=r_s, right=pd.DataFrame({'year': model_years}), how='cross')
        reduction_condition = pd.merge(df_years, reduction_condition)

        p_i = pd.read_csv('kalibrering/energy_requirement_policy_improvements.csv')

        p_i = explode_column_alias(p_i, 'building_category', all_building_categories, 'default')
        p_i = explode_column_alias(p_i, 'TEK', all_teks, 'default')
        p_i['_src_p_i'] = 'src'

        policy_improvement = pd.merge(right=pd.DataFrame({'year': model_years}), left=p_i, how='cross')

        e_y = policy_improvement.copy()
        e_y.loc[:, 'year_no'] = e_y.loc[:, 'year'] - e_y.loc[:, 'period_start_year']
        e_y.loc[:, 'year_no'] = e_y.loc[:, 'year_no'].fillna(0)
        e_y['_src_e_y'] = 'src'

        policy_improvement_slice = e_y[~e_y.year_no.isna()].index
        e_y.loc[policy_improvement_slice, 'reduction_policy'] = e_y.loc[policy_improvement_slice].apply(
            yearly_reduction, axis=1)

        policy_improvement = e_y

        y_i = pd.read_csv('kalibrering/energy_requirement_yearly_improvements.csv')

        y_i = explode_column_alias(y_i, 'building_category', all_building_categories, 'default')
        y_i = explode_column_alias(y_i, 'TEK', all_teks, 'default')
        y_i.loc[:, 'efficiency_start_year'] = 2020
        y_i = pd.merge(y_i, pd.DataFrame({'year': model_years}), how='cross')
        y_i.loc[:, 'reduce_efficiency_improvement'] = 1.0 - y_i.loc[:, 'yearly_efficiency_improvement']
        y_i.loc[:, 'year_efficiency'] = y_i.loc[:, 'year'] - y_i.loc[:, 'efficiency_start_year']
        y_i['_src_y_i'] = 'src'

        yearly_improvements = pd.merge(y_i, policy_improvement, how='left')

        yearly_improvements['efficiency_start_year'] = yearly_improvements[
            ['period_end_year', 'efficiency_start_year']].max(axis=1).astype(int)
        yearly_improvements.loc[:, 'year_efficiency'] = (
                    yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:, 'efficiency_start_year']).clip(0)
        yearly_improvements.loc[:, 'reduction_yearly'] = (1.0 - yearly_improvements.loc[:,
                                                                'yearly_efficiency_improvement']) ** yearly_improvements.loc[
                                                                                                     :,
                                                                                                     'year_efficiency']
        yearly_improvements.loc[:, 'year_efficiency'] = yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:,
                                                                                             'efficiency_start_year']

        m_nrg_yi = pd.merge(left=energy_requirements.copy(), right=yearly_improvements.copy(), how='left')
        merged = pd.merge(left=m_nrg_yi.copy(), right=reduction_condition.copy(),
                          on=['building_category', 'TEK', 'purpose', 'building_condition', 'year'], how='left')

        merged.loc[:, 'reduction_yearly'] = merged.loc[:, 'reduction_yearly']
        merged.loc[:, 'reduction_policy'] = merged.loc[:, 'reduction_policy'].fillna(1.0)
        merged.loc[:, 'reduction_share'] = merged.loc[:, 'reduction_share'].fillna(1.0)
        merged['reduction_condition'] = merged['reduction_condition'].fillna(1.0)

        merged['reduced_kwh_m2'] = (merged['kwh_m2'] * merged['reduction_condition'].fillna(1.0) *
                                    merged['reduction_yearly'].fillna(1.0) * merged['reduction_policy'].fillna(1.0))
        merged['behavior_kwh_m2'] = merged['reduced_kwh_m2'] * merged['behavior_factor']

        merged = merged.rename(columns={'kwh_m2': 'original_kwh_m2'})
        merged['kwh_m2'] = merged['behavior_kwh_m2']
        return merged[['building_category', 'TEK', 'building_condition','year', 'purpose',
                       'original_kwh_m2', 'reduced_kwh_m2', 'behavior_factor', 'kwh_m2']]


    def calculate_energy_requirements(
            self,
            building_categories: typing.Iterable[BuildingCategory] = None) -> typing.Iterable[pd.Series]:
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

        return self.calculate_for_building_category(building_categories, self.database_manager)

    @staticmethod
    def new_instance(period, calibration_year, database_manager=None):
        # Warn about non-standard calibration year
        if period.start != 2010 and calibration_year != calibration_year:
            logger.warning(f'EnergyRequirements {period.start=} {calibration_year=}')
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        instance = EnergyRequirement(tek_list=dm.get_tek_list(), period=period, calibration_year=calibration_year,
                                     database_manager=dm)
        return instance


def calculate_energy_requirement_reduction_by_condition(
        energy_requirements: float,
        condition_reduction: pd.DataFrame,
        building_category,
        tek,
        purpose
) -> pd.DataFrame:
    """
    Calculate the reduced energy requirements for building_category, TEK, purpose for every conditions.

    Parameters
    ----------
    energy_requirements : pd.DataFrame
        DataFrame containing the energy requirements for different buildings.
        Must include columns: 'building_category', 'TEK', 'purpose', ' kwh_m2'.
    condition_reduction : pd.DataFrame
        DataFrame containing the reduction conditions.
        Must include columns: 'building_condition', 'reduction'.
    building_category, : BuildingCategory | str
        the requirements building category
    tek : str
        name of requirement tek
    purpose : str
        The purpose of the requirement

    Returns
    -------
    pd.DataFrame
        DataFrame with the reduced energy requirements.
        Includes columns: 'building_category', 'TEK', 'purpose', 'building_condition', ' kwh_m2'.
    """
    df = condition_reduction
    df['kwh_m2'] = energy_requirements
    df['TEK'] = tek
    df['purpose'] = purpose
    df['building_category'] = building_category

    df.kwh_m2 = df.kwh_m2 * (1.0 - df['reduction_share'])

    return df[['building_category',
               'TEK',
               'purpose',
               'building_condition',
               'kwh_m2']]


def calculate_proportional_energy_change_based_on_end_year(
        energy_requirements: pd.Series,
        requirement_at_period_end: typing.Union[float, None],
        period: YearRange) -> pd.Series:
    """
    Calculate proportional energy savings to a Pandas Series over a specified period.

    Parameters
    ----------
    energy_requirements : pd.Series
        A Pandas Series containing the initial energy requirements. The index must correspond to years
    requirement_at_period_end : float
        The energy requirement at the end of the period.
    period : YearRange
        A named tuple containing the start and end years of the period used for the proportional energy change.

    Returns
    -------
    pd.Series
        A Pandas Series with the energy requirements adjusted proportionally over the specified period.
    Raises
    ------
    ValueError
        If period is a subset of the years in the energy_requirements index.
    """
    if requirement_at_period_end is None:
        return energy_requirements
    if not all(year in energy_requirements.index for year in period):
        msg = f'Did not find all years from {period.start} - {period.end} in energy_requirements'
        raise ValueError(msg)

    kwh_m2 = energy_requirements.copy()
    # Ensure values beyond the period end are set to the end requirement
    kwh_m2.loc[period.end:] = requirement_at_period_end
    # Apply linear interpolation for the period
    kwh_m2.loc[period] = np.linspace(
        kwh_m2.loc[period.start],
        requirement_at_period_end,
        len(period))

    return kwh_m2


def calculate_energy_requirement_reduction(
        energy_requirements: pd.Series,
        yearly_reduction: float,
        reduction_period: YearRange) -> pd.Series:
    """
    Calculate the energy requirement reduction over a specified period.

    Parameters
    ----------
    energy_requirements : pd.Series
        A pandas Series containing the initial energy requirements.
    yearly_reduction : float
        The yearly reduction rate (e.g., 0.1 for 10% reduction).
    reduction_period : pd.Index
        The period over which the reduction is applied.

    Returns
    -------
    pd.Series
        A pandas Series with the reduced energy requirements over the specified period.
    """
    if not all(year in energy_requirements.index for year in reduction_period):
        msg = f'Did not find all years from {reduction_period.start} - {reduction_period.end} in energy_requirements'
        raise ValueError(msg)
    kwh_m2 = energy_requirements.copy()
    reduction_factor = 1.0 - yearly_reduction

    reduction_factors = pd.Series([reduction_factor] * len(reduction_period)).cumprod()
    reduction_factors.index = reduction_period
    kwh_m2.loc[reduction_period] = round((kwh_m2.loc[reduction_period] * reduction_factors), 14)

    return kwh_m2


def calculate_lighting_reduction(energy_requirement: pd.Series,
                                 yearly_reduction: float,
                                 end_year_energy_requirement: float,
                                 interpolated_reduction_period: YearRange = YearRange(2018, 2030),
                                 year_range: YearRange = YearRange(2010, 2050)):
    """
        Calculate the lighting energy requirement reduction over a specified period.

        Parameters
        ----------
        energy_requirement : pd.Series
            The initial energy requirements for lighting.
        yearly_reduction : float
            The yearly reduction rate in energy requirements.
        end_year_energy_requirement : float
            The target energy requirement by the end of the interpolated reduction period.
        interpolated_reduction_period : YearRange, optional
            The period over which the energy requirement is interpolated to reach the end year requirement.
            Default is YearRange(2018, 2030).
        year_range : YearRange, optional
            The overall period for the calculation. Default is YearRange(2010, 2050).

        Returns
        -------
        pd.Series
            The calculated lighting energy requirements over the specified period.

        Notes
        -----
        This function first calculates the proportional energy change based on the end year requirement
        and then applies a yearly reduction rate to determine the final energy requirements.
"""

    proportional_reduced_energy_requirement = calculate_proportional_energy_change_based_on_end_year(
        energy_requirements=energy_requirement,
        requirement_at_period_end=end_year_energy_requirement,
        period=interpolated_reduction_period)

    lighting = calculate_energy_requirement_reduction(
        energy_requirements=proportional_reduced_energy_requirement,
        yearly_reduction=yearly_reduction,
        reduction_period=YearRange(interpolated_reduction_period.end + 1, year_range.end))

    return lighting


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
    # df = pd.concat([s for s in er.calculate_energy_requirements()])
    # print(df)
    logger.error('DONE')
    os.startfile(xlsx_filename, 'open')


if __name__ == '__main__':
    main()
