import argparse
import os
import sys
import typing

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rich.pretty import pprint

from ebm.model import BuildingCategory
from ebm.model.bema import load_construction_building_category
from ebm.model.new_buildings import NewBuildings
from model import DatabaseManager, Buildings
from model.area_forecast import AreaForecast
from model.building_condition import BuildingCondition

ROUND_PRECISION = 10

logger.info = pprint


def main():
    """ Program used to test nybygging calculation main function """
    load_dotenv()

    default_building_categories: typing.List[str] = [str(b) for b in iter(BuildingCategory)]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')

    arg_parser.add_argument('building_categories', type=str, nargs='*', default=default_building_categories)
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    error_count = 0
    categories_with_errors = []
    for b_category in arguments.building_categories:
        building_category: BuildingCategory = BuildingCategory.from_string(b_category)
        logger.info(f'Checking {building_category=}')

        category_error_count = validate_accumulated_constructed_floor_area(building_category)
        if category_error_count > 0:
            logger.error(f'Got {category_error_count} errors for category {building_category}')
            categories_with_errors.append((building_category, category_error_count))
        error_count = category_error_count + error_count
    if error_count > 0:
        logger.error(f'Got {error_count} errors in total')
        logger.error(f'{categories_with_errors=}')

    sys.exit(error_count)


def load_accumulated_constructed_floor_area(building_category: BuildingCategory) -> pd.Series:
    spreadsheet_name = os.environ.get('BEMA_SPREADSHEET')

    wb: Workbook = load_workbook(spreadsheet_name)
    sheet_name: Worksheet = wb[wb.sheetnames[0]]

    df = load_construction_building_category(worksheet=sheet_name, building_category=building_category)

    return df.accumulated_constructed_floor_area


def validate_accumulated_constructed_floor_area(building_category) -> int:
    if building_category == 'house':
        logger.warning('Skipping House')
        return 0
    if building_category == 'apartment_block':
        logger.warning('Skipping House')
        return 0

    expected_values: pd.Series = load_accumulated_constructed_floor_area(building_category)

    # Prerequisites for calculate_construction
    demolition_floor_area = NewBuildings.calculate_floor_area_demolished(building_category)
    construction_floor_area = building_category.yearly_construction_floor_area()

    db = DatabaseManager()

    area_forecast = build_area_forecast(building_category, db)

    demolition_floor_area = pd.Series(area_forecast.calc_total_demolition_area_per_year(),
                                      index=[y for y in range(2010, 2050 + 1)])

    yearly_constructed = NewBuildings.calculate_commercial_construction(
        building_category=building_category,
        total_floor_area=building_category.total_floor_area_2010(),
        yearly_construction_floor_area=construction_floor_area,
        demolition_floor_area=demolition_floor_area)

    construction_floor_area = yearly_constructed.accumulated_constructed_floor_area
    years = construction_floor_area.index

    error_count = 0
    for year, current_value, expected_value in zip(years, construction_floor_area, expected_values):
        if round(current_value, ROUND_PRECISION) != round(expected_value, ROUND_PRECISION):
            error_count = error_count + 1
            logger.error(f'Expected {expected_value} got {current_value} {building_category.name} {year=} ')
            logger.debug(f'The difference is {expected_value - current_value}. {ROUND_PRECISION=}')
            logger.debug(f'{yearly_constructed.loc[year]}')
        else:
            logger.debug(f'Found expected value {expected_value} {year=} {current_value=}')
    return error_count


def build_area_forecast(building_category: BuildingCategory, db: DatabaseManager) -> AreaForecast:
    """
    This function makes and AreaForecast object for a building category using configuration and input
    from DatabaseManager

    Args:
        building_category: building category used for AreaForecast and Building i.e `kindergarten`
        db: common DatabaseManager

    Returns: AreaForcast

    """
    tek_list = db.get_tek_list()
    tek_params = db.get_tek_params(tek_list)
    scurve_params = db.get_scurve_params()
    area_params = db.get_area_parameters()
    scurve_condition_list = BuildingCondition.get_scruve_condition_list()
    building = Buildings(building_category, tek_list, tek_params, scurve_condition_list, scurve_params, area_params)
    tek_list = building.tek_list  # get filtered tek list for given building category
    shares_per_condition = building.get_shares()
    tek_params = db.get_tek_params(tek_list)
    full_condition_list = BuildingCondition.get_full_condition_list()

    area_forecast = AreaForecast(model_start_year=2010, end_year=2050, building_category=building_category,
                                 area_params=area_params, tek_list=tek_list, tek_params=tek_params,
                                 condition_list=full_condition_list, shares_per_condtion=shares_per_condition)
    return area_forecast


if __name__ == '__main__':
    main()
