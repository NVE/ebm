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

ebm_rates = get_ebm_rush_rates(building_category, database_manager)
bema_rates = load_bema_rush_rates(building_category, database_manager)

ebm_scurves = get_ebm_scurves(building_category, database_manager) 
bema_scurves = load_bema_scurves(building_category)

logger.info(f'BEMA')
print(bema_rates)
logger.info(f'EBM')
print(ebm_rates)