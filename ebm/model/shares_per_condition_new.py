import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters
from ebm.model.tek import TEK
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange

class SharesPerConditionNew():
    """
    Calculates area shares over time per condition for all TEKs within a building category.
    """
    
    # TODO: 
    # - add checks to control calculations:
    #       - for example control total values and that original condition should not exceed 100%
    #       _ negative values checks             
    # - make code less repetative:
    #       - ideally, there could be a calc_shares_tek() method, that takes building_condition as input
    #       - then, there could be an own calc_shares() method, that loops trough the tek_list for a given building_condition
    #       - make self.model_years to a pd.Series RangeIndex

    def __init__(self, 
                 tek_list: typing.List[str], 
                 tek_params: typing.Dict[str, TEKParameters], 
                 scurves: typing.Dict[str, pd.Series],
                 never_shares: typing.Dict[str, float],
                 period: YearRange = YearRange(2010, 2050)):
        
        self.tek_list = tek_list
        self.tek = TEK(tek_params)
        self.model_start_year = period.start
        self.model_end_year = period.end
        self.model_years = period.year_range

        # Set S-curve parameter attributes 
        self.scurve_small_measure = scurves[BuildingCondition.SMALL_MEASURE]
        self.scurve_renovation = scurves[BuildingCondition.RENOVATION]
        self.scurve_demolition = scurves[BuildingCondition.DEMOLITION]
        self.never_share_small_measure = never_shares[BuildingCondition.SMALL_MEASURE]
        self.never_share_renovation = never_shares[BuildingCondition.RENOVATION]
        self.never_share_demolition = never_shares[BuildingCondition.DEMOLITION]

    def _scurve_per_model_year(self, tek:str, scurve: pd.Series) -> pd.Series:
        """
        Helper method to get scurve rates per model years relevant for the specified TEK. 
        """
        # Get the building year for the specific TEK
        building_year = self.tek.get_building_year(tek)

        # Convert the model_years range to a RangeIndex
        model_years = pd.Index(self.model_years)

        # Calculate the building age for each model year
        building_age_per_year = pd.Series(model_years - building_year, index=model_years) 
        
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

    def calc_shares_demolition_tek(self, tek: str) -> pd.Series:
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
        # Get the building year for the specific TEK
        building_year = self.tek.get_building_year(tek)

        # Convert the model_years range to a RangeIndex
        model_years = pd.Index(self.model_years)

        # Calculate the building age for each model year
        building_age_per_year = pd.Series(model_years - building_year, index=model_years) 
        
        # Filter to only include valid ages
        building_age_per_year = building_age_per_year[building_age_per_year > 0]

        # Define scurve 
        scurve = self.scurve_demolition

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

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=model_years)

        # The share in year n is calculated by taking the difference between the rate in year n and n-1
        shares[scurve_per_year.index] = scurve_per_year.diff().fillna(0)
        
        # Accumulate the shares over the model period
        shares = shares.cumsum()

        # Use the rate of the year if that year corresponds to the year after the building was constructed 
        if (building_year + 1) in model_years:
            shares.loc[model_years == building_year + 1] = scurve_per_year.loc[building_year + 1]

        # Set share to 0 in the start year 
        shares.loc[model_years == self.model_start_year] = 0

        # Set share to 0 in years before and including the year the building was constructed
        shares.loc[model_years <= building_year] = 0

        return shares
    
    def calc_shares_demolition(self) -> typing.Dict[str, pd.Series]:
        """
        Calculate demolition shares for all TEKs in the list.

        This method loops through all TEKs in `self.tek_list` and calls the `calc_shares_demolition_tek` method 
        for each TEK to calculate the demolition shares over time. The results are stored in a dictionary where 
        each key is the TEK identifier, and the value is a Pandas Series containing the demolition shares for 
        each model year.

        Returns:
        - dict: A dictionary where the keys are TEK identifiers (str) and the values are Pandas Series representing 
                the demolition shares for each year from the start year to the end year.
        """
        tek_shares = {}
        for tek in self.tek_list:
            shares = self.calc_shares_demolition_tek(tek)
            tek_shares[tek] = shares

        return tek_shares

    def calc_shares_small_measure_total_tek(self, tek:str) -> pd.Series:
        """
        """
        # Get the building year for the specific TEK
        building_year = self.tek.get_building_year(tek)

        # Retrieve S-curve rates per model year
        scurve_per_year = self._scurve_per_model_year(tek, self.scurve_small_measure)

        # Retrieve demolition shares per model year
        condition_shares = self.calc_shares_demolition_tek(tek)

        # Convert the model_years range to a RangeIndex
        model_years = pd.Index(self.model_years)

        # Calculate max limit for doing a renovation measure (small measure or renovation)
        measure_limit = 1 - condition_shares - self.never_share_small_measure

        # Define an empty shares series with model years as index
        shares = pd.Series(0.0, index=model_years)

        # Set share to the S-curve rate for the corresponding model year
        shares[scurve_per_year.index] = scurve_per_year
        
        # Set share to the measure limit value if the S-curve rate exceeds the measure limit
        shares[shares > measure_limit] = measure_limit

        # Set share to 0 in years before and including the year the building was constructed
        shares.loc[model_years <= building_year] = 0

        return shares
        
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
    
    tek = tek_list[1]

    shares = shares.calc_shares_small_measure_total_tek(tek)
    print(shares)
    
    #for tek in tek_list:
    #    shares = shares.calc_shares_small_measure_total_tek(tek)
    #    logger.info(tek)
    