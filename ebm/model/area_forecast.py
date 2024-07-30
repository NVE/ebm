import typing
import pandas as pd

from .data_classes import TEKParameters
from .tek import TEK
from .area import Area

#TODO: 
# - Got to evaluate if get_area_per_condition method should only be limited to TEKs before 'nybygging', or integrated with the rest of TEKs 

# Comments:
# - condition_list: must contain all 5 conditions -> must update input data of condition_list or hardcode, and adjust methods for scurve in buildings
# - create an Area data_class? if so, the class can take area_params as input and get relevant data (for the building cat and tek) trough the class
# - could use tek_list as input argument and loop trough all TEKs in this class:
#       - then there can be one method for area_per_tek and one where all are grouped together, e.g. with TEK as keys in a dict for example
#       - this could be used to filter the area parameters, for example an area dataclass 

# Possible issue in the future:
# - problemer med riving og nybygging kobling dersom tidshorisonten overstiger tidligste alder for riving på nye TEKer

class AreaForecast():

    DEMOLITION = 'demolition'

    def __init__(self,
                 start_year: int,
                 building_category: str,
                 area_params: pd.DataFrame,
                 tek_list: typing.List[str],   
                 tek_params: typing.Dict[str, TEKParameters], 
                 condition_list: typing.List[str],
                 shares_per_condtion: typing.Dict) -> None:

        self.start_year = start_year
        self.building_category = building_category
        self.area = Area(area_params)
        self.tek_list = tek_list
        self.tek = TEK(tek_params)                                  
        self.condition_list = condition_list            
        self.shares_per_condition = shares_per_condtion
        self.acc_construction_area = _accumulated_construction_area_per_year()

    # TODO: remove method after merge with construction class
    def _accumulated_construction_area_per_year(self) -> typing.List:
        """
        Temporary method to retrieve accumulated construction area per year as list. To be deleted.
        """
        df = pd.read_excel('input/temporary_construction_data.xlsx')
        df = df.melt(id_vars='building_category')
        df = df[df['building_category'] == self.building_category]
        acc_construction_area_per_year = df['value'].tolist()
        return acc_construction_area_per_year
            
    def _calc_area_pre_construction_per_tek(self, tek: str) -> typing.Dict[str, typing.List]:
        """
        Calculates and distributes the area per condition for a given TEK used prior to construction (defined by the model start year).

        Parameters:
        - tek (str): The TEK value to calculate the area for.

        Returns:
        - area_per_condition (Dict[str, List]): A dictionary where the keys are conditions and the values are lists of area per year.   
        """
        # Retrieve the total area in the start year
        area_start_year = self.area.get_area_per_building_category_tek(self.building_category, tek) 

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
    
    def calc_area_pre_construction(self) -> typing.Dict[str, typing.Dict[str, typing.List]]:
        """
        Calculates and distributes the area per condition for all TEK's used prior to construction (defined by the model start year).
        
        Returns:
        - area_per_tek (Dict): A dictionary where the keys are TEK values and the values are dictionaries of area per condition.   
        """
        area_per_tek = {}
        for tek in self.tek_list:
            tek_end_year = self.tek.get_end_year(tek)
            # Control that the TEK period is before the model start year (when new buildings are constructed) 
            if tek_end_year < self.start_year:
                area_per_condition = self._calc_area_pre_construction_per_tek(tek)
                area_per_tek[tek] = area_per_condition

        return area_per_tek
    
    def calc_total_demolition_area_per_year(self) -> typing.List:
        """
        Aggregates the area that is demolished per year across all TEK's used prior to construction (defined by the model start year). 

        Returns:
        - total_demolition (List): A list of the total area that is demolished per year.
        """
        area_pre_construction = self.calc_area_pre_construction()
        # Fill a list with the demolition area per year for each TEK
        demolition_list = []
        for tek in area_pre_construction:
            demolition_per_tek = area_pre_construction[tek][self.DEMOLITION]                    
            demolition_list.append(demolition_per_tek) 

        # Aggregate the demolition lists to get accumumulated area over time
        total_demolition = [sum(demolition_area) for demolition_area in zip(*demolition_list)]

        # Calculate total demolished area per year
        total_demolition_per_year = [total_demolition[0]] + [current - previous for previous, current in zip(total_demolition[:-1], total_demolition[1:])]

        return total_demolition_per_year
            
            

        
        
