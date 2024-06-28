import typing
from .database_manager import DatabaseManager
from .scurve import SCurve
from .tek import TEK
import re


class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """
    
    #TODO:
    # - add a get_shares_per_tek class that gets shares per tek for all renovation states

    # Keys in S-curve parameter dictionary
    KEY_EARLIEST_AGE = 'earliest_age_for_measure'
    KEY_AVERAGE_AGE = 'average_age_for_measure'
    KEY_LAST_AGE = 'last_age_for_measure'
    KEY_RUSH_YEARS = 'rush_period_years'
    KEY_RUSH_SHARE = 'rush_share'
    KEY_NEVER_SHARE = 'never_share'

    def __init__(self, building_category):
        
        self.building_category = building_category
        self.database = DatabaseManager()
        self.condition_list = self.database.get_condition_list()
        self.tek_id_list = self.database.get_tek_id_list()
        self.s_curve_params = self._s_curve_params()
        self._set_s_curve_per_condition()

        # Set the class variable in TEK class
        TEK.set_s_curve_params(self.s_curve_params)
            
    def _s_curve_params(self) -> typing.Dict:
        """
        Create a dictionary that holds S-curves and the "never share" parameter per building condition. 

        This method retrieves input parameters for each building condition, calculates the S-curve,
        and stores the S-curve along with the "never share" parameter in a dictionary. The dictionary 
        is used as an input argument in the TEK class. 

        Returns:
        - s_curve_params (dict): A dictionary where keys are building conditions (str) and values 
                                 are lists containing the S-curve dictionary and the "never share" parameter (float).
        """
        s_curve_params = {}

        for condition in self.condition_list:

            # Retrieve input parameters for the given building category and condition
            input_params = self.database.get_s_curve_params_per_building_category_and_condition(self.building_category, condition)
            
            # Calculate the S-curve 
            s = SCurve(input_params.earliest_age_for_measure, input_params.average_age_for_measure, input_params.last_age_for_measure, input_params.rush_period_years, input_params.rush_share, input_params.never_share)
            s_curve = s.calculate_s_curve()
            
            # Store the parameters in the dictionary
            s_curve_params[condition] = [s_curve, input_params.never_share]
        
        return s_curve_params

    # TODO: create an alternative method to get s curve data. the parameters are not needed in this class, but should be accesible for users
    def _set_s_curve_per_condition(self):
        """
        Get input parameters for each building condition, calculate the corresponding S-curve
        and set as instance variable.

        Returns:
        - instance variable of S-curve (dict) per building condition. 
        """
        for condition in self.condition_list:
            s_curve = self.s_curve_params[condition][0]
            
            # Convert building condition to lowercase with underscores before uppercase letters
            attr_name = condition.replace(' ', '_').lower()
            attr_name = f"s_curve_{attr_name}"

            # Create dynamic instance variables
            setattr(self, attr_name, s_curve)
    
    def get_demolition_shares_per_tek(self):
        """
        Calculate demolition shares for all TEK's associated with the building.

        Returns:
        - demolition_shares (dict): A dictionary where each key is a TEK ID and the corresponding 
                                    value is a list of demolition shares (float) for each year 
                                    from the start year to the end year.
        """
        demolition_shares = {}
        for tek_id in self.tek_id_list:
            # Create TEK instance for each TEK ID
            tek = TEK(tek_id)
            
            # Calculate annual demolition shares
            shares = tek.get_shares_demolition()
            
            # Store the shares in the dictionary
            demolition_shares[tek_id] = shares
        
        return demolition_shares
    
    def get_total_small_measure_shares_per_tek(self):

        total_small_measure_shares = {}
        for tek_id in self.tek_id_list:
            # Create TEK instance for each TEK ID
            tek = TEK(tek_id)
            
            # Calculate annual shares for small measures
            shares = tek.get_shares_small_measure_total()

            # Store the shares in the dictionary
            total_small_measure_shares[tek_id] = shares
        
        return total_small_measure_shares
    
    def get_total_renovation_shares_per_tek(self):

        total_renovation_shares = {}
        for tek_id in self.tek_id_list:
            # Create TEK instance for each TEK ID
            tek = TEK(tek_id)
            
            # Calculate annual shares for small measures
            shares = tek.get_shares_renovation_total()

            # Store the shares in the dictionary
            total_renovation_shares[tek_id] = shares
        
        return total_renovation_shares
    
    def get_renovation_shares_per_tek(self):
        
        renovation_shares = {}
        for tek_id in self.tek_id_list:
            tek = TEK(tek_id)
            shares = tek.get_shares_renovation()
            renovation_shares[tek_id] = shares

        return renovation_shares

    def get_small_measure_shares_per_tek(self):
        
        small_measure_shares = {}
        for tek_id in self.tek_id_list:
            tek = TEK(tek_id)
            shares = tek.get_shares_small_measure()
            small_measure_shares[tek_id] = shares

        return small_measure_shares
    
    def get_renovation_and_small_measure_shares_per_tek(self):

        renovation_small_measure_shares = {}
        for tek_id in self.tek_id_list:
            tek = TEK(tek_id)
            shares = tek.get_shares_renovation_and_small_measure()
            renovation_small_measure_shares[tek_id] = shares

        return renovation_small_measure_shares

    def get_original_condition_shares_per_tek(self):

        original_condition_shares = {}
        for tek_id in self.tek_id_list:
            tek = TEK(tek_id)
            shares = tek.get_shares_original_condition()
            original_condition_shares[tek_id] = shares

        return original_condition_shares






      

