from collections import namedtuple

import numpy as np
import pandas as pd
import pytest

from ebm.holiday_home_energy import (
    HolidayHomeEnergy,
    energy_usage_by_holiday_homes,
    population_over_holiday_homes,
    project_electricity_usage,
    project_fossil_fuel_usage,
    project_fuelwood_usage,
    projected_electricity_usage_holiday_homes,
    projected_fuelwood_usage_holiday_homes,
    projected_holiday_homes,
    sum_holiday_homes,
)
from ebm.model.data_classes import YearRange

Spreadsheet = namedtuple('Spreadsheet',
                         ('population',
                          'holiday_homes_by_category',
                          'electricity_usage_stats',
                          'fuelwood_usage_stats',
                          'fossil_fuel_usage_stats'))


@pytest.fixture()
def spreadsheet() -> Spreadsheet:
    s = Spreadsheet(
        # 16og32 Befolkning (input)
        population=pd.Series(
            data=[4503436, 4524066, 4552252, 4577457, 4606363, 4640219, 4681134, 4737171, 4799252, 4858199, 4920305,
                  4985870, 5051275, 5109056, 5165802, 5213985, 5258317, 5295619, 5328212, 5367580, 5391369, 5425270,
                  5488984, 5550203, 5600121, 5638838, 5666689, 5694657, 5722427, 5749712, 5776723, 5803284, 5829350,
                  5855072, 5880318, 5905184, 5928866, 5951491, 5973100, 5993766, 6013501, 6032325, 6050194, 6067121,
                  6083032, 6097893, 6111684, 6124356, 6135899, 6146321], name='population',
            index=YearRange(2001, 2050).to_index()),
        # 21 Hytter, sommerhus og lignende fritidsbygg (input)
        # 22 Helårsboliger og våningshus benyttet som fritidsbolig (input)
        holiday_homes_by_category=pd.DataFrame(data={
            'chalet': {2001: 354060, 2002: 358997, 2003: 363889, 2004: 368933, 2005: 374470, 2006: 379169, 2007: 383112,
                       2008: 388938, 2009: 394102, 2010: 398884, 2011: 405883, 2012: 410333, 2013: 413318, 2014: 416621,
                       2015: 419449, 2016: 423041, 2017: 426932, 2018: 431028, 2019: 434809, 2020: 437833, 2021: 440443,
                       2022: 445715, 2023: 449009}.values(),
            'converted': {2001: 23267, 2002: 26514, 2003: 26758, 2004: 26998, 2005: 27376, 2006: 27604, 2007: 27927,
                          2008: 28953, 2009: 29593, 2010: 30209, 2011: 32374, 2012: 32436, 2013: 32600, 2014: 32539,
                          2015: 32559, 2016: 32727, 2017: 32808, 2018: 32891, 2019: 32869, 2020: 32906, 2021: 33099,
                          2022: 33283, 2023: 32819}.values()},
            index=YearRange(2001, 2023).to_index()),
        # 02 Elektrisitet i fritidsboliger statistikk (GWh) (input)
        electricity_usage_stats=pd.Series(
            data=[1128.0, 1173.0, 1183.0, 1161.0, 1235.0, 1317.0, 1407.0, 1522.0, 1635.0, 1931.0, 1818.0, 1929.0,
                  2141.0, 2006.0, 2118.0, 2278.0, 2350.0, 2417.0, 2384.0, 2467.0, 2819.0, 2318.0, 2427.0],
            index=YearRange(2001, 2023).to_index(), name='gwh'),
        # 04 Ved i fritidsboliger statistikk (GWh)
        fuelwood_usage_stats=pd.Series(
            data=[880.0, 1050.0, 1140.0, 1090.0, 1180.0, 990.0, 700.0, 1000.0, 900.0, 1180.0, 1100.0, 1070.0, 1230.0,
                  1170.0, 1450.0, 1270.0, 1390.0, 1390.0],
            index=YearRange(2006, 2023).to_index()),
        # XX ingen input, mer hardkodet
        fossil_fuel_usage_stats=pd.Series(data=[100], index=YearRange(2006, 2006).to_index(), name='kwh'))
    return s


