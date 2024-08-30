import argparse
import sys
import typing
import os

from loguru import logger
from dotenv import load_dotenv
import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.bema_validation import *

database_manager = DatabaseManager()
building_category = BuildingCategory.APARTMENT_BLOCK

building = Buildings.build_buildings(building_category, database_manager)
tek_list = building.tek_list
tek_params = building.tek_params

print(tek_list)
for tek in tek_params:
    print(tek)