import pandas as pd

def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'purpose': ['heating_rv', 'heating_rv'],
        'heating_rv_factor': [1.0, 1.0]})
    return df

def default_calibrate_energy_consumption():
    df = pd.DataFrame({
        'building_category': [],
        'to': [],
        'from': [],
        'factor': []}
    )
    return df