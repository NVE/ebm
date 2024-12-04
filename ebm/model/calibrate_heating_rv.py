import pandas as pd


def transform(heating_rv: pd.Series, heating_rv_factor=None) -> pd.Series:
    if heating_rv_factor is None:
        return heating_rv
    calibrated = heating_rv * heating_rv_factor
    calibrated.name = heating_rv.name
    return calibrated


def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'heating_rv_factor': [1.0, 1.0]})
    return df

