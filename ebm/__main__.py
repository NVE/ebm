"""EBM start from where when running as a script or module"""
import os
import pathlib
import sys
import typing

import pandas as pd
from loguru import logger

from ebm.cmd.helpers import load_environment_from_dotenv
from ebm.cmd.result_handler import  append_result, \
    transform_model_to_horizontal, EbmDefaultHandler
from ebm.cmd.pipeline import export_energy_model_reports
from ebm.cmd.run_calculation import validate_years, configure_loglevel, configure_json_log_from_env
from ebm.cmd import prepare_main
from ebm.cmd.initialize import init, create_output_directory

from ebm.model.building_category import BuildingCategory
from ebm.model.database_manager import DatabaseManager
from ebm.model.enums import ReturnCode
from ebm.model.file_handler import FileHandler

df = None


def main() -> typing.Tuple[ReturnCode, typing.Union[pd.DataFrame, None]]:
    """
    Main function to execute the EBM module as a script.

    This function serves as the entry point for the script. It handles argument parsing,
    initializes necessary components, and orchestrates the main workflow of the script.

    Returns
    -------
    exit code : tuple[ReturnCode, pd.DataFrame]
        zero when the program exits gracefully
    """
    load_environment_from_dotenv()
    configure_loglevel(log_format=os.environ.get('LOG_FORMAT', None))
    configure_json_log_from_env()

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
    model_years = validate_years(start_year=arguments.start_year, end_year=arguments.end_year)

    input_directory = arguments.input
    logger.info(f'Using data from "{input_directory}"')
    database_manager = DatabaseManager(file_handler=FileHandler(directory=input_directory))

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

    output_file_return_code = prepare_main.check_output_file_status(output_file, arguments.force, default_path,
                                                                    program_name)
    if output_file_return_code!= ReturnCode.OK:
        return output_file_return_code, None

    step_choice = arguments.step

    convert_result_to_horizontal: bool = arguments.horizontal_years

    default_handler = EbmDefaultHandler()

    model = None

    files_to_open = [output_file]

    if step_choice == 'energy-use':
        output_directory = output_file if output_file.is_dir() else output_file.parent
        files_to_open = export_energy_model_reports(model_years, database_manager, output_directory)
    else:
        model = default_handler.extract_model(model_years, building_categories, database_manager, step_choice)

        if convert_result_to_horizontal and (step_choice in ['area-forecast', 'energy-requirements']) and output_file.suffix=='.xlsx':
            sheet_name_prefix = 'area' if step_choice == 'area-forecast' else 'energy'
            logger.debug(f'Transform heating {step_choice}')

            df = transform_model_to_horizontal(model.reset_index())
            append_result(output_file, df, f'{sheet_name_prefix} condition')

            model = model.reset_index()
            # Demolition should not be summed any further
            model = model[model.building_condition!='demolition']
            model['building_condition'] = 'all'
            df = transform_model_to_horizontal(model)
            append_result(output_file, df, f'{sheet_name_prefix} TEK')

            model['TEK'] = 'all'
            df = transform_model_to_horizontal(model)
            append_result(output_file, df, f'{sheet_name_prefix} category')
        else:
            default_handler.write_tqdm_result(output_file, model, csv_delimiter)

    for file_to_open in files_to_open:
        if arguments.open or os.environ.get('EBM_ALWAYS_OPEN', 'FALSE').upper() == 'TRUE':
            logger.info(f'Open {file_to_open}')
            os.startfile(file_to_open, 'open')
        else:
            logger.debug(f'Finished {file_to_open}')

    return ReturnCode.OK, model


if __name__ == '__main__':
    exit_code, result = main()
    df = result
