import numpy as np
import pandas as pd


class HolidayHomeEnergy:
    def __init__(self, population_by_year):
        self.population = population_by_year
        pass

    def calculate(self, energy_consumption):
        pass


def sum_holiday_homes(*holiday_homes: pd.Series) -> pd.Series:
    return pd.DataFrame(holiday_homes).sum(axis=0)


def population_over_holiday_homes(population: pd.Series,
                                  holiday_homes: pd.Series) -> pd.Series:
    return population / holiday_homes


def projected_holiday_homes(population: pd.Series,
                            holiday_homes: pd.Series) -> pd.Series:
    return population / holiday_homes.mean()


def electricity_usage_by_holiday_home(
    electricity_usage: pd.Series,
    holiday_homes: pd.Series
) -> pd.Series:
    """

    row (08) 14 Elektrisitet pr fritidsbolig staitsikk (kWh)

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
    if 2019 not in electricity_usage.index:
        raise ValueError('2019 is not in the index of the provided Series')
    if not any(electricity_usage.isna()):
        raise ValueError('Expected empty energy_usage for projection')
    if len(electricity_usage.index) <= 40:
        raise ValueError('Expected at least 40 years in electricity_usage index')
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
                     name='projected_electricity_usage_holiday_homes',
                     index=electricity_usage.index)
