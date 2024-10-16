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
from ebm.cmd.run_calculation import calculate_building_category_area_forecast, \
    area_forecast_result_to_horisontal_dataframe, area_forecast_result_to_dataframe, make_arguments, validate_years, \
    calculate_building_category_energy_requirements
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.buildings import Buildings
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler




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

    database_manager.file_handler.validate_input_files()
    database_manager.file_handler.make_output_directory(output_filename.parent)

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
        area_forecast_result = calculate_building_category_area_forecast(building_category=building_category,
                                                           database_manager=database_manager,
                                                           start_year=start_year,
                                                           end_year=end_year)
        result = area_forecast_result
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

        if 'energy_requirements' in arguments.step:
            energy_requirements_result = calculate_building_category_energy_requirements(
                building_category=building_category,
                area_forecast=df,
                database_manager=database_manager,
                start_year=start_year,
                end_year=end_year)
            df = energy_requirements_result

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


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
