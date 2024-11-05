import numpy as np
import pandas as pd

from ebm.model.data_classes import YearRange


class HolidayHomeEnergy:
    def __init__(self, population_by_year):
        self.population = population_by_year
        pass

    def calculate(self, energy_consumption):
        pass


def calculate_projected_electricity_usage(usage: pd.Series, homes: pd.Series, population: pd.Series) -> pd.Series:
    holiday_homes_by_year = sum_holiday_homes(homes.iloc[:, 0], homes.iloc[:, 1])
    holiday_homes_by_population = population_over_holiday_homes(population, holiday_homes_by_year)
    projected_holiday_homes_by_year = projected_holiday_homes(population, holiday_homes_by_population)

    usage_by_homes = electricity_usage_by_holiday_home(usage, holiday_homes_by_year)
    padded_usage = pd.concat([usage_by_homes, pd.Series({y: np.nan for y in YearRange(2024, 2050)})])
    projected_electricity_usage = projected_electricity_usage_holiday_homes(padded_usage)

    projected_electricity_usage_gwh = projected_holiday_homes_by_year * projected_electricity_usage / 1_000_000
    projected_electricity_usage_gwh.name = 'gwh'

    return projected_electricity_usage_gwh


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
        A pandas Series with with np.nan values in electricity usage replaced by projected energy use. Years with
            values in energy_usage has a projected usage of np.nan

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

    first_range = [electricity_usage[2019] + (i * 75) for i in range(1, 6)]

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
