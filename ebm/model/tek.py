from .database_manager import *

class TEK():
    """
    Holds all TEK parameters and getter methods for retrieving them.
    """
    
    def __init__(self, tek_params: typing.Dict[str, TEKParameters]):
        
        self.tek_params = tek_params

    def get_building_year(self, tek: str):
        """
        get tek params
        """
        params_per_tek = self.tek_params[tek]
        building_year = params_per_tek.building_year
        return building_year
    
    def get_start_year(self, tek: str):
        """
        get tek params
        """
        params_per_tek = self.tek_params[tek]
        start_year = params_per_tek.start_year
        return start_year
    
    def get_end_year(self, tek: str):
        """
        get tek params
        """
        params_per_tek = self.tek_params[tek]
        end_year = params_per_tek.end_year
        return end_year
        
        





