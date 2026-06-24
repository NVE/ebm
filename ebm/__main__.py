"""EBM start from where when running as a script or module"""
import os

os.environ['DISABLE_PANDERA_IMPORT_WARNING'] = 'True'
import pathlib
import platform
import sys

import pandas as pd
from loguru import logger

from ebm.cmd import prepare_main
from ebm.cmd.helpers import configure_json_log, configure_loglevel, load_environment_from_dotenv, open_file
from ebm.cmd.initialize import create_output_directory, init, list_available_datasets
from ebm.cmd.migrate import migrate_directories
from ebm.cmd.pipeline import export_energy_model_reports
from ebm.cmd.result_handler import EbmDefaultHandler, append_result, transform_model_to_horizontal
from ebm.cmd.run_calculation import validate_years
from ebm.model.building_category import BuildingCategory
from ebm.model.database_manager import DatabaseManager
from ebm.model.enums import ReturnCode
from ebm.model.file_handler import FileHandler

df = None


def main() -> tuple[ReturnCode, pd.DataFrame | None]:
    """
    Execute the EBM module as a script.

    This function serves as the entry point for the script. It handles argument parsing,
    initializes necessary components, and orchestrates the main workflow of the script.

    Returns
    -------
    exit code : tuple[ReturnCode, pd.DataFrame]
        zero when the program exits gracefully

    """
    load_environment_from_dotenv()

    configure_loglevel(log_format=os.environ.get('LOG_FORMAT', '{level.icon} <level>{message}</level>'))
    configure_json_log()

    logger.debug(f'Starting {sys.executable} {__file__}')

    program_name = 'ebm'
    default_path = pathlib.Path('output/ebm_output.xlsx')

    arguments = prepare_main.make_arguments(program_name, default_path)
    if arguments.step == 'list-input':
        list_available_datasets()
        return ReturnCode.OK, None
    
    # Make local variable from arguments for clarity
    building_categories = [BuildingCategory.from_string(b_c) for b_c in arguments.categories]
    if not building_categories:
        building_categories = list(BuildingCategory)

    # `;` Will normally be interpreted as line end when typed in a shell. If the
    # delimiter is empty make the assumption that the user used ;. An empty delimiter is not valid anyway.
    csv_delimiter = arguments.csv_delimiter if arguments.csv_delimiter else ';'


    input_directory = arguments.input
    logger.debug('Using platform {os}', os=platform.system())
    logger.info(f'Using data from "{input_directory}"')
    database_manager = DatabaseManager(file_handler=FileHandler(directory=input_directory))

    # Create input directory if requested (via command or legacy flag)
    if arguments.step == 'create-input' or arguments.create_input:
        if arguments.create_input:
            logger.warning('The --create-input flag is deprecated. Use "ebm create-input" command instead.')
        # When used as a command, dataset and input dir can be passed positionally:
        #   ebm create-input <dataset> <input_dir>
        # argparse captures them as output_file and create_input_dir respectively.
        dataset = arguments.dataset
        if dataset is None and arguments.step == 'create-input' and arguments.output_file != default_path:
            dataset = arguments.output_file.name
        if arguments.create_input_dir is not None:
            input_directory = arguments.create_input_dir
            database_manager = DatabaseManager(file_handler=FileHandler(directory=input_directory))
        source_directory = None
        if dataset:
            data_directory = pathlib.Path(__file__).parent / 'data'
            source_directory = data_directory / dataset
            if not source_directory.is_dir():
                available = sorted(p.name for p in data_directory.iterdir() if p.is_dir())
                logger.error(f'Dataset "{dataset}" not found. Available datasets: {", ".join(available)}')
                return ReturnCode.FILE_NOT_ACCESSIBLE, None
        if init(database_manager.file_handler, source_directory=source_directory):
            logger.success('Finished creating input files in {input_directory}',
                           input_directory=database_manager.file_handler.input_directory)
            return ReturnCode.OK, None
        # Exit with 0 for success. The assumption is that the user would like to review the input before proceeding.
        return ReturnCode.MISSING_INPUT_FILES, None
    if arguments.migrate:
        migrate_directories([database_manager.file_handler.input_directory])
        logger.success('Finished migration')
        return ReturnCode.OK, None

    missing_input_error = f"""
Use `<program name> create-input --input={input_directory}` to create an input directory with the default input files
""".strip().replace('\n',  ' ')


    # Make sure all required files exists
    try:
        missing_files = database_manager.file_handler.check_for_missing_files()
        if missing_files:
            print(missing_input_error, file=sys.stderr)
            return ReturnCode.MISSING_INPUT_FILES, None
    except FileNotFoundError as file_not_found:
        if str(file_not_found).startswith('Input Directory Not Found'):
            logger.error(f'Input Directory "{input_directory}" Not Found')
            print(missing_input_error, file=sys.stderr)
            return ReturnCode.FILE_NOT_ACCESSIBLE, None

    if database_manager.file_handler.is_calibrated():
        logger.info(f'Input directory "{input_directory}" contains calibration files', directory=database_manager.file_handler.input_directory.name)

    database_manager.file_handler.validate_input_files()

    end_year = arguments.end_year if arguments.end_year else database_manager.get_population_forecast_end_year()
    model_years = validate_years(start_year=arguments.start_year, end_year=end_year)

    step_choice = arguments.step
    output_file = arguments.output_file

    if step_choice == 'energy-use':
        try:
            # When the default file-based path is used, fall back to its parent directory
            if output_file == default_path:
                output_file = default_path.parent
            output_directory = prepare_main.resolve_output_directory_for_energy_use(output_file)
            create_output_directory(output_directory=output_directory)
        except (NotADirectoryError, ValueError, OSError) as ex:
            logger.error(str(ex))
            return ReturnCode.FILE_NOT_ACCESSIBLE, None
    else:
        create_output_directory(filename=output_file)

        output_file_return_code = prepare_main.check_output_file_status(output_file, arguments.force, default_path,
                                                                        program_name)
        if output_file_return_code!= ReturnCode.OK:
            return output_file_return_code, None

    convert_result_to_horizontal: bool = arguments.horizontal_years

    default_handler = EbmDefaultHandler()

    model = None

    files_to_open = [output_file]

    if step_choice == 'energy-use':
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

            model['building_code'] = 'all'
            df = transform_model_to_horizontal(model)
            append_result(output_file, df, f'{sheet_name_prefix} category')
            logger.success('Wrote {filename}', filename=output_file)
        else:
            default_handler.write_tqdm_result(output_file, model, csv_delimiter)

    for file_to_open in files_to_open:
        if arguments.open or os.environ.get('EBM_ALWAYS_OPEN', 'FALSE').upper() == 'TRUE':
            open_file(file_to_open)

        else:
            logger.debug(f'Finished {file_to_open}')

    return ReturnCode.OK, model




if __name__ == '__main__':
    exit_code, result = main()
    df = result
