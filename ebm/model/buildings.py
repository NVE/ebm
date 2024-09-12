import typing

import pandas as pd

from .area_forecast import AreaForecast
from .building_category import BuildingCategory
from .building_condition import BuildingCondition
from .data_classes import TEKParameters, YearRange
from .database_manager import DatabaseManager
from .filter_scurve_params import FilterScurveParams
from .filter_tek import FilterTek
from .scurve import SCurve
from .scurve_processor import ScurveProcessor
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
        self.scurves = ScurveProcessor(self.scurve_condition_list, self.scurve_params).get_scurves()
        self.never_shares = ScurveProcessor(self.scurve_condition_list, self.scurve_params).get_never_shares()
        self.shares_per_condition = self.get_shares()
        self.area_params = area_params #TODO: change so that the area params are filtered on building category? 

    def get_shares(self, years: YearRange = YearRange(2010, 2050)) -> typing.Dict:
        """ 
        Calculate the shares per condition for all TEKs in the building category.

        This method initializes the `SharesPerCondition` class with the TEK list, TEK parameters,
        and S-curve data, and retrieves the shares per condition for the building category.

        Returns:
        - shares_condition (dict): A dictionary where the keys are the condition names and the values are
                                   the shares per condition for each TEK.
        """
        shares_condition = SharesPerCondition(self.tek_list, self.tek_params, self.scurves, self.never_shares,
                                              model_start_year=years.start,
                                              model_end_year=years.end)

        shares_per_condition = shares_condition.shares_per_condition
        return shares_per_condition

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

    def build_area_forecast(self,
                            database_manager: DatabaseManager,
                            model_start_year: int = 2010,
                            model_end_year: int = 2050) -> AreaForecast:
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
        dm = database_manager if database_manager else DatabaseManager()
        area_parameters = dm.get_area_parameters()
        tek_params = dm.get_tek_params(self.tek_list)
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
    def build_buildings(building_category: BuildingCategory,
                        database_manager: DatabaseManager = None) -> 'Buildings':
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
        dm = database_manager if database_manager else DatabaseManager()
        tek_list = dm.get_tek_list()
        tek_params = dm.get_tek_params(tek_list)
        scurve_params = dm.get_scurve_params()
        area_params = dm.get_area_parameters()
        scurve_condition_list = BuildingCondition.get_scruve_condition_list()
        building = Buildings(building_category=building_category,
                             tek_list=tek_list,
                             tek_params=tek_params,
                             scurve_condition_list=scurve_condition_list,
                             scurve_params=scurve_params,
                             area_params=area_params)
        return building
