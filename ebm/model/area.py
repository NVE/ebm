from loguru import logger
import pandas as pd

from ebm.model.building_condition import BuildingCondition


def transform_area_forecast_to_area_change(area_forecast: pd.DataFrame,
                                           tek_parameters: pd.DataFrame | None=None) -> pd.DataFrame:
    construction_by_year = transform_construction_by_year(area_forecast, tek_parameters)
    construction_by_year.loc[:, 'demolition_construction'] = 'construction'

    demolition_by_year = transform_cumulative_demolition_to_yearly_demolition(area_forecast)
    demolition_by_year.loc[:, 'demolition_construction'] = 'demolition'
    demolition_by_year.loc[:, 'm2'] = -demolition_by_year.loc[:, 'm2']

    area_change = pd.concat([
        demolition_by_year[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']],
        construction_by_year.reset_index()[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']]
    ])
    return area_change.fillna(0.0)


def transform_cumulative_demolition_to_yearly_demolition(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Convert accumulated demolition area data to yearly demolition values.

    This function filters the input DataFrame for rows where the building condition is demolition,
    and calculates the yearly change in square meters (m2) by computing the difference between
    consecutive years within each group defined by building category and TEK standard.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data. Must include the columns:
        'building_category', 'TEK', 'year', 'building_condition', and 'm2'.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ['building_category', 'TEK', 'year', 'm2'], where 'm2' represents
        the yearly demolition area (difference from the previous year). Missing values are filled with 0.

    Notes
    -----
    - The function assumes that the input data is cumulative and sorted by year.
    - The first year in each group will have a demolition value of 0.
    """

    cumulative_demolition = area_forecast[area_forecast['building_condition'] == BuildingCondition.DEMOLITION].copy()
    cumulative_demolition['m2'] = cumulative_demolition['m2'].fillna(0)
    grouped_demolition = cumulative_demolition.groupby(by=['building_category', 'TEK', 'building_condition'], as_index=False)
    yearly_demolition = cumulative_demolition
    yearly_demolition['diff'] = grouped_demolition.diff()['m2']
    return yearly_demolition[['building_category', 'TEK', 'year', 'diff']].rename(columns={'diff': 'm2'})


def transform_construction_by_year(area_forecast, tek_parameters):
    tek_params = tek_parameters
    if tek_params is None:
        tek_params = pd.DataFrame(
            data=[['TEK17', 2025, 2020, 2050]],
            columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])
        logger.warning('Using default TEK17 for construction')
    area_forecast = area_forecast.merge(tek_params, on='TEK', how='left')
    constructed = area_forecast.query(
        'year>=period_start_year and year <=period_end_year and building_condition!="demolition"').copy()
    constructed = constructed[['building_category', 'TEK', 'year', 'building_condition', 'm2']]
    constructed = constructed.set_index(['building_category', 'TEK', 'year', 'building_condition'])[['m2']].unstack()

    constructed['total'] = constructed.sum(axis=1)

    constructed=constructed.groupby(by=['building_category', 'TEK'], as_index=False).diff()
    constructed = constructed.reset_index()[['building_category', 'TEK', 'year', 'total']]
    constructed.columns = ['building_category', 'TEK', 'year', 'm2']
    return constructed


def transform_demolition_construction(energy_use: pd.DataFrame, area_change: pd.DataFrame) -> pd.DataFrame:
    df = energy_use[energy_use['building_condition']=='renovation_and_small_measure']

    energy_use_m2 = df.groupby(by=['building_category', 'building_condition', 'TEK', 'year'], as_index=False).sum()[['building_category',  'TEK', 'year', 'kwh_m2']]

    dem_con = pd.merge(left=area_change, right=energy_use_m2, on=['building_category', 'TEK', 'year'])
    dem_con['gwh'] = (dem_con['kwh_m2'] * dem_con['m2']) / 1_000_000
    return dem_con[['year', 'demolition_construction', 'building_category', 'TEK', 'm2', 'gwh']]


def merge_tek_and_condition(area_forecast:pd.DataFrame) -> pd.DataFrame:
    all_existing_area = area_forecast.copy()
    all_existing_area.loc[:, 'TEK'] = 'all'
    all_existing_area.loc[:, 'building_condition'] = 'all'

    return all_existing_area


def filter_existing_area(area_forecast):
    existing_area = area_forecast.query('building_condition!="demolition"').copy()
    existing_area = existing_area[['year','building_category','TEK','building_condition']+['m2']]
    return existing_area