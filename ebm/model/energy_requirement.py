import itertools
import typing

from loguru import logger
import numpy as np
import pandas as pd

from ebm.model import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement_filter import EnergyRequirementFilter
from ebm.model.filter_tek import FilterTek


class EnergyRequirement:
    """
    """

    # TODO: add input params for yearly efficiency improvements and policy measure improvements
    def __init__(self,
                 tek_list: typing.List[str],
                 period: YearRange = YearRange(2010, 2050),
                 calibration_year: int = 1999):
        self.tek_list = tek_list
        self.period = period
        self.calibration_year = calibration_year
        if calibration_year == period.start:
            logger.trace(f'Calibration year {calibration_year} is same as start year {period.start}')
        elif calibration_year not in period.subset(1):
            logger.debug(f'Calibration year {calibration_year} is outside period {period.start}-{period.end}')


    def calculate_for_building_category(self,
                                        building_category: BuildingCategory,
                                        database_manager: DatabaseManager = None) -> typing.Iterable[pd.Series]:
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
        er_filter = EnergyRequirementFilter.new_instance(building_category, database_manager)
        heating_rv_factor = database_manager.get_calibrate_heating_rv()
        
        for tek, purpose in itertools.product(FilterTek.get_filtered_list(building_category, self.tek_list),
                                              [str(p) for p in EnergyPurpose]):
            energy_requirement_original_condition = er_filter.get_original_condition(tek=tek, purpose=purpose)
            yearly_improvements = er_filter.get_yearly_improvements(tek=tek, purpose=purpose)
            reduction_share = er_filter.get_reduction_per_condition(purpose=purpose, tek=tek)
            policy_improvement = er_filter.get_policy_improvement(tek=tek, purpose=purpose)

            requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
                energy_requirements=energy_requirement_original_condition,
                condition_reduction=reduction_share,
                building_category=building_category,
                tek=tek,
                purpose=purpose)

            heating_reduction = pd.merge(left=requirement_by_condition,
                                         right=pd.DataFrame({'year': self.period.year_range}),
                                         how='cross')

            for building_condition in BuildingCondition.existing_conditions():
                if policy_improvement:
                    kwh_m2 = heating_reduction[
                        heating_reduction['building_condition'] == building_condition].copy().set_index('year').kwh_m2
                    kwh_m2.name = 'kwh_m2'
                    energy_req_end = kwh_m2.iloc[0] * (1.0 - policy_improvement[1])
                    lighting = calculate_lighting_reduction(kwh_m2,
                                                            yearly_reduction=yearly_improvements,
                                                            end_year_energy_requirement=energy_req_end,
                                                            interpolated_reduction_period=policy_improvement[0],
                                                            year_range=self.period)
                    heating_reduction.loc[
                        heating_reduction['building_condition'] == building_condition, 'kwh_m2'] = lighting.values
                else:
                    kwh_m2 = heating_reduction[
                        heating_reduction['building_condition'] == building_condition].copy().set_index('year').kwh_m2
                    kwh_m2.name = 'kwh_m2'
                    improvement = calculate_energy_requirement_reduction(
                        kwh_m2,
                        yearly_improvements,
                        YearRange(self.calibration_year + 1, self.period.end))

                    heating_reduction.loc[
                        heating_reduction['building_condition'] == building_condition, 'kwh_m2'] = improvement.values

                result = heating_reduction.loc[heating_reduction['building_condition'] == building_condition]
                result = result.set_index(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])

                yield result.kwh_m2

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

        for building_category in building_categories:
            yield from self.calculate_for_building_category(building_category)

    @staticmethod
    def new_instance(period, calibration_year, database_manager=None):
        # Warn about non-standard calibration year
        if period.start != 2010 and calibration_year != calibration_year:
            logger.warning(f'EnergyRequirements {period.start=} {calibration_year=}')
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        return EnergyRequirement(tek_list=dm.get_tek_list(), period=period, calibration_year=calibration_year)


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


if __name__ == '__main__':
    er = EnergyRequirement.new_instance(YearRange(2020, 2050), calibration_year=2020)
    df = pd.concat([s for s in er.calculate_energy_requirements()])
    print(df)
    