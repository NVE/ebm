import pandas as pd
import pytest

from ebm.model.scurve import SCurve


def test_scurve():
    """
    Test using numbers for apartment_block small_measure
    building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
    apartment_block, small_measure, 5, 20, 20, 50, 0.8, 0.1
    """

    s_curve = SCurve(earliest_age=5,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.1)
    result = s_curve.get_rates_per_year_over_building_lifetime()
    expected = [0.0] * 4 + [0.01] * 5 + [0.04] * 20 + [0.0025] * 20 + [0.0] * 81
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')

    pd.testing.assert_series_equal(result, expected_curve)


def test_calc_rates_apartment_block_small_measure():
    s_curve = SCurve(earliest_age=5,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.1)

    # was 0.009999999999999995
    assert s_curve._calc_pre_rush_rate() == 0.01
    assert s_curve._calc_rush_rate() == 0.04
    # was 0.0024999999999999988
    assert s_curve._calc_post_rush_rate() == 0.0025


def test_calc_rates_apartment_block_renovation():
    s_curve = SCurve(earliest_age=10,
                     average_age=30,
                     rush_years=14,
                     last_age=60,
                     rush_share=0.6,
                     never_share=0.15)

    # Bema: 0,96153846153846200000 %
    assert s_curve._calc_pre_rush_rate() == 0.0096153846154

    # 4,285714285714290 %
    # 0.0428571428571429
    assert s_curve._calc_rush_rate() == 0.0428571428571
    # Bema: 0,54347826087 %
    # 0.005434782608695652
    # 0.0054347826087

    assert s_curve._calc_post_rush_rate() == 0.0054347826087


def test_calc_rates_apartment_block_demolition():
    s_curve = SCurve(earliest_age=60,
                     average_age=90,
                     rush_years=40,
                     last_age=150,
                     rush_share=0.7,
                     never_share=0.05)

    assert s_curve._calc_pre_rush_rate() == 0.0125
    assert s_curve._calc_rush_rate() == 0.0175
    assert s_curve._calc_post_rush_rate() == 0.003125


def test_calc_rates_office_demolition():
    s_curve = SCurve(earliest_age=50,
                     average_age=100,
                     rush_years=30,
                     last_age=130,
                     rush_share=0.7,
                     never_share=0.05)

    curve = s_curve.get_rates_per_year_over_building_lifetime()
    expected = [0.0] * 49 + [0.0035714285714285713] * 35 + [0.02333333333] * 30 + [0.008333333] * 15 + [0.0]
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')
    pd.testing.assert_series_equal(curve, expected_curve)

    cumsum = s_curve.calc_scurve()
    expected_cumsum = expected_curve.cumsum()
    pd.testing.assert_series_equal(cumsum, expected_cumsum)


def test_calc_rates_culture_small_measure():
    """ Test that rate for culture small measure is correct"""
    s_curve = SCurve(earliest_age=3,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.01)

    curve = s_curve.get_rates_per_year_over_building_lifetime()
    expected_curve = pd.Series(data=[0.0] * 2 + [0.0135714285714] * 7 + [0.04] * 20 + [0.00475] * 20 + [0.0] * 81,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')
    pd.testing.assert_series_equal(curve, expected_curve)


def test_calc_rates_culture_rehabilitation():
    """ Test that rate for culture rehabilitation is correct"""
    s_curve = SCurve(earliest_age=5,
                     average_age=65,
                     rush_years=40,
                     last_age=100,
                     rush_share=0.75,
                     never_share=0.05)

    curve = s_curve.get_rates_per_year_over_building_lifetime()
    expected_curve = pd.Series(data=[0.0] * 4 + [0.00250] * 40 + [0.01875] * 40 + [0.00666667] * 15 + [0.0] * 31,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')
    pd.testing.assert_series_equal(curve, expected_curve)


def test_calc_pre_rush_rate_kindergarten():
    s_curve = SCurve(earliest_age=3,
                     average_age=25,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.01)
    # was  0,791666666666666 %
    expected = 0.0079166666667

    assert s_curve._calc_pre_rush_rate() == expected


def test_scurve_init_positive_value_checks():
    """
    The scurve constructor should raise ValueError when any argument is less than zero
    """
    legal_values = {'average_age': 3, 'earliest_age': 3, 'rush_years': 20, 'last_age': 50, 'rush_share': 0.8,
                    'never_share': 0.01}

    with pytest.raises(ValueError):
        SCurve(**{**legal_values, 'earliest_age': -1})
    with pytest.raises(ValueError, match='Illegal value for average_age'):
        SCurve(**{**legal_values, 'average_age': -2})
    with pytest.raises(ValueError, match='Illegal value for last_age'):
        SCurve(**{**legal_values, 'last_age': -1})
    with pytest.raises(ValueError, match='Illegal value for rush_share'):
        SCurve(**{**legal_values, 'rush_share': -0.1})
    with pytest.raises(ValueError, match='Illegal value for never_share'):
        SCurve(**{**legal_values, 'never_share': -0.2})


def test_scurve_init_mention_all_illegal_arguments_when_raising_value_error():
    """Test that SCurve init list all arguments with errors in ValueError"""
    with pytest.raises(ValueError, match='Illegal value for earliest_age average_age last_age'):
        SCurve(earliest_age=-1, average_age=-1, rush_years=20, last_age=-1, rush_share=0.8, never_share=0.01)
