import numpy as np
import pandas as pd
import pytest

from ebm.model.altcurve import AltCurve
from ebm.model.scurve import SCurve


def test_scurve_apartment_block_small_measure():
    """
    Test using numbers for apartment_block small_measure
    building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
    apartment_block, small_measure, 5, 20, 20, 50, 0.8, 0.1
    """
    a_curve = AltCurve(earliest_age=5,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.1,
                     building_category='apartment_block',
                     condition='small_measure')
    result = a_curve.get_rates_per_year_over_building_lifetime().xs(key=('apartment_block', 'small_measure'), level=('building_category', 'condition'))
    expected = [0.0] * 4 + [0.01] * 5 + [0.04] * 20 + [0.0025] * 20 + [0.0] * 81
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='rate')

    pd.testing.assert_series_equal(result, expected_curve)


def test_scurve_house_demolition():
    """
    Test using numbers for house demolition
    building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
    house,demolition,60,90,40,150,0.7,0.05
    """
    a_curve=AltCurve(earliest_age=60, average_age=90, rush_years=40, rush_share=0.7, last_age=150, never_share=0.05, building_lifetime=150,
                    building_category='house', condition='demolition')
    result = a_curve.get_rates_per_year_over_building_lifetime().xs(key=('house', 'demolition'), level=('building_category', 'condition'))
    expected = [0.0] * 59 + [0.0125] * 10 + [0.0175] * 40 + [0.003125] * 40 + [0.0] * 1
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, len(expected)+1)], name='age'), name='rate')

    pd.testing.assert_series_equal(result, expected_curve)


@pytest.mark.parametrize(('rush_years', 'average_age', 'earliest_age'), [
    (36, 77, 58), (37, 77, 58), (39, 77, 58), (38, 77, 58),
    (30, 23, 7), (30, 23, 9), (30, 23, 8),
])
def test_scurve_long_rush_period_does_not_cause_division_by_zero_error_in_pre_rush(rush_years, average_age, earliest_age):
    a_curve = AltCurve(
        earliest_age=earliest_age,
        rush_years=rush_years,
        average_age=average_age,
        last_age=129,
        rush_share=0.7,
        never_share=0.05)

    result = a_curve.calc_scurve()
    assert isinstance(result, pd.DataFrame)

    assert result.index.get_level_values(level='building_category').unique() == 'unknown'
    assert result.index.get_level_values(level='condition').unique() == 'unknown'




@pytest.mark.parametrize('last_age', [81, 82])
def test_scurve_long_rush_period_does_not_cause_division_by_zero_error_in_post_rush(last_age):
    a_curve = AltCurve(
        earliest_age=58,
        average_age=77,
        rush_years=6,
        rush_share=0.7,
        last_age=last_age,
        never_share=0.01,
        building_category='bc',
        condition='c',
    )
    altcurve = a_curve.calc_scurve()
    assert altcurve.rate_acc.max() == 1.0 - 0.01


def test_calc_rates_apartment_block_small_measure():
    a_curve = AltCurve(earliest_age=5,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.1)

    result = a_curve.calc_scurve().rate.loc[('unknown', 'unknown')].round(4)

    assert result.dtype == np.float64
    assert result.name == 'rate'

    assert result.loc[slice(1, 4)].to_list()== [0.0,0.0,0.0,0.0]

    pre_rush_range = slice(5, 9)
    expected_pre_rush_value = 0.01
    assert result.loc[pre_rush_range].to_list() == [expected_pre_rush_value] * 5

    rush_range = slice(11, 29)
    expected_rush_rate = 0.04
    assert result.loc[rush_range].to_list() == [expected_rush_rate] * 19

    expected_post_rush_rate = 0.0025
    post_rush_range = slice(30, 49)
    assert result.loc[post_rush_range].to_list() == [expected_post_rush_rate] * 20

    assert (result.loc[slice(50, None)] == 0.0).all()


def test_calc_rates_apartment_block_renovation():
    a_curve = AltCurve(earliest_age=10,
                     average_age=30,
                     rush_years=14,
                     last_age=60,
                     rush_share=0.6,
                     never_share=0.15)

    result = a_curve.calc_scurve().rate.loc[('unknown', 'unknown')]
    assert (result.loc[10:22].round(6) == 0.009615).all()
    assert (result.loc[23:36].round(8) == 0.04285714).all()
    assert (result.loc[37:59].round(8) == 0.00543478).all()


def test_calc_rates_apartment_block_demolition():
    a_curve = AltCurve(earliest_age=60,
                     average_age=90,
                     rush_years=40,
                     last_age=150,
                     rush_share=0.7,
                     never_share=0.05)

    result: pd.Series = a_curve.calc_scurve().rate.loc[('unknown', 'unknown')].round(6)
    assert (result.loc[60:69] == 0.0125).all()
    assert (result.loc[70:109] == 0.0175).all()
    assert (result.loc[110:149] == 0.003125).all()

def test_calc_rates_office_demolition():
    a_curve = AltCurve(earliest_age=50,
                     average_age=100,
                     rush_years=30,
                     last_age=130,
                     rush_share=0.7,
                     never_share=0.05)

    curve = a_curve.calc_scurve().reset_index().set_index(['age']).rate
    expected = [0.0] * 49 + [0.0035714285714285713] * 35 + [0.02333333333] * 30 + [0.008333333] * 15 + [0.0]
    expected_curve = pd.Series(data=expected,
                               index=pd.Index([i for i in range(1, 131)],
                                              name='age'), name='rate')

    pd.testing.assert_series_equal(curve, expected_curve)

    cumsum = a_curve.calc_scurve().reset_index().set_index(['age']).rate.cumsum()
    expected_cumsum = expected_curve.cumsum()
    pd.testing.assert_series_equal(cumsum, expected_cumsum)


