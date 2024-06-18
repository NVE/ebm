class SCurve():
    """
    Calculates S-curve per renovation state.
    """ 
       
    def __init__(self, input_df):
        
        #TODO: 
        # - move building_lifetime to congif?
        # - add negative values checks
        # - change input_df so that the class takes the parameters or datastructure with params, where dtype is pre-defined. Filtering can be done in DB manager.
        # - create instance variables dynamically from column names? or change to constans? -> change to constans for now
        # - change name of methods to be more accurate, e.g. the current s-curve method (snakk med Benedicte)
        # - change s_curve method to only return a list of shares? The year key in the dict is not necessary in further calculations. -> YES, change this.

        self._building_lifetime = 130
        self._earliest_renovation_age = int(self._get_input_value(input_df, 'earliest_renovation_age'))
        self._average_age = int(self._get_input_value(input_df, 'average_age'))
        self._last_renovation_age = int(self._get_input_value(input_df, 'last_renovation_age'))
        self._rush_period_years = int(self._get_input_value(input_df, 'rush_period_years'))
        self._rush_share = self._get_input_value(input_df, 'rush_share')
        self._never_share = self._get_input_value(input_df, 'never_share')

        # Calculate yearly rates
        self._pre_rush_rate, self._rush_rate, self._post_rush_rate = self._calculate_yearly_rates()     #TODO: divide into three separate methods
        
        # Calculate S-curves
        self.rates_per_year = self.get_rates_per_year_over_building_lifetime() 
        self.s_curve = self.calculate_s_curve() 

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

    def _calculate_yearly_rates(self):
        """
        Calculate yearly renovation rates from input parameters.
         
        Yearly rates represent the percentage share of area that is renovated per year in 
        different periods along the S-curve. 

        Returns:
        - pre_rush_rate (float): Yearly renovation rate in the pre-rush period.
        - rush_rate (float): Yearly renovation rate in the rush period.
        - post_rush_rate (float): Yearly renovation rate in the post-rush period.
        """
        pre_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._average_age - self._earliest_renovation_age - (self._rush_period_years/2)))
        rush_rate = self._rush_share / self._rush_period_years
        post_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._last_renovation_age - self._average_age - (self._rush_period_years/2)))
        
        return pre_rush_rate, rush_rate, post_rush_rate

    def get_rates_per_year_over_building_lifetime(self):
        """
        Create a dictionary that holds the yearly renovation rates over the building lifetime.

        This method defines the periods in the S-curve, adds the yearly renovation rates to
        the corresponding periods and stores them in a dictionary. 

        Returns:
        - rates_per_year_dict (dict): Dictionary with 'Year' and 'Rate' keys containing the years and corresponding rates.
        """

        # Define the length of the different periods in the S-curve
        earliest_years = self._earliest_renovation_age - 1
        pre_rush_years = int(self._average_age - self._earliest_renovation_age - (self._rush_period_years/2))
        rush_years = self._rush_period_years
        post_rush_years = int(self._last_renovation_age - self._average_age - (self._rush_period_years/2))
        last_years = self._building_lifetime - earliest_years - pre_rush_years - rush_years - post_rush_years
        
        # Redefine periods for Demolition, as the post_rush_year calculation isn't the same as for Small measures and Rehabilition
        if last_years < 0:
            last_years = 0 
            post_rush_years = self._building_lifetime - earliest_years - pre_rush_years - rush_years

        # Create dict where the yearly rates are placed according to their corresponding period in the buildings lifetime 
        years = list(range(1, self._building_lifetime + 1))
        rates = (
            [0] * earliest_years + 
            [self._pre_rush_rate] * pre_rush_years +
            [self._rush_rate] * rush_years +
            [self._post_rush_rate] * post_rush_years +
            [0] * last_years
        )  
        
        # Use tuples due to immutability
        years = tuple(years)
        rates = tuple(rates)

        rates_per_year_dict = {'year': years, 'rate': rates}
        
        return rates_per_year_dict

    def calculate_s_curve(self):
        """
        Calculates S-curve by accumulating the yearly renovation rates over the building lifetime.

        Returns:
        - s_curve_dict (dict): Dictionary with 'year' and 'rate' keys containing the years and accumulated rates of the S-curve.
        """
        years = self.rates_per_year['year']
        rates = self.rates_per_year['rate']
        
        # Iterate over the rates and accumulate them in a list
        accumulated_rates = []
        acc_rate = 0
        for rate in rates:
            acc_rate += rate
            accumulated_rates.append(acc_rate)

        # Use tuples due to immutability
        accumulated_rates = tuple(accumulated_rates)

        s_curve_dict = {'year': years, 'rate': accumulated_rates}

        return s_curve_dict
    