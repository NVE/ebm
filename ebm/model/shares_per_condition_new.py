import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters
from ebm.model.tek import TEK
from ebm.model.building_condition import BuildingCondition

class SharesPerConditionNew():
    """
    Calculates area shares over time per condition for all TEKs within a building category.
    """
    
    # TODO: 
    # - add start and end year as input arguments, as they should be defined outside the class
    # - add negative values checks 
    # - add checks to control calculations, for example control total values and that original condition should not exceed 100%
    # - make code less repetative (e.g for loops on tek_list -> change to own method?)

    def __init__(self, 
                 tek_list: typing.List[str], 
                 tek_params: typing.Dict[str, TEKParameters], 
                 scurves: typing.Dict[str, pd.Series],
                 never_shares: typing.Dict[str, float],
                 model_start_year: int = 2010,
                 model_end_year: int = 2050):
        
        self.tek_list = tek_list
        self.tek = TEK(tek_params)
        self.model_start_year = model_start_year
        self.model_end_year = model_end_year
        self.model_years = range(model_start_year, model_end_year + 1)

        # Set S-curve parameter attributes 
        self.scurve_small_measure = scurves[BuildingCondition.SMALL_MEASURE]
        self.scurve_renovation = scurves[BuildingCondition.RENOVATION]
        self.scurve_demolition = scurves[BuildingCondition.DEMOLITION]
        self.never_share_small_measure = never_shares[BuildingCondition.SMALL_MEASURE]
        self.never_share_renovation = never_shares[BuildingCondition.RENOVATION]
        self.never_share_demolition = never_shares[BuildingCondition.DEMOLITION]

    def calc_shares_demolition_tek(self, tek) -> pd.Series:
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
        - The share is set to 0 in model years before and up until the building year of the TEK. There should be
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

        # Set share to 0 in years before the the building_year + 1
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
    
    #tek_shares = shares.calc_shares_demolition_tek(tek_list[0])
    shares_per_tek = shares.calc_shares_demolition()
    
    print(shares_per_tek)