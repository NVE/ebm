class SCurve():
    """
    Calculates S-curve per renovation state
    """ 
       
    def __init__(self, input_df):
        
        #TODO: move building_lifetime to congif?

        self._building_lifetime = 130
        self._earliest_renovation_age = int(self._get_input_value(input_df, 'earliest_renovation_age'))
        self._average_age = int(self._get_input_value(input_df, 'average_age'))
        self._last_renovation_age = int(self._get_input_value(input_df, 'last_renovation_age'))
        self._rush_period_years = int(self._get_input_value(input_df, 'rush_period_years'))
        self._rush_share = self._get_input_value(input_df, 'rush_share')
        self._never_share = self._get_input_value(input_df, 'never_share')
        self._pre_rush_rate, self._rush_rate, self._post_rush_rate = self._calculate_yearly_rates() 
        self.s_curve = self.calculate_s_curve() 
        self.s_curve_acc = self.calculate_s_curve_acc() 

    def _get_input_value(self, df, col):
        """
        Filters input dataframe by column name and returns column value

        Parameters: 
            - df: Pandas dataframe
            - col: str 

        Returns:
            - value: filtered column value
        """
        value = df.loc[df.index[0], col]
        return value

    def _calculate_yearly_rates(self):
        """
        Calculates yearly renovation rates, which is the percentage share of area that is renovated per year in a period. 

        Returns:
            - pre_rush_rate: float, yearly renovation rate in the pre-rush period
            - rush_rate: float, yearly renovation rate in the rush period
            - post_rush_rate: float, yearly renovation rate in the post-rush period
        """
        pre_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._average_age - self._earliest_renovation_age - (self._rush_period_years/2)))
        rush_rate = self._rush_share / self._rush_period_years
        post_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._last_renovation_age - self._average_age - (self._rush_period_years/2)))
        
        return pre_rush_rate, rush_rate, post_rush_rate

    def calculate_s_curve(self):
        """
        Calculates S-curves

        Returns:
            - s_curve_dict: dict with year and yearly rates
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
        Calculates accumulated S-curve

        Returns:
            - s_curve_acc_dict: dict with year and accumulated rates 
        """
        years = self.s_curve['Year']
        rates = self.s_curve['Rate']

        accumulated_rates = (sum(rates[:i+1]) for i in range(len(rates)))
        s_curve_acc_dict = {'Year': years, 'Accumulated Rate': accumulated_rates}

        return s_curve_acc_dict
    

## TESTING
"""from DatabaseManager import *
building_type = "Apartment"
database = DatabaseManager()
input = database.get_s_curve_input(building_type, 'Rehabilitation')

s = SCurve(input)
"""