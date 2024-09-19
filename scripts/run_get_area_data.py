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
from ebm.model.shares_per_condition import SharesPerCondition

from ebm.model.bema_validation import *


database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

area_start_year = database_manager.get_area_start_year()[building_category]
print(area_start_year)