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
def construction1(building_category):
    return construction_new(building_category)

@pytest.fixture
def construction2(building_category):
    return construction_old(building_category)


def construction_new(building_category: BuildingCategory):

    database_manager = DatabaseManager()
    area_start_year = database_manager.get_area_start_year()[building_category]

    building = Buildings.build_buildings(building_category, database_manager)

    tek_list = building.tek_list
    tek_params = building.tek_params
    shares_per_condition = building.shares_per_condition

    area_forecast_new = AreaForecastNew(building_category, area_start_year, tek_list, tek_params, shares_per_condition)
    demolition_new = area_forecast_new.calc_total_demolition_area_per_year()
    construction_new = ConstructionCalculator.calculate_construction(building_category, 
                                                                           demolition_new,
                                                                           database_manager, 
                                                                           YearRange(2010, 2050)).accumulated_constructed_floor_area
    return construction_new

def construction_old(building_category: BuildingCategory):
    database_manager = DatabaseManager()
    building = Buildings.build_buildings(building_category, database_manager)
    area_forecast_old = building.build_area_forecast(database_manager)

    demolition_old = pd.Series(data=area_forecast_old.calc_total_demolition_area_per_year(), index=YearRange(2010,2050))
    yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_old,
                                                                        database_manager, YearRange(2010,2050))
    construction_old = yearly_constructed.accumulated_constructed_floor_area

    return construction_old

@pytest.mark.parametrize("building_category", BuildingCategory)
def test_compare_series(construction1, construction2):

    pd.testing.assert_series_equal(construction1, construction2, check_names=False, check_index_type=False)






