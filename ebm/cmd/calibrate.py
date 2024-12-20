import pathlib

from loguru import logger
import pandas as pd

import pyperclip
from dotenv import load_dotenv

from ebm.model import DatabaseManager, FileHandler
from ebm.model.calibrate_heating_systems import extract_area_forecast, extract_energy_requirements, \
    extract_heating_systems
from ebm.model.data_classes import YearRange


CALIBRATION_YEAR = 2023

model_period = YearRange(2020, 2050)
start_year = model_period.start
end_year = model_period.end


def run_calibration(database_manager,
                    calibration_year,
                    area_forecast: pd.DataFrame = None):
    """

    Parameters
    ----------
    database_manager : ebm.model.database_manager.DatabaseManager

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    load_dotenv(pathlib.Path('.env'))

    calibration_directory = pathlib.Path('kalibrering')
    input_directory = database_manager.file_handler.input_directory

    logger.info(f'Using input directory "{input_directory}"')
    logger.info('Extract area forecast')
    area_forecast = extract_area_forecast(database_manager) if area_forecast is None else area_forecast

    logger.info('Extract energy requirements')
    energy_requirements = extract_energy_requirements(area_forecast, database_manager)

    logger.info('Extract heating systems')
    heating_systems = extract_heating_systems(energy_requirements, database_manager)

    return heating_systems


def main():
    transformed = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023)
    tabbed = transformed.round(1).to_csv(sep='\t', header=False, index_label=None).replace('.', ',')
    pyperclip.copy(tabbed)


if __name__ == '__main__':
    main()
