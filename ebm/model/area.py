import numpy as np
import pandas as pd

from ebm.model.building_condition import BuildingCondition


def extract_area_change(area_forecast: pd.DataFrame) -> pd.DataFrame:
    df = area_forecast[area_forecast.TEK=='TEK17'].copy()

    df = df.set_index(['building_category', 'TEK', 'year', 'building_condition']).unstack()
    df.columns=df.columns.get_level_values(1)
    df['total']=df.sum(axis=1)
    df['m2'] = df['total'] - df['total'].shift()

    df['demolition_construction'] = 'construction'

    construction = df[['demolition_construction','m2']].copy()
    construction['m2'] = construction['m2'].clip(lower=np.nan)

    demolition = area_forecast[area_forecast['building_condition']==BuildingCondition.DEMOLITION].copy()
    demolition.loc[:, 'demolition_construction'] = 'demolition'
    demolition.loc[:, 'm2'] = -demolition.loc[:, 'm2']

    area_change = pd.concat([
        demolition[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']],
        construction.reset_index()[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']]
    ])
    return area_change


def transform_demolition_construction(energy_use: pd.DataFrame, area_change: pd.DataFrame) -> pd.DataFrame:
    df = energy_use[energy_use['building_condition']=='renovation_and_small_measure']

    energy_use_m2 = df.groupby(by=['building_category', 'building_condition', 'TEK', 'year'], as_index=False).sum()[['building_category',  'TEK', 'year', 'kwh_m2']]

    dem_con = pd.merge(left=area_change, right=energy_use_m2, on=['building_category', 'TEK', 'year'])
    dem_con['gwh'] = (dem_con['kwh_m2'] * dem_con['m2']) / 1_000_000
    return dem_con[['year', 'demolition_construction', 'building_category', 'TEK', 'm2', 'gwh']]