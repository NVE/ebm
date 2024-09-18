import argparse
import os
import sys
import typing

from dotenv import load_dotenv
from loguru import logger

from ebm.model.bema_validation import validate_rush_rates, validate_scurves, validate_shares, validate_construction, \
    validate_area
from ebm.model.building_category import BuildingCategory
from ebm.model.database_manager import DatabaseManager


def main():
    load_dotenv()
    
    default_building_categories: typing.List[str] = [str(b) for b in iter(BuildingCategory)]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('building_categories', type=str, nargs='*', default=default_building_categories)
    arg_parser.add_argument('--validate', type=str, choices=['rush_rates', 'scurves', 'shares', 'construction', 'area', '*'], nargs='?', default='*')
    arg_parser.add_argument('--precision', '-p', type=int, default=5,
                            help='Number of decimals to consider in comparison')
    arguments: argparse.Namespace = arg_parser.parse_args()
    
    #TODO: fix if statement
    if not arguments.debug or os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    precision: int = arguments.precision
    if precision < 0:
        print('Precision cannot be lower than 0', sys.stderr)
        return -1

    database_manager = DatabaseManager()

    logger.info(f'Using {os.environ.get("BEMA_SPREADSHEET")}')
    logger.debug(f'{precision=}')
    for b_category in arguments.building_categories:
        building_category: BuildingCategory = BuildingCategory.from_string(b_category)
        
        logger.info(building_category)

        if arguments.validate in ['rush_rates', '*']:
            validate_rush_rates(building_category, database_manager, precision=precision)
        
        if arguments.validate in ['scurves', '*']:
            validate_scurves(building_category, database_manager, precision=precision)

        if arguments.validate in ['shares', '*']:
            validate_shares(building_category, database_manager, precision=precision)

        if arguments.validate in ['construction', '*']:    
            validate_construction(building_category, database_manager, precision=precision)

        if arguments.validate in ['area', '*']:    
            validate_area(building_category, database_manager, precision=precision)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
