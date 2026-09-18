import os
import pathlib
from typing import NoReturn

import pandas as pd
from dotenv import load_dotenv
from ebm.model.bema import map_sort_order
from ebm.model.calibrate_heating_systems import load_area_forecast, load_energy_need, load_heating_systems

from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.services.files import make_unique_path
from loguru import logger

CALIBRATION_YEAR = 2023

model_period = YearRange(2020, 2050)
start_year = model_period.start
end_year = model_period.end


def run_calibration(database_manager: DatabaseManager,  # noqa: D417
                    calibration_year: int,
                    area_forecast: pd.DataFrame = None,
                    write_to_output: bool = False) -> pd.DataFrame:
    """
    Calculate calibrated heating system.

    Parameters
    ----------
    database_manager : ebm.model.database_manager.DatabaseManager
    calibration_year : int
    area_forecast : pd.DataFrame
    write_to_output: bool, optional (default False)

    Returns
    -------
    pandas.core.frame.DataFrame

    """
    load_dotenv(pathlib.Path('.env'))

    input_directory = database_manager.file_handler.input_directory

    logger.info(f'Using input directory "{input_directory}"')
    logger.debug('Extract area forecast')
    model_period = load_model_period(database_manager)

    if model_period.start > calibration_year > model_period.end:
        msg = f'Calibration year {calibration_year} is outside model years {model_period.start}-{model_period.end}'
        raise ValueError(msg)

    area_forecast = load_area_forecast(database_manager, model_period) if area_forecast is None else area_forecast
    if write_to_output:
        write_dataframe(area_forecast[area_forecast.year == calibration_year], 'area_forecast')

    logger.debug('Extract energy requirements')
    energy_requirements = load_energy_need(area_forecast, database_manager, model_period)
    if write_to_output:
        en_req = energy_requirements.xs(calibration_year, level='year').reset_index().sort_values(
            by='building_category', key=lambda x: x.map(map_sort_order))
        write_dataframe(en_req, 'energy_requirements')
        grouped = en_req[['building_category', 'm2', 'kwh_m2', 'energy_requirement']].groupby(
            by=['building_category'], as_index=False).agg({'m2': 'first', 'kwh_m2': 'first', 'energy_requirement': 'sum'})
        grouped = grouped.sort_values(by='building_category', key=lambda x: x.map(map_sort_order))
        write_dataframe(grouped, 'energy_requirements_sum', sheet_name='sum')

    logger.debug('Extract heating systems')
    heating_systems = load_heating_systems(energy_requirements, database_manager, model_period)
    if write_to_output:
        write_dataframe(heating_systems.xs(calibration_year, level='year'), 'heating_systems')

    return heating_systems


def load_model_period(database_manager: DatabaseManager) -> YearRange:
    def load_ebm_year(key: str, default) -> int:
        start_year = int(os.environ.get(key, default))
        return start_year

    start_year = load_ebm_year('EBM_START_YEAR', 2020) or 2020
    end_year = load_ebm_year('EBM_END_YEAR', database_manager.get_population_forecast_end_year()) or 2050
    model_period = YearRange(start_year, end_year)
    return model_period





def write_dataframe(df: pd.DataFrame, name: str='dataframe', sheet_name: str='Sheet1') -> None:
    """
    Write dataframe df to excel spreadsheet.

    Notes
    -----
     - .xlsx added to the name
     - If the file exists a number will be added to the filename
     - The file will be written to the subdirectory `output`

    """
    output_directory = pathlib.Path('output')
    if output_directory.is_dir():
        logger.debug(f'Writing {name} to file')
        output_file = output_directory / f'{name}.xlsx'
        output_file = make_unique_path(output_file)
        df.to_excel(output_file, merge_cells=False, sheet_name=sheet_name)
        logger.success(f'Wrote {name} to {output_file} ! {sheet_name if sheet_name!="Sheet1" else ""}')
    else:
        logger.warning(f'Cannot write to {output_directory}. Directory does not exists')


def main() -> NoReturn:  # noqa: D103
    raise NotImplementedError('Running calibrate as a script is not supported')


if __name__ == '__main__':
    main()
