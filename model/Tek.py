from DatabaseManager import *
from Buildings import *
import re

class TEK():
    
    def __init__(self, tek_id, s_curve_params):
        
        self.id = tek_id
        self.database = DatabaseManager()
        self.tek_id_params = self.database.get_tek_params_per_id(tek_id)
        self.building_year = self._get_input_value(self.tek_id_params, 'building_year')
        self.s_curve_params = s_curve_params
        self._set_s_curve_param_variables()

    def _get_input_value(self, df, col):
        """
        Retrieve a value from a specified column in a Pandas DataFrame.

        Parameters:
        - df (pd.DataFrame): The input Pandas DataFrame from which to retrieve the value.
        - col (str): The name of the column from which to retrieve the value.

        Returns:
        - value: The value from the specified column in the first row of the DataFrame.

        Raises:
        - KeyError: If the specified column does not exist in the DataFrame.
        - IndexError: If the DataFrame is empty.
        """
        value = df.loc[df.index[0], col]
        return value

    def _set_s_curve_param_variables(self):
        """
        Get S-curve parameters per renovation type from input dictionary and set as instance variables.

        This method retrieves values from the self.s_curve_params dictionary. This is a dictionary where the
        keys are renovation types and values are lists containing the S-curve and the "never share" parameter.
        After retrieving the values, the method sets dynamic instance variables for each renovation type:
        - s_curve_<renovation_type>: Stores the S-curve.
        - never_share_<renovation_type>: Stores the "never share" parameter.
        
        Example:

        If the renovation type is 'SmallMeasures', the method will create instance variables:
            - self.s_curve_small_measures
            - self.never_share_small_measures
        """
        for key in self.s_curve_params:
            # Get values from dictionary 
            values = self.s_curve_params[key]
            s_curve = values[0]
            never_share = values[1]

            # Convert renovation type (key) to lowercase with underscores before uppercase letters
            renovation_type = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower() 

            # Create dynamic instance variables
            setattr(self, f"s_curve_{renovation_type}", s_curve)
            setattr(self, f"never_share_{renovation_type}", never_share)


        

    def get_demolition_s_curve(self):
        pass
    
#TEST

d = DatabaseManager()
l = d.get_tek_id_list()
tek_id = l[0]

s = Buildings('SmallHouse')
s_curve_params = s.s_curve_params_dict

t = TEK(tek_id, s_curve_params)
#print(t.s_curve_demolition)




    