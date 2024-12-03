import pandas as pd

#heating_rv = heating_rv.extract().transform(eq_reduction_per_condition)

#calibrated_heating_rv = calibrate_heating_rv.extract().transform(heating_rv)


class CalibrateHeatingRVTransformer:
    heating_rv_factor: pd.Series

    def __init__(self, heating_rv_factor=None):
        self.heating_rv_factor = heating_rv_factor

    def transform(self, heating_rv: pd.Series):
        if not self.heating_rv_factor:
            return heating_rv
        return heating_rv * self.heating_rv_factor


class EbmCalibration:
    heating_rv: CalibrateHeatingRVTransformer


def extract(database_manager) -> CalibrateHeatingRVTransformer:
    calibrate_heating_rv = database_manager.get_calibrate_heating_rv()
    return calibrate_heating_rv


def transform(heating_rv: pd.Series, heating_rv_factor=None) -> pd.Series:
    if heating_rv_factor is None:
        return heating_rv
    calibrated = heating_rv * heating_rv_factor
    calibrated.name = heating_rv.name
    return calibrated


def load(self):
    raise NotImplemented(f'{__name__}.load not implemented')


def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'heating_rv_factor': [1.0, 1.0]})
    return df

