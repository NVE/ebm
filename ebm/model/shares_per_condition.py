import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters, YearRange
from ebm.model.building_condition import BuildingCondition

class SharesPerCondition():
    """
    Calculates accumulated (percentage) shares of floor area that is of a certain building condition over the model period,
    for all TEKs within a building category.
    """
    # TODO: 
    # - update all docstrings to numpy format
    # - code improvements and less repetative:
    #   - add more arguments to method and split up functionality into smaller helper methods
    #   - don't call other calculations methods inside calculation methods, but add the result from them as params
    #   - create own helper method for calculating max measure limit
    #   - create own helper method for setting share to 0 in years before and including the year the building was constructed
    #   - allow 'building_condition' to be 'str' and methods to accept upper case and space?


    def __init__(self, 
                 tek_list: typing.List[str], 
                 tek_params: typing.Dict[str, TEKParameters], 
                 scurves: typing.Dict[str, pd.Series],
                 never_shares: typing.Dict[str, float],
                 period: YearRange = YearRange(2010, 2050)):
        
        self.tek_list = tek_list
        self.tek_params = tek_params
        self.scurves = scurves
        self.never_shares = never_shares
        self.period = period
        self.period_index = pd.Index(period.year_range, name = 'year')

        # Internal method to control all share calculations
        #self._control_shares()

    def _control_series_values(self, series: pd.Series):
        """
        Check if the provided pandas series contains any negative or NA values.

        Parameters:
        - series (pd.Series): The input series to be checked.

        Raises:
        - ValueError: If the series contains negative values.
        - ValueError: If the series contains NA values.
        """
        if (series < 0).any():
            raise ValueError("The series contains negative values. Not allowed in S-curves or Condition shares series.")
        
        if series.isna().any():
            raise ValueError("The series contains missing (NA) values. Not allowed in S-curves or Condition shares series")
        
    def _scurve_per_year(self, tek:str, scurve: pd.Series) -> pd.Series:
        """
        Retrieve the S-curve rates for years in the model period, corresponding to the building's age for a given TEK. 
            
        This method calculates the building age for each model year based on the construction year of the TEK, and 
        filters the provided S-curve rates accordingly. Then, the corresponding model years are assigned to the filtered
        S-curve rates. The filtering ensures that only the rates for years after the construction of the building is included. 

        Parameters:
        - tek (str): The identifier for the specific TEK for which the S-curve rates are calculated.
        - scurve (pd.Series): The S-curve rates for the relevant building condition, indexed by building age.

        Returns:
        - pd.Series: A series of S-curve rates indexed by the model years.

        Raises:
        - ValueError: If any of the building ages are not present in the S-curve index.
        - ValueError: If the S-curve calculations results in negative values or contains missing (NA) values.
        """
        # Get the building year for the specific TEK
        construction_year = self.tek_params[tek].building_year
        
        # Calculate the building age for each model year
        building_age_per_year = pd.Series(self.period_index - construction_year, index=self.period_index) 

        # Only include valid ages (ages corresponding to years after the construction of the building)
        building_age_per_year = building_age_per_year[building_age_per_year > 0]

        # Control that the building ages are present in the S-curve before filtering
        if not building_age_per_year.isin(scurve.index).all():
            missing_ages = building_age_per_year[~building_age_per_year.isin(scurve.index)]
            msg = (
                f"\n"
                f"Building ages not present in S-curve while calculating shares.\n"
                f"The building year of {tek} might not be compatible with the model horizon. Control this parameter.\n"
                f"\n"
                f" - The building year of {tek} is: {construction_year}.\n"
                f" - Building ages not present in S-curve: {missing_ages.to_list()}"
            )
            logger.error(msg)
            raise ValueError(f"Building ages not present in S-curve index for {tek}.")

        # Filter the scruve rates on the relevant building ages
        scurve = scurve.loc[building_age_per_year.values]

        # Assign the corresponding model years to the index of the filtered S-curve
        scurve_per_year = scurve.set_axis(building_age_per_year.index, axis=0)

        self._control_series_values(scurve_per_year)
        return scurve_per_year

    def calc_demolition(self, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area that is demolished over the model period for a specified TEK.

        The calculation in this method is based on the demolition S-curve. The demolition share is calculated by taking
        the difference between the S-curve rate in the current year and the previous year, and then accumulating these
        differences over time. Specific conditions are applied to modify the general calculation logic as outlined below:

        - The share is set to 0 in the model start year. The floor area of a TEK in the start year is considered to 
          be the area at the end of the year. Therefore, no building measures should be taken in this year.  
        - The share is set to 0 in model years before and during the construciton year of the TEK. There should be 
          no measures taken in the first year that the building is constructed. In other words, the first measure 
          can only be taken when the building is one year old.
        - The share is set to the S-curve rate of the given model year if that year corresponds to the year after 
          the building was constructed. This is only the case if the building is constructed after the start year
          of the model period. In this case, the S-curve rate at age 1 should be used, and after that the general 
          calculation method is applied.   

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A Pandas Series with the calculated demolition shares for the specific TEK, where the index 
                     represents the model years and the values are the respective demolition shares.
        
        Raises:
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.        
        """
        # Retrieve S-curve rates per model year
        scurve_per_year = self._scurve_per_year(tek, self.scurves[BuildingCondition.DEMOLITION])

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=self.period_index)

        # The share in year n is calculated by taking the difference between the rate in year n and n-1
        shares[scurve_per_year.index] = scurve_per_year.diff().fillna(0)
        
        # Accumulate the shares over the model period
        shares = shares.cumsum()

        # Get the building year for the specific TEK
        construction_year = self.tek_params[tek].building_year

        # Use the rate of the year if that year corresponds to the year after the building was constructed 
        if (construction_year + 1) in self.period_index:
            shares.loc[self.period_index == construction_year + 1] = scurve_per_year.loc[construction_year + 1]

        # Set share to 0 in the start year 
        shares.loc[self.period_index == self.period.start] = 0

        # Set share to 0 in years before and including the year the building was constructed
        shares.loc[self.period_index <= construction_year] = 0

        self._control_series_values(shares)
        return shares
    
    def _calc_max_measure_share(self, demolition_shares: pd.Series, never_share: float):
        """
        Calculates the maximum share of a buildings area that is available for a renovation or 
        small measure each year.

        The available area is found by substracting 1 with the share of area that has been demolished by that 
        year and the share of area that never will be subjected to a measure during the buildings lifetime. If
        the value is 1, then 100% of the area can undergo a measure, and there is no available area if the value
        is 0. 

        Parameters
        ----------  
        demolition_shares: pd.Series
            Accumulated share of area that is demoilshed per year for a given TEK.
        never_share: float
            The share of area that never will undergo 'renovation' or 'small_measure'.

        Returns
        -------
        pd.Series
            Series with max measure shares per year. 
        """
        return 1 - demolition_shares - never_share

    def _calc_small_measure_or_renovation(self, tek: str, building_condition: BuildingCondition) -> pd.Series:
        """
        Calculate the accumulated share of floor area that has undergone either small measures or renovation over the
        model period for a specified TEK.

        The share represents the total accumulated floor area affected by either condition (small measure or renovation).
        Importantly, the share doesn't necessarily represent floor area that is exclusively affected by the given building
        condition. When calculating the renovation share for exmaple, the share represent all the floor area that's been 
        renovated, but portions of this area may also have undergone a small measure (and vice versa). 

        The calculation is based on the rates from the respective S-curve (small measure or renovation), while ensuring 
        that the total share does not exceed the available area (adjusted for demolished area and area that never will 
        be subjected to any measures/conditions).

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.
        - building_condition (BuildingCondition): The condition for which to calculate shares, either `small_measure` 
          or `renovation`. 

        Returns:
        - pd.Series: A series with the calculated share of floor area that has undergone small measures or renovation, 
                     with the index representing model years.

        Raises:
        - ValueError: If the `building_condition` is not `small_measure` or `renovation`.
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.
        """
        if (building_condition != BuildingCondition.SMALL_MEASURE) and (building_condition != BuildingCondition.RENOVATION):
            msg = f"Invalid building_condition. Value must be {BuildingCondition.SMALL_MEASURE} or {BuildingCondition.RENOVATION}"
            raise ValueError(msg) 

        # Retrieve S-curve rates per model year
        scurve_per_year = self._scurve_per_year(tek, self.scurves[building_condition])

        # Calculate max limit for doing a renovation measure (small measure or renovation)
        max_share = self._calc_max_measure_share(self.calc_demolition(tek), self.never_shares[building_condition])

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=self.period_index)

        # Set share to the S-curve rate for the corresponding model year
        shares[scurve_per_year.index] = scurve_per_year
        
        # Set share to the measure limit value if the S-curve rate exceeds the measure limit
        shares[shares > max_share] = max_share

        # Set share to 0 in years before and including the year the building was constructed
        construction_year = self.tek_params[tek].building_year
        shares.loc[self.period_index <= construction_year] = 0

        self._control_series_values(scurve_per_year)
        return shares
    
    def calc_renovation(self, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area exclusively renovated over the model period for a specific TEK.

        The share is determined by excluding any area subjected to small measures from the total share of area that's
        renovated. The share is also adjusted based on the available area (adjusted for demolished area and area that 
        never will be subjected to any measures/conditions).

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A series representing the share of floor area renovated each year over the model period, 
                     with the index corresponding to the model years.

        Raises:
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.
        """
        # Retrieve total shares for renovation and small measure
        shares_small_measure_total = self._calc_small_measure_or_renovation(tek, BuildingCondition.SMALL_MEASURE)
        shares_renovation_total = self._calc_small_measure_or_renovation(tek, BuildingCondition.RENOVATION)

        # Calculate max limit for doing a renovation measure (denoting the available area)
        max_share = self._calc_max_measure_share(self.calc_demolition(tek), 
                                                 self.never_shares[BuildingCondition.RENOVATION])

        # Set share to be the difference between the max measure limit and total shares for small measure
        shares = max_share - shares_small_measure_total 

        # Set share to 0 in years where the total shares for small measure exceeds the measure limit
        shares[shares < 0] = 0 

        # Find years where the total shares for building measures is lower than the measure limit  
        shares_total = shares_small_measure_total + shares_renovation_total
        years_to_filter = shares_total[shares_total < max_share].index

        # Use the total shares for renovation in years where the total shares for building measures is lower than the measure limit   
        shares[years_to_filter] = shares_renovation_total[years_to_filter]

        # Set share to 0 in years before and including the year the building was constructed
        construction_year = self.tek_params[tek].building_year
        shares.loc[self.period_index <= construction_year] = 0

        self._control_series_values(shares)
        return shares
    
    def calc_renovation_and_small_measure(self, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area that undergoes both renovation and small measures over the model period 
        for a specified TEK.

        The share is calculated by substracting the share for area that's exclusively renovated from the share representing the 
        total area thats been renovated. The share for total renovatedarea also includes area that's been affected by small measures. 
        Thus, excluding area that's exclusively renovated from the total share willdetermine the area that's been affected by both 
        renovation and small measures.      

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A series representing the share of floor area undergoing both renovation and small measures, 
                     with the index corresponding to the model years.

        Raises:
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.
        """
        # Retrieve shares for renovation only
        shares_renovation = self.calc_renovation(tek)

        # Retrieve total shares for renovation 
        shares_renovation_total = self._calc_small_measure_or_renovation(tek, BuildingCondition.RENOVATION)

        # Set share by substracting renovation (only) shares from total renovation shares 
        shares = shares_renovation_total - shares_renovation

        # Set share to 0 in years before and including the year the building was constructed
        construction_year = self.tek_params[tek].building_year
        shares.loc[self.period_index <= construction_year] = 0

        self._control_series_values(shares)
        return shares

    def calc_small_measure(self, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area that's exclusively affected by small measures over the model period 
        for a specific TEK.

        The share is calculated by subtracting the share for area that's affected by both renovation and small measures 
        from the total share of area that's undegone small measures.

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A series representing the share of floor area exclusively affected by small measures, with the index 
                     corresponding to the model years.

        Raises:
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.
        """
        # Retrieve total shares for renovation small measure
        shares_small_measure_total = self._calc_small_measure_or_renovation(tek, BuildingCondition.SMALL_MEASURE)

        # Retrieve shares for renovation and small measure
        shares_renovation_small_measure = self.calc_renovation_and_small_measure(tek)

        # Calculate share for only small measure
        shares = shares_small_measure_total - shares_renovation_small_measure

        # Set share to 0 in years before and including the year the building was constructed
        construction_year = self.tek_params[tek].building_year
        shares.loc[self.period_index <= construction_year] = 0

        self._control_series_values(shares)
        return shares 

    def calc_original_condition(self, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area that remains in its original condition over the model period 
        for a specific TEK.

        This method computes the share of floor area that has not undergone any measures or renovation, by subtracting 
        the shares of all other relevant building conditions from 1.0. 

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A series representing the share of floor area in its original condition, with the index corresponding 
                     to the model years.

        Raises:
        - ValueError: If the shares calculation results in negative values or contains missing (NA) values.
        """
        # Retrieve shares for the different conditions
        shares_demolition = self.calc_demolition(tek)
        shares_renovation = self.calc_renovation(tek)
        shares_renovation_and_small_measure = self.calc_renovation_and_small_measure(tek)
        shares_small_measure = self.calc_small_measure(tek)

        # Calculate shares
        shares = 1.0 - shares_demolition - shares_renovation - shares_renovation_and_small_measure - shares_small_measure

        # Check if the start year of the TEK is after the start year of the model period
        tek_start_year = self.tek_params[tek].start_year
        if tek_start_year > self.period.start:
            # Set share to 0 in years before the start year of the TEK
            shares.loc[self.period_index < tek_start_year] = 0
        
        self._control_series_values(shares)
        return shares

    def calc_shares(self, condition: BuildingCondition, tek: str) -> pd.Series:
        """
        Calculate the accumulated share of floor area affected by the specified building condition (e.g., demolition, 
        renovation) over the model period for a given TEK.

        This method calculates the floor area shares for a specified building condition by calling the appropriate 
        calculation method based on the given building condition.

        Parameters:
        - condition (BuildingCondition): The building condition for which the shares need to be calculated. 
                                         It must be one of the enumerated values from the `BuildingCondition` class.
        - tek (str): The identifier for the specific TEK.

        Returns:
        - pd.Series: A series representing the calculated shares of floor area for the specified condition and TEK, 
                     with the index corresponding to the model years.

        Raises:
        - ValueError: If an invalid building condition is provided or if the calculated shares do not match the criterias 
                      defined in the calculation method for that building condition. 
        """
        if condition not in BuildingCondition:
            msg = f"Invalid building condition"
            raise ValueError(msg)
        
        if condition == BuildingCondition.SMALL_MEASURE:
            shares = self.calc_small_measure(tek)
        
        if condition == BuildingCondition.RENOVATION:
            shares = self.calc_renovation(tek)
        
        if condition == BuildingCondition.RENOVATION_AND_SMALL_MEASURE:
            shares = self.calc_renovation_and_small_measure(tek)
        
        if condition == BuildingCondition.DEMOLITION:
            shares = self.calc_demolition(tek)
        
        if condition == BuildingCondition.ORIGINAL_CONDITION:
            shares = self.calc_original_condition(tek) 

        return shares

    def calc_shares_all_teks(self, condition: BuildingCondition, tek_list: typing.List[str] = None) -> typing.Dict[str, pd.Series]:
        """
        Calculate the accumulated shares of floor area affected by the specified building condition for all TEKs over the model period.

        This method computes the floor area shares for a specified building condition for the provided list of TEKs (or all available TEKs
        if none are provided). It loops through each TEK in the `tek_list` and calls the `calc_shares` method for that condition.

        Parameters:
        - condition (BuildingCondition): The building condition for which the shares need to be calculated for all TEKs.
        - tek_list (List[str], optional): A list of TEK identifiers (strings) to calculate the shares for. If not provided, it defaults to `self.tek_list`.

        Returns:
        - dict: A dictionary where the keys are TEK identifiers (str), and the values are Pandas Series representing the calculated shares 
                for each TEK over the model period.

        Raises:
        - ValueError: If an invalid building condition is provided or if the calculated shares do not match the criteria for any TEK.              
        """
        if tek_list == None:
            tek_list = self.tek_list

        shares_tek = {}
        for tek in tek_list:
            shares_tek[tek] = self.calc_shares(condition, tek)

        return shares_tek

    def calc_shares_all_conditions_teks(self, tek_list: typing.List[str] = None) -> typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]]:
        """
        Calculate the accumulated shares of floor area for all building conditions across all TEKs over the model period.

        This method computes the shares for all building conditions (e.g., demolition, renovation, small measures) across 
        the provided list of TEKs (or all available TEKs if none are provided). It organizes the results into a nested dictionary,
        where the first-level keys represent building conditions and the values are dictionaries of TEK-specific share data.

        Returns:
        - dict: A nested dictionary where:
            - The first-level keys are `BuildingCondition` values.
            - The second-level keys are TEK identifiers (str).
            - The second-level values are Pandas Series representing the calculated shares for each TEK over time.

        Raises:
        - ValueError: If the calculated shares do not meet the criteria for any building condition or TEK.
        """
        if tek_list == None:
            tek_list = self.tek_list

        shares_condition = {}
        for condition in BuildingCondition:
            shares_condition[condition] = self.calc_shares_all_teks(condition, tek_list)
        
        return shares_condition
    
    def _control_shares(self, precision: int = 10):
        """
        Ensure the total shares for each TEK across all building conditions sum up to 1.0 for each model year.

        This internal method verifies that the sum of shares for all building conditions equals 1.0 for each year 
        in the model period for every TEK. It also controls for certain conditions, such as ensuring the total shares
        before the TEK's start year are 0.0 and those after are 1.0. If shares do not meet these criteria, the method 
        raises an error.

        Parameters:
        - precision (int, optional): The number of decimal places to which the share values are rounded.

        Raises:
        - ValueError: If the total shares for any TEK do not sum up to 1.0 or if the shares before or after the TEK's 
                      start year are not valid.
        """
        logger.info("Controlling total shares...")
        for tek in self.tek_list:
            shares = pd.Series(0.0, index=self.period_index)
            for condition in BuildingCondition:
                condition_shares = self.calc_shares(condition, tek)
                shares += condition_shares
            
            # Round values according to precision
            if precision != None:
                shares = round(shares, precision)

            # Control total shares values
            tek_start_year = self.tek_params[tek].start_year
            if tek_start_year > self.period.start:
                pre_tek_start = shares.loc[self.period_index < tek_start_year]
                post_tek_start = shares.loc[self.period_index >= tek_start_year]
                
                if not (pre_tek_start == 0.0).all():
                    invalid_shares = pre_tek_start[pre_tek_start != 0.0]
                    msg = f"Total shares doesn't match criteria for {tek}. Values should be 0.0 before year {tek_start_year}. Invalid shares: {invalid_shares}"
                    raise ValueError()
                if not (post_tek_start == 1.0).all():
                    invalid_shares = post_tek_start[post_tek_start != 1.0]
                    msg = f"Total shares doesn't match criteria for {tek}. Values should be 1.0 after year {tek_start_year}. Invalid shares: {invalid_shares}"
                    raise ValueError(msg)
            else: 
                if not (shares == 1.0).all():
                    invalid_shares = shares[shares != 1.0]
                    msg = f"Total shares doesn't match criteria for {tek}. Values should be 1.0 in all model years. Invalid shares: {invalid_shares}"
                    raise ValueError(msg)

if __name__ == '__main__':

    from ebm.model.database_manager import DatabaseManager
    from ebm.model.building_category import BuildingCategory
    from ebm.model.database_manager import DatabaseManager
    from ebm.model.building_category import BuildingCategory
    from ebm.model.filter_scurve_params import FilterScurveParams
    from ebm.model.scurve_processor import ScurveProcessor
    from ebm.model.filter_tek import FilterTek

    database_manager = DatabaseManager()
    building_category = BuildingCategory.HOUSE
    
    # Retrieve scurve data
    scurve_condition_list = BuildingCondition.get_scruve_condition_list()
    scurve_data_params = database_manager.get_scurve_params()
    scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)
    scurve_processor = ScurveProcessor(scurve_condition_list, scurve_params)
    scurves = scurve_processor.get_scurves()
    never_shares = scurve_processor.get_never_shares()

    # Initiate SharesPerCondition object
    tek_list = FilterTek.get_filtered_list(building_category, database_manager.get_tek_list())
    tek_params = database_manager.get_tek_params(tek_list)
    shares = SharesPerCondition(tek_list, tek_params, scurves, never_shares)
    
    tek = tek_list[6]
    s = shares.calc_shares(BuildingCondition.ORIGINAL_CONDITION, tek)
    print(s)