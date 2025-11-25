import argparse
import os
import pathlib
import time
from dataclasses import dataclass

import pandas as pd
from dotenv import load_dotenv
from ebm.__version__ import version
from ebm.cmd.calibrate import run_calibration, write_dataframe
from ebm.cmd.helpers import configure_loglevel
from ebm.model.calibrate_energy_requirements import EnergyConsumptionCalibrationWriter, EnergyRequirementCalibrationWriter
from ebm.model.calibrate_heating_systems import DistributionOfHeatingSystems, group_heating_systems_by_energy_carrier
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.services.calibration_writer import ComCalibrationReader, ExcelComCalibrationResultWriter, ExcelComCalibrationStatusWriter
from loguru import logger

LOG_FORMAT = """
<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
""".strip()  # noqa: E501
PROGRAM_NAME = 'ebm-calibrate'


@dataclass
class CalibrateConfig:  # noqa: D101
    write_to_disk: bool | None = False
    calibration_spreadsheet_name: str | None = None
    calibration_sheet: str | None = None
    energy_consumption_calibration_file: str | None = None
    energy_requirements_calibration_file: str | None = None
    energy_source_target_cells:str | None = None
    ebm_calibration_energy_heating_pump: str| None = None
    hs_distribution_cells: str | None = None
    calibration_year_cell: str | None = None
    calibration_workbook_name: str | None = None
    calibration_sheet_name: str | None = None
    output_directory: pathlib.Path | None = None

    def __post_init__(self):   # noqa: C901
        """Load calibration config from environment variables when None."""
        if self.write_to_disk is None:
            self.write_to_disk = os.environ.get('EBM_WRITE_TO_DISK', 'False').upper() == 'TRUE'
        if self.calibration_spreadsheet_name is None:
            self.calibration_spreadsheet_name = os.environ.get("EBM_CALIBRATION_OUT",
                                                               "Kalibreringsark.xlsx!Ut")
        if self.calibration_sheet is None:
            self.calibration_sheet = os.environ.get("EBM_CALIBRATION_SHEET",
                                                    "Kalibreringsark.xlsx!Kalibreringsfaktorer")
        if self.energy_requirements_calibration_file is None:
            self.energy_requirements_calibration_file = os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
                                                              f'kalibrering/{FileHandler.CALIBRATE_ENERGY_REQUIREMENT}')
        if self.energy_consumption_calibration_file is None:
            self.energy_consumption_calibration_file = os.environ.get('EBM_CALIBRATION_ENERGY_CONSUMPTION',
                                                             f'kalibrering/{FileHandler.CALIBRATE_ENERGY_CONSUMPTION}')
        if self.energy_source_target_cells is None:
            self.energy_source_target_cells = os.environ.get('EBM_CALIBRATION_ENERGY_SOURCE_USAGE',
                                                             'C64:E68')
        if self.ebm_calibration_energy_heating_pump is None:
            self.ebm_calibration_energy_heating_pump = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_PUMP',
                                                                      'C72:E74')
        if self.hs_distribution_cells is None:
            self.hs_distribution_cells = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_SYSTEMS_DISTRIBUTION',
                                                        'C32:F44')
        if self.calibration_year_cell is None:
            self.calibration_year_cell = os.environ.get('EBM_CALIBRATION_YEAR_CELL', 'C63')

        if self.output_directory is None:
            self.output_directory = os.environ.get('EBM_OUTPUT_DIRECTORY', pathlib.Path('output'))
        self.calibration_workbook_name = self.calibration_sheet.split('!')[0]
        self.calibration_sheet_name = self.calibration_sheet.split('!')[1] if '!' in self.calibration_sheet else 'Kalibreringsfaktorer'


