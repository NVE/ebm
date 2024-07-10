import typing
import re

from .database_manager import DatabaseManager
from .scurve import SCurve
from .tek import TEK
from .shares_per_condition import SharesPerCondition

# TODO: 
# add years list to scurve dict and shares per condition: years = list(range(1, self._building_lifetime + 1))


class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """

    # Constants used in _filter_tek_list. Remove when model is updated with new 2020 data
    CATEGORY_APARTMENT = 'apartment_block'
    CATEGORY_HOUSE = 'house'
    COMMERCIAL_BUILDING = 'COM'
    RESiDENTIAL_BUILDING = 'RES'
    APARTMENT_PRE_TEK49 = 'PRE_TEK49_RES1'
    HOUSE_PRE_TEK49 = 'PRE_TEK49_RES2'

    def __init__(self, building_category: str):
        
        self.building_category = building_category
        self.database = DatabaseManager()
        self.tek_list = self._filter_tek_list(self.database.get_tek_list())  
        self.tek_params = self.database.get_tek_params(self.tek_list)
        self.condition_list = self.database.get_condition_list()
        self.scurve_data = self._get_scurve_data()
        self.shares_per_condition = self.get_shares()

    def _filter_tek_list(self, tek_list: typing.List[str]) -> typing.List[str]:
        """
        Filters the provided TEK list based on the building category.

        Parameters:
        - tek_list (List[str]): List of TEK strings to be filtered.

        Returns:
        - filtered_tek_list (List[str]): Filtered list of TEK strings.
        """
        residential_building_list = [self.CATEGORY_APARTMENT, self.CATEGORY_HOUSE]
        
        if self.building_category in residential_building_list:
            # Filter out all TEKs associated with commercial buildings
            filtered_tek_list = [tek for tek in tek_list if self.COMMERCIAL_BUILDING not in tek]

            # Further filtering based on the specific residential building category
            if self.building_category == self.CATEGORY_APARTMENT:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != self.HOUSE_PRE_TEK49]
            elif self.building_category == self.CATEGORY_HOUSE:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != self.APARTMENT_PRE_TEK49]

        else:
            # Filter out all TEKs associated with residential buildings
             filtered_tek_list = [tek for tek in tek_list if self.RESiDENTIAL_BUILDING not in tek]

        return filtered_tek_list
            
    def _get_scurve_data(self) -> typing.Dict:
        """
        Create a dictionary that holds S-curves and the "never share" parameter per building condition. 

        This method retrieves input parameters for each building condition, calculates the S-curve,
        and stores the S-curve along with the "never share" parameter in a dictionary. The dictionary 
        is used as an input argument in the TEK class. 

        Returns:
        - scurve_data (dict): A dictionary where keys are building conditions (str) and values 
                              are lists containing the S-curve tuple and the "never share" parameter (float).
        """
        scurve_data = {}

        # Retrieve dictionary with S-curve parameters for the given building category and condition list
        scurve_params = self.database.get_scurve_params_per_building_category(self.building_category, self.condition_list)

        for condition in self.condition_list:

            # Filter S-curve parameters dictionary on condition
            scurve_params_condition = scurve_params[condition]
            
            # Calculate the S-curve 
            s = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                       scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share)
            scurve = s.calc_scurve()
            
            # Store the parameters in the dictionary
            scurve_data[condition] = [scurve, scurve_params_condition.never_share]
        
        return scurve_data

    def get_scurve(self, condition: str) -> typing.Dict:
        """
        Get the S-curve data for a specific building condition.

        This method retrieves the S-curve data for a specified building condition from the 
        `scurve_data` dictionary, which contains the precomputed S-curve for each condition.

        Parameters:
        - condition (str): The condition for which to retrieve the S-curve data (e.g., 'Renovation', 'Demolition').

        Returns:
        - scurve (dict): A dictionary containing the S-curve data for the specified condition.
                         The dictionary has 'year' as keys representing the years in the building
                         lifetime and 'scurve' as values representing the corresponding S-curve values.
        """
        scurve_list = self.scurve_data[condition][0]
        year_list = list(range(1, len(scurve_list) + 1))
        scurve = {'year':year_list, 'scurve':scurve_list}
        return scurve

    def get_shares(self) -> typing.Dict:
        """ 
        Calculate the shares per condition for all TEKs in the building category.

        This method initializes the `SharesPerCondition` class with the TEK list, TEK parameters,
        and S-curve data, and retrieves the shares per condition for the building category.

        Returns:
        - shares_condition (dict): A dictionary where the keys are the condition names and the values are
                                   the shares per condition for each TEK.
        """
        shares_condition = SharesPerCondition(self.tek_list, self.tek_params, self.scurve_data).shares_per_condition
        return shares_condition   

    def get_shares_per_condition(self, condition: str) -> typing.Dict:
        """
        Get the shares for a specific condition for all TEKs in the building category.

        This method retrieves the shares for a specified condition from the `shares_per_condition`
        dictionary, which contains the shares per condition for each TEK.

        Parameters:
        - condition (str): The condition for which to retrieve the shares (e.g., 'Renovation', 'Demolition').

        Returns:
        - shares (dict): A dictionary where the keys are the TEKs and the values are the shares for the specified condition.
        """
        shares = self.shares_per_condition[condition]
        return shares