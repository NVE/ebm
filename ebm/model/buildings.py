import typing

import pandas as pd

from .building_category import BuildingCategory
from .database_manager import DatabaseManager
from .area_forecast import AreaForecast
from .building_condition import BuildingCondition
from .data_classes import TEKParameters
from .filter_tek import FilterTek
from .filter_scurve_params import FilterScurveParams
from .scurve import SCurve
from .shares_per_condition import SharesPerCondition



# TODO:
# - remove _filter_tek_list and _filter_tek_params when the model is updated with new 2020 data.
# - add model years to a getter method for shares_per_condition dictionary, for user readability


class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """

    def __init__(self, 
                 building_category: str,
                 tek_list: typing.List[str],
                 tek_params: typing.Dict[str, TEKParameters],
                 scurve_condition_list: typing.List[str],
                 scurve_params: pd.DataFrame,
                 area_params: pd.DataFrame):
        
        self.building_category = building_category
        self.scurve_condition_list = scurve_condition_list
        self.tek_list = FilterTek.get_filtered_list(self.building_category, tek_list)  
        self.tek_params = FilterTek.get_filtered_params(self.tek_list, tek_params)
        self.scurve_params = FilterScurveParams.filter(self.building_category, self.scurve_condition_list, scurve_params) 
        self.scurve_data = self._get_scurve_data()
        self.shares_per_condition = self.get_shares()
        self.area_params = area_params #TODO: change so that the area params are filtered on building category? 

    def _get_scurve_data(self) -> typing.Dict:
        """
        Create a dictionary that holds S-curves and the "never share" parameter per building condition. 

        This method uses input S-curve parameters for each building condition (self.scurve_params), 
        calculates the S-curve, and stores the S-curve along with the "never share" parameter in a dictionary.
        The dictionary is used as an input argument in the TEK class. 

        Returns:
        - scurve_data (dict): A dictionary where keys are building conditions (str) and values 
                              are lists containing the S-curve tuple and the "never share" parameter (float).
        """
        scurve_data = {}

        for condition in self.scurve_condition_list:
            if condition not in self.scurve_params:
                msg = f'Encounted unknown condition {condition} while making scurve'
                raise ValueError(msg)
            
            # Filter S-curve parameters dictionary on condition
            scurve_params_condition = self.scurve_params[condition]
            
            # Calculate the S-curve 
            s = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                       scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share)
            scurve = s.calc_scurve()
            
            # Store the parameters in the dictionary
            scurve_data[condition] = [scurve, scurve_params_condition.never_share]
        
        return scurve_data

    def get_scurve(self, condition: str) -> typing.Dict:
        """
        Get the S-curve data for a specific building condition.

        This method retrieves the S-curve data for a specified building condition from the 
        `scurve_data` dictionary, which contains the precomputed S-curve for each condition.

        Parameters:
        - condition (str): The condition for which to retrieve the S-curve data (e.g., 'Renovation', 'Demolition').

        Returns:
        - scurve (dict): A dictionary containing the S-curve data for the specified condition.
                         The dictionary has 'year' as keys representing the years in the building
                         lifetime and 'scurve' as values representing the corresponding S-curve values.
        """
        scurve_list = self.scurve_data[condition][0]
        year_list = list(range(1, len(scurve_list) + 1))
        scurve = {'year':year_list, 'scurve':scurve_list}
        return scurve

    def get_shares(self) -> typing.Dict:
        """ 
        Calculate the shares per condition for all TEKs in the building category.

        This method initializes the `SharesPerCondition` class with the TEK list, TEK parameters,
        and S-curve data, and retrieves the shares per condition for the building category.

        Returns:
        - shares_condition (dict): A dictionary where the keys are the condition names and the values are
                                   the shares per condition for each TEK.
        """
        shares_condition = SharesPerCondition(self.tek_list, self.tek_params, self.scurve_data).shares_per_condition
        return shares_condition   

    # TODO: 
    # - add optional parameters to filter on specific TEKs and Years
    # - use BuildingCondition, so that the missing function can handle typo's for condition
    def get_shares_per_condition(self, condition: str) -> typing.Dict:
        """
        Get the shares for a specific condition for all TEKs in the building category.

        This method retrieves the shares for a specified condition from the `shares_per_condition`
        dictionary, which contains the shares per condition for each TEK.

        Parameters:
        - condition (str): The condition for which to retrieve the shares (e.g., 'Renovation', 'Demolition').

        Returns:
        - shares (dict): A dictionary where the keys are the TEKs and the values are the shares for the specified condition.
        """
        shares = self.shares_per_condition[condition]
        return shares

    def build_scurve(self, building_condition: BuildingCondition):
        """
        Build a SCurve object from the Building object. Reuse scurve_params from the Buildings (self) object.

        Parameters:
        - building_condition (str): The condition to create Scurve object for.

        Returns:
        - scurve: SCurve 
        """
        # Get relevant ScurveParameters dataclass from filtering scurve_params dictionary on building condition
        scurve_params_condition = self.scurve_params[building_condition]
            
        # Create the SCurve object
        scurve = SCurve(
            scurve_params_condition.earliest_age,
            scurve_params_condition.average_age,
            scurve_params_condition.last_age,
            scurve_params_condition.rush_years,
            scurve_params_condition.rush_share,
            scurve_params_condition.never_share)
        
        return scurve

    def build_area_forecast(self, database_manager: DatabaseManager, model_start_year: int = 2010, model_end_year: int = 2050):
        """
        Build a AreaForcast object from the Building object. Reuse building_category, tek_list, shares_per_condtion from
            the Buildings (self) object.

        Parameters
        ----------
        database_manager: ebm.model.DatabaseManager
            used to load area_params and tek_params
        model_start_year: int, default 2010
        model_end_year: int, default 2050

        Returns area_forecast: AreaForecast
        -------
        """
        area_parameters = database_manager.get_area_parameters()
        tek_params = database_manager.get_tek_params(self.tek_list)
        shares = self.get_shares()

        area_forecast = AreaForecast(
            model_start_year=model_start_year, 
            model_end_year=model_end_year,
            building_category=self.building_category,
            area_params=area_parameters,
            tek_list=self.tek_list,
            tek_params=tek_params,
            condition_list=BuildingCondition.get_full_condition_list(),
            shares_per_condtion=shares)
        return area_forecast

    @staticmethod
    def build_buildings(building_category: BuildingCategory, database_manager: DatabaseManager) -> 'Buildings':
        """
        Builds a Buildings object for building_category and read configuration from DatabaseManager.
          the DatabaseManager must implement .get_tek_list() .get_area_parameters() db.get_scurve_params()
          .get_area_parameters()

        Parameters
        ----------
        - building_category: BuildingCategory
        - database_manager: DatabaseManager

        Returns 
        -------
        - building: Buildings
        """

        tek_list = database_manager.get_tek_list()
        tek_params = database_manager.get_tek_params(tek_list)
        scurve_params = database_manager.get_scurve_params()
        area_params = database_manager.get_area_parameters()
        scurve_condition_list = BuildingCondition.get_scruve_condition_list()
        building = Buildings(building_category=building_category,
                             tek_list=tek_list,
                             tek_params=tek_params,
                             scurve_condition_list=scurve_condition_list,
                             scurve_params=scurve_params,
                             area_params=area_params)
        return building
