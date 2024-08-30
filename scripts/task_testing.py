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
from ebm.model.bema_validation import *

#TODO: use DB manager to get relevant data to run s-curve class from here

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

## Test: refactor scruve datatype
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
scurve_data_params = database_manager.get_scurve_params()

scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)

condition = BuildingCondition.SMALL_MEASURE
scurve_params_condition = scurve_params[condition]

# Calculate the S-curve 
s = SCurve(scurve_params_condition.earliest_age, 
           scurve_params_condition.average_age, 
           scurve_params_condition.last_age,
           scurve_params_condition.rush_years, 
           scurve_params_condition.rush_share, 
           scurve_params_condition.never_share)

rates_per_year = s.get_rates_per_year_over_building_lifetime()
scurve = s.calc_scurve()

#print(scurve)

#building = Buildings.build_buildings(building_category, database_manager)
