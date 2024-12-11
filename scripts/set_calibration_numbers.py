import os
import pathlib
import time

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from rich.pretty import pprint
from ebm.cmd.calibrate import run_calibration
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model import FileHandler, DatabaseManager
from ebm.model.calibrate_heating_rv import EnergyRequirementCalibrationWriter
from ebm.services.calibration_writer import CalibrationResultWriter, ComCalibrationReader

LOG_FORMAT = """
<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
""".strip()


def main():
    start_time = time.time()
    load_dotenv(pathlib.Path('.env'))
    configure_loglevel(format=LOG_FORMAT)

    calibration_out = os.environ.get("EBM_CALIBRATION_OUT", "")
    calibration_sheet = os.environ.get("EBM_CALIBRATION_SHEET", "")
    DEBUG = os.environ.get('DEBUG', 'False').capitalize() == 'True'
    logger.info(f'Loading {calibration_sheet}')
    com_calibration_reader = ComCalibrationReader()
    values = com_calibration_reader.extract()
    if DEBUG:
        pprint(values)
    logger.info(f'Make {calibration_sheet} compatible with ebm')
    transformed = com_calibration_reader.transform(values)
    if DEBUG:
        pprint(transformed)
    logger.info('Write calibration to ebm')
    enreq_writer = EnergyRequirementCalibrationWriter()
    enreq_writer.load(transformed, os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
                                                  'kalibrering/slettmeg.csv'))
    calibration_result_writer = CalibrationResultWriter()
    logger.info('Calculate calibrated energy use')
    area_forecast = None
    area_forecast_file = pathlib.Path('kalibrering/area_forecast.csv')
    if area_forecast_file.is_file():
        logger.info(f'  Using {area_forecast_file}')
        area_forecast = pd.read_csv(area_forecast_file)
    df = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023,
                         area_forecast=area_forecast)
    logger.info(f'Writing calculated energy use to {calibration_out}')
    calibration_result_writer.extract()
    df = calibration_result_writer.transform(df)
    calibration_result_writer.load()
    logger.info(f'Calibrated {calibration_out} in {round(time.time() - start_time, 2)} seconds')


if __name__ == '__main__':
    main()

