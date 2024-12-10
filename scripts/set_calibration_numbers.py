import os
import pathlib
import sys

from dotenv import load_dotenv
from loguru import logger
from rich.pretty import pprint
from ebm.cmd.calibrate import run_calibration
from ebm.model import FileHandler, DatabaseManager
from ebm.model.calibrate_heating_rv import EnergyRequirementCalibrationWriter
from ebm.services.calibration_writer import CalibrationResultWriter, ComCalibrationReader

load_dotenv(pathlib.Path('.env'))

com_calibration_reader = ComCalibrationReader()

values = com_calibration_reader.extract()
pprint('extracted')
pprint(values)
pprint('transformed')
transformed = com_calibration_reader.transform(values)
pprint(transformed)

pprint('write')
enreq_writer = EnergyRequirementCalibrationWriter()
enreq_writer.load(transformed, os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
                                              'kalibrering/slettmeg.csv'))


calibration_result_writer = CalibrationResultWriter()

df = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023)

calibration_result_writer.extract()
df = calibration_result_writer.transform(df)
calibration_result_writer.load()