def calibrate_with_spreadsheet(calibration_config: CalibrateConfig, calibration_year: int) -> None:
    """Read calibration parameters from open spreadsheet and updated results from new ebm calculation."""
    com_calibration_reader = ComCalibrationReader(calibration_config.calibration_workbook_name,
                                                  calibration_config.calibration_sheet_name)
    calibration = com_calibration_reader.extract()
    logger.info(f'Make {calibration_config.calibration_sheet} compatible with ebm')
    energy_source_by_building_group = com_calibration_reader.transform(calibration)

    logger.info('Write calibration to ebm input')
    eq_calibration_writer = EnergyRequirementCalibrationWriter()
    eq_calibration_writer.load(energy_source_by_building_group, calibration_config.energy_requirements_calibration_file)
    ec_calibration_writer = EnergyConsumptionCalibrationWriter()
    ec_calibration = ec_calibration_writer.transform(energy_source_by_building_group)
    ec_calibration_writer.load(ec_calibration, calibration_config.energy_consumption_calibration_file)

    logger.info('Calculate calibrated energy use')
    area_forecast = None
    area_forecast_file = pathlib.Path('kalibrert/area_forecast.csv')
    if area_forecast_file.is_file():
        logger.info(f'Using dataframe cached in {area_forecast_file}')
        area_forecast = pd.read_csv(area_forecast_file)
    database_manager = DatabaseManager(FileHandler(directory='kalibrering'))
    df = run_calibration(database_manager, calibration_year=calibration_year,
                         area_forecast=area_forecast, write_to_output=calibration_config.write_to_disk)

    logger.debug('Transform heating systems')
    energy_source_by_building_group = group_heating_systems_by_energy_carrier(df)
    energy_source_by_building_group = energy_source_by_building_group.xs(calibration_year, level='year')
    if calibration_config.write_to_disk:
        if not calibration_config.output_directory.is_dir():
            calibration_config.output_directory.mkdir()
        write_dataframe(energy_source_by_building_group, 'energy_source_by_building_group')
    energy_source_by_building_group = energy_source_by_building_group.fillna(0)

    logger.info(f'Writing heating systems distribution to {calibration_config.calibration_spreadsheet_name}')
    hs_distribution_writer = ExcelComCalibrationResultWriter(
        excel_filename=calibration_config.calibration_spreadsheet_name,
        target_cells=calibration_config.hs_distribution_cells)
    distribution_of_heating_systems = DistributionOfHeatingSystems()
    shares_start_year = distribution_of_heating_systems.extract(database_manager)
    heating_systems_distribution = distribution_of_heating_systems.transform(shares_start_year)
    hs_distribution_writer.extract()
    hs_distribution_writer.transform(heating_systems_distribution)
    hs_distribution_writer.load()

    logger.info(f'Writing energy_source using to {calibration_config.calibration_spreadsheet_name}')
    energy_source_excel_com_writer = ExcelComCalibrationResultWriter(
        excel_filename=calibration_config.calibration_spreadsheet_name,
        target_cells=calibration_config.energy_source_target_cells)
    energy_source_excel_com_writer.extract()
    energy_source_excel_com_writer.transform(energy_source_by_building_group)
    energy_source_excel_com_writer.load()

    logger.info(f'Writing calculated energy pump use to {calibration_config.calibration_spreadsheet_name}')
    heatpump_excel_com_writer = ExcelComCalibrationResultWriter(
        excel_filename=calibration_config.calibration_spreadsheet_name,
        target_cells=calibration_config.ebm_calibration_energy_heating_pump)
    heatpump_excel_com_writer.extract()
    heatpump_excel_com_writer.transform(energy_source_by_building_group)
    heatpump_excel_com_writer.load()

    logger.info('Writing calibration year header to {spreadsheet_name}', spreadsheet_name=calibration_config.calibration_spreadsheet_name)
    updated_header = f'Energibruk {calibration_year} resultater fra EBM'
    calibration_year_writer = ExcelComCalibrationStatusWriter(excel_filename=calibration_config.calibration_spreadsheet_name,
                                                              target_cells=calibration_config.calibration_year_cell,
                                                              value=updated_header)
    calibration_year_writer.load()


def load_arguments() -> argparse.Namespace:
    """
    Make command line arguments for ebm-calibrate.

    Returns
    -------
    argparse.Namespace

    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
    arg_parser.add_argument('--version', '-v', action='version', version=f'{PROGRAM_NAME} {version}')
    arg_parser.add_argument('--calibration-year', '--ebm-calibration-year',
                            type=int,
                            nargs='?',
                            default=int(os.environ.get('EBM_CALIBRATION_YEAR', '2023')))
    arguments = arg_parser.parse_args()
    return arguments


def main() -> None:
    """Run calibration from command line on an open spreadsheet using win32com."""
    configure_loglevel(log_format=os.environ.get('LOG_FORMAT', LOG_FORMAT))
    load_dotenv(pathlib.Path('.env'))
    arguments = load_arguments()

    start_time = time.time()

    calibration_year = arguments.calibration_year
    logger.info('Using calibration year: {calibration_year}', calibration_year=calibration_year)

    calibration_config = CalibrateConfig()

    logger.info(f'Loading {calibration_config.calibration_sheet}')

    calibrate_with_spreadsheet(calibration_config, calibration_year)

    logger.info(f'Calibrated {calibration_config.calibration_spreadsheet_name} in {round(time.time() - start_time, 2)} seconds')


if __name__ == '__main__':
    main()
