import typing

import pandas as pd

from ebm.model.building_category import BuildingCategory

class FilterTek:

    CATEGORY_APARTMENT = 'apartment_block'
    CATEGORY_HOUSE = 'house'
    COMMERCIAL_BUILDING = 'COM'
    RESIDENTIAL_BUILDING = 'RES'
    PRE_TEK49_APARTMENT = 'PRE_TEK49_RES_1950'
    PRE_TEK49_HOUSE = 'PRE_TEK49_RES_1940'

    @staticmethod
    def get_filtered_list(building_category: BuildingCategory, tek_list: typing.List[str]) -> typing.List[str]:
        """
        Filters the provided TEK list based on the building category.

        Parameters:
        - building_category (BuildingCategory): The category of the building.
        - tek_list (List[str]): List of TEK strings to be filtered.

        Returns:
        - filtered_tek_list (List[str]): Filtered list of TEK strings.
        """
        residential_building_list = [FilterTek.CATEGORY_APARTMENT, FilterTek.CATEGORY_HOUSE]
        
        if building_category in residential_building_list:
            # Filter out all TEKs associated with commercial buildings
            filtered_tek_list = [tek for tek in tek_list if FilterTek.COMMERCIAL_BUILDING not in tek]

            # Further filtering based on the specific residential building category
            if building_category == FilterTek.CATEGORY_APARTMENT:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != FilterTek.PRE_TEK49_HOUSE]
            elif building_category == FilterTek.CATEGORY_HOUSE:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != FilterTek.PRE_TEK49_APARTMENT]

        else:
            # Filter out all TEKs associated with residential buildings
            filtered_tek_list = [tek for tek in tek_list if FilterTek.RESIDENTIAL_BUILDING not in tek]

        return filtered_tek_list
    

    #TODO: add static method for filtering tek_params

if __name__ == '__main__':

    from ebm.model.building_category import BuildingCategory
    from ebm.model.database_manager import DatabaseManager
    
    building_category = BuildingCategory.HOUSE
    database_manager = DatabaseManager()
    tek_list = database_manager.get_tek_list()
    print(tek_list)
    tek_list = FilterTek.get_filtered_list(building_category, tek_list)
    print(tek_list)
