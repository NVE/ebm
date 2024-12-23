import pathlib
import typing

from loguru import logger
import pandas as pd


class EnergyRequirementCalibrationWriter:

    def __init__(self):
        pass

    def load(self, df: pd.DataFrame, to_file: typing.Union[str, pathlib.Path] = None):
        logger.debug(f'Save {to_file}')
        if to_file is None:
            to_file = pathlib.Path('input/calibrate_heating_rv.xlsx')
        file_path: pathlib.Path = to_file if isinstance(to_file, pathlib.Path) else pathlib.Path(to_file)
        df = df[df['group'] == 'energy_requirements']
        df = df.rename(columns={'variable': 'purpose'})
        df = df[['building_category', 'purpose', 'heating_rv_factor']].reset_index(drop=True)
        if file_path.suffix == '.csv':
            df.to_csv(file_path, index=False)
        elif file_path.suffix == '.xlsx':
            df.to_excel(file_path, index=False)
        logger.info(f'Wrote {to_file}')


class EnergyConsumptionCalibrationWriter:

    def __init__(self):
        pass

    def load(self, df: pd.DataFrame, to_file: typing.Union[str, pathlib.Path] = None):
        logger.debug(f'Save {to_file}')
        if to_file is None:
            to_file = pathlib.Path('input/calibrate_energy_consumption.xlsx')
        file_path: pathlib.Path = to_file if isinstance(to_file, pathlib.Path) else pathlib.Path(to_file)
        df = df[df['group'] == 'energy_consumption']
        df = df[['building_category', 'variable', 'heating_rv_factor']].reset_index(drop=True)
        if file_path.suffix == '.csv':
            df.to_csv(file_path, index=False)
        elif file_path.suffix == '.xlsx':
            df.to_excel(file_path, index=False)
        logger.info(f'Wrote {to_file}')


def transform(heating_rv: pd.Series, heating_rv_factor=None) -> pd.Series:
    if heating_rv_factor is None:
        return heating_rv
    calibrated = heating_rv * heating_rv_factor
    calibrated.name = heating_rv.name
    return calibrated


def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'purpose': ['heating_rv', 'heating_rv'],
        'heating_rv_factor': [1.0, 1.0]})
    return df


def create_heating_rv(database_manager):
    file_handler = database_manager.file_handler
    heating_rv = file_handler.input_directory / 'calibrate_heating_rv.xlsx'
    if not heating_rv.is_file():
        logger.info(f'Creating {heating_rv}')
        df = default_calibrate_heating_rv()
        df.to_excel(heating_rv)


class EbmCalibration:
    energy_requirement_original_condition: pd.Series
    pass


class CalibrationReader:
    def extract(self) -> pd.Series:
        pass

    def transform(self) -> pd.Series:
        pass

    def load(self) -> None:
        pass


class CalibrationWriter:
    pass
