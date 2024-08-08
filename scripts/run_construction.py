import argparse
import collections.abc
import os
import sys

import pandas as pd
from dotenv import load_dotenv
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rich.pretty import pprint
from loguru import logger

from ebm.model import BuildingCategory
from ebm.model.new_buildings import NewBuildings
from ebm.model.bema import load_construction_building_category

ROUND_PRECISION = 3

logger.info = pprint


def main():
    """ Program used to test nybygging calculation main function """
    load_dotenv()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('building_categories', type=str, nargs='*', default=[str(b) for b in iter(BuildingCategory)])
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    error_count = 0
    for b_category in arguments.building_categories:
        building_category: BuildingCategory = BuildingCategory.from_string(b_category)
        logger.info(f'Checking {building_category=}')

        error_count = validate_accumulated_constructed_floor_area(building_category) + error_count
    if error_count > 0:
        logger.error(f'Got {error_count} errors in total')

    sys.exit(error_count)


def load_accumulated_constructed_floor_area(building_category: BuildingCategory) -> pd.Series:
    spreadsheet_name = os.environ.get('BEMA_SPREADSHEET')

    wb: Workbook = load_workbook(spreadsheet_name)
    sheet_name: Worksheet = wb[wb.sheetnames[0]]

    df = load_construction_building_category(sheet=sheet_name, building_category=building_category)

    return df.accumulated_constructed_floor_area


def validate_accumulated_constructed_floor_area(building_category) -> int:
    if building_category == 'house':
        logger.warning('Skipping House')
        return 0
    if building_category == 'apartment_block':
        logger.warning('Skipping House')
        return 0

    expected_values: pd.Series = load_accumulated_constructed_floor_area(building_category)

    yearly_constructed = NewBuildings.calculate_construction(building_category=building_category,
                                                             total_floor_area=0,
                                                             yearly_demolition_floor_area=None)

    construction_floor_area = yearly_constructed.accumulated_constructed_floor_area
    years = construction_floor_area.index

    error_count = 0
    for year, current_value, expected_value in zip(years, construction_floor_area, expected_values):
        if round(current_value, ROUND_PRECISION) != round(expected_value, ROUND_PRECISION):
            error_count = error_count + 1
            logger.error(f'Expected {expected_value} got {current_value} {building_category.name} {year=} ')
            logger.debug(f'The difference is {expected_value - current_value}')
            logger.debug(f'{yearly_constructed.loc[year]}')
        else:
            logger.debug(f'Found expected value {expected_value} {year=} {current_value=}')
    return error_count


if __name__ == '__main__':
    main()
