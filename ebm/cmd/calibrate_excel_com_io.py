import os
import pathlib
import time

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.cmd.calibrate import run_calibration
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model import FileHandler, DatabaseManager
from ebm.model.calibrate_energy_requirements import EnergyRequirementCalibrationWriter
from ebm.model.calibrate_heating_systems import DistributionOfHeatingSystems, transform_heating_systems
from ebm.services.calibration_writer import ComCalibrationReader, CalibrationResultWriter

LOG_FORMAT = """
<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
""".strip()


def main():
    start_time = time.time()
    load_dotenv(pathlib.Path('.env'))
    configure_loglevel(format=LOG_FORMAT)

    calibration_year = int(os.environ.get('EBM_CALIBRATION_YEAR', 2023))
    calibration_out = os.environ.get("EBM_CALIBRATION_OUT", "Kalibreringsark.xlsx!Ut")
    calibration_sheet = os.environ.get("EBM_CALIBRATION_SHEET", "Kalibreringsark.xlsx!Kalibreringsfaktorer")

    energy_requirements_calibration_file = os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
                                                          'kalibrering/calibrate_heating_rv.xlsx')
    energy_source_target_cells = os.environ.get('EBM_CALIBRATION_ENERGY_SOURCE_USAGE', 'C64:E68')
    ebm_calibration_energy_heating_pump = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_PUMP', 'C72:E74')
    hs_distribution_cells = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_SYSTEMS_DISTRIBUTION', 'C32:F44')

    logger.info(f'Loading {calibration_sheet}')

    com_calibration_reader = ComCalibrationReader(*calibration_sheet.split('!'))
    values = com_calibration_reader.extract()

    logger.info(f'Make {calibration_sheet} compatible with ebm')
    energy_source_by_building_group = com_calibration_reader.transform(values)

    logger.info('Write calibration to ebm')
    enreq_writer = EnergyRequirementCalibrationWriter()
    enreq_writer.load(energy_source_by_building_group, energy_requirements_calibration_file)

    logger.info('Calculate calibrated energy use')
    area_forecast = None
    area_forecast_file = pathlib.Path('kalibrering/area_forecast.csv')
    if area_forecast_file.is_file():
        logger.info(f'  Using {area_forecast_file}')
        area_forecast = pd.read_csv(area_forecast_file)

    df = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023,
                         area_forecast=area_forecast)
    logger.info('Transform heating systems')

    energy_source_by_building_group = transform_heating_systems(df, calibration_year)
    energy_source_by_building_group = energy_source_by_building_group.fillna(0)

    logger.info(f'Writing heating systems distribution to {calibration_out}')
    hs_distribution_writer = CalibrationResultWriter(excel_filename=calibration_out,
                                                     target_cells=hs_distribution_cells)

    distribution_of_heating_systems_by_building_group = DistributionOfHeatingSystems().transform(df)
    hs_distribution_writer.extract()
    hs_distribution_writer.transform(distribution_of_heating_systems_by_building_group)
    hs_distribution_writer.load()

    logger.info(f'Writing energy_source using writer to {calibration_out}')
    writer = CalibrationResultWriter(excel_filename=calibration_out,
                                     target_cells=energy_source_target_cells)
    writer.extract()
    writer.transform(energy_source_by_building_group)
    writer.load()
    logger.info(f'Writing calculated energy pump use to {calibration_out}')
    writer = CalibrationResultWriter(excel_filename=calibration_out,
                                     target_cells=ebm_calibration_energy_heating_pump)
    writer.extract()
    writer.transform(energy_source_by_building_group)
    writer.load()
    logger.info(f'Calibrated {calibration_out} in {round(time.time() - start_time, 2)} seconds')


if __name__ == '__main__':
    main()
