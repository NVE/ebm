import argparse
import os
import pathlib
import sys
import textwrap
from typing import List, Dict

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.__version__ import version
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.buildings import Buildings
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement
from ebm.model.file_handler import FileHandler

TEK = """PRE_TEK49_RES_1950
PRE_TEK49_RES_1940
PRE_TEK49_COM
TEK49_RES
TEK49_COM
TEK69_RES_1976
TEK69_RES_1986
TEK69_COM
TEK87_RES
TEK87_COM
TEK97_RES
TEK97_COM
TEK07
TEK10
TEK17
TEK21""".strip().split('\n')


def make_arguments(program_name, default_path: pathlib.Path) -> argparse.Namespace:
    """
    Create and parse command-line arguments for the area forecast calculation.

    Parameters
    ----------
    program_name : str
        Name of this program
    default_path : pathlib.Path
        Default path for the output file.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.

    Notes
    -----
    The function sets up an argument parser with various options including version, debug mode,
    filename, force write, open file after writing, CSV delimiter, building categories,
    creating default input, start year, and end year.
    """

    default_building_categories: List[str] = [str(b) for b in iter(BuildingCategory)]
    default_building_conditions = [str(condition) for condition in iter(BuildingCondition)]
    default_tek = TEK

    arg_parser = argparse.ArgumentParser(prog=program_name,
                                         description=f'Calculate EBM area forecast v{version}',
                                         formatter_class=argparse.RawTextHelpFormatter
                                         )
    arg_parser.add_argument('--version', '-v', action='version', version=f'calculate-area-forcast {version}')
    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
    arg_parser.add_argument('step', type=str, nargs='?',
                            choices=['area-forecast', 'energy-requirements'],
                            default='energy-requirements')
    arg_parser.add_argument('output_file', nargs='?', type=str, default=default_path,
                            help=textwrap.dedent(
                                f'''The location of the file you want to be written. default: {default_path}
    If the file already exists the program will terminate without overwriting. 
    Use "-" to output to the console instead'''))
    arg_parser.add_argument('--categories', '--building-categories', '-c',
                            nargs='*', type=str, default=default_building_categories,
                            help=textwrap.dedent(f"""
                                   One or more of the following building categories: 
                                       {", ".join(default_building_categories)}"""
                                                 ))
    arg_parser.add_argument('--input', '--input-directory', '-i',
                            nargs='?', type=str, default=os.environ.get('EBM_INPUT_DIRECTORY', 'input'),
                            help='path to the directory with input files')
    arg_parser.add_argument('--conditions', '--building-conditions', '-n',
                            nargs='*', type=str, default=default_building_conditions,
                            help=argparse.SUPPRESS)
                            #help=textwrap.dedent(f"""
                            #       One or more of the following building conditions:
                            #           {", ".join(default_building_conditions)}"""
                            #                     ))
    arg_parser.add_argument('--tek', '-t',
                            nargs='*', type=str, default=default_tek,
                            help=argparse.SUPPRESS)
                            #help=textwrap.dedent(f"""
                            #           One or more of the following TEK:
                            #               {", ".join(default_tek)}"""
                            #                     ))
    arg_parser.add_argument('--force', '-f', action='store_true',
                            help='Write to <filename> even if it already exists')
    arg_parser.add_argument('--open', '-o', action='store_true',
                            help='Open <filename> with default application after writing. (Usually Excel)')
    arg_parser.add_argument('--csv-delimiter', '--delimiter', '-e', type=str, default=',',
                            help='A single character to be used for separating columns when writing csv. ' +
                                 'Default: "," Special characters like ; should be quoted ";"')
    arg_parser.add_argument('--create-input', action='store_true',
                            help='Create input directory with all required files in the current working directory')
    arg_parser.add_argument('--start_year', nargs='?', type=int, default=2010, help=argparse.SUPPRESS)
    arg_parser.add_argument('--end_year', nargs='?', type=int, default=2050, help=argparse.SUPPRESS)

    arg_parser.add_argument('--horizontal', '--horisontal', action='store_true',
                            help='Show years horizontal (left to right)')
    arguments = arg_parser.parse_args()
    return arguments


def area_forecast_result_to_dataframe(building_category: BuildingCategory,
                                      forecast: Dict[str, list],
                                      start_year: int,
                                      end_year: int) -> pd.DataFrame:
    """
    Create a dataframe from a forecast

    Parameters
    ----------
    building_category : BuildingCategory
    forecast : Dict[str, list[float]]
    start_year : int (2010)
    end_year : int (2050)

    Returns dataframe : pd.Dataframe
        A dataframe of all area values in forecast indexed by building_category, tek and year
    -------

    """
    dataframe = None
    for tek, conditions in forecast.items():
        index_rows = [(str(building_category), tek, y,) for y in range(start_year, end_year + 1)]
        index_names = ['building_category', 'tek', 'year']
        df = pd.DataFrame(data=conditions,
                          index=pd.MultiIndex.from_tuples(index_rows, names=index_names))
        if dataframe is not None:
            dataframe = pd.concat([dataframe, df])
        else:
            dataframe = df
    return dataframe


