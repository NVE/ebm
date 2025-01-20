import os
import pathlib
import sys

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.cmd.calibrate import run_calibration
from ebm.model.calibrate_energy_requirements import create_heating_rv
from ebm.cmd.run_calculation import calculate_building_category_area_forecast,  make_arguments, validate_years, \
    calculate_building_category_energy_requirements, calculate_heating_systems, calculate_energy_use, configure_loglevel
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler

from ebm.model.building_condition import BEMA_ORDER as building_condition_order
from ebm.model.building_category import BEMA_ORDER as building_category_order
from ebm.model.tek import BEMA_ORDER as tek_order


RETURN_CODE_OK = 0
RETURN_CODE_FILE_EXISTS = 1
RETURN_CODE_FILE_NOT_ACCESSIBLE = 2
RETURN_CODE_MISSING_INPUT_FILES = 3


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
    load_dotenv(pathlib.Path('.env'))

    configure_loglevel()

    logger.debug(f'Starting {sys.executable} {__file__}')

    program_name = 'calc-area-forecast'
    default_path = pathlib.Path('output/ebm_output.xlsx')

    arguments = make_arguments(program_name, default_path)

    # Make local variable from arguments for clarity
    building_categories = [BuildingCategory.from_string(b_c) for b_c in arguments.categories]
    if not building_categories:
        building_categories = list(BuildingCategory)
    building_conditions = [BuildingCondition(condition) for condition in arguments.conditions]

    # `;` Will normally be interpreted as line end when typed in a shell. If the
    # delimiter is empty make the assumption that the user used ;. An empty delimiter is not valid anyway.
    csv_delimiter = arguments.csv_delimiter if arguments.csv_delimiter else ';'

    # Make sure everything is working as expected
    validate_years(end_year=arguments.end_year, start_year=arguments.start_year)

    database_manager = DatabaseManager(file_handler=FileHandler(directory=arguments.input))

    # Create input directory if requested
    if arguments.create_input:
        database_manager.file_handler.create_missing_input_files()
        logger.info(f'Finished creating input files in {database_manager.file_handler.input_directory}')
        # Exit with 0 for success. The assumption is that the user would like to review the input before proceeding.
        return RETURN_CODE_OK

    # Make sure all required files exists
    missing_files = database_manager.file_handler.check_for_missing_files()
    if missing_files:
        print(f"""
    Use {program_name} --create-input to create an input directory with default files in the current directory
    """.strip(),
              file=sys.stderr)
        return RETURN_CODE_MISSING_INPUT_FILES

    database_manager.file_handler.validate_input_files()
    output_file = arguments.output_file
    database_manager.file_handler.make_output_directory(output_file.parent)

    if output_file.is_file() and output_file != default_path and not arguments.force:
        # If the file already exists and is not the default, display error and exit unless --force was used.
        logger.error(f'{output_file}. already exists.')
        print(f"""
You can overwrite the {output_file}. by using --force: {program_name} {' '.join(sys.argv[1:])} --force
""".strip(),
              file=sys.stderr)
        return RETURN_CODE_FILE_EXISTS
    if output_file.name != '-' and not file_is_writable(output_file):
        logger.error(f'{output_file} is not writable')
        return RETURN_CODE_FILE_NOT_ACCESSIBLE

    logger.info('Loading area forecast')

    model = None
    calibration_year = arguments.calibration_year
    step_choice = arguments.step
    transform_to_horizontal_years = arguments.horizontal_years

    if calibration_year:
        model = run_calibration(database_manager, calibration_year)
        calibration_directory = pathlib.Path('kalibrering')
        if not calibration_directory.is_dir():
            calibration_directory.mkdir()
        calibration_manager = DatabaseManager(FileHandler(directory=calibration_directory))
        calibration_manager.file_handler.create_missing_input_files()
        create_heating_rv(calibration_manager)
    elif step_choice == 'energy-use':
        model = calculate_energy_use()
    else:
        for building_category in building_categories:
            df = extract_model(arguments, building_category, building_conditions, database_manager, step_choice)
            if model is None:
                model = df
            else:
                model = pd.concat([model, df])

    if transform_to_horizontal_years and step_choice == 'heating-systems':
        write_horizontal_heating_systems(output_file, model)
    elif transform_to_horizontal_years and (step_choice in ['area-forecast', 'energy-requirements']) and output_file.suffix=='.xlsx':
        sheet_name_prefix = 'area' if step_choice == 'area-forecast' else 'energy'
        write_horizontal_excel(output_file, model, sheet_name=f'{sheet_name_prefix} condition')

        model = model.reset_index()
        model['building_condition'] = 'all'
        write_horizontal_excel(output_file, model, sheet_name=f'{sheet_name_prefix} TEK')

        model['TEK'] = 'all'
        write_horizontal_excel(output_file, model, sheet_name=f'{sheet_name_prefix} category')
    else:
        write_tqdm_result(output_file, csv_delimiter, model)

    if arguments.open:
        os.startfile(output_file, 'open')
    sys.exit(RETURN_CODE_OK)


def write_horizontal_heating_systems(output_file: pathlib.Path, model: pd.DataFrame):
    from ebm.model.calibrate_heating_systems import transform_heating_systems
    hs2 = model
    d = []
    for year in range(2020, 2051):
        energy_source_by_building_group = transform_heating_systems(hs2, year)
        energy_source_by_building_group['year'] = year
        d.append(energy_source_by_building_group)
    r = pd.concat(d)
    r2 = r.reset_index()[['building_category', 'energy_source', 'year', 'energy_use']]
    hz = r2.pivot(columns=['year'], index=['building_category', 'energy_source'], values=['energy_use']).reset_index()

    hz.columns = ['building_category', 'energy_source'] + [y for y in range(2020, 2051)]

    more_options = {'mode': 'w'}
    if output_file.is_file():
        more_options = {'if_sheet_exists': 'replace', 'mode': 'a'}

    with pd.ExcelWriter(output_file, engine='openpyxl', **more_options) as writer:
        hz.to_excel(writer, sheet_name='heating-systems', index=False, startcol=2)


