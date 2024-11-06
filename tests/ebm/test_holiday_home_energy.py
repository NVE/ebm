import numpy as np
import pandas as pd
import pytest

from ebm.holiday_home_energy import sum_holiday_homes, population_over_holiday_homes, projected_holiday_homes, \
    projected_electricity_usage_holiday_homes, electricity_usage_by_holiday_home, \
    projected_electricity_usage_holiday_homes, calculate_projected_electricity_usage
from ebm.model.data_classes import YearRange


def test_sum_holiday_homes():
    category_1 = pd.Series({2001: 11, 2002: 12, 2003: 13, 2004: 14})
    category_2 = pd.Series({2001: 1, 2002: 2, 2003: 3, 2004: 4})
    category_3 = pd.Series({2001: 100, 2002: 200, 2003: 300, 2004: 400})

    result = sum_holiday_homes(category_1, category_2, category_3)
    expected = pd.Series({2001: 112, 2002: 214, 2003: 316, 2004: 418})

    pd.testing.assert_series_equal(result, expected)


def test_population_over_holiday_homes():
    pop = pd.Series(data={2001: 100, 2002: 110})
    homes = pd.Series(data={2001: 10, 2002: 11})
    result = population_over_holiday_homes(population=pop,
                                           holiday_homes=homes)
    expected = pd.Series({2001: 10, 2002: 10.0})

    pd.testing.assert_series_equal(result, expected)


def test_projected_holiday_homes():
    population = pd.Series(data={2004: 200, 2005: 220})
    homes = pd.Series(data={2001: 10, 2002: 11, 2003: 12})
    result = projected_holiday_homes(population=population,
                                     holiday_homes=homes)
    expected = pd.Series({2004: 18.18181818, 2005: 20.0})

    pd.testing.assert_series_equal(result, expected)


def test_electricity_usage_by_holiday_home():
    electricity_usage = pd.Series({2001: 1128, 2002: 1173, 2003: 1183})
    homes = pd.Series(data={2001: 377_327, 2002: 385_511, 2003: 390_647})

    result = electricity_usage_by_holiday_home(electricity_usage, homes)
    expected = pd.Series(data={2001: 2989.449,
                               2002: 3042.715,
                               2003: 3028.309}, name='kwh')

    pd.testing.assert_series_equal(result, expected)


def test_projected_electricity_usage_holiday_homes():
    """
    Tests that the correct projection is returned from projected_electricity_usage_holiday_homes.
    """
    electricity_usage = pd.Series({y: 2.0 if y < 2024 else np.nan for y in range(2001, 2051)}, name='kwh')
    electricity_usage.index.name = 'year'
    # The projection is exclusively calculated from 2019, so it is the only year that really need a sensible value.
    electricity_usage[2019] = 100.0
    result = projected_electricity_usage_holiday_homes(electricity_usage)

    expected = pd.Series(data=[np.nan]*23 +
                              [100.0 + (75 * i) for i in range(1, 6)] +
                              [475.0 + (50 * i) for i in range(1, 5)] +
                              [675.0 + (25 * i) for i in range(1, 9)] +
                              [875.0 for i in range(1, 11)],
                         index=pd.Index([y for y in range(2001, 2051)], name='year'),
                         name='projected_electricity_usage_kwh')

    pd.testing.assert_series_equal(result, expected)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_missing_2019():
    """
    projected_electricity_usage_holiday_homes assumes 2019 in the index. Make sure the assumption is True
    """
    electricity_usage = pd.Series({y: 2.0 if y < 2024 else np.nan for y in range(2020, 2024)})
    with pytest.raises(ValueError, match='2019 is not in the index of the provided Series'):
        projected_electricity_usage_holiday_homes(electricity_usage)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_missing_nan_from_end():
    """
    projected_electricity_usage_holiday_homes use np.nan to figure out where to start the projection.
        Make sure there are np.nan in energy_usage
    """
    electricity_usage = pd.Series({y: y + 0.1 for y in range(2001, 2042)})

    with pytest.raises(ValueError, match='Expected empty energy_usage for projection'):
        projected_electricity_usage_holiday_homes(electricity_usage)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_electricity_usage_is_too_short():
    """
    projected_electricity_usage_holiday_homes assumes at least 41 years in the index
    """
    electricity_usage = pd.Series({y: y + 0.1 if y < 2024 else np.nan for y in range(2001, 2041)})

    with pytest.raises(ValueError, match='Expected at least 41 years in electricity_usage index'):
        projected_electricity_usage_holiday_homes(electricity_usage)