def test_holiday_home_energy_call_project_functions(spreadsheet):
    holiday_home_energy = HolidayHomeEnergy(**spreadsheet._asdict())

    projections = holiday_home_energy.calculate_energy_usage()

    projected_electricity_usage = next(projections)
    expected_electricity_usage = pd.Series(
        data=[1128.0, 1173.0, 1183.0, 1161.0, 1235.0, 1317.0, 1407.0, 1522.0, 1635.0, 1931.0, 1818.0, 1929.0, 2141.0,
              2006.0, 2118.0, 2278.0, 2350.0, 2417.0, 2384.0, 2467.0, 2819.0, 2318.0, 2427.0, 2511.2188, 2570.5439,
              2625.309, 2675.4518, 2726.0161, 2764.3374, 2802.6652, 2841.0968, 2879.5415, 2905.223, 2930.8463,
              2956.3427, 2981.7578, 3006.6811, 3031.1697, 3055.2375, 3078.9154, 3089.053, 3098.7227, 3107.9017,
              3116.5969, 3124.7702, 3132.404, 3139.4883, 3145.9977, 3151.9272, 3157.2808], name='gwh',
        index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(projected_electricity_usage, expected_electricity_usage)

    projected_fuelwood_usage = next(projections)
    expected_fuelwood_usage = pd.Series(
        data=[np.nan, np.nan, np.nan, np.nan, np.nan, 880.0, 1050.0, 1140.0, 1090.0, 1180.0, 990.0, 700.0, 1000.0,
              900.0, 1180.0, 1100.0, 1070.0, 1230.0, 1170.0, 1450.0, 1270.0, 1390.0, 1390.0, 1364.2943, 1376.5647,
              1386.0817, 1392.9277, 1399.8025, 1406.6287, 1413.3356, 1419.9752, 1426.5041, 1432.9114, 1439.2341,
              1445.4398, 1451.5521, 1457.3734, 1462.9349, 1468.2466, 1473.3265, 1478.1775, 1482.8047, 1487.197,
              1491.3579, 1495.2689, 1498.9219, 1502.3119, 1505.4268, 1508.2642, 1510.826], name='gwh',
        index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(projected_fuelwood_usage, expected_fuelwood_usage)

    projected_fossil_fuel_usage = next(projections)
    expected_fossil_fuel_usage = pd.Series(
        data=[np.nan] * 5 + [100.0] * 45, name='gwh', index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(projected_fossil_fuel_usage, expected_fossil_fuel_usage)


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

    result = energy_usage_by_holiday_homes(electricity_usage, homes)
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
                              [875.0 for _ in range(1, 11)],
                         index=pd.Index([y for y in range(2001, 2051)], name='year'),
                         name='projected_electricity_usage_kwh')

    pd.testing.assert_series_equal(result, expected)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_missing_2019():
    """
    projected_electricity_usage_holiday_homes assumes 2019 in the index. Make sure the assumption is True
    """
    expected = 'The required year 2019 is not in the index of electricity_usage for the electricity projection'
    electricity_usage = pd.Series({y: 2.0 if y < 2024 else np.nan for y in range(2020, 2024)})
    with pytest.raises(
            ValueError,
            match=expected):
        projected_electricity_usage_holiday_homes(electricity_usage)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_missing_nan_from_end():
    """
    projected_electricity_usage_holiday_homes use np.nan to figure out where to start the projection.
        Make sure there are NaN in energy_usage
    """
    electricity_usage = pd.Series({y: y + 0.1 for y in range(2001, 2042)})

    with pytest.raises(ValueError, match='Expected empty energy_usage for projection'):
        projected_electricity_usage_holiday_homes(electricity_usage)


def test_projected_electricity_usage_holiday_homes_raise_value_error_when_electricity_usage_is_too_short():
    """
    projected_electricity_usage_holiday_homes assumes at least 41 years in the index
    """
    electricity_usage = pd.Series({y: y + 0.1 if y < 2024 else np.nan for y in range(2001, 2041)})

    msg = 'At least 41 years of electricity_usage is required to predict future electricity use'
    with pytest.raises(ValueError, match=msg):
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


def test_calculate_fuelwood_by_holiday_home():
    """ Calculate fuel wood by holiday using spreadsheet data """
    years = YearRange(2006, 2023).to_index()
    holiday_homes = pd.Series(data=[406773, 411039, 417891, 423695, 429093, 438257, 442769, 445918, 449160, 452008,
                                    455768, 459740, 463919, 467678, 470739, 473542, 478998, 481828],
                              index=years)
    fuelwood_usage = pd.Series(
        data=[880.0, 1050.0, 1140.0, 1090.0, 1180.0, 990.0, 700.0, 1000.0, 900.0, 1180.0, 1100.0, 1070.0, 1230.0,
              1170.0, 1450.0, 1270.0, 1390.0, 1390.0],
        index=years)

    result = energy_usage_by_holiday_homes(fuelwood_usage, holiday_homes)

    expected = pd.Series(
        data=[2163.3688, 2554.5021, 2727.9841, 2572.6053, 2749.9866, 2258.9485, 1580.9598, 2242.5648, 2003.7403,
              2610.5733, 2413.5086, 2327.4024, 2651.3249, 2501.7213, 3080.2632, 2681.9163, 2901.891, 2884.8469],
        index=years, name='kwh')

    assert isinstance(result, pd.Series)
    pd.testing.assert_series_equal(result, expected)


def test_projected_fuelwood_usage_holiday_homes():
    years = YearRange(2001, 2050).to_index()
    fuelwood_by_holiday_home = pd.Series(
        data=[np.nan] * 5 +
             [2163.3688, 2554.5021, 2727.9841, 2572.6053, 2749.9866, 2258.9485, 1580.9598, 2242.5648, 2003.7403,
              2610.5733, 2413.5086, 2327.4024, 2651.3249, 2501.7213, 3080.2632, 2681.9163, 2901.891, 2884.8469] +
             [np.nan] * 27,
        index=years, name='kwh')

    actual = projected_fuelwood_usage_holiday_homes(fuelwood_by_holiday_home)

    expected = pd.Series([np.nan] * 23 + [2810.1277] * 27, index=years)

    pd.testing.assert_series_equal(actual, expected)


def test_project_fuelwood_usage(spreadsheet):
    """
       Test project_fuelwood_usage using spreadsheet values
    """
    years = YearRange(2006, 2023).to_index()
    # 04 Ved i fritidsboliger statistikk (GWh)
    fuelwood_usage = pd.Series(
        data=[880.0, 1050.0, 1140.0, 1090.0, 1180.0, 990.0, 700.0, 1000.0, 900.0, 1180.0, 1100.0, 1070.0, 1230.0,
              1170.0, 1450.0, 1270.0, 1390.0, 1390.0],
        index=years)

    actual = project_fuelwood_usage(fuelwood_usage, spreadsheet.holiday_homes_by_category, spreadsheet.population)
    expected = pd.Series(
        data=[np.nan] * 23 + [1364.2943, 1376.5647, 1386.0817, 1392.9277, 1399.8025, 1406.6287, 1413.3356, 1419.9752,
                              1426.5041, 1432.9114, 1439.2341, 1445.4398, 1451.5521, 1457.3734, 1462.9349, 1468.2466,
                              1473.3265, 1478.1775, 1482.8047, 1487.197, 1491.3579, 1495.2689, 1498.9219, 1502.3119,
                              1505.4268, 1508.2642, 1510.826], name='gwh', index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(actual, expected)


def test_project_fossil_fuel_usage(spreadsheet):
    """
    Test project_fuelwood_usage using spreadsheet values
    """

    fuelwood_usage = pd.Series(data=[100], index=YearRange(2006, 2006).to_index(), name='kwh')

    actual = project_fossil_fuel_usage(fuelwood_usage, spreadsheet.holiday_homes_by_category, spreadsheet.population)
    expected = pd.Series(
        data=[np.nan] * 5 + [100.0] * 45, name='gwh', index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(actual, expected)


def test_project_electricity_usage(spreadsheet):
    """
    Test project_electricity_usage using spreadsheet values
    """
    # 09 Elektrisitet pr fritidsbolig framskrevet (kWh)
    electricity_usage = pd.Series(
        data=[1128.0, 1173.0, 1183.0, 1161.0, 1235.0, 1317.0, 1407.0, 1522.0, 1635.0, 1931.0, 1818.0, 1929.0, 2141.0,
              2006.0, 2118.0, 2278.0, 2350.0, 2417.0, 2384.0, 2467.0, 2819.0, 2318.0, 2427.0],
        index=YearRange(2001, 2023).to_index(), name='gwh')

    result = project_electricity_usage(electricity_usage, spreadsheet.holiday_homes_by_category, spreadsheet.population)

    expected = pd.Series(
        data=[np.nan] * 23 + [2511.2188, 2570.5439, 2625.309, 2675.4518, 2726.0161, 2764.3374, 2802.6652, 2841.0968,
                              2879.5415, 2905.223, 2930.8463, 2956.3427, 2981.7578, 3006.6811, 3031.1697, 3055.2375,
                              3078.9154, 3089.053, 3098.7227, 3107.9017, 3116.5969, 3124.7702, 3132.404, 3139.4883,
                              3145.9977, 3151.9272, 3157.2808],
        name='gwh',
        index=YearRange(2001, 2050).to_index())

    pd.testing.assert_series_equal(result, expected)
