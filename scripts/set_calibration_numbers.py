import os
import pathlib

from dotenv import load_dotenv
from loguru import logger
from rich.pretty import pprint
from ebm.cmd.calibrate import run_calibration
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model import FileHandler, DatabaseManager
from ebm.model.calibrate_heating_rv import EnergyRequirementCalibrationWriter
from ebm.services.calibration_writer import CalibrationResultWriter, ComCalibrationReader


logger.info('Loading .env')
load_dotenv(pathlib.Path('.env'))

configure_loglevel()

com_calibration_reader = ComCalibrationReader()
logger.info('Loading calibration')
values = com_calibration_reader.extract()

pprint(values)
logger.info('Make spreadsheet calibration ebm compatible')
transformed = com_calibration_reader.transform(values)
pprint(transformed)
logger.info('Write calibration to ebm')
enreq_writer = EnergyRequirementCalibrationWriter()
enreq_writer.load(transformed, os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
                                              'kalibrering/slettmeg.csv'))


calibration_result_writer = CalibrationResultWriter()

logger.info('Calculate calibrated energy use')
df = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023)

calibration_result_writer.extract()
df = calibration_result_writer.transform(df)
calibration_result_writer.load()

logger.info('done')

