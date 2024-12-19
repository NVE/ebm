import os
import pathlib
import time

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from rich.pretty import pprint
from ebm.cmd.calibrate import run_calibration, transform_heating_systems
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model import FileHandler, DatabaseManager
from ebm.model.calibrate_energy_requirements import EnergyRequirementCalibrationWriter
from ebm.services.calibration_writer import CalibrationResultWriter, ComCalibrationReader, \
    HeatingSystemsDistributionWriter

LOG_FORMAT = """
<green>{time:HH:mm:ss.SSS}</green> | <blue>{elapsed}</blue> | <level>{level: <8}</level> | <cyan>{function: <20}</cyan>:<cyan>{line: <3}</cyan> - <level>{message}</level>
""".strip()


class DistributionOfHeatingSystems:

    def transform(self, df):
        df = df.reset_index()
        df['building_group'] = 'Yrkesbygg'

        df = df[df['building_category'] != 'storage_repairs']
        df.loc[df['building_category'].isin(['house', 'apartment_block']), 'building_group'] = 'Bolig'

        distribution_of_heating_systems_by_building_group = df.groupby(by=['building_group', 'heating_systems'])[
            ['TEK_shares']].mean()
        return distribution_of_heating_systems_by_building_group


def main():
    start_time = time.time()
    load_dotenv(pathlib.Path('.env'))
    configure_loglevel(format=LOG_FORMAT)

    calibration_out = os.environ.get("EBM_CALIBRATION_OUT", "Kalibreringsark.xlsx!Ut")
    calibration_sheet = os.environ.get("EBM_CALIBRATION_SHEET", "Kalibreringsark.xlsx!Kalibreringsfaktorer")

    logger.info(f'Loading {calibration_sheet}')

    com_calibration_reader = ComCalibrationReader()
    values = com_calibration_reader.extract()

    logger.info(f'Make {calibration_sheet} compatible with ebm')
    energy_source_by_building_group = com_calibration_reader.transform(values)

    logger.info('Write calibration to ebm')
    enreq_writer = EnergyRequirementCalibrationWriter()
    enreq_writer.load(energy_source_by_building_group, os.environ.get('EBM_CALIBRATION_ENERGY_REQUIREMENT',
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
    logger.info('Transform heating systems')

    energy_source_by_building_group = transform_heating_systems(df, int(os.environ.get('EBM_CALIBRATION_YEAR', 2023)))
    energy_source_by_building_group = energy_source_by_building_group.fillna(0)

    logger.info(f'Writing heating systems distribution to {calibration_out}')
    hs_distribution_cells = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_SYSTEMS_DISTRIBUTION', 'C33:F44')
    hs_distribution_writer = HeatingSystemsDistributionWriter(excel_filename=calibration_out,
                                                              target_cells=hs_distribution_cells)

    distribution_of_heating_systems_by_building_group = DistributionOfHeatingSystems().transform(df)
    hs_distribution_writer.extract()
    hs_distribution_writer.transform(distribution_of_heating_systems_by_building_group)
    hs_distribution_writer.load()

    logger.info(f'Writing calculated energy use to {calibration_out}')
    calibration_result_writer.extract()
    calibration_result_writer.transform(energy_source_by_building_group)
    calibration_result_writer.load()
    logger.info(f'Calibrated {calibration_out} in {round(time.time() - start_time, 2)} seconds')


if __name__ == '__main__':
    main()

