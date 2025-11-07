import pandas as pd
from loguru import logger

from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.scurve import SCurve


def transform_area_forecast_to_area_change(area_forecast: pd.DataFrame,
                                           building_code_parameters: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Transform area forecast data into yearly area changes due to construction and demolition.

    This function processes forecasted area data and optional building_code parameters to compute
    the net yearly area change. It distinguishes between construction (positive area change)
    and demolition (negative area change), and returns a combined DataFrame.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data, including construction and demolition.

    building_code_parameters : pandas.DataFrame, optional
        A DataFrame containing building_code-related parameters used to refine construction data.
        If None, construction is assumed to be of TEK17. (transform_construction_by_year)

    Returns
    -------
    pandas.DataFrame
        A DataFrame with yearly area changes. Columns include:
        - 'building_category': Category of the building.
        - 'building_code': building_code classification.
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
    construction_by_year = transform_construction_by_year(area_forecast, building_code_parameters)
    construction_by_year.loc[:, 'demolition_construction'] = 'construction'

    demolition_by_year = transform_cumulative_demolition_to_yearly_demolition(area_forecast)
    demolition_by_year.loc[:, 'demolition_construction'] = 'demolition'
    demolition_by_year.loc[:, 'm2'] = -demolition_by_year.loc[:, 'm2']

    area_change = pd.concat([
        demolition_by_year[['building_category', 'building_code', 'year', 'demolition_construction', 'm2']],
        construction_by_year.reset_index()[['building_category', 'building_code', 'year', 'demolition_construction', 'm2']],
    ])
    return area_change.fillna(0.0)


def transform_cumulative_demolition_to_yearly_demolition(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Convert accumulated demolition area data to yearly demolition values.

    This function filters the input DataFrame for rows where the building condition is demolition,
    and calculates the yearly change in square meters (m2) by computing the difference between
    consecutive years within each group defined by building category and building_code standard.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data. Must include the columns:
        'building_category', 'building_code', 'year', 'building_condition', and 'm2'.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ['building_category', 'building_code', 'year', 'm2'], where 'm2' represents
        the yearly demolition area (difference from the previous year). Missing values are filled with 0.

    Notes
    -----
    - The function assumes that the input data is cumulative and sorted by year.
    - The first year in each group will have a demolition value of 0.

    """
    if area_forecast is None:
        raise ValueError('Expected area_forecast of type pandas DataFrame. Got «None» instead.')
    expected_columns = ('building_category', 'building_code', 'building_condition', 'year', 'm2')
    missing_columns = [c for c in expected_columns if c not in area_forecast.columns]
    if missing_columns:
        columns_str = ", ".join(missing_columns)
        raise ValueError('Column %s not found in area_forecast.', columns_str)

    df = area_forecast[area_forecast['building_condition'] == BuildingCondition.DEMOLITION].copy()
    df = df.set_index(['building_category', 'building_code', 'building_condition', 'year']).sort_index()
    df['m2'] = df['m2'].fillna(0)
    df['diff'] = df.groupby(by=['building_category', 'building_code', 'building_condition']).diff()['m2']

    return df.reset_index()[['building_category', 'building_code', 'year', 'diff']].rename(columns={'diff': 'm2'})


def transform_construction_by_year(area_forecast: pd.DataFrame,
                                   building_code_parameters: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Calculate yearly constructed building area based on building_code parameters.

    This function filters the input forecast data to include only construction (non-demolition)
    within the building_code-defined construction period. It then calculates the yearly change in constructed
    area (m2) for each combination of building category and building_code standard.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data. Must include the columns:
        'building_category', 'building_code', 'year', 'building_condition', and 'm2'.

    building_code_parameters : pandas.DataFrame or None, optional
        A DataFrame containing building_code construction period definitions with columns:
        ['building_code', 'building_year', 'period_start_year', 'period_end_year'].
        If None, a default TEK17 period is used (2020-2050 with building year 2025).

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns ['building_category', 'building_code', 'year', 'm2'], where 'm2' represents
        the yearly constructed area in square meters.

    Notes
    -----
    - The function assumes that the input data is cumulative and calculates the difference
      between consecutive years to derive yearly values.
    - Construction is defined as all building conditions except 'demolition'.
    - If no building_codeparameters are provided, a default TEK17 range is used.

    """
    if area_forecast is None:
        raise ValueError('Expected area_forecast of type pandas DataFrame. Got «None» instead.')

    expected_columns = ('building_category', 'building_code', 'building_condition', 'year', 'm2')
    missing_columns = [c for c in expected_columns if c not in area_forecast.columns]
    if missing_columns:
        raise ValueError('Column % not found in area_forecast', ", ".join(missing_columns))

    building_code_params = building_code_parameters
    if building_code_params is None:
        building_code_params = pd.DataFrame(
            data=[['TEK17', 2025, 2020, 2050]],
            columns=['building_code', 'building_year', 'period_start_year', 'period_end_year'])
        logger.warning('Using default TEK17 for construction')

    expected_columns = ('building_code', 'building_year', 'period_start_year', 'period_end_year')
    missing_columns = [c for c in expected_columns if c not in building_code_params.columns]
    if missing_columns:
        raise ValueError('Column %s not found in building_code_parameters', ", ".join(missing_columns))

    area_forecast = area_forecast.merge(building_code_params, on='building_code', how='left')
    constructed = area_forecast.query(
        'period_end_year >= year and building_condition!="demolition"').copy()
    constructed = constructed[['building_category', 'building_code', 'year', 'building_condition', 'm2']]
    constructed = constructed.set_index(['building_category', 'building_code', 'year', 'building_condition'])[['m2']].unstack()  # noqa: PD010

    constructed['total'] = constructed.sum(axis=1)

    constructed=constructed.groupby(by=['building_category', 'building_code'], as_index=False).diff()
    constructed = constructed.reset_index()[['building_category', 'building_code', 'year', 'total']]
    constructed.columns = ['building_category', 'building_code', 'year', 'm2']
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
        - 'building_code'
        - 'year'
        - 'kwh_m2'

    area_change : pandas.DataFrame
        A DataFrame containing area changes due to construction and demolition, including columns:
        - 'building_category'
        - 'building_code'
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
        - 'building_code': building_codeclassification.
        - 'm2': Area change in square meters.
        - 'gwh': Energy use in gigawatt-hours (GWh), calculated as (kWh/m² * m²) / 1,000,000.

    Notes
    -----
    - Only energy use data with 'building_condition' equal to 'renovation_and_small_measure' is considered.
    - The merge is performed on 'building_category', 'building_code', and 'year'.

    """
    df = energy_use[energy_use['building_condition']=='renovation_and_small_measure']

    energy_use_m2 = (df
        .groupby(by=['building_category', 'building_condition', 'building_code', 'year'], as_index=False)
        .sum()[['building_category',  'building_code', 'year', 'kwh_m2']]
    )

    dem_con = pd.merge(left=area_change, right=energy_use_m2, on=['building_category', 'building_code', 'year'])  # noqa: PD015
    dem_con['gwh'] = (dem_con['kwh_m2'] * dem_con['m2']) / 1_000_000
    return dem_con[['year', 'demolition_construction', 'building_category', 'building_code', 'm2', 'gwh']]


def merge_building_code_and_condition(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Add general building_codeand building condition categories to area forecast data.

    This function creates a copy of the input DataFrame and assigns the value 'all' to both
    the 'building_code' and 'building_condition' columns. This is useful for aggregating or analyzing
    data across all building_codetypes and building conditions.

    Parameters
    ----------
    area_forecast : pandas.DataFrame
        A DataFrame containing forecasted building area data, including at least the columns
        'building_code' and 'building_condition'.

    Returns
    -------
    pandas.DataFrame
        A modified copy of the input DataFrame where:
        - 'building_code' is set to 'all'
        - 'building_condition' is set to 'all'

    Notes
    -----
    - This function does not modify the original DataFrame in place.
    - Useful for creating aggregate views across all building_codeand condition categories.

    """
    all_existing_area = area_forecast.copy()
    all_existing_area.loc[:, 'building_code'] = 'all'
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
        - 'building_code'
        - 'building_condition'
        - 'm2'

    Returns
    -------
    pandas.DataFrame
        A filtered DataFrame containing only rows where 'building_condition' is not 'demolition',
        with the following columns:
        - 'year'
        - 'building_category'
        - 'building_code'
        - 'building_condition'
        - 'm2'

    Notes
    -----
    - The function returns a copy of the filtered DataFrame to avoid modifying the original.
    - Useful for isolating existing building stock from forecast data.

    """
    existing_area = area_forecast.query('building_condition!="demolition"').copy()
    existing_area = existing_area[['year','building_category','building_code','building_condition','m2']]
    return existing_area


def building_condition_scurves(scurve_parameters: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate yearly rate for building_condition s-curves for building_category, building_code and year.

    Parameters
    ----------
    scurve_parameters : pd.DataFrame
        Scurve parameters as define in the scurve.csv.

    Returns
    -------
    pd.DataFrame
        Yearly accumulated scurves by building_category, building_code, and building_code

    """
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
    """
    Calculate accumulated building_condition s-curves for building_category, building_code and year.

    Parameters
    ----------
    scurve_parameters : pd.DataFrame
        Scurve parameters as define in the scurve.csv.

    Returns
    -------
    pd.DataFrame
        Yearly accumulated scurves by building_category, building_code, and building_code

    """
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


def multiply_s_curves_with_floor_area(s_curves_by_condition: pd.DataFrame, with_area: pd.DataFrame) -> pd.DataFrame:
    """
    Multiply existing area with s_curves_by_condition to figure out building condition by year.

    Parameters
    ----------
    s_curves_by_condition : pd.DataFrame
        s_curves dataframe with building_category, building_condition and year.
    with_area :
        Total floor area for building_category and building_code.

    Returns
    -------
    pd.DataFrame
        yearly floor area for each building_category, building_code and building_condition

    """
    floor_area_by_condition = s_curves_by_condition.multiply(with_area['area'], axis=0)
    floor_area_forecast = floor_area_by_condition.stack().reset_index()  # noqa: PD013
    floor_area_forecast = floor_area_forecast.rename(columns={'level_3': 'building_condition', 0: 'm2'})  # m²
    return floor_area_forecast


def merge_total_area_by_year(construction_by_building_category_yearly: pd.Series, existing_area: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Constructed area with existing area.

    Parameters
    ----------
    construction_by_building_category_yearly : pd.Series
        Floor area constructed by year with columns building_category, year.
    existing_area : pd.DataFrame
        Existing area by year with columns building_category, year.

    Returns
    -------
    pd.DataFrame
        Dataframe with constructed and existing area

    """
    total_area_by_year = pd.concat([existing_area.drop(columns=['year_r'], errors='ignore'),
                                    construction_by_building_category_yearly])
    return total_area_by_year


def calculate_existing_area(area_parameters: pd.DataFrame,
                            building_code_parameters: pd.DataFrame,
                            years: YearRange) -> pd.DataFrame:
    """
    Calculate the existing building area over a range of years based on area parameters and building codes.

    Parameters
    ----------
    area_parameters : pd.DataFrame
        A DataFrame indexed by 'building_category' and 'building_code', containing area-related data.
    building_code_parameters : pd.DataFrame
        A DataFrame containing at least a 'building_code' column, used to define valid codes.
    years : YearRange
        A sequence of years (e.g., list, range, or array-like) over which to compute the existing area.

    Returns
    -------
    pd.DataFrame
        A DataFrame indexed by ['building_category', 'building_code', 'year'] with merged area data,
        including all combinations of categories, codes, and years.

    """
    index = pd.MultiIndex.from_product(
        iterables=[area_parameters.index.get_level_values(level='building_category').unique(), building_code_parameters.building_code.unique(), years],
        names=['building_category', 'building_code', 'year'])
    # Reindex the DataFrame to include all combinations, filling missing values with NaN
    area = index.to_frame().set_index(['building_category', 'building_code', 'year']).reindex(index).reset_index()
    # Optional: Fill missing values with a default, e.g., 0
    existing_area = pd.merge(left=area_parameters, right=area, on=['building_category', 'building_code'], suffixes=('_r', ''))  # noqa: PD015
    existing_area = existing_area.set_index(['building_category', 'building_code', 'year'])
    return existing_area


def construction_with_building_code(building_category_demolition_by_year: pd.Series,
                                    building_code: pd.DataFrame,
                                    construction_floor_area_by_year: pd.DataFrame,
                                    years:YearRange) -> pd.Series:
    """
    Merge building_category demolition floor area by year with building_code.

    Parameters
    ----------
    building_category_demolition_by_year : pd.Series
        floor area demolished by year
    building_code : pd.DataFrame
        building_code_parameters dataframe
    construction_floor_area_by_year : pd.DataFrame
        floor area constructed by building_category and year
    years : YearRange
        period years

    Returns
    -------
    pd.Series
        Merged building_category demolition floor area by year with building_code

    """
    if not years:
        years = YearRange.from_series(building_category_demolition_by_year)

    building_code_years = years.cross_join(building_code)

    filtered_building_code_years = building_code_years.query(f'period_end_year>={years.start}')

    construction_with_building_code = pd.merge( # noqa: PD015 = pd.merge
        left=construction_floor_area_by_year,
        right=filtered_building_code_years[['year', 'building_code', 'period_start_year', 'period_end_year']],
        left_on=['year'], right_on=['year'])

    query_period_start_end = 'period_start_year > year or period_end_year < year'
    construction_with_building_code.loc[
        construction_with_building_code.query(query_period_start_end).index, 'constructed_floor_area'] = 0.0

    df = construction_with_building_code.set_index(['building_category', 'building_code', 'year'])[['constructed_floor_area']]

    s = df.groupby(by=['building_category', 'building_code'])['constructed_floor_area'].cumsum()
    s.name = 'area'

    return s


def sum_building_category_demolition_by_year(demolition_by_year: pd.Series) -> pd.Series:
    """
    Return sum of demolition by building_category and year.

    Parameters
    ----------
    demolition_by_year : pd.Series
        Yearly demolition with building_category, year and optional column building_code

    Returns
    -------
    pd.Series
        Demolished floor area by building_category and year

    """
    demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()
    return demolition_by_building_category_year


def calculate_demolition_floor_area_by_year(
        area_parameters: pd.DataFrame, s_curve_demolition: pd.Series,
        years: YearRange = YearRange(2020, 2050)) -> pd.Series: # noqa: B008 = function call in argument default
    """
    Calculate the demolition floor area by year multiplying area parameters and the S-curve.

    Parameters
    ----------
    area_parameters : pandas.DataFrame
        A multi-indexed DataFrame containing floor area data. Expected to include an 'area' column.
        The index should include year information to filter between 2020 and 2050.

    s_curve_demolition : pandas.Series
        A Series representing the demolition S-curve values indexed by year.

    years : YearRange
        YearRange of all years that will to present in demolition_by_year

    Returns
    -------
    pandas.Series
        A Series named 'demolition' representing the calculated demolition floor area
        for each year between 2020 and 2050.

    """
    demolition_by_year = area_parameters.loc[:, 'area'] * s_curve_demolition.loc[:]
    demolition_by_year.name = 'demolition'

    demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(years.start, years.end))]
    return demolition_by_year.demolition


def calculate_commercial_construction(population: pd.Series,
                                      area_by_person: float | pd.Series,
                                      demolition: pd.Series) -> pd.DataFrame:
    """
    Calculate a projection of constructed floor area by using population and floor_area_by_person.

    Parameters
    ----------
    population : pd.Series
        population by year
    area_by_person : pd.Series
        float or pd.Series containing the floor area per person for the building_category
    demolition : pd.Series
        yearly demolition to be added to the floor area.

    Returns
    -------
    pd.Dataframe
        floor area constructed by year
        accumulated contracted floor area

    """
    if not demolition.index.isin(population.index).all():
        raise ValueError('years in demolition series not present in popolutation series')

    total_area = area_by_person * population.loc[demolition.index]
    demolition_prev_year = demolition.shift(periods=1, fill_value=0)
    yearly_constructed = total_area.diff().fillna(0) + demolition_prev_year
    yearly_constructed.loc[2020] = 0.0

    accumulated_constructed = yearly_constructed.cumsum()
    commercial_construction = pd.DataFrame({
        'demolished_floor_area': demolition,
        'net_constructed_floor_area': total_area.diff().fillna(0),
        "constructed_floor_area": yearly_constructed,
        "accumulated_constructed_floor_area": accumulated_constructed,
    })
    return commercial_construction
