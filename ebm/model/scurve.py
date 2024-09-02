import typing
import pandas as pd

class SCurve():
    """
    Calculates S-curve per building condition.
    """ 

    #TODO: 
    # - add negative values checks
    # - add check to control that defined periods match building lifetime index in get_rates_per_year
    
    def __init__(self, 
                 earliest_age: int,
                 average_age: int,
                 last_age: int,
                 rush_years: int,
                 rush_share: float,
                 never_share: float,
                 building_lifetime: int = 130):

        self._building_lifetime = building_lifetime
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

    def get_rates_per_year_over_building_lifetime(self) -> pd.Series:
        """
        Create a series that holds the yearly measure rates over the building lifetime.

        This method defines the periods in the S-curve, adds the yearly measure rates to
        the corresponding periods, and stores them in a pandas Series.

        Returns:
        - rates_per_year (pd.Series): A Series containing the yearly measure rates over the building lifetime 
                                      with an index representing the age from 1 to the building lifetime.
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

        # Create list where the yearly rates are placed according to their corresponding period in the buildings lifetime 
        rates_per_year = (
            [0] * earliest_years + 
            [self._pre_rush_rate] * pre_rush_years +
            [self._rush_rate] * rush_years +
            [self._post_rush_rate] * post_rush_years +
            [0] * last_years
        )  
        
        # Create a pd.Series with an index from 1 to building_lifetime 
        index = range(1, self._building_lifetime + 1)
        rates_per_year = pd.Series(rates_per_year, index=index, name='scurve')
        rates_per_year.index.name = 'age'

        return rates_per_year

    def calc_scurve(self) -> pd.Series:
        """
        Calculates the S-curve by accumulating the yearly measure rates over the building's lifetime.

        This method returns a pandas Series representing the S-curve, where each value corresponds 
        to the accumulated rate up to that age.

        Returns:
        - scurve (pd.Series): A Series containing the accumulated rates of the S-curve 
                              with an index representing the age from 1 to the building lifetime.
        """
        # Get rates_per_year and accumulate them over the building lifetime
        rates_per_year = self.get_rates_per_year_over_building_lifetime() 
        scurve = rates_per_year.cumsum()
        return scurve
