import logging
import typing

import numpy as np
import pandas as pd

from ebm.model import DatabaseManager
from ebm.model.data_classes import YearRange


class HolidayHomeEnergy:
    def __init__(self,
                 population: pd.Series,
                 holiday_homes_by_category: pd.DataFrame,
                 electricity_usage_stats: pd.Series,
                 fuelwood_usage_stats: pd.Series,
                 fossil_fuel_usage_stats: pd.Series):
        self.population = population
        self.fossil_fuel_usage_stats = fossil_fuel_usage_stats
        self.fuelwood_usage_stats = fuelwood_usage_stats
        self.electricity_usage_stats = electricity_usage_stats
        self.holiday_homes_by_category = holiday_homes_by_category

    def calculate_energy_usage(self) -> typing.Iterable[pd.Series]:
        """
        Calculate projected energy usage for holiday homes.

        This method projects future energy usage for electricity, fuelwood, and fossil fuels
        based on historical data and combines these projections with existing statistics.

        Yields
        ------
        Iterable[pd.Series]
            A series of projected energy usage values for electricity, fuelwood, and fossil fuels,
            with NaN values filled from the existing statistics.
        """
        electricity_projection = project_electricity_usage(self.electricity_usage_stats,
                                                           self.holiday_homes_by_category,
                                                           self.population)
        yield electricity_projection.combine_first(self.electricity_usage_stats)

        fuelwood_projection = project_fuelwood_usage(self.fuelwood_usage_stats,
                                                     self.holiday_homes_by_category,
                                                     self.population)
        yield fuelwood_projection.combine_first(self.fuelwood_usage_stats)

        fossil_fuel_projection = project_fossil_fuel_usage(self.fossil_fuel_usage_stats,
                                                           self.holiday_homes_by_category,
                                                           self.population)
        yield fossil_fuel_projection

    @staticmethod
    def new_instance(database_manager: DatabaseManager = None) -> 'HolidayHomeEnergy':
        dm = database_manager or DatabaseManager()
        logging.warning('Loading holiday_homes from hard coded data')
        holiday_homes = holiday_homes_by_category = pd.DataFrame(data={
            'chalet': {2001: 354060, 2002: 358997, 2003: 363889, 2004: 368933, 2005: 374470, 2006: 379169,
                       2007: 383112, 2008: 388938, 2009: 394102, 2010: 398884, 2011: 405883, 2012: 410333,
                       2013: 413318, 2014: 416621, 2015: 419449, 2016: 423041, 2017: 426932, 2018: 431028,
                       2019: 434809, 2020: 437833, 2021: 440443, 2022: 445715, 2023: 449009}.values(),
            'converted': {2001: 23267, 2002: 26514, 2003: 26758, 2004: 26998, 2005: 27376, 2006: 27604, 2007: 27927,
                          2008: 28953, 2009: 29593, 2010: 30209, 2011: 32374, 2012: 32436, 2013: 32600, 2014: 32539,
                          2015: 32559, 2016: 32727, 2017: 32808, 2018: 32891, 2019: 32869, 2020: 32906, 2021: 33099,
                          2022: 33283, 2023: 32819}.values()}, index=YearRange(2001, 2023).to_index())
        logging.warning('Loading electricity_usage_stats from hard coded data')
        # 02 Elektrisitet i fritidsboliger statistikk (GWh) (input)
        electricity_usage_stats = pd.Series(
            data=[1128.0, 1173.0, 1183.0, 1161.0, 1235.0, 1317.0, 1407.0, 1522.0, 1635.0, 1931.0, 1818.0, 1929.0,
                  2141.0, 2006.0, 2118.0, 2278.0, 2350.0, 2417.0, 2384.0, 2467.0, 2819.0, 2318.0, 2427.0],
            index=YearRange(2001, 2023).to_index(), name='gwh')
        logging.warning('Loading fuelwood_usage_stats from hard coded data')
        # 04 Ved i fritidsboliger statistikk (GWh)
        fuelwood_usage_stats = pd.Series(
            data=[880.0, 1050.0, 1140.0, 1090.0, 1180.0, 990.0, 700.0, 1000.0, 900.0, 1180.0, 1100.0, 1070.0,
                  1230.0, 1170.0, 1450.0, 1270.0, 1390.0, 1390.0], index=YearRange(2006, 2023).to_index())
        logging.warning('Loading fossil_fuel_usage_stats from hard coded data')
        fossil_fuel_usage_stats=pd.Series(data=[100], index=YearRange(2011, 2011).to_index(), name='kwh')
        return HolidayHomeEnergy(dm.get_construction_population()['population'],
                                 holiday_homes,
                                 electricity_usage_stats,
                                 fuelwood_usage_stats,
                                 fossil_fuel_usage_stats)


def project_electricity_usage(electricity_usage_stats: pd.Series,
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


def project_fuelwood_usage(fuelwood_usage_stats: pd.Series,
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


def project_fossil_fuel_usage(fossil_fuel_usage_stats: pd.Series,
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
        msg = 'The required year 2019 is not in the index of electricity_usage for the electricity projection'
        raise ValueError(msg)
    if not any(electricity_usage.isna()):
        raise ValueError('Expected empty energy_usage for projection')
    if len(electricity_usage.index) <= 40:
        raise ValueError('At least 41 years of electricity_usage is required to predict future electricity use')
    left_pad_len = len(electricity_usage) - electricity_usage.isna().sum()

    initial_e_u = electricity_usage[2019]
    first_range = [initial_e_u + (i * 75) for i in range(1, 6)]

    second_range = [first_range[-1] + (i * 50) for i in range(1, 5)]

    third_range = [second_range[-1] + (i * 25) for i in range(1, 9)]

    right_pad_len = len(electricity_usage) - left_pad_len - len(first_range) - len(second_range) - len(third_range)
    right_padding = [third_range[-1]] * right_pad_len

    return pd.Series(([np.nan] * left_pad_len) +
                     first_range +
                     second_range +
                     third_range +
                     right_padding,
                     name='projected_electricity_usage_kwh',
                     index=electricity_usage.index)


if __name__ == '__main__':
    holiday_home_energy = HolidayHomeEnergy.new_instance()
    for energy_usage, h in zip(holiday_home_energy.calculate_energy_usage(), ['electricity', 'fuelwood', 'fossil fuel']):
        print('====', h, '====')
        print(energy_usage)