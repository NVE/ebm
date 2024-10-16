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


class EnergyRequirement:
    """
    """

    # TODO: add input params for yearly efficiency improvements and policy measure improvements
    def __init__(self,
                 tek_list: typing.List[str],
                 period: YearRange = YearRange(2010, 2050),
                 calibration_year: int = 2019):
        self.tek_list = tek_list
        self.period = period
        self.calibration_year = calibration_year

        
    def get_energy_req_per_condition(
            self,
            energy_req_purpose: typing.Dict[str, typing.Union[float, pd.Series]] = None) \
            -> typing.Dict[str, typing.Dict[BuildingCondition, typing.Union[float, pd.Series]]]:
        """
        Take dict for a single purpose and distribute the energy req values on the different building conditions.
        Note: building_condition demolition cannot be used.

        Parameters
        ----------
        - dict for a single purpose (keys are TEK identifiers, values are either floats or series)

        Returns
        -------
        - altered purpose dict, where building condition keys are added and values are the energy requirement

        note:
        - the values can either be
        """

        for building_category in [b for b in BuildingCategory]:
            er_filter = EnergyRequirementFilter(building_category, DatabaseManager().get_energy_req_original_condition(
                building_category=building_category), None, None, None)
            for tek, purpose in itertools.product(self.tek_list,  [str(p) for p in EnergyPurpose]):
                if not building_category.is_residential() and 'RES' in tek:
                    continue
                if building_category.is_residential() and 'COM' in tek:
                    continue

                building_conditions = [b for b in BuildingCondition if b != BuildingCondition.DEMOLITION]

                energy_requirement_original_condition = er_filter.get_original_condition(
                    tek=tek, purpose=purpose)
                yearly_improvements = er_filter.get_yearly_improvements(tek=tek, purpose=purpose)
                reduction_share = er_filter.get_reduction_per_condition(purpose=purpose, tek=tek)
                policy_improvement = er_filter.get_policy_improvement(
                    tek=tek, purpose=purpose)

                requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
                    energy_requirements=energy_requirement_original_condition,
                    condition_reduction=reduction_share)

                heating_reduction = pd.merge(left=requirement_by_condition,
                                             right=pd.DataFrame({'year': YearRange(2010, 2050).year_range}),
                                             how='cross')

                for building_condition in building_conditions:
                    if policy_improvement[1]:
                        kwh_m2 = heating_reduction[heating_reduction['building_condition'] == building_condition].copy().set_index('year').kwh_m2
                        kwh_m2.name = 'kwh_m2'
                        energy_req_end = kwh_m2.iloc[0] * (1-0.6)
                        kwh_m2_policy = calculate_proportional_energy_change_based_on_end_year(
                            kwh_m2,
                            energy_req_end,
                            policy_improvement[0])
                        improvement = calculate_energy_requirement_reduction(
                            kwh_m2_policy,
                            yearly_improvements,
                            YearRange(2031, 2050))
                        heating_reduction.loc[
                            heating_reduction['building_condition'] == building_condition, 'kwh_m2'] = improvement.values
                    else:
                        kwh_m2 = heating_reduction[heating_reduction['building_condition'] == building_condition].copy().set_index('year').kwh_m2
                        kwh_m2.name = 'kwh_m2'
                        improvement = calculate_energy_requirement_reduction(
                            kwh_m2,
                            yearly_improvements,
                            YearRange(2018, 2050))

                        heating_reduction.loc[heating_reduction['building_condition'] == building_condition, 'kwh_m2'] = improvement.values
                yield heating_reduction

    @staticmethod
    def new_instance(database_manager=None):
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        return EnergyRequirement(tek_list=dm.get_tek_list(), period=YearRange(2010, 2050), calibration_year=2019)


def calculate_energy_requirement_reduction_by_condition(
        energy_requirements: pd.DataFrame,
        condition_reduction: pd.DataFrame
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

    Returns
    -------
    pd.DataFrame
        DataFrame with the reduced energy requirements.
        Includes columns: 'building_category', 'TEK', 'purpose', 'building_condition', ' kwh_m2'.
    """
    df = pd.merge(energy_requirements, condition_reduction, how='cross')

    df.kwh_m2 = df.kwh_m2 * (1.0 - df['reduction'])

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
    kwh_m2.loc[reduction_period] = (kwh_m2.loc[reduction_period] * reduction_factors)

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

    based_on_end_year = calculate_proportional_energy_change_based_on_end_year(
        energy_requirement,
        end_year_energy_requirement,
        interpolated_reduction_period)

    lighting = calculate_energy_requirement_reduction(
        based_on_end_year,
        yearly_reduction=yearly_reduction,
        reduction_period=YearRange(interpolated_reduction_period.end + 1, year_range.end))

    return lighting
