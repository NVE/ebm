import itertools
from typing import Union

import numpy as np
import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager


def calculate_construction(building_category: BuildingCategory, demolition_floor_area: Union[pd.Series, list],
                           database_manager: DatabaseManager, period: YearRange) -> pd.DataFrame:
    """
    Calculate constructed floor area for buildings based using provided demolition_floor_area and input data from database_manager.

    Parameters.
    ----------

    building_category: BuildingCategory
    demolition_floor_area: pd.Series expects index=2010..2050
    database_manager: DatabaseManager
    period : YearRange

    Raises
    -----
    This function always raises NotImplementedError.

    Returns
    -------
    calculated_construction: pd.DataFrame
                                       dataframe columns include;
                                       (building_growth)
                                       (demolished_floor_area)
                                       (constructed_floor_area)
                                       (accumulated_constructed_floor_area)
                                       (total_floor_area)
                                       (floor_area_over_population_growth)
                                       (households)
                                       (household_size)
                                       (population)
                                       (population_growth)


    """
    msg = 'calculate_construction is no longer implemented. Use extractor.calculate_construction instead.'
    raise NotImplementedError(msg)


def calculate_constructed_floor_area(constructed_floor_area: pd.Series, total_floor_area: pd.Series,
                                     period: YearRange) -> pd.Series:
    """
    Calculate the constructed floor area over a specified period.

    Parameters
    ----------
    constructed_floor_area : pd.Series
        A pandas Series to store the constructed floor area for each previous year.
    total_floor_area : pd.Series
        A pandas Series containing the total floor area for each year.
    period : YearRange
        An object containing the start year, end year, and the range of years.

    Returns
    -------
    pd.Series
        A pandas Series containing the constructed floor area for each year in the period.

    Notes
    -----
    The constructed floor area is calculated from year 6 onwards by subtracting the previous year's
    floor area from the current year's floor area and adding the previous year's demolition floor area.

    """
    # Calculate constructed floor area from year 6 by subtracting last year's floor area with current floor area
    # and adding last year's demolition.
    # Calculate constructed floor area from year 6 by substracting last years floor area with current floor area
    #  and adding last years demolition.
    for year in [y for y in period if y not in constructed_floor_area.index and y > period.start]:
        floor_area = total_floor_area.loc[year]
        previous_year_floor_area = total_floor_area.loc[year - 1]
        constructed = floor_area - previous_year_floor_area
        constructed_floor_area[year] = constructed
    constructed_floor_area.name = 'constructed_floor_area'
    constructed_floor_area.index.name = 'year'
    return constructed_floor_area


def calculate_floor_area_growth(total_floor_area: pd.Series, period: YearRange) -> pd.Series:
    """
    Calculate the growth of floor area over a specified period.

    Parameters
    ----------
    total_floor_area : pd.Series
        A pandas Series containing the total floor area for each year.
    period : YearRange
        An object containing the start year, end year, and the range of years.

    Returns
    -------
    pd.Series
        A pandas Series containing the floor area growth for each year in the period.

    Notes
    -----
    The growth for the first year in the period is set to NaN. The growth for the next four years
    is calculated based on the change in total floor area from the previous year.

    Examples
    --------
    >>> total_floor_area = pd.Series({2020: 1000, 2021: 1100, 2022: 1210, 2023: 1331, 2024: 1464})
    >>> period = YearRange(2020, 2024)
    >>> calculate_floor_area_growth(total_floor_area, period)
    2020       NaN
    2021    0.1000
    2022    0.1000
    2023    0.1000
    2024    0.1000
    dtype: float64

    """
    floor_area_growth = pd.Series(data=itertools.repeat(0.0, len(period.year_range)), index=period.year_range)
    floor_area_growth.loc[period.start] = np.nan
    # The next 4 years of building growth is calculated from change in total_floor_area
    for year in range(period.start + 1, period.start + 5):
        if year in total_floor_area.index:
            floor_area_growth.loc[year] = (total_floor_area.loc[year] / total_floor_area.loc[year - 1]) - 1
    return floor_area_growth


