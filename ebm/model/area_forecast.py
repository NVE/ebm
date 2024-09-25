import typing

import pandas as pd

from .area import Area
from .building_condition import BuildingCondition
from .data_classes import TEKParameters
from .tek import TEK


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
                 building_category: str,
                 area_params: pd.DataFrame,
                 tek_list: typing.List[str],   
                 tek_params: typing.Dict[str, TEKParameters], 
                 condition_list: typing.List[str],
                 shares_per_condtion: typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]],
                 model_start_year: int = 2010,
                 model_end_year: int = 2050,) -> None:

        self.model_start_year = model_start_year
        self.model_end_year = model_end_year
        self.building_category = building_category
        self.area = Area(area_params)
        self.tek_list = tek_list
        self.tek = TEK(tek_params)                                  
        self.condition_list = condition_list  

        #TODO: remove after refactoring to series
        self.shares_per_condition = self._convert_shares_to_series(shares_per_condtion)

    # TODO: remove after refactoring to series
    def _convert_shares_to_series(self, shares_per_condtion: typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]]):
        converted_shares = {}
        for condition, tek_shares in shares_per_condtion.items():
            converted_tek_shares = {}
            for tek in tek_shares:
                shares = tek_shares[tek]
                if isinstance(shares, pd.Series):
                    converted_tek_shares[tek] = shares.to_list()
                else:
                    converted_tek_shares[tek] = shares
            
            converted_shares[condition] = converted_tek_shares
        
        return converted_shares
    
    def _calc_area_pre_construction_tek(self, tek: str) -> typing.Dict[str, typing.List]:
        """
        Calculates the area per condition for a given TEK used prior to construction.

        Construction of new buildings first begins in the model start year. Thus, this method only works for TEK's that are
        used in periods before the model start year. For these TEK's, the area per condition is calculated over the model years. 
        This is done by multiplying the area of the TEK in the model start year with the corresponding building condition share 
        in model year *n*. 

        Parameters:
        - tek (str): The TEK value to calculate the area for.

        Returns:
        - area_per_condition (Dict[str, List]): A dictionary where the keys are conditions and the values are lists of area per year.   
        """
        # Retrieve the total area in the model start year
        area_start_year = self.area.get_area_per_building_category_tek(self.building_category, tek) 
        
        # Empty dictionary to be filled with area per condition in for loop
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
        Calculates the area per condition for all TEK's used prior to construction.

        Construction of new buildings first begins in the model start year. Thus, this method iterates through each TEK in
        the TEK list and checks if the model start year is after the TEK period. For these TEKs, the method calculates the
        area per condition over the model years. This is done by multiplying the area of the TEK in the model start year with
        the corresponding building condition share in model year *n*. The results are stored in a dictionary with TEK values 
        as keys and another dictionary as values, where the nested dictionary contains conditions as keys and lists of area 
        per year as values.
        
        Returns:
        - area_per_tek (Dict): A dictionary where the keys are TEK identifiers and the values are dictionaries of area per condition.   
        """
        # Dictionary to be filled with area per condition over model years for each TEK  
        area_per_tek = {}
        for tek in self.tek_list:
            tek_end_year = self.tek.get_end_year(tek)
            # Control that the TEK period is before the model start year (when new buildings are constructed) 
            if tek_end_year < self.model_start_year:
                area_per_condition = self._calc_area_pre_construction_tek(tek)
                area_per_tek[tek] = area_per_condition

        return area_per_tek
    
    def calc_total_demolition_area_per_year(self) -> typing.List:
        """
        Aggregates the area that is demolished per model year across all TEK's used prior to construction. 

        Returns:
        - total_demolition (List): A list of the total area that is demolished per model year.
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


    def _calc_area_with_construction_tek(self, tek: str, accumulated_constructed_floor_area: typing.List) -> typing.Dict[str, typing.List]:
        """
        Calculates the area per condition for a given TEK used in a period with construction of new buildings.

        This method calculates the area for each building condition over the model years, taking into account the accumulated 
        area from construction of new buildings within the period of the given TEK. 

        Parameters:
        - tek (str): The TEK identifier to filter on.
        - accumulated_constructed_floor_area (list): List with accumulated construction per year of the model horizon, 
                                                     which can be retrieved from the ConstructionCalculator class.

        Returns:
        - area_per_condition (dict): A dictionary with conditions as keys and lists of area per year as values.
        """
        # Retrieve accumulated construction area per year (TODO: edit after merge with construction class)

        model_years = [*range(self.model_start_year, self.model_end_year+1)]
        tek_start_year = self.tek.get_start_year(tek)
        tek_end_year = self.tek.get_end_year(tek)

        try:
            area_start_year = self.area.get_area_per_building_category_tek(self.building_category, tek)
        except ValueError:
            area_start_year = 0.0

        # Empty dictionary to be filled with area per condition in for loop
        area_per_condition = {}
        for condition in self.condition_list:
            # Empty list to be filled with area per year for given condition in for loop
            area_per_year = []
            shares_per_year = self.shares_per_condition[condition][tek]
            for idx, year in enumerate(model_years):
                # Get share for the current model year
                share = shares_per_year[idx]
                # Set area to 0 before the start of their TEK period
                if year < tek_start_year:
                    area = 0.0
                # Distinct calculation method if the start year of the model horizon is within the TEK period
                elif tek_start_year <= self.model_start_year <= tek_end_year:
                        # Get area and new construction area in the model start year
                        construction_start_year = accumulated_constructed_floor_area[0]
                        area = share * (area_start_year + construction_start_year)
                # Distinct calculation if the TEK period begins after the start year of the model horizon
                else:
                    # Retrieve index for start and end year of TEK period in modelyear list
                    idx_tek_start_year = model_years.index(tek_start_year)
                    idx_tek_end_year = model_years.index(tek_end_year) 
                    # Retrieve construction area for specific model years used in calculation
                    construction_year_before_tek_period = accumulated_constructed_floor_area[idx_tek_start_year - 1]
                    construction_tek_end_year = accumulated_constructed_floor_area[idx_tek_end_year]
                    construction_current_year = accumulated_constructed_floor_area[idx]
                    # Accumuluated construction area is only added in the years of the TEK period    
                    if tek_start_year <= year <= tek_end_year:
                        area = share * (construction_current_year - construction_year_before_tek_period + area_start_year)
                    # The construction area is held constant from the last year of the TEK period 
                    else:
                        area = share * (construction_tek_end_year - construction_year_before_tek_period + area_start_year)

                area_per_year.append(round(area, 5))
            area_per_condition[condition] = area_per_year    
        return area_per_condition


    def calc_area_with_construction(self, accumulated_constructed_floor_area: typing.List[float] = None) -> typing.Dict[str, typing.Dict[str, typing.List]]:
        """
        Calculates the area per condition for all TEK's used in periods with construction of new buildings.

        Construction of new buildings first begins in the model start year. Thus, this method iterates through each TEK in
        the TEK list and checks if the model start year is within the TEK period or prior to it. For these TEKs, the method
        calculates the area per condition over the model years, taking into account the accumulated area from construction 
        within the period of the given TEK. The results are stored in a dictionary with TEK values as keys and another 
        dictionary as values, where the nested dictionary contains conditions as keys and lists of area per year as values.

        Returns:
        - area_per_tek (dict): A dictionary where keys are TEK identifies and values are dictionaries with conditions as keys 
                               and lists of area per year as values.
        """
        # Dictionary to be filled with area per condition over model years for each TEK
        area_per_tek = {}
        for tek in self.tek_list:
            # Retrieve the start and end year of the TEK period
            tek_start_year = self.tek.get_start_year(tek)
            tek_end_year = self.tek.get_end_year(tek)
            # Control that the model start year is within the TEK period or prior to it, as construction starts in the model start year
            if (tek_start_year <= self.model_start_year <= tek_end_year) or (self.model_start_year <= tek_start_year):
                # Calculate the area per condition for TEKs used in periods with construction 
                area_per_condition = self._calc_area_with_construction_tek(tek, accumulated_constructed_floor_area)
                area_per_tek[tek] = area_per_condition

        return area_per_tek

    def calc_area(self, accumulated_constructed_floor_area: typing.List[float] = None) -> typing.Dict[str, typing.Dict[str, typing.List]]:
        """
        Calculates area per condition over the model years for all TEKs.

        This method calculates and retrieves the area per condition over model years for TEKs with and without construction
        and combines them into a single dictionary.

        Returns:
        - area (dict): A dictionary where keys are TEK identifies and values are dictionaries with conditions as keys 
                       and lists of area per year as values.
        """
        # Calculate and retrieve area per condition over model years for TEKs with and without construction
        area_pre_construction = self.calc_area_pre_construction()
        area_with_construction = self.calc_area_with_construction(accumulated_constructed_floor_area)

        #TODO: add check to control if same TEK's are present in both dictonaries, then raise ValueError

        # Combine dictionaries 
        area = area_pre_construction.copy()
        for tek in area_with_construction:
            area[tek] = area_with_construction[tek]
        
        return area
    