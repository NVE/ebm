import typing
import pandas as pd

from .data_classes import TEKParameters
from .tek import TEK
from .area import Area

#TODO: 
# - Got to evaluate if get_area_per_condition method should only be limited to TEKs before 'nybygging', or integrated with the rest of TEKs 
# - get_are_per_condition currently only works for TEKs that does not include 'nybygging'. E.g. breaks when tek is not in TEK column of area_params data
# - get_are_per_tek does not currently work, as it loops through all the teks in the tek_list. While TEKs in area_params df only goes to TEK97/TEK07
#       - possible solution: got to add a 'break' at the last TEK in the TEK column of the area_params df
#       - this can e.g. be done by editing the tek list based on the TEKs in the area_params. Can pass the column as a series or dataclass or something   

# Comments:
# - condition_list: must contain all 5 conditions -> must update input data of condition_list or hardcode, and adjust methods for scurve in buildings
# - create an Area data_class? if so, the class can take area_params as input and get relevant data (for the building cat and tek) trough the class
# - could use tek_list as input argument and loop trough all TEKs in this class:
#       - then there can be one method for area_per_tek and one where all are grouped together, e.g. with TEK as keys in a dict for example
#       - this could be used to filter the area parameters, for example an area dataclass 

class AreaForecast():

    def __init__(self,
                 building_category: str,
                 area_params: pd.DataFrame,
                 tek_list: typing.List[str],   
                 tek_params: typing.Dict[str, TEKParameters], 
                 condition_list: typing.List[str],
                 shares_per_condtion: typing.Dict) -> None:

        self.building_category = building_category
        self.area = Area(area_params)
        self.tek_list = tek_list
        self.tek = TEK(tek_params)                                  
        self.condition_list = condition_list            
        self.shares_per_condition = shares_per_condtion
    
    def get_area_per_condition(self, tek: str) -> typing.Dict[str, typing.List]:
        """
        unfinished method

        Process:
        loop trough condition_lists, get relevant condition shares for the given tek, 
        loop trough index of shares list, perform calculation (area * share for current year),
        append area to area_per_year list
 
        - do i need tek_params in this method?
        - need to add different if statements for performing calculation if this is going to work for every single tek
        """

        # Retrieve the total area in the start year
        area_start_year = self.area.get_area_per_building_category_tek(self.building_category, tek) 

        #tek_building_year = self.tek.get_building_year(tek)
        #tek_start_year = self.tek.get_start_year(tek)

        area_per_condition = {}
        for condition in self.condition_list:     
            
            area_per_year = []
            shares = self.shares_per_condition[condition]
            shares_tek = shares[tek]
            n_modelyears = len(shares_tek)
            for n in range(0, n_modelyears):
                share = shares_tek[n]
                area = area_start_year * share
                area_per_year.append(area) 
                
            area_per_condition[condition] = area_per_year 

        return area_per_condition
    
    def get_area_per_tek(self):
        """
        unfinished method
        """
        area_per_tek = {}
        for tek in self.tek_list:
            print(tek)
            area_per_condition = self.get_area_per_condition(tek)
            area_per_tek[tek] = area_per_condition
        return area_per_tek
            

        
        
