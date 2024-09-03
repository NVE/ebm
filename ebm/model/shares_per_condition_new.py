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
        

    def calc_shares_demolition_tek(self, tek: str) -> typing.Dict:
        """
        """
        building_year = self.tek.get_building_year(tek)

        shares = pd.Series(0.0, index=self.model_years)

        for year in shares.index:
            building_age = year - building_year

            if year == self.model_start_year or building_year >= year:
                # Set share to 0 in the start year and if the building isn't buildt yet
                shares[year] = 0
            elif building_year == year - 1:
                # Set share to the current rate/share if the building year is equal to year-1
                shares[year] = self.scurve_demolition[building_age]
            else:
                # Get rates/shares from the demolition S-curve based on building age                
                rate = self.scurve_demolition[building_age]
                prev_rate = self.scurve_demolition[building_age - 1]

                # Calculate percentage share by subtracting rate from previous year's rate
                shares[year] = rate - prev_rate

        # Accumulate shares over the modelyears
        shares = shares.cumsum()

        return shares
    
    #TODO: change to vecotorized operations / drop for loop 
    def calc_shares_demolition(self) -> typing.Dict:
        """
        """
        tek_shares = {}
        for tek in self.tek_list:
            building_year = self.tek.get_building_year(tek)

            shares = pd.Series(0.0, index=self.model_years)

            for year in shares.index:
                building_age = year - building_year

                if year == self.model_start_year or building_year >= year:
                    # Set share to 0 in the start year and if the building isn't buildt yet
                    shares[year] = 0
                elif building_year == year - 1:
                    # Set share to the current rate/share if the building year is equal to year-1
                    shares[year] = self.scurve_demolition[building_age]
                else:
                    # Get rates/shares from the demolition S-curve based on building age                
                    rate = self.scurve_demolition[building_age]
                    prev_rate = self.scurve_demolition[building_age - 1]

                    # Calculate percentage share by subtracting rate from previous year's rate
                    shares[year] = rate - prev_rate

            # Accumulate shares over the modelyears
            shares = shares.cumsum()
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
    

