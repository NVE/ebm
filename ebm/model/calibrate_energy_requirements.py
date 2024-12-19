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
        df = df[['building_category', 'purpose', 'heating_rv_factor']].reset_index(drop=True)
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
