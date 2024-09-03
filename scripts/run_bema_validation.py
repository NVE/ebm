import argparse
import sys
import typing
import os

from loguru import logger
from dotenv import load_dotenv
import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.bema_validation import validate_rush_rates, validate_scurves, validate_shares, validate_construction, validate_area

def main():
    load_dotenv()
    
    default_building_categories: typing.List[str] = [str(b) for b in iter(BuildingCategory)]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('building_categories', type=str, nargs='*', default=default_building_categories)
    arg_parser.add_argument('--validate', type=str, choices=['rush_rates', 'scurves', 'shares', 'construction', 'area', '*'], nargs='?', default='*')
    arguments: argparse.Namespace = arg_parser.parse_args()
    
    #TODO: fix if statement
    if not arguments.debug or os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    
    database_manager = DatabaseManager()
    
    for b_category in arguments.building_categories:
        building_category: BuildingCategory = BuildingCategory.from_string(b_category)
        
        logger.info(building_category)

        if arguments.validate in ['rush_rates', '*']:
            validate_rush_rates(building_category, database_manager)
        
        if arguments.validate in ['scurves', '*']:
            validate_scurves(building_category, database_manager)

        if arguments.validate in ['shares', '*']:
            validate_shares(building_category, database_manager)

        if arguments.validate in ['construction', '*']:    
            validate_construction(building_category, database_manager)

        if arguments.validate in ['area', '*']:    
            validate_area(building_category, database_manager)

if __name__ == '__main__':
    main()
