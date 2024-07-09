import typing
import re

from .database_manager import DatabaseManager
from .scurve import SCurve
from .tek import TEK
from .shares_per_condition import SharesPerCondition


class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """
    
    #TODO:
    # - add method to control tek_list and use it when setting instance var of tek_list

    def __init__(self, building_category):
        
        self.building_category = building_category
        self.database = DatabaseManager()
        self.condition_list = self.database.get_condition_list()
        self.tek_list = self.database.get_tek_list() 
        self.tek_params = self.database.get_tek_params(self.tek_list)

        self.scurve_data = self._get_scurve_data()
        self.shares_per_condition = self.get_shares()
            
    def _get_scurve_data(self) -> typing.Dict:
        """
        Create a dictionary that holds S-curves and the "never share" parameter per building condition. 

        This method retrieves input parameters for each building condition, calculates the S-curve,
        and stores the S-curve along with the "never share" parameter in a dictionary. The dictionary 
        is used as an input argument in the TEK class. 

        Returns:
        - scurve_data (dict): A dictionary where keys are building conditions (str) and values 
                              are lists containing the S-curve dictionary and the "never share" parameter (float).
        """
        scurve_data = {}

        for condition in self.condition_list:

            # Retrieve input parameters for the given building category and condition
            input_params = self.database.get_scurve_params_per_building_category_and_condition(self.building_category, condition)
            
            # Calculate the S-curve 
            s = SCurve(input_params.earliest_age, input_params.average_age, input_params.last_age, 
                       input_params.rush_years, input_params.rush_share, input_params.never_share)
            scurve = s.calc_scurve()
            
            # Store the parameters in the dictionary
            scurve_data[condition] = [scurve, input_params.never_share]
        
        return scurve_data

    def get_scurve(self, condition: str) -> typing.Dict:
        """
        Get the S-curve data for a specific building condition.

        This method retrieves the S-curve data for a specified building condition from the 
        `scurve_data` dictionary, which contains the precomputed S-curve for each condition.

        Parameters:
        - condition (str): The condition for which to retrieve the S-curve data (e.g., 'Renovation', 'Demolition').

        Returns:
        - scurve (dict): A dictionary containing the S-curve data for the specified condition.. 
        """
        scurve = self.scurve_data[condition][0]
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