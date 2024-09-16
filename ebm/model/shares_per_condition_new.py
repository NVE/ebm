import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters, YearRange
from ebm.model.building_condition import BuildingCondition

class SharesPerConditionNew():
    """
    Calculates area shares over time per condition for all TEKs within a building category.
    """
    # TODO: 
    # - add 'year' to series index
    # - add checks to control calculations:
    #       - for example control total values and that original condition should not exceed 100%
    #       - negative values checks             
    # - make code less repetative (overall):
    #       - ideally, there could be a calc_shares_tek() method, that takes building_condition as input
    #       - then, there could be an own calc_shares() method, that loops trough the tek_list for a given building_condition
    # - code improvements:
    #       - create own helper method for calculating max measure limit
    #       - create own helper method for setting share to 0 in years before and including the year the building was constructed


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
        self.model_years = pd.Index(period.year_range)

    def _scurve_per_model_year(self, tek:str, scurve: pd.Series) -> pd.Series:
        """
        Get S-curve rates per model years relevant for the specified TEK. 
        """
        # Get the building year for the specific TEK
        building_year = self.tek_params[tek].building_year
        
        # Calculate the building age for each model year
        building_age_per_year = pd.Series(self.model_years - building_year, index=self.model_years) 
        
        # Filter to only include valid ages
        building_age_per_year = building_age_per_year[building_age_per_year > 0]

        # Control that the building ages are present in the S-curve before filtering
        if not building_age_per_year.isin(scurve.index).all():
            missing_ages = building_age_per_year[~building_age_per_year.isin(scurve.index)]
            msg = (
                f"\n"
                f"Building ages not present in S-curve while calculating shares.\n"
                f"The building year of {tek} might not be compatible with the model horizon. Control this parameter.\n"
                f"\n"
                f" - The building year of {tek} is: {building_year}.\n"
                f" - Building ages not present in S-curve: {missing_ages.to_list()}"
            )
            logger.error(msg)
            raise ValueError(f"Building ages not present in S-curve index for {tek}.")

        # Filter the scruve rates on the relevant building ages
        scurve = scurve.loc[building_age_per_year.values]

        # Assign the corresponding model years to the index of the filtered S-curve
        scurve_per_year = scurve.set_axis(building_age_per_year.index, axis=0)

        return scurve_per_year

    def calc_demolition(self, tek: str) -> pd.Series:
        """
        Calculate the percentage share of area that is demolished over time for a specific TEK.

        This method calculates the demolition shares for a specific TEK for each year from the start year to 
        the end year. It uses an S-curve to define the demolition rates and adjusts them based on the building 
        age in each year.

        The demolition share is calculated by taking the difference between the S-curve rate in the current year 
        and the previous year, and then accumulating these differences over time. Specific conditions are applied 
        to modify the general calculation logic as outlined below:

        - The share is set to 0 in the model start year. The floor area of a TEK in the start year is considered
          to be the area at the end of the year. Therefore, no building measures should be taken in this year.  
        - The share is set to 0 in model years before and including the building year of the TEK. There should be
          no measures taken in the first year that the building is constructed. In other words, the first measure
          can only be taken when the building is one year old.
        - The share is set to the S-curve rate of the model year if that year corresponds to the year after the 
          building was constructed. This is only the case if the building is constructed after the start year of 
          the model period. In this case, the S-curve rate at age 1 should be used, and after that the general 
          calculation method is applied.   

        Arguments:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A Pandas Series with the calculated demolition shares for the specific TEK, where the index 
                     represents the model years and the values are the respective demolition shares.
        """
        # Retrieve S-curve rates per model year
        scurve_per_year = self._scurve_per_model_year(tek, self.scurves[BuildingCondition.DEMOLITION])

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=self.model_years)

        # The share in year n is calculated by taking the difference between the rate in year n and n-1
        shares[scurve_per_year.index] = scurve_per_year.diff().fillna(0)
        
        # Accumulate the shares over the model period
        shares = shares.cumsum()

        # Get the building year for the specific TEK
        building_year = self.tek_params[tek].building_year

        # Use the rate of the year if that year corresponds to the year after the building was constructed 
        if (building_year + 1) in self.model_years:
            shares.loc[self.model_years == building_year + 1] = scurve_per_year.loc[building_year + 1]

        # Set share to 0 in the start year 
        shares.loc[self.model_years == self.period.start] = 0

        # Set share to 0 in years before and including the year the building was constructed
        shares.loc[self.model_years <= building_year] = 0

        return shares
    
    def _calc_total(self, tek: str, building_condition: BuildingCondition) -> pd.Series:
        """
        Calculate the percentage share of floor area that has undergone either small measures or renovation over the
        time horizon for a specific TEK.

        This method calculates the percentage share of floor area that has undergone either small measures or renovation 
        for each year in the model period. The share represents the total accumulated area affected by either condition 
        (small measure or renovation). It is important to note that an area counted in one measure does not exclude it 
        from being counted in the other, meaning that the area can undergo both small measures and renovation.

        The calculation is based on the rates from the respective S-curve (small measure or renovation), while ensuring 
        that the total share does not exceed the available area (adjusted for demolished areas and areas that are 
        never subjected to these measures).

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.
        - building_condition (BuildingCondition): The condition for which to calculate shares, either `SMALL_MEASURE` 
        or `RENOVATION`. The method will raise an error if another condition is provided.

        Returns:
        - pd.Series: A series with the calculated share of area that has undergone small measures or renovation, 
        with the index representing model years.

        Raises:
        - ValueError: If the `building_condition` is not `SMALL_MEASURE` or `RENOVATION`.
        """
        if (building_condition != BuildingCondition.SMALL_MEASURE) and (building_condition != BuildingCondition.RENOVATION):
            msg = f"Invalid building_condition. Value must be {BuildingCondition.SMALL_MEASURE} or {BuildingCondition.RENOVATION}"
            raise ValueError(msg) 

        # Retrieve S-curve rates per model year
        scurve_per_year = self._scurve_per_model_year(tek, self.scurves[building_condition])

        # Retrieve demolition shares per model year
        shares_demolition = self.calc_demolition(tek)

        # Calculate max limit for doing a renovation measure (small measure or renovation)
        measure_limit = 1 - shares_demolition - self.never_shares[building_condition]

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=self.model_years)

        # Set share to the S-curve rate for the corresponding model year
        shares[scurve_per_year.index] = scurve_per_year
        
        # Set share to the measure limit value if the S-curve rate exceeds the measure limit
        shares[shares > measure_limit] = measure_limit

        # Set share to 0 in years before and including the year the building was constructed
        building_year = self.tek_params[tek].building_year
        shares.loc[self.model_years <= building_year] = 0

        return shares
    
    def calc_renovation(self, tek: str) -> pd.Series:
        """
        Calculate the percentage share of floor area that only undergoes renovation over time for a specific TEK.

        This method calculates the share of a building's floor area that is renovated each year over the 
        model period. The share represents the portion of the area that undergoes only renovation (not including 
        any small measures). 

        Parameters:
        - tek (str): The identifier for the specific TEK for which the shares are calculated.

        Returns:
        - pd.Series: A series representing the share of floor area renovated each year over the model period, 
        with the index corresponding to the model years.
        """
        # Retrieve demolition shares per model year
        shares_demolition = self.calc_demolition(tek)
        
        # Retrieve total shares for renovation and small measure
        shares_small_measure_total = self._calc_total(tek, BuildingCondition.SMALL_MEASURE)
        shares_renovation_total = self._calc_total(tek, BuildingCondition.RENOVATION)

        # Calculate max limit for doing a renovation measure
        measure_limit = 1- shares_demolition - self.never_shares[BuildingCondition.RENOVATION] 

        # Set share to be the difference between the max measure limit and total shares for small measure
        shares = measure_limit - shares_small_measure_total 

        # Set share to 0 in years where the total shares for small measure exceeds the measure limit
        shares[shares < 0] = 0 

        # Find years where the total shares for building measures is lower than the measure limit  
        shares_total = shares_small_measure_total + shares_renovation_total
        years_to_filter = shares_total[shares_total < measure_limit].index

        # Use the total shares for renovation in years where the total shares for building measures is lower than the measure limit   
        shares[years_to_filter] = shares_renovation_total[years_to_filter]

        # Set share to 0 in years before and including the year the building was constructed
        building_year = self.tek_params[tek].building_year
        shares.loc[self.model_years <= building_year] = 0

        return shares
    
    def calc_renovation_and_small_measure(self, tek: str) -> pd.Series:
        """
        Calculate the percentage share of floor area that undergoes both renovation and small measure over time for a specific TEK.

        The share is calculated by subtracting the renovation share from the total renovation share.
        """
        # Retrieve shares for renovation only
        shares_renovation = self.calc_renovation(tek)

        # Retrieve total shares for renovation 
        shares_renovation_total = self._calc_total(tek, BuildingCondition.RENOVATION)

        # Set share by substracting renovation (only) shares from total renovation shares 
        shares = shares_renovation_total - shares_renovation

        # Set share to 0 in years before and including the year the building was constructed
        building_year = self.tek_params[tek].building_year
        shares.loc[self.model_years <= building_year] = 0

        return shares

    def calc_small_measure(self, tek: str) -> pd.Series:
        """
        Calculate the percentage share of floor area that only undergoes small measures over time for a specific TEK.

        The share is calculated by subtracting the combined share of renovation and small measure from 
        the total small measures share.
        """
        # Retrieve total shares for renovation small measure
        shares_small_measure_total = self._calc_total(tek, BuildingCondition.SMALL_MEASURE)

        # Retrieve shares for renovation and small measure
        shares_renovation_small_measure = self.calc_renovation_and_small_measure(tek)

        # Calculate share for only small measure
        shares = shares_small_measure_total - shares_renovation_small_measure

        # Set share to 0 in years before and including the year the building was constructed
        building_year = self.tek_params[tek].building_year
        shares.loc[self.model_years <= building_year] = 0

        return shares 

    def calc_original_condition(self, tek: str) -> pd.Series:
        """
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
            shares.loc[self.model_years < tek_start_year] = 0
        
        return shares

    def calc_shares_tek(self, tek: str, condition: BuildingCondition) -> pd.Series:
        """
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

    def calc_shares_condition(self, condition: BuildingCondition) -> typing.Dict[str, pd.Series]:
        """
        Calculate shares for all TEK's of a specified building condition.
        
        Returns:
        - dict: A dictionary where the keys are TEK identifiers (str) and the values are Pandas Series representing 
                the shares for a building condition for each year in the model period.
        """
        shares_tek = {}
        for tek in self.tek_list:
            shares_tek[tek] = self.calc_shares_tek(tek, condition)

        return shares_tek

    def calc_shares(self) -> typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]]:
        """
        Create a dictionary of shares per condition for all TEKs.
        """
        shares_condition = {}
        for condition in BuildingCondition:
            shares_condition[condition] = self.calc_shares_condition(condition)
        
        return shares_condition

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
    shares = SharesPerConditionNew(tek_list, tek_params, scurves, never_shares)
    
    s = shares.calc_shares_tek(tek_list[1], BuildingCondition.SMALL_MEASURE)
    s = shares.calc_shares_condition(BuildingCondition.SMALL_MEASURE)
    s = shares.calc_shares()
    
    print(s)