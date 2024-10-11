import typing

import numpy as np
import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose


class EnergyRequirement:
    """
    """

    # TODO: add input params for yearly efficiency improvements and policy measure improvements
    def __init__(self,
                 building_category: BuildingCategory,
                 energy_by_floor_area: typing.Dict[EnergyPurpose, typing.Dict[str, float]], 
                 heating_reduction: typing.Dict[str, typing.Dict[BuildingCondition, float]],
                 area_forecast: typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]],
                 tek_list: typing.List[str],   
                 # tek_params: typing.Dict[str, TEKParameters],
                 calibration_year: int = 2019,
                 period: YearRange = YearRange(2010, 2050)) -> None:
        
        self.building_category = building_category  
        self.energy_by_floor_area = energy_by_floor_area
        self.heating_reduction = heating_reduction
        self.area_forecast = area_forecast
        self.tek_list = tek_list
        #self.tek_params = tek_params                                  
        self.calibration_year = calibration_year  
        self.period = period
        
        def get_energy_req_per_condition(self, energy_req_purpose: typing.Dict[str, typing.Union[float, pd.Series]]) -> typing.Dict[str, typing.Dict[BuildingCondition, typing.Union[float, pd.Series]]]:
            """
            take dict for a single purpose and distribute the energy req values on the different building conditions (all except demoliton)
            
            Parameters
            ----------
            - dict for a single purpose (keys are TEK identifiers, values are either floats or series)  

            Returns 
            -------
            - altered purpose dict, where building condition keys are added and values are the energy requirement 

            note: 
            - the values can either be 
            """
            pass

        def calc_heating_rv_reduction(self):
            """
            reduce Heating RV according to rates in heating_reduction data.
            - match tek and building condition and perform calculation
            - calculation: energy_req * (1 - rate)

            note:
            - regarding matching of TEK's: if TEK string in heating_reduction data does not match, then default is used 
            """
            pass

        def calc_energy_req_effeciency_improvement_rates(self):
            """
            calculate yearly energy req by taking the original energy req and adjusting for yearly efficiency improvements

            - this method will only be called for the purposes that have efficiency improvements specified in the input data and
            do not have a policy measure specified in the input data 
            - the effiency improvements are applied similarly across building conditions, so the incoming data does not need be per condition

            calculation method:
                - there is no efficiency improvements before after the calibration year
                - after the calibration year, the original energy req is multiplied by: (1 - efficiency rate)^(current year - calibration year)

            Returns 
            -------
            series or dict with series
                series: indexed by model years and the value is the adjusted energy requirement (kwh_m2) 
            """
            pass

        def calc_energy_req_policy_measure_improvements(self):
            """
            calculate yearly energy req by adjusting for the efficiency improvements of the policy measure, and adjusting
            for yearly efficiency improvements in the years that the policy measure doesn't apply  

            - this method will only be called for the purposes that have a policy measure specified in the input data
            - the effiency improvements are applied similarly across building conditions, so the incoming data does not need be per condition 

            calculation method:
                - there is no efficiency improvements before after the calibration year
                - policy period: interpolate to distribute the efficiency improvement of the policy across the 
                  policy period. 
                - outside of policy period (and after calibration year): adjust the energy req according to the yearly
                  efficiency improvement rate. TODO: Check if this should be applied as with the other method or as in BEMA, as they are different.    

            Returns 
            -------
            series or dict with series
                series: indexed by model years and the value is the adjusted energy requirement (kwh_m2) 
            """
            pass

        def calc_energy_req_per_year(self):
            """
            "main" function to calculate the energy requirement per year for each purpose, tek and building condition
            
            This method should determine the appropriate calculation method that should be called for each purpose based on
            the parameters in the different input data that is given to this class. Steps and calculations:

            1. all energy requirement data must be converted to series, where the value is repeated n periods corresponding
            to the model years

            2. checks on purpose and input data to decide which calculation should be performed.
                - if purpose is heating_rv, then perform that calculation. Or alter the input data to also have a purpose identifier to search for. 
                    - must first convert data to have the 4 building conditions 
                - if purpose is in yearly_improvements data, then perform that calculation from after the calibration year
                - check if purpose is in policy measure, then perform that calculation for the period specified by the years in the input
                    - both of the calculations are regardless of the condition, so only performed on the initial value. After the series is calculated,
                    building conditions can be added (same series for all conditions)

            3. after calculations method is decided, the calculations should be performed for each tek.
               - check if the TEK is present in the relevant input data, if not use the 'default' value
               
            """
            pass


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
        requirement_at_period_end: float,
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