def test_projected_electricity_usage_holiday_homes_using_spreadsheet_data():
    """
    Tests that the correct projection is returned from projected_electricity_usage_holiday_homes when using
        numbers from Energibruk fritidsboliger.xlsx
    """
    usage = [2989.4495, 3042.7147, 3028.3094, 2932.3291, 3073.3166, 3237.678, 3423.0329, 3642.0981, 3858.9079,
             4500.1899, 4148.2509, 4356.6736, 4801.3312, 4466.1145, 4685.7578, 4998.157, 5111.5848, 5209.9612,
             5097.5244, 5240.696, 5953.0094, 4839.2686, 5037.0672] + [np.nan] * 27

    electricity_usage = pd.Series(data=usage, name='kwh', index=YearRange(2001, 2050).to_index())
    electricity_usage.index.name = 'year'
    result = projected_electricity_usage_holiday_homes(electricity_usage)

    expected = pd.Series(
        data=[np.nan] * 23 + [5172.5244, 5247.5244, 5322.5244, 5397.5244, 5472.5244, 5522.5244, 5572.5244, 5622.5244,
                              5672.5244, 5697.5244, 5722.5244, 5747.5244, 5772.5244, 5797.5244, 5822.5244, 5847.5244,
                              5872.5244, 5872.5244, 5872.5244, 5872.5244, 5872.5244, 5872.5244, 5872.5244, 5872.5244,
                              5872.5244, 5872.5244, 5872.5244],
        index=YearRange(2001, 2050).to_index(), name='projected_electricity_usage_kwh')

    pd.testing.assert_series_equal(result, expected)


def test_electricity_usage():
    electricity_usage = None  # 09 Elektrisitet pr fritidsbolig framskrevet (kWh)
    electricity_usage = pd.Series(
        data=[1128.0, 1173.0, 1183.0, 1161.0, 1235.0, 1317.0, 1407.0, 1522.0, 1635.0, 1931.0, 1818.0, 1929.0, 2141.0,
              2006.0, 2118.0, 2278.0, 2350.0, 2417.0, 2384.0, 2467.0, 2819.0, 2318.0, 2427.0],
        index=YearRange(2001, 2023).to_index(), name='gwh')
    population = pd.Series(
        data=[4503436, 4524066, 4552252, 4577457, 4606363, 4640219, 4681134, 4737171, 4799252, 4858199, 4920305,
              4985870, 5051275, 5109056, 5165802, 5213985, 5258317, 5295619, 5328212, 5367580, 5391369, 5425270,
              5488984, 5550203, 5600121, 5638838, 5666689, 5694657, 5722427, 5749712, 5776723, 5803284, 5829350,
              5855072, 5880318, 5905184, 5928866, 5951491, 5973100, 5993766, 6013501, 6032325, 6050194, 6067121,
              6083032, 6097893, 6111684, 6124356, 6135899, 6146321], name='population',
        index=YearRange(2001, 2050).to_index())
    holiday_homes = pd.DataFrame(data={
        'chalet': {2001: 354060, 2002: 358997, 2003: 363889, 2004: 368933, 2005: 374470, 2006: 379169,
                   2007: 383112, 2008: 388938, 2009: 394102, 2010: 398884, 2011: 405883, 2012: 410333,
                   2013: 413318, 2014: 416621, 2015: 419449, 2016: 423041, 2017: 426932, 2018: 431028,
                   2019: 434809, 2020: 437833, 2021: 440443, 2022: 445715, 2023: 449009}.values(),
        'converted': {2001: 23267, 2002: 26514, 2003: 26758, 2004: 26998, 2005: 27376, 2006: 27604, 2007: 27927,
                      2008: 28953, 2009: 29593, 2010: 30209, 2011: 32374, 2012: 32436, 2013: 32600, 2014: 32539,
                      2015: 32559, 2016: 32727, 2017: 32808, 2018: 32891, 2019: 32869, 2020: 32906, 2021: 33099,
                      2022: 33283, 2023: 32819}.values()}, index=YearRange(2001, 2023).to_index())
    # 02 Elektrisitet i fritidsboliger statistikk
    # 16og32 Befolkning (input)
    # 21 Hytter, sommerhus og lignende fritidsbygg (input)

    result = calculate_projected_electricity_usage(electricity_usage, holiday_homes, population)

    expected = pd.Series(
        data=[np.nan] * 23 + [2511.2188, 2570.5439, 2625.309, 2675.4518, 2726.0161, 2764.3374, 2802.6652, 2841.0968,
                         2879.5415, 2905.223, 2930.8463, 2956.3427, 2981.7578, 3006.6811, 3031.1697, 3055.2375,
                         3078.9154, 3089.053, 3098.7227, 3107.9017, 3116.5969, 3124.7702, 3132.404, 3139.4883,
                         3145.9977, 3151.9272, 3157.2808],
        name='gwh',
        index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(result, expected)
