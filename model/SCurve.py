
class SCurve():
    
    def __init__(self, input_df):
        
        #TODO: Add input validtion (loguru). For example, control that periods equal building_lifetime 

        self._building_lifetime = 130   #TODO: move to config?
        self._rush_share = self._get_input_value(input_df, 'rush_share')
        self._never_share = self._get_input_value(input_df, 'never_share')
        self._earliest_years = int(self._get_input_value(input_df, 'earliest_renovation_age') - 1)
        self._rush_years = int(self._get_input_value(input_df, 'rush_period_years'))
        self._pre_rush_years = int(self._get_input_value(input_df, 'average_age') - (self._earliest_years + 1) - (self._rush_years/2))
        self._post_rush_years = int(self._get_input_value(input_df, 'last_renovation_age') - self._get_input_value(input_df, 'average_age') - (self._rush_years/2))
        self._last_years = self._building_lifetime - self._earliest_years - self._pre_rush_years - self._rush_years - self._post_rush_years

        self._pre_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / self._pre_rush_years)
        self._post_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / self._post_rush_years)
        self._rush_rate = self._rush_share / self._rush_years

        if self._last_years < 0:
            self._last_years = 0 
            self._post_rush_years = self._building_lifetime - self._earliest_years - self._pre_rush_years - self._rush_years

        self._s_curve = self.calculate_s_curve()
        self._s_curve_acc = self.calculate_s_curve_acc() 

    def _get_input_value(self, df, col):
        value = df.loc[df.index[0], col]
        return value

    def calculate_s_curve(self):
        
        years = list(range(1, self._building_lifetime + 1))
        rates = (
            [0] * self._earliest_years + 
            [self._pre_rush_rate] * self._pre_rush_years +
            [self._rush_rate] * self._rush_years +
            [self._post_rush_rate] * self._post_rush_years +
            [0] * self._last_years
        ) 
        
        years = tuple(years)
        rates = tuple(rates)
        
        s_curve_dict = {'Year': years, 'Rate': rates}
        
        return s_curve_dict

    def calculate_s_curve_acc(self):
        years = self._s_curve['Year']
        rates = self._s_curve['Rate']

        accumulated_rates = (sum(rates[:i+1]) for i in range(len(rates)))
        s_curve_acc_dict = {'Year': years, 'Accumulated Rate': accumulated_rates}

        return s_curve_acc_dict