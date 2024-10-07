import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters,YearRange
from ebm.model.building_condition import BuildingCondition
from ebm.model.building_category import BuildingCategory
from ebm.model.energy_purpose import EnergyPurpose

class EnergyRequirement():
    """
    """

    #TODO: add input params for yearly efficiency improvements and policy measure improvements
    def __init__(self,
                 building_category: BuildingCategory,
                 energy_by_floor_area: typing.Dict[EnergyPurpose, typing.Dict[str, float]], 
                 heating_reduction: typing.Dict[str, typing.Dict[BuildingCondition, float]],
                 area_forecast: typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]],
                 tek_list: typing.List[str],   
                 #tek_params: typing.Dict[str, TEKParameters], 
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
            the parameters in the different input data that is given to this class.


            """
            pass
    
