import os
import pathlib
import sys
import typing

import dotenv
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.cmd.result_handler import transform_heating_systems_to_horizontal, write_horizontal_excel, \
    transform_model_to_horizontal, EbmDefaultHandler, transform_holiday_homes_to_horizontal, \
    transform_to_sorted_heating_systems
from ebm.cmd.run_calculation import validate_years, calculate_energy_use, configure_loglevel
from ebm.cmd import prepare_main
from ebm.cmd.initialize import init, create_output_directory

from ebm.model.building_category import BuildingCategory
from ebm.model.database_manager import DatabaseManager
from ebm.model.enums import ReturnCode
from ebm.model.file_handler import FileHandler

df = None


def main() -> typing.Tuple[ReturnCode, typing.Union[pd.DataFrame, None]]:
    """
    Main function to execute the script.

    This function serves as the entry point for the script. It handles argument parsing,
    initializes necessary components, and orchestrates the main workflow of the script.

    Returns
    -------
    exit code : int
        zero when the program exits gracefully
    """
    env_file = pathlib.Path(dotenv.find_dotenv(usecwd=True))
    if env_file.is_file():
        logger.debug(f'Using {env_file}')
        load_dotenv(pathlib.Path('.env').absolute())
    else:
        logger.debug(f'{env_file.absolute()} not found')

    configure_loglevel(os.environ.get('LOG_FORMAT', None))

    logger.debug(f'Starting {sys.executable} {__file__}')

    program_name = 'ebm'
    default_path = pathlib.Path('output/ebm_output.xlsx')

    arguments = prepare_main.make_arguments(program_name, default_path)

    # Make local variable from arguments for clarity
    building_categories = [BuildingCategory.from_string(b_c) for b_c in arguments.categories]
    if not building_categories:
        building_categories = list(BuildingCategory)

    # `;` Will normally be interpreted as line end when typed in a shell. If the
    # delimiter is empty make the assumption that the user used ;. An empty delimiter is not valid anyway.
    csv_delimiter = arguments.csv_delimiter if arguments.csv_delimiter else ';'

    # Make sure everything is working as expected
    validate_years(end_year=arguments.end_year, start_year=arguments.start_year)

    database_manager = DatabaseManager(file_handler=FileHandler(directory=arguments.input))

    # Create input directory if requested
    if arguments.create_input:
        if init(database_manager.file_handler):
            logger.info(f'Finished creating input files in {database_manager.file_handler.input_directory}')
            return ReturnCode.OK, None
        # Exit with 0 for success. The assumption is that the user would like to review the input before proceeding.
        return ReturnCode.MISSING_INPUT_FILES, None

    # Make sure all required files exists
    missing_files = database_manager.file_handler.check_for_missing_files()
    if missing_files:
        print(f"""
    Use {program_name} --create-input to create an input directory with default files in the current directory
    """.strip(),
              file=sys.stderr)
        return ReturnCode.MISSING_INPUT_FILES, None

    database_manager.file_handler.validate_input_files()
    
    output_file = arguments.output_file
    create_output_directory(filename=output_file)

    output_file_status: ReturnCode = prepare_main.check_output_file_status(output_file,
                                                                           arguments.force,
                                                                           default_path,
                                                                           program_name)
    if output_file_status!= ReturnCode.OK:
        return output_file_status, None

    step_choice = arguments.step

    transform_to_horizontal_years = arguments.horizontal_years

    default_handler = EbmDefaultHandler()

    model = default_handler.extract_model(arguments, building_categories, database_manager, step_choice)
    if step_choice == 'energy-use':
        logger.debug('Transform heating systems')
        holiday_homes = transform_holiday_homes_to_horizontal(calculate_energy_use())
        hz = transform_heating_systems_to_horizontal(model)
        heating_systems_hz = transform_to_sorted_heating_systems(hz, holiday_homes)
        if output_file.name == '-':
            print(heating_systems_hz.to_markdown(index=False))
        write_horizontal_excel(output_file, heating_systems_hz, 'energy-use')
    elif transform_to_horizontal_years and (step_choice in ['area-forecast', 'energy-requirements']) and output_file.suffix=='.xlsx':
        sheet_name_prefix = 'area' if step_choice == 'area-forecast' else 'energy'
        logger.debug(f'Transform heating {step_choice}')

        df = transform_model_to_horizontal(model.reset_index())
        write_horizontal_excel(output_file, df, f'{sheet_name_prefix} condition')

        model = model.reset_index()
        # Demolition should not be summed any further
        model = model[model.building_condition!='demolition']
        model['building_condition'] = 'all'
        df = transform_model_to_horizontal(model)
        write_horizontal_excel(output_file, df, f'{sheet_name_prefix} TEK')

        model['TEK'] = 'all'
        df = transform_model_to_horizontal(model)
        write_horizontal_excel(output_file, df, f'{sheet_name_prefix} category')
    else:
        default_handler.write_result2(output_file, csv_delimiter, model)


    if arguments.open or os.environ.get('EBM_ALWAYS_OPEN', 'FALSE').upper() == 'TRUE':
        os.startfile(output_file, 'open')

    return ReturnCode.OK, model


if __name__ == '__main__':
    exit_code, result = main()
    df = result
