import pandas as pd

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

    # Should this be 0.001?
    assert s_curve._calc_pre_rush_rate() == 0.01 #0.009999999999999995
    assert s_curve._calc_rush_rate() == 0.04
    # Should this be 0.0025 ?
    assert s_curve._calc_post_rush_rate() == 0.0025 #0.0024999999999999988


def test_calc_rates_office_demolition():
    s_curve = SCurve(earliest_age=50,
                     average_age=100,
                     rush_years=30,
                     last_age=130,
                     rush_share=0.7,
                     never_share=0.05)

    result = s_curve.get_rates_per_year_over_building_lifetime()
    expected = [0.0] * 49 + [0.0035714285714285713] * 35 + [0.02333333333] * 30 + [0.008333333] * 15 + [0.0]
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')

    pd.testing.assert_series_equal(result, expected_curve)


def test_calc_pre_rush_rate_kindergarten():
    s_curve = SCurve(earliest_age=3,
                     average_age=25,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.01)
    # 0,791666666666666 %
    expected = 0.007916666666666667

    assert s_curve._calc_pre_rush_rate() == expected