def test_calc_rates_culture_small_measure():
    """Test that rate for culture small measure is correct"""
    a_curve = AltCurve(earliest_age=3,
                     average_age=20,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.01)

    curve = a_curve.calc_scurve().reset_index().set_index(['age']).rate
    expected_curve = pd.Series(data=[0.0] * 2 + [0.0135714285714] * 7 + [0.04] * 20 + [0.00475] * 20 + [0.0] * 81,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')
    pd.testing.assert_series_equal(curve, expected_curve, check_names=False)


def test_calc_rates_culture_rehabilitation():
    """Test that rate for culture rehabilitation is correct"""
    a_curve = AltCurve(earliest_age=5,
                     average_age=65,
                     rush_years=40,
                     last_age=100,
                     rush_share=0.75,
                     never_share=0.05)

    curve = a_curve.calc_scurve().reset_index().set_index(['age']).rate
    expected_curve = pd.Series(data=[0.0] * 4 + [0.00250] * 40 + [0.01875] * 40 + [0.00666667] * 15 + [0.0] * 31,
                               index=pd.Index([i for i in range(1, 131)], name='age'), name='scurve')
    pd.testing.assert_series_equal(curve, expected_curve, check_names=False)


def test_calc_pre_rush_rate_kindergarten():
    a_curve = AltCurve(earliest_age=3,
                     average_age=25,
                     rush_years=20,
                     last_age=50,
                     rush_share=0.8,
                     never_share=0.01)
    # was  0,791666666666666 %
    expected = 0.007916666666666664

    result = a_curve.calc_scurve().reset_index().set_index(['age'])
    assert result.pre_rate.dtype == np.float64
    assert (result.pre_rate == expected).all()

    rate = result.rate
    assert (rate.loc[3:14] == expected).all()


def test_scurve_init_positive_value_checks():
    """
    The scurve constructor should raise ValueError when any argument is less than zero
    """
    legal_values = {'average_age': 3, 'earliest_age': 3, 'rush_years': 20, 'last_age': 50, 'rush_share': 0.8,
                    'never_share': 0.01}

    with pytest.raises(ValueError, match='Illegal value for earliest_age'):
        AltCurve(**{**legal_values, 'earliest_age': -1})
    with pytest.raises(ValueError, match='Illegal value for average_age'):
        AltCurve(**{**legal_values, 'average_age': -2})
    with pytest.raises(ValueError, match='Illegal value for last_age'):
        AltCurve(**{**legal_values, 'last_age': -1})
    with pytest.raises(ValueError, match='Illegal value for rush_share'):
        AltCurve(**{**legal_values, 'rush_share': -0.1})
    with pytest.raises(ValueError, match='Illegal value for never_share'):
        AltCurve(**{**legal_values, 'never_share': -0.2})


@pytest.mark.parametrize(
    ('earliest_age','average_age','rush_years','last_age','rush_share','never_share'),
    [
        pytest.param(10, 30, 14, 60, 0.6, 0.15, id='apartment_block+renovation'),
        pytest.param(5,20,20,50,0.8,0.1, id='apartment_block+small_measure'),
        pytest.param(60,90,40,150,0.7,0.05, id='apartment_block+demolition'),
        pytest.param(3,23,30,80,0.8,0.01, id='house+small_measure'),
        pytest.param(10,37,24,75,0.65,0.05, id='house+renovation'),
        pytest.param(60,90,40,150,0.7,0.05, id='house+demolition'),
        pytest.param(3,25,20,50,0.8,0.01, id='kindergarten+small_measure'),
        pytest.param(10,50,40,90,0.7,0.05, id='kindergarten+renovation'),
        pytest.param(50,100,30,130,0.7,0.05, id='kindergarten+demolition'),
    ])
def test_calc_compare_rates(earliest_age :int,average_age:int,rush_years:int,last_age:int,rush_share:float,never_share:float):
    a_curve = AltCurve(earliest_age=earliest_age, average_age=average_age, rush_years=rush_years, last_age=last_age,
                       rush_share=rush_share, never_share=never_share)
    new_rates = a_curve.calc_scurve().rate.loc[('unknown', 'unknown')]

    s_curve = SCurve(earliest_age=earliest_age, average_age=average_age, rush_years=rush_years, last_age=last_age,
                     rush_share=rush_share, never_share=never_share)
    old_rates = s_curve.get_rates_per_year_over_building_lifetime()

    pd.testing.assert_series_equal(new_rates, old_rates, check_names=False)

    new_cumsum = a_curve.calc_scurve().rate_acc.loc[('unknown', 'unknown')]
    old_cumsum = s_curve.calc_scurve()
    pd.testing.assert_series_equal(new_cumsum, old_cumsum, check_names=False)


def test_scurve_init_mention_all_illegal_arguments_when_raising_value_error():
    """Test that AltCurve init list all arguments with errors in ValueError"""
    with pytest.raises(ValueError, match='Illegal value for earliest_age average_age last_age'):
        AltCurve(earliest_age=-1, average_age=-1, rush_years=20, last_age=-1, rush_share=0.8, never_share=0.01)


if __name__ == "__main__":
    import sys
    pytest.main([sys.argv[0]])
