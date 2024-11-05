import numpy as np
import pandas as pd

from ebm.model.data_classes import YearRange


class HolidayHomeEnergy:
    def __init__(self, population_by_year):
        self.population = population_by_year
        pass

    def calculate(self, energy_consumption):
        pass


def calculate_projected_electricity_usage(electricity_usage_stats: pd.Series,
                                          holiday_homes_by_category: pd.DataFrame,
                                          population: pd.Series) -> pd.Series:
    """
    Calculate the projected electricity usage for holiday homes.

    This function projects the future electricity usage for holiday homes based on historical
    electricity usage statistics, the number of holiday homes by category, and population data.

    Population is used to work out what years are needed in the projection.

    Parameters
    ----------
    electricity_usage_stats : pd.Series
        A pandas Series containing historical electricity usage statistics.
    holiday_homes_by_category : pd.DataFrame
        A pandas DataFrame containing the number of holiday homes by year. Each column is considered as a category.
    population : pd.Series
        A pandas Series containing population data.

    Returns
    -------
    pd.Series
        A pandas Series with the projected electricity usage in gigawatt-hours (GWh) for future years.

    Raises
    ------
    ValueError
        If the input Series do not meet the expected criteria.
    """
    total_holiday_homes_by_year = sum_holiday_homes(holiday_homes_by_category.iloc[:, 0],
                                                    holiday_homes_by_category.iloc[:, 1])

    people_per_holiday_home = population_over_holiday_homes(population, total_holiday_homes_by_year)
    projected_holiday_homes_by_year = projected_holiday_homes(population, people_per_holiday_home)

    usage_by_homes = electricity_usage_by_holiday_home(electricity_usage_stats, total_holiday_homes_by_year)
    nan_padded_usage_by_homes = usage_by_homes.reindex(population.index, fill_value=np.nan)
    projected_electricity_usage = projected_electricity_usage_holiday_homes(nan_padded_usage_by_homes)

    projected_electricity_usage_gwh = projected_holiday_homes_by_year * projected_electricity_usage / 1_000_000
    projected_electricity_usage_gwh.name = 'gwh'

    return projected_electricity_usage_gwh


def calculate_projected_fuelwood_usage(fuelwood_usage_stats: pd.Series,
                                       holiday_homes_by_category: pd.DataFrame,
                                       population: pd.Series) -> pd.Series:
    total_holiday_homes_by_year = sum_holiday_homes(holiday_homes_by_category.iloc[:, 0],
                                                    holiday_homes_by_category.iloc[:, 1])

    people_per_holiday_home = population_over_holiday_homes(population, total_holiday_homes_by_year)
    projected_holiday_homes_by_year = projected_holiday_homes(population, people_per_holiday_home)

    usage_by_homes = calculate_fuelwood_by_holiday_home(fuelwood_usage_stats, total_holiday_homes_by_year)
    nan_padded_usage_by_homes = usage_by_homes.reindex(population.index, fill_value=np.nan)
    projected_fuelwood_usage = projected_fuelwood_usage_holiday_homes(nan_padded_usage_by_homes)

    projected_fuelwood_usage_gwh = projected_holiday_homes_by_year * projected_fuelwood_usage / 1_000_000
    projected_fuelwood_usage_gwh.name = 'gwh'

    return projected_fuelwood_usage_gwh


def calculate_projected_fossil_fuel_usage(fossil_fuel_usage_stats: pd.Series,
                                       holiday_homes_by_category: pd.DataFrame,
                                       population: pd.Series) -> pd.Series:
    projection = fossil_fuel_usage_stats.reindex(population.index, fill_value=np.nan)

    not_na = projection.loc[~projection.isna()].index
    projection_filter = projection.index > max(not_na)
    projection.loc[projection_filter] = projection.loc[not_na].mean()
    projection.name = 'gwh'
    return projection


def sum_holiday_homes(*holiday_homes: pd.Series) -> pd.Series:
    return pd.DataFrame(holiday_homes).sum(axis=0)


def population_over_holiday_homes(population: pd.Series,
                                  holiday_homes: pd.Series) -> pd.Series:
    """
    Average number of holiday homes by population.

    Parameters
    ----------
    population : pd.Series
    holiday_homes : pd.Series

    Returns
    -------
    pd.Series

    """
    return population / holiday_homes


def projected_holiday_homes(population: pd.Series,
                            holiday_homes: pd.Series) -> pd.Series:
    """
    Projects future number of holiday homes based on the population and historical average number of holiday homes

    Parameters
    ----------
    population : pd.Series
        population in every year of the projection
    holiday_homes : pd.Series
        historical number of holiday homes
    Returns
    -------
    pd.Series
        population over average number of holiday homes
    """
    return population / holiday_homes.mean()


