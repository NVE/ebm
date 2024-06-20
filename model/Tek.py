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
    # - add checks to control calculations, for example control total values and that original condition should not exceed 100%
    # - find an alternative to the class variable for s_curve_params

    # Model parameters
    START_YEAR = 2010
    END_YEAR = 2050

    # Column names
    COL_BUILDING_YEAR = 'building_year'
    COL_TEK_START_YEAR = 'tek_period_start_year' 
    COL_TEK_END_YEAR = 'tek_period_end_year'

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
        self.building_year = self._get_input_value(self.tek_id_params, self.COL_BUILDING_YEAR)
        self.tek_start_year = self._get_input_value(self.tek_id_params, self.COL_TEK_START_YEAR)
        self.tek_end_year = self._get_input_value(self.tek_id_params, self.COL_TEK_END_YEAR)

        # Define S-curve parameter attributes for IDE recognition
        self.s_curve_small_measure = None
        self.s_curve_renovation = None
        self.s_curve_demolition = None
        self.never_share_small_measure = None
        self.never_share_renovation = None
        self.never_share_demolition = None

        # Set S-curve parameter attributes
        if TEK.s_curve_params is not None:
            self.s_curve_params = TEK.s_curve_params
            self._set_s_curve_param_variables()
        
        self.shares_demolition = self.get_shares_demolition()
        self.shares_small_measure_total = self.get_shares_small_measure_total()
        self.shares_renovation_total = self.get_shares_renovation_total()
        self.shares_renovation = self.get_shares_renovation()
        self.shares_renovation_and_small_measure = self.get_shares_renovation_and_small_measure()
        self.shares_small_measure = self.get_shares_small_measure()
        self.shares_original_condition = self.get_shares_original_condition()

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
        Get S-curve parameters per building condition from input dictionary and set as instance variables.

        This method retrieves values from the self.s_curve_params dictionary. This is a dictionary where the
        keys are building conditions and values are lists containing the S-curve and the "never share" parameter.
        After retrieving the values, the method sets dynamic instance variables for each building condition:
        - s_curve_<condition>: Stores the S-curve.
        - never_share_<condition>: Stores the "never share" parameter.
        
        Example:

        If the building condition is 'Small measure', the method will create instance variables:
            - self.s_curve_small_measure
            - self.never_share_small_measure
        """
        for key in self.s_curve_params:
            # Get values from dictionary 
            values = self.s_curve_params[key]
            s_curve = values[0]
            never_share = values[1]

            # Convert building condition (key) to lowercase with underscores before uppercase letters
            condition = key.replace(' ', '_').lower() 

            # Create dynamic instance variables
            setattr(self, f"s_curve_{condition}", s_curve)
            setattr(self, f"never_share_{condition}", never_share)

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

        # Accumulate shares over the time horizon
        accumulated_shares = []
        acc_share = 0
        for share in shares:
            acc_share += share
            accumulated_shares.append(acc_share)

        return accumulated_shares
    
    def get_shares_small_measure_total(self):
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
                # Get Small measure share from S-curve and demolition share for current year
                small_measure_share = self.s_curve_small_measure['rate'][building_age - 1]
                demolition_share = self.shares_demolition[idx] 
                
                # Calculate max limit for doing a renovation measure (small measure or rehabilitation)
                measure_limit = 1 - demolition_share - self.never_share_small_measure
                
                if small_measure_share < measure_limit:
                    share = small_measure_share
                else: 
                    share = measure_limit
            
            shares.append(share)
                
        return shares
    
    def get_shares_renovation_total(self):
        """
        Calculate the percentage share of area that is renovated over time.

        This method calculates the percentage share of renovations for each year 
        from the start year to the end year. It uses the accumulated rates from the 
        renovation S-curve.

        Returns:
        - shares (list): A list of renovation shares (float) for each year from the
                         start year to the end year.
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):
            building_age = year - self.building_year

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                # Get renovation share from S-curve and demolition share for current year
                renovation_share = self.s_curve_renovation['rate'][building_age - 1]
                demolition_share = self.shares_demolition[idx]                
                
                # Calculate max limit for doing a renovation measure (small measure or renovation)
                measure_limit = 1 - demolition_share - self.never_share_renovation
                
                if renovation_share < measure_limit:
                    share = renovation_share
                else: 
                    share = measure_limit 
            
            shares.append(share)
                
        return shares

    def get_shares_renovation(self):
        """
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                share_small_measure_total = self.shares_small_measure_total[idx]
                share_renovation_total = self.shares_renovation_total[idx]
                share_demolition = self.shares_demolition[idx]  
                measure_limit = 1- share_demolition - self.never_share_renovation 

                if (share_small_measure_total + share_renovation_total) < measure_limit:
                    share = share_renovation_total
                elif share_small_measure_total > measure_limit:
                    share = 0
                else:
                    share = measure_limit - share_small_measure_total

            shares.append(share)

        return shares

    def get_shares_renovation_and_small_measure(self):
        """
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                share_renovation_total = self.shares_renovation_total[idx]
                share_renovation = self.shares_renovation[idx]
                share = share_renovation_total - share_renovation
            
            shares.append(share)

        return shares
    
    def get_shares_small_measure(self):
        """
        """
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):

            if self.building_year >= year:
                # Set share to 0 if the building isn't buildt yet
                share = 0
            else:
                share_small_measure_total = self.shares_small_measure_total[idx]
                share_renovation_and_small_measure = self.shares_renovation_and_small_measure[idx]
                share = share_small_measure_total - share_renovation_and_small_measure
            
            shares.append(share)

        return shares
    
    def get_shares_original_condition(self):
        shares =  []

        for idx, year in enumerate(range(self.START_YEAR, self.END_YEAR + 1)):
            # Set share to 0 in years before the start year of the TEK if the TEK start year is after the start year of the model horizon
            if (self.tek_start_year > self.START_YEAR) and (year < self.tek_start_year ):
                share = 0
            else:
                share_small_measure = self.shares_small_measure[idx]
                share_renovation = self.shares_renovation[idx]
                share_renovation_and_small_measure = self.shares_renovation_and_small_measure[idx]
                share_demolition = self.shares_demolition[idx]
                share = 1 - share_small_measure - share_renovation - share_renovation_and_small_measure - share_demolition  

            shares.append(share)

        return shares             
        





