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

# HELP FUNCTIONS --------------------------

# Lists to series in dict
def dict_with_lists_to_series(dict1):

    for key, lists in dict1.items():
        series = pd.Series(lists, index=range(2010, 2050+1), name='area')
        series.index.name = 'year'
        dict1[key] = series.astype(np.float64)
    
    return dict1

# Function to compare dictionaries 
def compare_dict_of_series(dict1, dict2):

    logger.info('Comparing dictionaries...')

    if dict1.keys() != dict2.keys():
        print('Keys are different')

    for key in dict1:
        
        series1 = dict1[key]
        series2 = dict2[key]

        if series1.equals(series2) == False:
            print(f'Not equal: {key}')

            comp = series1.compare(series2)
            print(comp)
            

# Function to compare nested dictionaries
def compare_nested_dict_of_series(dict1, dict2, precision):

    logger.info('Comparing dictionaries...')

    if dict1.keys() != dict2.keys():
        print('Keys are different')

    for condition in dict1:

        tek_shares1 = dict1[condition]
        tek_shares2 = dict2[condition]

        for tek in tek_shares1:
            series1 = tek_shares1[tek]
            series2 = tek_shares2[tek]

            if series1.equals(series2) == False:
                print(f'Not equal: {condition}, {tek}')
                comp = series1.compare(series2)
                if precision != None:
                    comp['diff'] = round(comp.self, precision) - round(comp.other, precision)
                else:
                    comp['diff'] = comp.self - comp.other

                diff = comp[comp["diff"] != 0]
                if len(diff) > 0:
                    print(diff)
                else:
                    print(f'No difference with precision = {precision}')

# Compare dictionaries
def test_compare_nested_dict_of_series(dict1, dict2):

    logger.info('Comparing dictionaries...')

    if dict1.keys() != dict2.keys():
        assert print('Keys are different')

    for condition in dict1:

        tek_shares1 = dict1[condition]
        tek_shares2 = dict2[condition]

        for tek in tek_shares1:
            series1 = tek_shares1[tek]
            series2 = tek_shares2[tek]

            pd.testing.assert_series_equal(series1, series2)

# -----------------------------------------

# NEW AREA CLASS ---------------------

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

modelyears = YearRange(2010, 2050)

# create building object to retireve necessary parameters
building = Buildings.build_buildings(building_category, database_manager)

# Retrieve necessary parameters from building object
tek_list = building.tek_list
tek_params = building.tek_params
shares_per_condition = building.shares_per_condition

# retrieve area parameter
area_start_year = database_manager.get_area_start_year()[building_category]

# For testing with one tek
#tek = tek_list[5] # 4 = tek97 for commercial, 8 = tek21
#logger.info(tek)
#logger.info(f"construction year: {tek_params[tek].building_year}")
#logger.info(f"tek period: {tek_params[tek].start_year} - {tek_params[tek].end_year}")

#print(area_start_year)

area_forecast = AreaForecastNew(building_category, area_start_year, tek_list, tek_params, shares_per_condition)

demolition_floor_area = area_forecast.calc_total_demolition_area_per_year()

# calculate constructed floor area
constructed_floor_area = ConstructionCalculator.calculate_construction(building_category, 
                                                                       demolition_floor_area,
                                                                       database_manager,
                                                                       modelyears).accumulated_constructed_floor_area


#area_pre_construction = area_forecast.calc_area_pre_construction_per_tek_condition()
#area_construction = area_forecast.calc_area_with_construction_per_tek_condition(constructed_floor_area)
#area = area_forecast.calc_area(constructed_floor_area)

print(demolition_floor_area.diff().fillna(0))

# OLD AREA CLASS -----------------------

# Retrieve necessary parameters from building object
area_params = building.area_params
condition_list = BuildingCondition.get_full_condition_list()


area_old = AreaForecast(building_category, area_params, tek_list, tek_params, condition_list, shares_per_condition)

# get acc construction areae
demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=modelyears)
yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area,
                                                                       database_manager, modelyears)
constructed_floor_area = list(yearly_constructed.accumulated_constructed_floor_area)

area2 = area_old.calc_area(constructed_floor_area)

# convert series to lists
for tek, area_dict in area2.items():
    area2[tek] = dict_with_lists_to_series(area_dict)

#compare_nested_dict_of_series(area, area2, precision = None)

#test_compare_nested_dict_of_series(area, area2)
