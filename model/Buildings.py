from DatabaseManager import *
from SCurve import *
#from Tek import TEK
import re

class Buildings():

    def __init__(self, building_type):
        
        self.building_type = building_type
        self.database = DatabaseManager()
        self.renovation_type_list = self.database.get_renovation_type_list()
        self._set_s_curve_per_renovation_type()
        self.s_curve_params_dict = self._s_curve_params_dict()
        self.tek_id_list = self.database.get_tek_id_list()

    # TODO: remove method or create an alternative method to get s curve data
    def _set_s_curve_per_renovation_type(self):
        """
        Get input parameters for each renovation type, calculate the corresponding S-curve
        and set as instance variable.

        Returns:
        - instance variable of accumulated S-curve (dict) per renovation type. 
        """
        for renovation_type in self.renovation_type_list:
            # Get input parameters and calculate accumulated S-curve per renovation type 
            input_params = self.database.get_s_curve_params_per_building_and_renovation_type(self.building_type, renovation_type)
            acc_s_curve = SCurve(input_params).calculate_s_curve_acc()
            
            # Convert renovation type to lowercase with underscores before uppercase letters
            attr_name = re.sub(r'(?<!^)(?=[A-Z])', '_', renovation_type).lower()
            attr_name = f"acc_s_curve_{attr_name}"

            # Create dynamic instance variables
            setattr(self, attr_name, acc_s_curve)
    
    def _s_curve_params_dict(self):
        """
        Create a dictionary that holds S-curves and the "never share" parameter per renovation type. 

        This method retrieves input parameters for each renovation type, calculates the S-curve,
        and stores the S-curve along with the "never share" parameter in a dictionary. The dictionary 
        is used as an input argument in the TEK class. 

        Returns:
        - s_curve_params (dict): A dictionary where keys are renovation types (str) and values 
                                 are lists containing the S-curve dictionary and the "never share" parameter (float).
        """
        s_curve_params = {}

        for renovation_type in self.renovation_type_list:
            # Retrieve input parameters for the given building type and renovation type
            input_params = self.database.get_s_curve_params_per_building_and_renovation_type(self.building_type, renovation_type)
            
            # Calculate the S-curve and retrieve the "never share" parameter
            s = SCurve(input_params)
            s_curve = s.calculate_s_curve_acc()
            never_share = s._never_share
            
            # Store the results in the dictionary
            s_curve_params[renovation_type] = [s_curve, never_share]
        
        return s_curve_params

    def get_s_curves_per_tek(self):
        #for tek_id in self.tek_id_list:
            #tek = Tek(tek_id)
        pass

