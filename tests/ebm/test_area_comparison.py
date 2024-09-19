import argparse
import sys
import typing
import os
import pytest


from loguru import logger
from dotenv import load_dotenv
import pandas as pd
import numpy as np

from ebm.model.scurve import SCurve
from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.filter_scurve_params import FilterScurveParams
from ebm.model.scurve_processor import ScurveProcessor
from ebm.model.filter_tek import FilterTek
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.area_forecast_new import AreaForecastNew
from ebm.model.area_forecast import AreaForecast
from ebm.model.construction import ConstructionCalculator

from ebm.model.bema_validation import *

@pytest.fixture
def area1(building_category):
    return area_new(building_category)

@pytest.fixture
def area2(building_category):
    return area_old(building_category)

def area_new(building_category: BuildingCategory) -> typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]]:

    database_manager = DatabaseManager()
    area_start_year = database_manager.get_area_start_year()[building_category]

    building = Buildings.build_buildings(building_category, database_manager)

    tek_list = building.tek_list
    tek_params = building.tek_params
    shares_per_condition = building.shares_per_condition

    area_forecast = AreaForecastNew(building_category, area_start_year, tek_list, tek_params, shares_per_condition)

    demolition_floor_area = area_forecast.calc_total_demolition_area_per_year()
    constructed_floor_area = ConstructionCalculator.calculate_construction(building_category, 
                                                                           demolition_floor_area,
                                                                           database_manager, 
                                                                           YearRange(2010, 2050)).accumulated_constructed_floor_area
    
    area_new = area_forecast.calc_area(constructed_floor_area)
    return area_new


def area_old(building_category: BuildingCategory) -> typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]]:

    database_manager = DatabaseManager()
    building = Buildings.build_buildings(building_category, database_manager)
    area_forecast = building.build_area_forecast(database_manager)

    demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=YearRange(2010,2050))
    yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area,
                                                                        database_manager, YearRange(2010,2050))
    constructed_floor_area = list(yearly_constructed.accumulated_constructed_floor_area)
    
    area_old = area_forecast.calc_area(constructed_floor_area)

    def dict_with_lists_to_series(dict1):

        for key, lists in dict1.items():
            series = pd.Series(lists, index=YearRange(2010,2050).year_range, name='area')
            series.index.name = 'year'
            dict1[key] = series.astype(np.float64)
        
        return dict1
    
    for tek, area_dict in area_old.items():
        area_old[tek] = dict_with_lists_to_series(area_dict)

    return area_old

@pytest.mark.parametrize("building_category", BuildingCategory)
def test_compare_area_dictionaries(area1: typing.Dict, area2: typing.Dict):

    # Check if both dictionaries have the same keys
    assert area1.keys() == area2.keys(), "Dictionaries have different keys"

    for tek in area1:
        
        # Ensure the condition exists in both dictionaries
        assert tek in area2, f"{tek} not found in both dictionaries"

        tek_shares1 = area1[tek]
        tek_shares2 = area2[tek]

        assert tek_shares1.keys() == tek_shares2.keys(), f"Different keys in dictionaries for condition {tek}"

        for condition in tek_shares1:
            series1 = tek_shares1[condition]
            series2 = tek_shares2[condition]

            pd.testing.assert_series_equal(series1, series2, check_names=False, check_index_type=False, 
                                           obj=f"Series not equal for {tek}, {condition}")



