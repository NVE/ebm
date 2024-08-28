import argparse
import os
import pathlib
import sys
import typing

import pandas as pd
import rich.pretty
from dotenv import load_dotenv
from loguru import logger

from ebm.__version__ import __version__
from ebm.model.building_category import BuildingCategory
from ebm.model.buildings import Buildings
from ebm.model.construction import ConstructionCalculator
from ebm.model.database_manager import DatabaseManager


def main():
    logger.debug(f'Starting {sys.executable} {__file__}')
    arg_parser = argparse.ArgumentParser(description=f'Calculate EBM area forecast v{__version__}')
    arg_parser.add_argument('--version', action='store_true')
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('--start_year', nargs='?', type=int, default=2010)
    arg_parser.add_argument('--end_year', nargs='?', type=int, default=2050)

    arguments = arg_parser.parse_args()
    load_dotenv()
    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    if arguments.version:
        logger.info(f'ebm/energibruksmodell {__version__}')
        sys.exit(0)
    start_year, end_year = arguments.start_year, arguments.end_year

    validate_arguments(end_year, start_year)

    database_manager = DatabaseManager()
    building_category = BuildingCategory.HOUSE
    output_directory = pathlib.Path('output')
    output_file = output_directory / 'ebm_area_forecast.xlsx'

    validate_output_directory(output_directory)

    result = calculate_building_category_area_forecast(
        building_category=building_category,
        database_manager=database_manager,
        start_year=arguments.start_year,
        end_year=arguments.end_year)
    output = None
    for tek, conditions in result.items():
        df = pd.DataFrame(data=conditions, index=pd.MultiIndex.from_tuples([(str(building_category), tek, y, ) for y in range(start_year, end_year +1)], names=['building_category', 'tek', 'year']))
        if output is not None:
            output = pd.concat([output, df])
        else:
            output = df
        rich.pretty.pprint(tek)
        rich.pretty.pprint(df)

    rich.pretty.pprint(output)
    output.to_excel(output_file)
    sys.exit(0)


def validate_output_directory(output_directory):
    if not output_directory.is_dir():
        logger.debug(f'Creating output directory {output_directory}')
        output_directory.mkdir()


def validate_arguments(end_year, start_year):
    if start_year >= end_year:
        msg = f'Unexpected input start year ({start_year} is greater than end year ({end_year})'
        raise ValueError(msg)
    if start_year + 40 != end_year:
        msg = f'Unexpected input end_year ({end_year}) is not 40 years after start_year ({start_year + 40})'
        raise ValueError(msg)
    if start_year != 2010 or end_year != 2050:
        msg = 'Unexpected input '
        if start_year != 2010:
            msg = f'{msg} start_year={start_year} currently only 2010 is supported '
        if end_year != 2050:
            msg = f'{msg} end_year={end_year}, currently only 2050 is supported '
        raise ValueError(msg)


def calculate_building_category_area_forecast(building_category, database_manager, start_year, end_year):
    buildings = Buildings.build_buildings(building_category=building_category,
                                          database_manager=database_manager)
    years = [y for y in range(start_year, end_year + 1)]

    area_forecast = buildings.build_area_forecast(database_manager, start_year, end_year)
    demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=years)
    yearly_constructed = ConstructionCalculator.calculate_construction(building_category,
                                                                       demolition_floor_area,
                                                                       database_manager)

    constructed_floor_area = yearly_constructed.accumulated_constructed_floor_area
    forecast: typing.Dict = area_forecast.calc_area([v for v in constructed_floor_area])

    return forecast


if __name__ == '__main__':
    main()