def write_horizontal_excel(output_file: pathlib.Path, model: pd.DataFrame, sheet_name='condition'):
    logger.info(f'write horizontal {output_file} {sheet_name}')
    hz = model.reset_index().copy()
    value_column = 'energy_requirement' if 'energy_requirement' in hz.columns else 'm2'
    hz = hz.groupby(by=['building_category', 'TEK', 'building_condition', 'year'], as_index=False).sum()[
        ['building_category', 'TEK', 'building_condition', 'year', value_column]]
    hz = hz.pivot(columns=['year'], index=['building_category', 'TEK', 'building_condition'], values=[
        value_column]).reset_index()

    hz = hz.sort_values(by=['building_category', 'TEK', 'building_condition'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'TEK' else x.map(
                            building_condition_order) if x.name == 'building_condition' else x)
    hz.columns = ['building_category', 'TEK', 'building_condition'] + [y for y in range(2020, 2051)]

    more_options = {'mode': 'w'}
    if output_file.is_file():
        more_options = {'if_sheet_exists': 'replace', 'mode': 'a'}

    with pd.ExcelWriter(output_file, engine='openpyxl', **more_options) as writer:
        hz.to_excel(writer, sheet_name=sheet_name, index=False, startcol=2)


def extract_model(arguments, building_category, building_conditions, database_manager, step_choice):
    area_forecast_result = calculate_building_category_area_forecast(
        building_category=building_category,
        database_manager=database_manager,
        start_year=arguments.start_year,
        end_year=arguments.end_year)
    df = area_forecast_result
    df = df.set_index(['building_category', 'TEK', 'building_condition', 'year'])
    if building_conditions:
        df = df.loc[:, :, [str(s) for s in building_conditions]]
    if arguments.tek:
        tek_in_index = [t for t in arguments.tek if any(df.index.isin([t], level=1))]
        df = df.loc[:, tek_in_index, :]
    if 'energy-requirements' in step_choice or 'heating-systems' in step_choice:
        energy_requirements_result = calculate_building_category_energy_requirements(
            building_category=building_category,
            area_forecast=df,
            database_manager=database_manager,
            start_year=arguments.start_year,
            end_year=arguments.end_year)
        df = energy_requirements_result

        if 'heating-systems' in step_choice:
            df = calculate_heating_systems(energy_requirements=energy_requirements_result,
                                           database_manager=database_manager)
    return df


def write_result(output_file, csv_delimiter, output, sheet_name='area forecast'):
    logger.debug(f'Writing to {output_file}')
    if str(output_file) == '-':
        try:
            print(output.to_markdown())

        except ImportError:
            print(output.to_string())
    elif output_file.suffix == '.csv':
        output.to_csv(output_file, sep=csv_delimiter)
        logger.info(f'Wrote {output_file}')
    else:
        excel_writer = pd.ExcelWriter(output_file, engine='openpyxl')
        output.to_excel(excel_writer, sheet_name=sheet_name, merge_cells=False, freeze_panes=(1, 3))
        excel_writer.close()
        logger.info(f'Wrote {output_file}')


def write_tqdm_result(output_file, output, csv_delimiter=','):
    try:
        from tqdm import tqdm
    except ImportError:
        # When tqdm is not installed we use write_result instead
        write_result(output_file, csv_delimiter, output)
        return

    logger.debug(f'Writing to {output_file}')
    if str(output_file) == '-':
        try:
            print(output.to_markdown())
        except ImportError:
            print(output.to_string())
            return
    logger.info('reset index')
    output = output.reset_index()
    logger.info('resat index')
    with tqdm(total=len(output), desc="Writing to spreadsheet") as pbar:
        if output_file.suffix == '.csv':
            for i in range(0, len(output), 100):  # Adjust the chunk size as needed
                building_category = output.iloc[i].building_category
                pbar.update(100)
                output.iloc[i:i + 100].to_csv(output_file, mode='a', header=(i == 0), index=False, sep=csv_delimiter)
                pbar.display(f'Writing {building_category}')
            pbar.display(f'Wrote {output_file}')
        else:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as excel_writer:
                for i in range(0, len(output), 100):  # Adjust the chunk size as needed
                    building_category = output.iloc[i].name[0] if 'building_category' not in output.columns else output.building_category
                    pbar.set_description(f'Writing {building_category}')
                    output.iloc[i:i + 100].to_excel(excel_writer, startrow=i, header=(i == 0), merge_cells=False)
                    pbar.update(100)
                pbar.set_description(f'Closing {output_file}')
        pbar.set_description(f'Wrote {output_file}')


def file_is_writable(output_file: pathlib.Path) -> bool:
    if not output_file.is_file():
        # If the parent directory is writable we should be good to go
        return os.access(output_file.parent, os.W_OK)

    access = os.access(output_file, os.W_OK)
    if not access:
        return False

    # It is not enough to check that the file is writable in Windows. We must also check that it is possible to open
    # the file
    try:
        with output_file.open('a'):
            pass
    except PermissionError as ex:
        # Unable to open a file that is reported as writable by the operating system. In that case it is a good chance
        # that the file is already open. Error log our assumption and return False
        logger.error(str(ex) + '. File already open?')
        return False
    return True


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
