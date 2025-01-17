import pandas as pd

from ebm.model.calibrate_heating_systems import transform_heating_systems
from ebm.model.data_classes import YearRange


def group_heating_systems_energy_source_by_year(hs: pd.DataFrame, year_range: YearRange=None) -> pd.DataFrame:
    years = year_range if year_range else YearRange(hs.year.min(), hs.year.max())
    df = hs.set_index(['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'heating_systems'])
    d = []
    for year in years:
        energy_source_by_building_group = transform_heating_systems(df, year)
        energy_source_by_building_group['year'] = year
        d.append(energy_source_by_building_group)

    return pd.concat(d)


def group_heating_systems_energy_source_by_year_horizontal(hs: pd.DataFrame, year_range: YearRange=None) -> pd.DataFrame:
    df = group_heating_systems_energy_source_by_year(hs, year_range)
    return df.reset_index().pivot(columns=['year'], index=['building_category', 'energy_source'], values=['energy_use'])

