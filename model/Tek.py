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
    # - add start and end year as input arguments? 
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
        
        self.shares_demolition = self.get_shares_demolition()
        self.shares_small_measures = self.get_shares_small_measures_total()
        self.shares_rehabilitation = self.get_shares_rehabilitation_total()

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

    def get_shares_demolition(self):
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

        # Iterate over years from start to end year
        for year in range(self.START_YEAR, self.END_YEAR + 1):
            building_age = year - self.building_year
            
            if year == self.START_YEAR or self.building_year >= year:
                # Set share to 0 in the start year and if the building isn't buildt yet
                share = 0
            elif self.building_year == year - 1:
                # Set share to the current rate/share if the building year is equal to year-1
                rate = self.s_curve_demolition['rate'][building_age - 1]
            else:
                # Get rates/shares from the demolition S-curve based on building age
                rate = self.s_curve_demolition['rate'][building_age - 1]
                prev_rate = self.s_curve_demolition['rate'][building_age - 2]

                # Calculate percentage share by subtracting rate from previous year's rate
                share = rate - prev_rate   
            
            shares.append(share)

        return shares
    
    def get_shares_small_measures_total(self):
        """
        Calculate the percentage share of area that have undergone small measures over the time horizon.

        This method calculates the percentage share of area that have undergone small measures 
        for each year from the start year to the end year. This share doesn't refer to area that 
        only have undergone a small measure, as the area may also have undergone rehabilition. 
        It uses the accumulated rates from the small measures S-curve. 

        Returns:
        - shares (list): A list of small measures renovation shares (float) for each year from the
                         start year to the end year.
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):
            building_age = year - self.building_year

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                # Get Small measures share from S-curve and demolition share for current year
                small_measure_share = self.s_curve_small_measures['rate'][building_age - 1]
                demolition_share = self.shares_demolition[idx] 
                
                # Calculate max limit for doing a renovation measure (small measure or rehabilitation)
                measure_limit = 1 - demolition_share - self.never_share_small_measures
                
                if small_measure_share < measure_limit:
                    share = small_measure_share
                else: 
                    share = measure_limit
            
            shares.append(share)
                
        return shares
    
    def get_shares_rehabilitation_total(self):
        """
        Calculate the percentage share of area that is rehabilitated over time.

        This method calculates the percentage share of rehabilitation renovations for each year 
        from the start year to the end year. It uses the accumulated rates from the rehabilitation 
        S-curve.

        Returns:
        - shares (list): A list of rehabilitation renovation shares (float) for each year from the
                         start year to the end year.
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):
            building_age = year - self.building_year

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                # Get rehabilitation share from S-curve and demolition share for current year
                rehabilitation_share = self.s_curve_rehabilitation['rate'][building_age - 1]
                demolition_share = self.shares_demolition[idx]                
                
                # Calculate max limit for doing a renovation measure (small measure or rehabilitation)
                measure_limit = 1 - demolition_share - self.never_share_rehabilitation
                
                if rehabilitation_share < measure_limit:
                    share = rehabilitation_share
                else: 
                    share = measure_limit 
            
            shares.append(share)
                
        return shares

    #def get_shares_rehabilitation():
        """
        calculation: 
        if (share_rehab_total + share_small_measure_total) < measure_limit_rehab):
            share = share_rehab_total
        elif share_small_measure_total > measure_limit:
            share = 0
        else: 
            share = measure_limit - share_small_measure_totals
        """

