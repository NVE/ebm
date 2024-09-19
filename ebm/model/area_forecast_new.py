import typing

import pandas as pd

from .area import Area
from .data_classes import TEKParameters,YearRange
from .building_condition import BuildingCondition
from .tek import TEK


# Comments:
# - condition_list: must contain all 5 conditions -> must update input data of condition_list or hardcode, and adjust methods for scurve in buildings
# - create an Area data_class? if so, the class can take area_params as input and get relevant data (for the building cat and tek) trough the class
# - could use tek_list as input argument and loop trough all TEKs in this class:
#       - then there can be one method for area_per_tek and one where all are grouped together, e.g. with TEK as keys in a dict for example
#       - this could be used to filter the area parameters, for example an area dataclass 

# Possible issue in the future:
# - problemer med riving og nybygging kobling dersom tidshorisonten overstiger tidligste alder for riving på nye TEKer

class AreaForecastNew():

    DEMOLITION = 'demolition'

    def __init__(self,
                 building_category: str,
                 area_params: pd.DataFrame,
                 tek_list: typing.List[str],   
                 tek_params: typing.Dict[str, TEKParameters], 
                 condition_list: typing.List[str],
                 shares_per_condtion: typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]],
                 period: YearRange = YearRange(2010, 2050)) -> None:

        self.building_category = building_category
        self.area_data = area_params
        self.tek_list = tek_list
        self.tek_params = tek_params                                  
        self.condition_list = condition_list  
        self.period = period

        #TODO: remove after refactoring to series
        self.shares_per_condition = self._convert_shares_to_series(shares_per_condtion)

    def get_area_per_building_category_tek(self, building_category: str, tek: str) -> int:
        """
        Retrieves the total area (m^2) of specific building category and TEK.

        This method filters the DataFrame `area_params` using the provided `building_category` and `tek`.
        It assumes that the filtered DataFrame will contain only one row. The area value from this row,
        in the column specified by `COL_AREA`, is then retrieved and returned.
        
        Parameters:
        - building_category (str): The building category to filter on.
        - tek (str): The TEK value to filter on.

        Returns:
        - area_value (int): The area value for the specified building category and TEK.
        """
        # Check if the building category is in the DataFrame
        if building_category not in self.area_data[self.COL_BUILDING_CATEGORY].values:
            raise ValueError(f"Building category '{building_category}' not found in the DataFrame.")
        
        # Filter dataframe on building category
        filtered_area_data = self.area_data[self.area_data[self.COL_BUILDING_CATEGORY] == building_category]

        # Check if the tek is in the DataFrame
        if tek not in filtered_area_data[self.COL_TEK].values:
            raise ValueError(f"'{tek}' not found in the DataFrame.")
        
        # Filter dataframe on building category and tek
        filtered_area_data = filtered_area_data[filtered_area_data[self.COL_TEK] == tek]
        
        # Retrieve the area value, assuming there is only one row in the filtered DataFrame
        area_value = filtered_area_data.iloc[0][self.COL_AREA]
        return area_value


if __name__ == '__main__':

    from ebm.model.database_manager import DatabaseManager
    from ebm.model.building_category import BuildingCategory
    from ebm.model.buildings import Buildings
    from ebm.model.filter_scurve_params import FilterScurveParams
    from ebm.model.scurve_processor import ScurveProcessor
    from ebm.model.filter_tek import FilterTek

    database_manager = DatabaseManager()
    building_category = BuildingCategory.HOUSE
    
    building = Buildings.build_buildings(building_category, database_manager)

    area_params = building.area_params
    tek_list = building.tek_list
    tek_params = building.tek_params
    condition_list = BuildingCondition.get_full_condition_list()
    shares_per_condition = building.shares_per_condition




    AreaForecastNew(building_category, area_params)