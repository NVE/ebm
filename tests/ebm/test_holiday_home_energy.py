import numpy as np
import pandas as pd
import pytest

from ebm.holiday_home_energy import sum_holiday_homes, population_over_holiday_homes, projected_holiday_homes, \
    projected_electricity_usage_holiday_homes, electricity_usage_by_holiday_home, projected_electricity_usage_holiday_homes


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
    electricity_usage = pd.Series({y: 2.0 if y < 2024 else np.nan for y in range(2001, 2051)})
    electricity_usage.index.name = 'year'
    electricity_usage[2019] = 100.0
    result = projected_electricity_usage_holiday_homes(
        electricity_usage
    )

    expected = pd.Series(data=[np.nan]*23 +
                              [100.0 + (75 * i) for i in range(1, 6)] +
                              [475.0 + (50 * i) for i in range(1, 5)] +
                              [675.0 + (25 * i) for i in range(1, 9)] +
                              [875.0 for i in range(1, 11)],
                         index=pd.Index([y for y in range(2001, 2051)], name='year'),
                         name='projected_electricity_usage_holiday_homes')

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


