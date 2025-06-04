from loguru import logger
import pandas as pd

from ebm.model.building_condition import BuildingCondition
from ebm.model.scurve import SCurve


def transform_area_forecast_to_area_change(area_forecast: pd.DataFrame,
                                           tek_parameters: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Transform area forecast data into yearly area changes due to construction and demolition.

    This function processes forecasted area data and optional TEK parameters to compute
    the net yearly area change. It distinguishes between construction (positive area change)
    and demolition (negative area change), and returns a combined DataFrame.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data, including construction and demolition.

    tek_parameters : pandas.DataFrame, optional
        A DataFrame containing TEK-related parameters used to refine construction data.
        If None, construction is assumed to be of TEK17. (transform_construction_by_year)

    Returns
    -------
    pandas.DataFrame
        A DataFrame with yearly area changes. Columns include:
        - 'building_category': Category of the building.
        - 'TEK': TEK classification.
        - 'year': Year of the area change.
        - 'demolition_construction': Indicates whether the change is due to 'construction' or 'demolition'.
        - 'm2': Area change in square meters (positive for construction, negative for demolition).

    Notes
    -----
    - Demolition areas are negated to represent area loss.
    - Missing values are filled with 0.0.
    - Assumes helper functions `transform_construction_by_year` and
      `transform_cumulative_demolition_to_yearly_demolition` are defined elsewhere.
    """
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
    if area_forecast is None:
        raise ValueError('Expected area_forecast of type pandas DataFrame. Got «None» instead.')
    expected_columns = ('building_category', 'TEK', 'building_condition', 'year', 'm2')
    missing_columns = [c for c in expected_columns if c not in area_forecast.columns]
    if missing_columns:
        raise ValueError(f'Column {", ".join(missing_columns)} not found in area_forecast')

    df = area_forecast[area_forecast['building_condition'] == BuildingCondition.DEMOLITION].copy()
    df = df.set_index(['building_category', 'TEK', 'building_condition', 'year']).sort_index()
    df['m2'] = df['m2'].fillna(0)
    df['diff'] = df.groupby(by=['building_category', 'TEK', 'building_condition']).diff()['m2']

    return df.reset_index()[['building_category', 'TEK', 'year', 'diff']].rename(columns={'diff': 'm2'})


def transform_construction_by_year(area_forecast: pd.DataFrame,
                                   tek_parameters: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Calculate yearly constructed building area based on TEK parameters.

    This function filters the input forecast data to include only construction (non-demolition)
    within the TEK-defined construction period. It then calculates the yearly change in constructed
    area (m2) for each combination of building category and TEK standard.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data. Must include the columns:
        'building_category', 'TEK', 'year', 'building_condition', and 'm2'.

    tek_parameters : pandas.DataFrame or None, optional
        A DataFrame containing TEK construction period definitions with columns:
        ['TEK', 'building_year', 'period_start_year', 'period_end_year'].
        If None, a default TEK17 period is used (2020–2050 with building year 2025).

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ['building_category', 'TEK', 'year', 'm2'], where 'm2' represents
        the yearly constructed area in square meters.

    Notes
    -----
    - The function assumes that the input data is cumulative and calculates the difference
      between consecutive years to derive yearly values.
    - Construction is defined as all building conditions except 'demolition'.
    - If no TEK parameters are provided, a default TEK17 range is used.
    """
    if area_forecast is None:
        raise ValueError('Expected area_forecast of type pandas DataFrame. Got «None» instead.')

    expected_columns = ('building_category', 'TEK', 'building_condition', 'year', 'm2')
    missing_columns = [c for c in expected_columns if c not in area_forecast.columns]
    if missing_columns:
        raise ValueError(f'Column {", ".join(missing_columns)} not found in area_forecast')

    tek_params = tek_parameters
    if tek_params is None:
        tek_params = pd.DataFrame(
            data=[['TEK17', 2025, 2020, 2050]],
            columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])
        logger.warning('Using default TEK17 for construction')

    expected_columns = ('TEK', 'building_year', 'period_start_year', 'period_end_year')
    missing_columns = [c for c in expected_columns if c not in tek_params.columns]
    if missing_columns:
        raise ValueError(f'Column {", ".join(missing_columns)} not found in tek_parameters')

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
    """
    Calculate energy use in GWh for construction and demolition activities based on area changes.

    This function filters energy use data for renovation and small measures, aggregates it by
    building category, TEK, and year, and merges it with area change data to compute the
    total energy use in GWh.

    Parameters
    ----------
    energy_use : pandas.DataFrame
        A DataFrame containing energy use data, including columns:
        - 'building_category'
        - 'building_condition'
        - 'TEK'
        - 'year'
        - 'kwh_m2'

    area_change : pandas.DataFrame
        A DataFrame containing area changes due to construction and demolition, including columns:
        - 'building_category'
        - 'TEK'
        - 'year'
        - 'demolition_construction'
        - 'm2'

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the following columns:
        - 'year': Year of the activity.
        - 'demolition_construction': Indicates whether the activity is 'construction' or 'demolition'.
        - 'building_category': Category of the building.
        - 'TEK': TEK classification.
        - 'm2': Area change in square meters.
        - 'gwh': Energy use in gigawatt-hours (GWh), calculated as (kWh/m² * m²) / 1,000,000.

    Notes
    -----
    - Only energy use data with 'building_condition' equal to 'renovation_and_small_measure' is considered.
    - The merge is performed on 'building_category', 'TEK', and 'year'.
    """

    df = energy_use[energy_use['building_condition']=='renovation_and_small_measure']

    energy_use_m2 = df.groupby(by=['building_category', 'building_condition', 'TEK', 'year'], as_index=False).sum()[['building_category',  'TEK', 'year', 'kwh_m2']]

    dem_con = pd.merge(left=area_change, right=energy_use_m2, on=['building_category', 'TEK', 'year'])
    dem_con['gwh'] = (dem_con['kwh_m2'] * dem_con['m2']) / 1_000_000
    return dem_con[['year', 'demolition_construction', 'building_category', 'TEK', 'm2', 'gwh']]


