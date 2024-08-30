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
from ebm.model.bema_validation import *

#TODO: use DB manager to get relevant data to run s-curve class from here

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE
scurve_condition_list = BuildingCondition.get_scruve_condition_list()

building = Buildings.build_buildings(building_category, database_manager)
scurve_data = building.scurve_data
scurve_params = building.scurve_params

print(scurve_params)
