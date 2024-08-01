import typing

from .database_manager import *

class TEK():
    """
    Holds all TEK parameters and getter methods for retrieving them.
    """
    
    def __init__(self, tek_params: typing.Dict[str, TEKParameters]):
        
        self.tek_params = tek_params

    def get_building_year(self, tek: str) -> int:
        """
        Retrieves the building year for the specified TEK.

        Parameters:
        - tek (str): The TEK string for which the building year is to be retrieved.

        Returns:
        - building_year (int): The building year associated with the specified TEK.
        """
        params_per_tek = self.tek_params[tek]
        building_year = params_per_tek.building_year
        return building_year
    
    def get_start_year(self, tek: str) -> int:
        """
        Retrieves the start year for the specified TEK.

        Parameters:
        - tek (str): The TEK string for which the start year is to be retrieved.

        Returns:
        - start_year (int): The start year associated with the specified TEK.
        """
        params_per_tek = self.tek_params[tek]
        start_year = params_per_tek.start_year
        return start_year
    
    def get_end_year(self, tek: str) -> int:
        """
        Retrieves the end year for the specified TEK.

        Parameters:
        - tek (str): The TEK string for which the end year is to be retrieved.

        Returns:
        - end_year (int): The end year associated with the specified TEK.
        """
        params_per_tek = self.tek_params[tek]
        end_year = params_per_tek.end_year
        return end_year
        
        





