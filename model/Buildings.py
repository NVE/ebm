from DatabaseManager import *
from SCurve import *
from Tek import *
import re

class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """

    #TODO:
    # - add a get_shares_per_tek class that gets shares per tek for all renovation states

    def __init__(self, building_category):
        
        self.building_category = building_category
        self.database = DatabaseManager()
        self.condition_list = self.database.get_condition_list()
        self.tek_id_list = self.database.get_tek_id_list()
        self._set_s_curve_per_condition()
        self.s_curve_params = self._s_curve_params()

        # Set the class variable in TEK class
        TEK.set_s_curve_params(self.s_curve_params)

    # TODO: create an alternative method to get s curve data. the parameters are not needed in this class, but should be accesible for users
    def _set_s_curve_per_condition(self):
        """
        Get input parameters for each building condition, calculate the corresponding S-curve
        and set as instance variable.

        Returns:
        - instance variable of S-curve (dict) per building condition. 
        """
        for condition in self.condition_list:
            # Get input parameters and calculate S-curve per building condition 
            input_params = self.database.get_s_curve_params_per_building_category_and_condition(self.building_category, condition)
            s_curve = SCurve(input_params).calculate_s_curve()
            
            # Convert building condition to lowercase with underscores before uppercase letters
            attr_name = condition.replace(' ', '_').lower()
            attr_name = f"s_curve_{attr_name}"

            # Create dynamic instance variables
            setattr(self, attr_name, s_curve)
    
    def _s_curve_params(self):
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
            
            # Calculate the S-curve and retrieve the "never share" parameter
            s = SCurve(input_params)
            s_curve = s.calculate_s_curve()
            never_share = s._never_share
            
            # Store the parameters in the dictionary
            s_curve_params[condition] = [s_curve, never_share]
        
        return s_curve_params

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

        small_measure_shares = {}
        for tek_id in self.tek_id_list:
            # Create TEK instance for each TEK ID
            tek = TEK(tek_id)
            
            # Calculate annual shares for small measures
            shares = tek.get_shares_small_measure_total()

            # Store the shares in the dictionary
            small_measure_shares[tek_id] = shares
        
        return small_measure_shares
    
    def get_total_renovation_shares_per_tek(self):

        renovation_shares = {}
        for tek_id in self.tek_id_list:
            # Create TEK instance for each TEK ID
            tek = TEK(tek_id)
            
            # Calculate annual shares for small measures
            shares = tek.get_shares_renovation_total()

            # Store the shares in the dictionary
            renovation_shares[tek_id] = shares
        
        return renovation_shares





      