def merge_tek_and_condition(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Add general TEK and building condition categories to area forecast data.

    This function creates a copy of the input DataFrame and assigns the value 'all' to both
    the 'TEK' and 'building_condition' columns. This is useful for aggregating or analyzing
    data across all TEK types and building conditions.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data, including at least the columns
        'TEK' and 'building_condition'.

    Returns
    -------
    pandas.DataFrame
        A modified copy of the input DataFrame where:
        - 'TEK' is set to 'all'
        - 'building_condition' is set to 'all'

    Notes
    -----
    - This function does not modify the original DataFrame in place.
    - Useful for creating aggregate views across all TEK and condition categories.
    """

    all_existing_area = area_forecast.copy()
    all_existing_area.loc[:, 'TEK'] = 'all'
    all_existing_area.loc[:, 'building_condition'] = 'all'

    return all_existing_area


def filter_existing_area(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out demolition entries from area forecast data to retain only existing areas.

    This function removes rows where the building condition is 'demolition' and returns
    a DataFrame containing only the relevant columns for existing building areas.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data, including at least the columns:
        - 'year'
        - 'building_category'
        - 'TEK'
        - 'building_condition'
        - 'm2'

    Returns
    -------
    pandas.DataFrame
        A filtered DataFrame containing only rows where 'building_condition' is not 'demolition',
        with the following columns:
        - 'year'
        - 'building_category'
        - 'TEK'
        - 'building_condition'
        - 'm2'

    Notes
    -----
    - The function returns a copy of the filtered DataFrame to avoid modifying the original.
    - Useful for isolating existing building stock from forecast data.
    """

    existing_area = area_forecast.query('building_condition!="demolition"').copy()
    existing_area = existing_area[['year','building_category','TEK','building_condition']+['m2']]
    return existing_area


def building_condition_scurves(scurve_parameters: pd.DataFrame) -> pd.DataFrame:
    scurves = []

    for r, v in scurve_parameters.iterrows():
        scurve = SCurve(earliest_age=v.earliest_age_for_measure,
                        average_age=v.average_age_for_measure,
                        last_age=v.last_age_for_measure,
                        rush_years=v.rush_period_years,
                        never_share=v.never_share,
                        rush_share=v.rush_share)

        rate = scurve.get_rates_per_year_over_building_lifetime().to_frame().reset_index()
        rate.loc[:, 'building_category'] = v['building_category']
        rate.loc[:, 'building_condition'] = v['condition']

        scurves.append(rate)


    df = pd.concat(scurves).set_index(['building_category', 'age', 'building_condition'])

    return df


def building_condition_accumulated_scurves(scurve_parameters: pd.DataFrame) -> pd.DataFrame:
    scurves = []

    for r, v in scurve_parameters.iterrows():
        scurve = SCurve(earliest_age=v.earliest_age_for_measure,
                        average_age=v.average_age_for_measure,
                        last_age=v.last_age_for_measure,
                        rush_years=v.rush_period_years,
                        never_share=v.never_share,
                        rush_share=v.rush_share)

        acc = scurve.calc_scurve().to_frame().reset_index()
        acc.loc[:, 'building_category'] = v['building_category']
        acc.loc[:, 'building_condition'] = v['condition'] + '_acc'

        scurves.append(acc)

    df = pd.concat(scurves).set_index(['building_category', 'age', 'building_condition'])

    return df
