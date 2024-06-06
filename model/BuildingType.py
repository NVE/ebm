from DatabaseManager import *
from SCurve import *
import re

class BuildingType():

    def __init__(self, building_type):
        
        self.building_type = building_type
        self.database = DatabaseManager()
        self.renovation_type_list = self.database.get_renovation_type_list()

        self.create_instance_var_of_s_curve_per_renovation_type(self.renovation_type_list)

    def create_instance_var_of_s_curve_per_renovation_type(self, renovation_type_list):
        """
        Get input parameters for each renovation type, calculate the corresponding S-curve and set instance variable.

        Parameters:
            - renovation_type_list: list

        Output:
            - acc_s_curve: dict, accumulated S-curve 
        """
        for renovation_type in renovation_type_list:
            # Get input parameters and calculate accumulated S-curve per renovation type 
            input_params = self.database.get_s_curve_params_per_building_and_renovation_type(self.building_type, renovation_type)
            acc_s_curve = SCurve(input_params).calculate_s_curve_acc()
            
            # Convert renovation type to lowercase with underscores before uppercase letters
            attr_name = re.sub(r'(?<!^)(?=[A-Z])', '_', renovation_type).lower()
            attr_name = f"acc_s_curve_{attr_name}"

            # Create dynamic instance variables
            setattr(self, attr_name, acc_s_curve)

# TEST
#t = BuildingType('Apartment')
#print(t.acc_s_curve_small_measures)
            