# noinspection PyTypeChecker
def area_forecast_result_to_horisontal_dataframe(building_category: BuildingCategory,
                                                 forecast: Dict[str, Dict[str, List[np.float64]]],
                                                 start_year: int,
                                                 end_year: int) -> pd.DataFrame:
    """
    Create a dataframe from a forecast with years listed horizontally from 2010-2050

    Parameters
    ----------
    building_category : BuildingCategory
    forecast : Dict[str, list[float]]
    start_year : int (2010)
    end_year : int (2050)

    Returns dataframe : pd.Dataframe
        A dataframe of all area values in forecast indexed by building_category, tek and year
    -------

    """
    rows = []
    for tek in forecast.keys():
        condition: str
        for condition, numbers in forecast.get(tek).items():
            row = [str(building_category), tek, condition]
            for number, year in zip(numbers, range(start_year, end_year + 1)):
                row.append(number)
            rows.append(row)

    df = pd.DataFrame(data=rows)
    df.columns = ['building_category', 'TEK', 'building_condition'] + [y for y in range(start_year, end_year + 1)]

    return df.set_index(['building_category', 'TEK', 'building_condition'])


def validate_years(end_year, start_year):
    """
    Validates the start and end year arguments.

    Parameters
    ----------
    end_year : int
        The end year to validate.
    start_year : int
        The start year to validate.

    Raises
    ------
    ValueError
        If `start_year` is greater than or equal to `end_year`.
        If `end_year` is not exactly 40 years after `start_year`.
        If `start_year` is not 2010 or `end_year` is not 2050.
    """
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


def calculate_building_category_energy_requirements(building_category: BuildingCategory,
                                                    area_forecast,
                                              database_manager: DatabaseManager,
                                              start_year: int,
                                              end_year: int):
    energy_requirement = EnergyRequirement.new_instance()

    series = []
    for s in energy_requirement.calculate_for_building_category(building_category=building_category,
                                                                database_manager=database_manager):
        series.append(s)
    df = pd.concat(series)
    df = df.rename({'TEK': 'tek'}, axis='index')
    df.index.names = ['building_category', 'tek', 'purpose', 'building_condition', 'year']
    q = area_forecast.reset_index().melt(id_vars=['building_category', 'tek', 'year'],
                                         value_vars=['demolition', 'original_condition', 'renovation', 'small_measure',
                                                     'renovation_and_small_measure', 'renovation'],
                                         var_name='building_condition',
                                         value_name='m2')

    q = q.set_index(['building_category', 'tek', 'building_condition', 'year'])

    merged = q.merge(df, left_index=True, right_index=True)
    merged['energy_requirement'] = merged.kwh_m2 * merged.m2

    return merged


def calculate_building_category_area_forecast(building_category: BuildingCategory,
                                              database_manager: DatabaseManager,
                                              start_year: int,
                                              end_year: int) -> Dict[str, list[float]]:
    """
    Calculates the area forecast for a given building category from start to end year (including).

    Parameters
    ----------
    building_category : BuildingCategory
        The category of buildings for which the area forecast is to be calculated.
    database_manager : DatabaseManager
        The database manager used to interact with the database.
    start_year : int
        The starting year of the forecast period.
    end_year : int
        The ending year of the forecast period.

    Returns
    -------
    dict
        A dictionary where keys are strings representing different area categories and values are lists of floats
            representing the forecasted areas for each year in the specified period.

    Notes
    -----
    This function builds the buildings for the specified category, calculates the area forecast, and accounts for
        demolition and construction over the specified period.
    """
    buildings = Buildings.build_buildings(building_category=building_category,
                                          database_manager=database_manager)
    years = YearRange(start_year, end_year)

    area_forecast = buildings.build_area_forecast(database_manager, years.start, years.end)
    demolition_floor_area = area_forecast.calc_total_demolition_area_per_year()
    constructed_floor_area = ConstructionCalculator.calculate_construction(building_category,
                                                                           demolition_floor_area,
                                                                           database_manager,
                                                                           period=years).accumulated_constructed_floor_area
    forecast: Dict = area_forecast.calc_area(constructed_floor_area)

    # Temporary method to convert series to list
    def nested_dict_series_to_list(nested_dict):
        return {
            key: {inner_key: value.tolist() for inner_key, value in inner_dict.items()}
            for key, inner_dict in nested_dict.items()
        }
    forecast = nested_dict_series_to_list(forecast)

    return forecast