import typing

class SCurve():
    """
    Calculates S-curve per building condition.
    """ 

    #TODO: 
    # - move building_lifetime to congif?
    # - add negative values checks
    # - change input_df so that the class takes the parameters or datastructure with params, where dtype is pre-defined. Filtering can be done in DB manager.
    # - create instance variables dynamically from column names? or change to constans? -> change to constans for now
    # - change name of methods to be more accurate, e.g. the current s-curve method (snakk med Benedicte)
    # - change s_curve method to only return a list of shares? The year key in the dict is not necessary in further calculations. -> YES, change this.

    # Column names
    BUILDING_LIFETIME = 130
    
    def __init__(self, 
                 earliest_age: int,
                 average_age: int,
                 last_age: int,
                 rush_years: int,
                 rush_share: float,
                 never_share: float):

        self._building_lifetime = self.BUILDING_LIFETIME
        self._earliest_age = earliest_age
        self._average_age = average_age
        self._last_age = last_age
        self._rush_years = rush_years
        self._rush_share = rush_share
        self._never_share = never_share

        # Calculate yearly rates
        self._pre_rush_rate = self._calc_pre_rush_rate() 
        self._rush_rate = self._calc_rush_rate()
        self._post_rush_rate = self._calc_post_rush_rate()
        
        # Calculate S-curves
        self.rates_per_year = self.get_rates_per_year_over_building_lifetime() 
        self.scurve = self.calc_scurve() 

    def _calc_pre_rush_rate(self) -> float:
        """
        Calculate the yearly measure rate for the pre-rush period.

        The pre-rush rate represents the percentage share of building area that has 
        undergone a measure per year during the period before the rush period begins.

        Returns:
        - pre_rush_rate (float): Yearly measure rate in the pre-rush period.
        """
        pre_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._average_age - self._earliest_age - (self._rush_years/2)))
        return pre_rush_rate
    
    def _calc_rush_rate(self) -> float:
        """
        Calculate the yearly measure rate for the rush period.

        The rush rate represents the percentage share of building area that has 
        undergone a measure per year during the rush period.

        Returns:
        - rush_rate (float): Yearly measure rate in the rush period.
        """
        rush_rate = self._rush_share / self._rush_years
        return rush_rate
    
    def _calc_post_rush_rate(self) -> float:
        """
        Calculate the yearly measure rate for the post-rush period.

        The post-rush rate represents the percentage share of building area that has 
        undergone a measure per year during the period after the rush period ends.

        Returns:
        - post_rush_rate (float): Yearly measure rate in the post-rush period.
        """
        post_rush_rate = (1 - self._rush_share - self._never_share) * (0.5 / (self._last_age - self._average_age - (self._rush_years/2)))
        return post_rush_rate

    def get_rates_per_year_over_building_lifetime(self) -> typing.Tuple:
        """
        Create a list that holds the yearly measure rates over the building lifetime.

        This method defines the periods in the S-curve, adds the yearly measure rates to
        the corresponding periods, and stores them in a list.

        Returns:
        - rates_per_year (List): List containing the yearly measure rates over the building lifetime (float or int).
        """

        # Define the length of the different periods in the S-curve
        earliest_years = self._earliest_age - 1
        pre_rush_years = int(self._average_age - self._earliest_age - (self._rush_years/2))
        rush_years = self._rush_years
        post_rush_years = int(self._last_age - self._average_age - (self._rush_years/2))
        last_years = self._building_lifetime - earliest_years - pre_rush_years - rush_years - post_rush_years
        
        # Redefine periods for Demolition, as the post_rush_year calculation isn't the same as for Small measures and Rehabilition
        if last_years < 0:
            last_years = 0 
            post_rush_years = self._building_lifetime - earliest_years - pre_rush_years - rush_years

        # Create dict where the yearly rates are placed according to their corresponding period in the buildings lifetime 
        rates_per_year = (
            [0] * earliest_years + 
            [self._pre_rush_rate] * pre_rush_years +
            [self._rush_rate] * rush_years +
            [self._post_rush_rate] * post_rush_years +
            [0] * last_years
        )  
        
        # Use tuples due to immutability
        rates_per_year = tuple(rates_per_year)
        
        return rates_per_year

    def calc_scurve(self) -> typing.Tuple:
        """
        Calculates the S-curve by accumulating the yearly measure rates over the building's lifetime.

        This method iterates over the yearly measure rates, accumulates them, and stores the accumulated
        rates in a tuple representing the S-curve.

        Returns:
        - scurve (Tuple): Tuple containing the accumulated rates of the S-curve (float or int).
        """
        rates = self.rates_per_year
        
        # Iterate over the rates and accumulate them in a list
        accumulated_rates = []
        acc_rate = 0
        for rate in rates:
            acc_rate += rate
            accumulated_rates.append(acc_rate)

        # Use tuples due to immutability
        scurve = tuple(accumulated_rates)

        return scurve
    