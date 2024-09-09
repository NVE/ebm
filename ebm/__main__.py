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

from ebm.__version__ import __version__
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.buildings import Buildings
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
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


def main() -> int:
    """
    Main function to execute the script.

    This function serves as the entry point for the script. It handles argument parsing,
    initializes necessary components, and orchestrates the main workflow of the script.

    Returns
    -------
    exit code : int
        zero when the program exits gracefully
    """
    load_dotenv()
    if '--debug' not in sys.argv and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    default_path = pathlib.Path('output/ebm_area_forecast.xlsx')

    logger.debug(f'Starting {sys.executable} {__file__}')

    program_name = 'calc-area-forecast'
    arguments = make_arguments(program_name, default_path)

    # Make local variable from arguments for clarity
    start_year, end_year = arguments.start_year, arguments.end_year
    output_filename = pathlib.Path(arguments.output_file)
    building_categories = [BuildingCategory.from_string(b_c) for b_c in arguments.categories]
    building_conditions = [BuildingCondition(condition) for condition in arguments.conditions]
    tek_filter = arguments.tek
    force_overwrite = arguments.force
    open_after_writing = arguments.open
    horizontal_years = arguments.horizontal
    input_directory = arguments.input
    create_input = arguments.create_input
    # `;` Will normally be interpreted as line end when typed in a shell. If the
    # delimiter is empty make the assumption that the user used ;. An empty delimiter is not valid anyway.
    csv_delimiter = arguments.csv_delimiter if arguments.csv_delimiter else ';'

    # Make sure everything is working as expected
    validate_years(end_year, start_year)

    database_manager = DatabaseManager(file_handler=FileHandler(directory=input_directory))

    # Create input directory if requested
    if create_input:
        database_manager.file_handler.create_missing_input_files()
        logger.info(f'Finished creating input files in {database_manager.file_handler.input_directory}')
        # Exit with 0 for success. The assumption is that the user would like to review the input before proceeding.
        return 0

    # Make sure all required files exists
    missing_files = database_manager.file_handler.check_for_missing_files()
    if missing_files:
        print(f"""
    Use {program_name} --create-input to create an input directory with default files in the current directory
    """.strip(),
              file=sys.stderr)
        return 2

    make_output_directory(output_filename.parent)
    if output_filename.is_file() and output_filename != default_path and not force_overwrite:
        # If the file already exists and is not the default, display error and exit unless --force was used.
        logger.error(f'{output_filename} already exists.')
        print(f"""
You can overwrite the {output_filename} by using --force: {program_name} {' '.join(sys.argv[1:])} --force
""".strip(),
              file=sys.stderr)
        return 1

    logger.info('Loading area forecast')

    output = None

    for building_category in building_categories:
        result = calculate_building_category_area_forecast(building_category=building_category,
                                                           database_manager=database_manager,
                                                           start_year=start_year,
                                                           end_year=end_year)
        if horizontal_years:
            df = area_forecast_result_to_horisontal_dataframe(building_category, result, start_year, end_year)
            if building_conditions:
                df = df.loc[:, :, [str(s) for s in building_conditions]]
            if tek_filter:
                tek_in_index = [t for t in tek_filter if any(df.index.isin([t], level=1))]
                df = df.loc[:, tek_in_index, :]
        else:
            df = area_forecast_result_to_dataframe(building_category, result, start_year, end_year)
            if building_conditions:
                df = df[[str(s) for s in building_conditions]]
            if tek_filter:
                tek_in_index = [t for t in tek_filter if any(df.index.isin([t], level=1))]
                df = df.loc[:, tek_in_index, :]
        if output is None:
            output = df
        else:
            output = pd.concat([output, df])

    logger.debug(f'Writing to {output_filename}')
    if str(output_filename) == '-':
        try:
            print(output.to_markdown())

        except ImportError:
            print(output.to_string())
    elif output_filename.suffix == '.csv':
        output.to_csv(output_filename, sep=csv_delimiter)
        logger.info(f'Wrote {output_filename}')
    else:
        excel_writer = pd.ExcelWriter(output_filename, engine='openpyxl')
        output.to_excel(excel_writer, sheet_name='area forecast', merge_cells=False, freeze_panes=(1, 3))
        excel_writer.close()
        logger.info(f'Wrote {output_filename}')

    if open_after_writing:
        os.startfile(output_filename, 'open')
    sys.exit(0)


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
                                         description=f'Calculate EBM area forecast v{__version__}',
                                         formatter_class=argparse.RawTextHelpFormatter
                                         )
    arg_parser.add_argument('--version', '-v', action='version', version=f'calculate-area-forcast {__version__}')
    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
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
                            help=textwrap.dedent(f"""
                                   One or more of the following building conditions: 
                                       {", ".join(default_building_conditions)}"""
                                                 ))
    arg_parser.add_argument('--tek', '-t',
                            nargs='*', type=str, default=default_tek,
                            help=textwrap.dedent(f"""
                                       One or more of the following TEK: 
                                           {", ".join(default_tek)}"""
                                                 ))
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
                            #help='Forecast start year. default: 2010, all other values are invalid')
    arg_parser.add_argument('--end_year', nargs='?', type=int, default=2050, help=argparse.SUPPRESS)
                            #help='Forecast end year (including). default: 2050, any other values are invalid')
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


def make_output_directory(output_directory: pathlib.Path) -> None:
    """
        Creates the output directory if it does not exist.

        Parameters
        ----------
        output_directory : pathlib.Path
            The path to the output directory.
        Raises
        -------
        IOError
            The output_directory exists, but it is a file.
        Returns
        -------
        None
    """
    if output_directory.is_file():
        raise IOError(f'{output_directory} is a file')
    if not output_directory.is_dir():
        logger.debug(f'Creating output directory {output_directory}')
        output_directory.mkdir()


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
    demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=years.range())
    constructed_floor_area = ConstructionCalculator.calculate_construction_as_list(
        building_category, demolition_floor_area, database_manager, period=years)

    forecast: Dict = area_forecast.calc_area(constructed_floor_area)
    return forecast


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
