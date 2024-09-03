import argparse
import sys
import typing
import os

from loguru import logger
from dotenv import load_dotenv
import pandas as pd

from ebm.model.scurve import SCurve
from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.filter_scurve_params import FilterScurveParams
from ebm.model.scurve_processor import ScurveProcessor
from ebm.model.filter_tek import FilterTek
from ebm.model.shares_per_condition_new import SharesPerConditionNew
from ebm.model.shares_per_condition import SharesPerCondition

from ebm.model.bema_validation import *


database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

# Refactor scruve datatype
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
scurve_data_params = database_manager.get_scurve_params()

scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)

scurve_processor = ScurveProcessor(scurve_condition_list, scurve_params)

scurves = scurve_processor.get_scurves()
never_shares = scurve_processor.get_never_shares()

# --------------------------

# help function
def dict_with_lists_to_series(dict1):

    for key, lists in dict1.items():
        series = pd.Series(lists, index=range(2010, 2050+1))
        dict1[key] = series
    
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

            print(series1.compare(series2))

# Function to compare nested dictionaries
def compare_nested_dict_of_series(dict1, dict2):

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


# Refactor Shares datatype

def create_shares_objects(building_category):
    database_manager = DatabaseManager()
    
    scurve_condition_list = BuildingCondition.get_scruve_condition_list()
    scurve_data_params = database_manager.get_scurve_params()
    scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)
    scurve_processor = ScurveProcessor(scurve_condition_list, scurve_params)
    scurves = scurve_processor.get_scurves()
    never_shares = scurve_processor.get_never_shares()

    tek_list = FilterTek.get_filtered_list(building_category, database_manager.get_tek_list())
    tek_params = database_manager.get_tek_params(tek_list)


    shares_new = SharesPerConditionNew(tek_list, tek_params, scurves, never_shares)
    shares_old = SharesPerCondition(tek_list, tek_params, scurves, never_shares)

    return shares_new, shares_old


for building_category in BuildingCategory: 

    logger.info(building_category)
    shares_new, shares_old = create_shares_objects(building_category)

    demo1 = shares_new.calc_shares_demolition()
    demo2 = shares_old.calc_shares_demolition()

    demo2 = dict_with_lists_to_series(demo2)

    compare_dict_of_series(demo1, demo2)
