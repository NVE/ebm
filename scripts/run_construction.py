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

logger.info = pprint


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('building_category', type=str, nargs='?', default='university')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    building_category = BuildingCategory.from_string(arguments.building_category)
    expected_values = load_expected_yearly_constructed(building_category)

    construction_floor_area = NewBuildings.calculate_yearly_construction(
        building_category=building_category
    )

    error_count = 0
    for (year, cfa), expected_value in zip(construction_floor_area.items(), expected_values):
        if round(cfa, precision) != round(expected_value, precision):
            error_count = error_count + 1
            logger.error(f'Expected {expected_value} was {cfa} {building_category.name} {year=} {cfa=}')
            logger.debug(f'The difference is {expected_value - round(cfa)}')
            logger.debug(f'{yearly_constructed.loc[year]}')
        else:
            logger.debug(f'Found expected value {expected_value} {year=} {cfa=}')
    return error_count


if __name__ == '__main__':
    main()