def electricity_usage_by_holiday_home(
    electricity_usage: pd.Series,
    holiday_homes: pd.Series
) -> pd.Series:
    """

    (08) 14 Elektrisitet pr fritidsbolig staitsikk (kWh) in Energibruk fritidsboliger.xlsx

    Parameters
    ----------
    electricity_usage : pd.Series
        Electricity usage by year from SSB https://www.ssb.no/statbank/sq/10103348 2001 - 2023
    holiday_homes : pd.Series
        Total number of holiday homes of any category from SSB https://www.ssb.no/statbank/sq/10103336
    Returns
    -------

    """
    s = electricity_usage * 1_000_000 / holiday_homes
    s.name = 'kwh'
    return s


def calculate_fuelwood_by_holiday_home(
    fuelwood_usage: pd.Series,
    holiday_homes: pd.Series
) -> pd.Series:
    """

    (10) 16 Ved pr fritidsbolig statistikk (kWh) 2019 - 2023

    Parameters
    ----------
    fuelwood_usage : pd.Series
        Electricity usage by year from SSB https://www.ssb.no/statbank/sq/10103505 2006 - 2023
    holiday_homes : pd.Series
        Total number of holiday homes of any category from SSB https://www.ssb.no/statbank/sq/10103336
    Returns
    -------
    pd.Series
        Named kwh like fuelwood_usage * 1_000_000 / holiday_homes
    """
    s = fuelwood_usage * 1_000_000 / holiday_homes
    s.name = 'kwh'
    return s


def projected_fuelwood_usage_holiday_homes(historical_fuelwood_usage: pd.Series) -> pd.Series:
    """
    Projects future fuelwood usage for holiday homes based on historical data. The projection
        is calculated as the mean of the last 5 years of historical_fuelwood_usage.

    Parameters
    ----------
    historical_fuelwood_usage : pd.Series

    Returns
    -------
    pd.Series
        A pandas Series with with NaN values in fuelwood usage replaced by projected use. Years present
            in historical_fuelwood_usage is returned as NaN
    """
    projected_fuelwood_usage = pd.Series(data=[np.nan] * len(historical_fuelwood_usage),
                                         index=historical_fuelwood_usage.index)

    not_na = historical_fuelwood_usage.loc[~historical_fuelwood_usage.isna()].index
    average = historical_fuelwood_usage.loc[not_na].iloc[-5:].mean()
    projection_filter = projected_fuelwood_usage.index > max(not_na)
    projected_fuelwood_usage.loc[projection_filter] = average
    return projected_fuelwood_usage


def projected_electricity_usage_holiday_homes(electricity_usage: pd.Series):
    """
    Project future electricity usage for holiday homes based on historical data.

    This function projects future electricity usage by creating three ranges of projections
    and padding the series with NaN values and the last projection value as needed.

    15 (09) Elektrisitet pr fritidsbolig framskrevet (kWh) in Energibruk fritidsboliger.xlsx

    Parameters
    ----------
    electricity_usage : pd.Series
        A pandas Series containing historical electricity usage data. The index should include the year 2019,
        and the Series should contain at least 40 years of data with some NaN values for projection.

    Returns
    -------
    pd.Series
        A pandas Series with with NaN values in electricity usage replaced by projected energy use. Years with
            values in energy_usage has a projected usage of NaN

    Raises
    ------
    ValueError
        If the year 2019 is not in the index of the provided Series.
        If there are no NaN values in the provided Series.
        If the length of the Series is less than or equal to 40.
    """
    if 2019 not in electricity_usage.index:
        raise ValueError('2019 is not in the index of the provided Series')
    if not any(electricity_usage.isna()):
        raise ValueError('Expected empty energy_usage for projection')
    if len(electricity_usage.index) <= 40:
        raise ValueError('Expected at least 41 years in electricity_usage index')
    left_padding = len(electricity_usage) - electricity_usage.isna().sum()

    initial_e_u = electricity_usage[2019]
    first_range = [initial_e_u + (i * 75) for i in range(1, 6)]

    second_range = [first_range[-1] + (i * 50) for i in range(1, 5)]

    third_range = [second_range[-1] + (i * 25) for i in range(1, 9)]

    right_pad_len = len(electricity_usage) - left_padding - len(first_range) - len(second_range) - len(third_range)
    right_padding = [third_range[-1]] * right_pad_len

    return pd.Series(([np.nan] * left_padding) +
                     first_range +
                     second_range +
                     third_range +
                     right_padding,
                     name='projected_electricity_usage_kwh',
                     index=electricity_usage.index)
