import typing

import pandas as pd

from .scurve import SCurve
from .data_classes import ScurveParameters
from .building_condition import BuildingCondition

# TODO:
# - add methods for retrieving yearly measure rates, which could be useful to print to output
# - consider integrating the FilterScurveParams method in this class
# - add control method that controls that the building conditions are those specified in the StrEnum for scurve_condition_list?

class ScurveProcessor:
    """    
    Processes and retrieves S-curve data for different building conditions.

    This class is responsible for handling the data flow related to S-curve calculations. 
    It retrieves the necessary parameters, calculates the S-curves for specified building conditions, 
    and provides access to the calculated S-curves and other related parameters.
    """

    def __init__(self, 
                 scurve_condition_list: typing.List[str],
                 scurve_params: typing.Dict[str, ScurveParameters]):
        
        self.scurve_condition_list = scurve_condition_list
        self.scurve_params = scurve_params

    
    def get_scurve_for_condition(self, building_condition: str) -> ScurveParameters:
        """
        Calculate and return the S-curve for a specific building condition.

        Parameters:
        - building_condition (str): The name of the building condition for which to calculate the S-curve.

        Returns:
        - pd.Series: A pandas Series representing the S-curve for the specified building condition, 
                     with the index representing the age of the building.
        """
        if building_condition not in self.scurve_params:
            msg = f'Encountered unknown building condition {building_condition} while making scurve'
            raise KeyError(msg)

        # Filter scurve params on building_condition
        scurve_params_condition = self.scurve_params[building_condition]

        # Calculate the S-curve 
        s = SCurve(
            scurve_params_condition.earliest_age, 
            scurve_params_condition.average_age, 
            scurve_params_condition.last_age,
            scurve_params_condition.rush_years, 
            scurve_params_condition.rush_share, 
            scurve_params_condition.never_share)
        
        scurve = s.calc_scurve()

        return scurve
    
    def get_never_share_for_condition(self, building_condition: str) -> float:
        """
        Retrieve the 'never_share' parameter for a specific building condition.

        Parameters:
        - building_condition (str): The name of the building condition for which to retrieve the 'never_share' parameter.

        Returns:
        - float: The 'never_share' parameter value for the specified building condition.
        """
        if building_condition not in self.scurve_params:
            msg = f'Encountered unknown building condition {building_condition} while retrieving the never share parameter'
            raise KeyError(msg)
    
        # Filter scurve params on building_condition
        scurve_params_condition = self.scurve_params[building_condition]

        # Retrieve never share for the given condition
        never_share = scurve_params_condition.never_share

        return never_share
    
    def get_scurves(self) -> typing.Dict[str, pd.Series]:
        """
        Generate a dictionary containing S-curves for all specified building conditions.

        Returns:
        - Dict[str, pd.Series]: A dictionary where the keys are building condition names and 
                                the values are pandas Series representing the S-curves.
        """
        scurves = {}
        for condition in self.scurve_condition_list:
            scurves[condition] = self.get_scurve_for_condition(condition) 

        return scurves
    
    def get_never_shares(self) -> typing.Dict[str, float]:
        """
        Generate a dictionary containing 'never_share' parameters for all specified building conditions.

        Returns:
        - Dict[str, float]: A dictionary where the keys are building condition names and 
                            the values are the 'never_share' parameter values.
        """
        never_shares = {}
        for condition in self.scurve_condition_list:
            never_shares[condition] = self.get_never_share_for_condition(condition)
        
        return never_shares