from DatabaseManager import *

import re

class TEK():
    """
    Holds all the attributes of a given TEK, with it's associated data and operations.

    Class Variables:
    - s_curve_params (dict): Stores S-curve parameters required for calculations. Must be set before
                             any instance methods are called.
    """
    
    # TODO: 
    # - move constants to config
    # - add negative values checks
    # - add checks to ensure that the class var s_curve_params have been properly initialized

    # Model parameters
    START_YEAR = 2010
    END_YEAR = 2050

    # Class variable to store S-curve parameters
    s_curve_params = None  

    @classmethod
    def set_s_curve_params(cls, s_curve_params):
        """
        Class method to set the s_curve_params class variable.

        Parameters:
        - s_curve_params (dict): Dictionary containing S-curve parameters for TEK calculations.
        """
        cls.s_curve_params = s_curve_params

    def __init__(self, tek_id):
        
        self.id = tek_id
        self.database = DatabaseManager()
        self.tek_id_params = self.database.get_tek_params_per_id(tek_id)
        self.building_year = self._get_input_value(self.tek_id_params, 'building_year')

        # Define S-curve parameter attributes for IDE recognition
        self.s_curve_small_measures = None
        self.s_curve_rehabilitation = None
        self.s_curve_demolition = None
        self.never_share_small_measures = None
        self.never_share_rehabilitation = None
        self.never_share_demolition = None

        # Set S-curve parameter attributes
        if TEK.s_curve_params is not None:
            self.s_curve_params = TEK.s_curve_params
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

    def get_demolition_shares(self):
        """
        Calculate the percentage share of area that is demolished over time.

        This method calculates the percentage share of demolition for each year 
        from the start year to the end year. It uses the accumulated rates from 
        the demolition S-curve to determine the share of demolition. The share 
        is calculated by subtracting the rate for the current year from the rate 
        for the previous year.

        The share is set to 0 in the start year, and if the building hasn't been
        built yet (building year of the TEK is after the current year). Additionally,
        the share is set to the rate of the current year in the building year of the 
        TEK if that year is after the start year.  

        Returns:
        - shares (list): A list of demolition shares (float) for each year from the
                         start year to the end year.

        """
        shares = []

        # Iterate over years from 2010 to 2050
        for year in range(self.START_YEAR, self.END_YEAR + 1):
            building_age = year - self.building_year
            
            if year == self.START_YEAR or self.building_year >= year:
                # Set share to 0 in the start year and if the building isn't buildt yet
                share = 0
            elif self.building_year == year - 1:
                # Set share to the current rate if the building year is equal to year-1
                rate = self.s_curve_demolition['accumulated_rate'][building_age - 1]
            else:
                # Get rates from the demolition S-curve based on building age
                rate = self.s_curve_demolition['accumulated_rate'][building_age - 1]
                prev_rate = self.s_curve_demolition['accumulated_rate'][building_age - 2]

                # Calculate percentage share by subtracting rate from previous year's rate
                share = rate - prev_rate 

            # Ensure share is non-negative
            share = max(0, share)  
            
            shares.append(share)

        return shares
    
#TEST

"""
d = DatabaseManager()
l = d.get_tek_id_list()
tek_id = l[0]

s = Buildings('SmallHouse')
s_curve_params = s.s_curve_params_dict

t = TEK(tek_id, s_curve_params)

#print(t.get_demolition_shares())
"""



    