def calculate_floor_area_over_building_growth(building_growth: pd.Series,
                                              population_growth: pd.Series,
                                              years: YearRange) -> pd.Series:
    """
    Calculate the floor area over building growth for a given range of years.

    Parameters
    ----------
    building_growth : pd.Series
        A pandas Series representing the building growth over the years.
    population_growth : pd.Series
        A pandas Series representing the population growth over the years.
    years : YearRange
        An object representing the range of years for the calculation.

    Returns
    -------
    pd.Series
        A pandas Series representing the floor area over building growth for each year in the specified range.

    Notes
    -----
    - The first year in the range is initialized with NaN.
    - For the first 4 years, the floor area over building growth is calculated directly from the building and population growth.
    - For the next 5 years, the mean floor area over building growth is used.
    - From the 11th year onwards, the value is set to 1.
    - For the years between the 11th and 21st, the value is interpolated linearly.

    Examples
    --------
    >>> building_growth = pd.Series([1.2, 1.3, 1.4, 1.5, 1.6], index=[2010, 2011, 2012, 2013, 2014])
    >>> pd.Series([1.1, 1.2, 1.3, 1.4, 1.5], index=[2010, 2011, 2012, 2013, 2014])
    >>> years = YearRange(start=2010, end=2050)
    >>> calculate_floor_area_over_building_growth(building_growth, population_growth, years)
    2010         NaN
    2011    1.083333
    2012    1.076923
    2013    1.071429
    2014    1.066667
    2015    1.074588
    2016    1.074588
    …
    2050    1.000000
    2051    1.000000
    dtype: float64

    """
    floor_area_over_population_growth = pd.Series(
        data=[np.nan] + list(itertools.repeat(1, len(years) - 1)),  # noqa: RUF005
        index=years.to_index())

    # Initialize with NaN for the first year
    floor_area_over_population_growth.loc[years.start] = np.nan

    # Calculate for the next 4 years
    for year in building_growth[(building_growth > 0) & (building_growth.index > years.start)].index:
        floor_area_over_population_growth[year] = building_growth.loc[year] / population_growth.loc[year]

    mean_idx = building_growth[building_growth > 0].index

    # If there is no growth, return 0
    if not any(mean_idx):
        return floor_area_over_population_growth

    # Calculate for the next 6 years using the mean
    mean_floor_area_population = floor_area_over_population_growth.loc[mean_idx].mean()
    for year in years.subset(list(years).index(max(mean_idx) + 1), 6):
        floor_area_over_population_growth.loc[year] = mean_floor_area_population

    # Set to 1 from the 11th year onwards
    if len(years) > 11:  # noqa: PLR2004
        for year in years.subset(11):
            floor_area_over_population_growth.loc[year] = 1

        # Interpolate linearly between the 11th and 21st years
        for year in years.subset(11, 10):
            floor_area_over_population_growth.loc[year] = \
                (floor_area_over_population_growth.loc[years.start + 10] - (year - (years.start + 10)) * (
                        (floor_area_over_population_growth.loc[
                             years.start + 10] -
                         floor_area_over_population_growth.loc[
                             years.start + 20]) / 10))
    return floor_area_over_population_growth


def calculate_population_growth(population: pd.Series) -> pd.Series:
    """
    Calculate the annual growth in building categories based on household changes.

    Parameters
    ----------
    population : pd.Series
        A pandas Series representing the population indexed by year.

    Returns
    -------
    pd.Series
        A pandas Series representing the annual growth population.

    """
    population_growth = (population / population.shift(1)) - 1
    population_growth.name = 'population_growth'
    return population_growth


def calculate_total_floor_area(floor_area_over_population_growth: pd.Series,
                               population_growth: pd.Series,
                               total_floor_area: pd.Series,
                               period: YearRange) -> pd.Series:
    """
    Calculate the total floor area over a given period based on population growth.

    Parameters
    ----------
    floor_area_over_population_growth : pd.Series
        A pandas Series containing the floor area change over population growth for each year.
    population_growth : pd.Series
        A pandas Series containing the population growth for each year.
    total_floor_area : pd.Series
        A pandas Series containing the total floor area for each year.
    period : YearRange
        A named tuple containing the start and end years of the period.

    Returns
    -------
    pd.Series
        Updated pandas Series with the total floor area for each year in the given period.

    Notes
    -----
    The calculation starts from `period.start + 5` to `period.end`. For each year, the total floor area is updated
    based on the formula:
        total_floor_area[year] = ((change_ratio * pop_growth) + 1) * previous_floor_area

    """
    calculated_total_floor_area = total_floor_area.copy()

    years_to_update = period.subset(offset=list(period).index(max(total_floor_area.index) + 1), length=-1)
    for year in years_to_update:
        change_ratio = floor_area_over_population_growth.loc[year]
        growth = population_growth.loc[year]
        previous_floor_area = calculated_total_floor_area.loc[year - 1]
        calculated_total_floor_area.loc[year] = ((change_ratio * growth) + 1) * previous_floor_area
    calculated_total_floor_area.name = 'total_floor_area'
    return calculated_total_floor_area
