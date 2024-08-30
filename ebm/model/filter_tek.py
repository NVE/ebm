import typing

from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import TEKParameters

class FilterTek:
    """
    Temporary class for filtering TEK lists and parameters. 
    """

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
    

    @staticmethod
    def get_filtered_params(tek_list: typing.List[str], tek_params: typing.Dict[str, TEKParameters]) -> typing.Dict[str, TEKParameters]:
        """
        Filters the TEK parameters to include only those relevant to the provided TEK list.

        This method takes a dictionary of TEK parameters and filters it to include only 
        the parameters for TEKs that are present in the `tek_list`. This ensures that 
        only the relevant TEK parameters are retained for use in subsequent calculations.

        Parameters:
        - tek_list (List[str]): A list of TEK identifiers to filter by.
        - tek_params (Dict[str, TEKParameters]): A dictionary where the keys are TEK identifiers 
                                                    and the values are TEKParameters objects containing
                                                    the parameters for each TEK.

        Returns:
        - filtered_tek_params (Dict[str, TEKParameters]): A dictionary containing only the TEK parameters
                                                        for the TEKs present in the `tek_list`.
        """
        filtered_tek_params = {}
        for tek in tek_list:
            filtered_tek_params[tek] = tek_params[tek]    

        return filtered_tek_params

