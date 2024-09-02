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
from ebm.model.shares_per_condition_series import SharesPerCondition
from ebm.model.bema_validation import *

#TODO: use DB manager to get relevant data to run s-curve class from here

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

tek_list = FilterTek.get_filtered_list(building_category, database_manager.get_tek_list())

## Test: refactor scruve datatype
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
scurve_data_params = database_manager.get_scurve_params()

scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)

scurve_processor = ScurveProcessor(scurve_condition_list, scurve_params)

scurves = scurve_processor.get_scurves()
never_shares = scurve_processor.get_never_shares()

print(scurves)
print(never_shares)

#shares = SharesPerCondition(tek_list, tek_params, )

#building = Buildings.build_buildings(building_category, database_manager)
