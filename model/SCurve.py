class SCurve():
    """
    Calculates S-curve per renovation state.
    """ 
       
    def __init__(self, input_df):
        
        #TODO: 
        # - move building_lifetime to congif?
        # - create instance variables dynamically from column names?
        # - change building_type to building_category (in input and code)?
        # - change name of methods to be more accurate, e.g. the current s-curve method (snakk med Benedicte)

        self._building_lifetime = 130
        self._earliest_renovation_age = int(self._get_input_value(input_df, 'earliest_renovation_age'))
        self._average_age = int(self._get_input_value(input_df, 'average_age'))
        self._last_renovation_age = int(self._get_input_value(input_df, 'last_renovation_age'))
        self._rush_period_years = int(self._get_input_value(input_df, 'rush_period_years'))
        self._rush_share = self._get_input_value(input_df, 'rush_share')
        self._never_share = self._get_input_value(input_df, 'never_share')

        # Calculate yearly rates
        self._pre_rush_rate, self._rush_rate, self._post_rush_rate = self._calculate_yearly_rates() 
        
        # Calculate S-curves
        self.s_curve = self.calculate_s_curve() 
        self.s_curve_acc = self.calculate_s_curve_acc() 

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

    def calculate_s_curve(self):
        """
        Calculates S-curves.

        This method defines the periods in the S-curve, adds the yearly renovation rates to
        the corresponding periods and stores them in a dictionary. 

        Returns:
        - s_curve_dict (dict): Dictionary with year and yearly rates.
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

        s_curve_dict = {'Year': years, 'Rate': rates}
        
        return s_curve_dict

    def calculate_s_curve_acc(self):
        """
        Calculates accumulated S-curve.

        Returns:
        - s_curve_acc_dict (dict): Dictionary with year and accumulated rates.
        """
        years = self.s_curve['Year']
        rates = self.s_curve['Rate']

        accumulated_rates = (sum(rates[:i+1]) for i in range(len(rates)))
        s_curve_acc_dict = {'Year': years, 'Accumulated Rate': accumulated_rates}

        return s_curve_acc_dict
    