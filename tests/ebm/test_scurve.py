import io

import pandas as pd
import pytest

from ebm import s_curve
from ebm.model.data_classes import YearRange
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


@pytest.fixture
def years():
    years = YearRange(2020, 2050)
    return years


@pytest.fixture
def tek_parameters():
    tek_parameters_tek69_csv = """
TEK,building_year,period_start_year,period_end_year
PRE_TEK49,1945,0,1948
TEK1949,1962,1949,1968
TEK1969,1977,1969,1986
TEK1987,1991,1987,1996
TEK1997,2002,1997,2006
TEK2007,2012,2007,2010
TEK2010,2018,2011,2019
TEK2017,2025,2020,2050
""".strip()
    tek_parameters = pd.read_csv(io.StringIO(tek_parameters_tek69_csv))
    return tek_parameters


@pytest.fixture
def scurves_parameters_house():
    scurve_parameters_house_csv = """
building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
house,small_measure,3,23,30,80,0.8,0.01
house,renovation,10,37,24,75,0.65,0.05
house,demolition,60,90,40,150,0.7,0.05""".strip()
    scurve_parameters = pd.read_csv(io.StringIO(scurve_parameters_house_csv))
    return scurve_parameters


def test_calculate_s_curves_return_correct_original_condition(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_original_condition = pd.Series(
        data=
            [0.05]*17 + [0.0404761904752992, 0.0257142857133991, 0.0109523809514991] + [0.01]*11+ # TEK69
            [1.0, 0.981, 0.962, 0.943, 0.924, 0.905, 0.87833, 0.851666, 0.815, 0.778333,
             0.741667, 0.705, 0.66833, 0.63167, 0.595, 0.55833, 0.5216667, 0.485, 0.448333, 0.41166667,
             0.375, 0.338333, 0.301666, 0.2479166, 0.1941666, 0.1404166, 0.086666, 0.05, 0.05, 0.05,
             0.05], # TEK10

        name='original_condition',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years], names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.original_condition, expected_original_condition)


def test_calculate_s_curves_return_correct_small_measure(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_small_measure = pd.Series(
        data=
        [0.2854166667, 0.2583333333, 0.23125, 0.2041666667, 0.1770833333,
         0.15, 0.1442307692, 0.1384615385, 0.1326923077, 0.1269230769,
         0.1211538462, 0.1153846154, 0.1096153846, 0.1038461538, 0.0980769231,
         0.0923076923, 0.0865384615, 0.0777930403, 0.0742857143, 0.0707783883,
         0.0534615385, 0.04, 0.04, 0.04, 0.04,
         0.04, 0.04, 0.04, 0.04, 0.04, 0.04, # TEK69
         0.0, 0.019, 0.038, 0.057, 0.076,
         0.095, 0.1216666667, 0.1483333333, 0.175, 0.2016666667,
         0.2283333333, 0.255, 0.2816666667, 0.3083333333, 0.335,
         0.3616666667, 0.3883333333, 0.415, 0.4416666667, 0.4683333333,
         0.495, 0.5216666667, 0.5483333333, 0.575, 0.6016666667,
         0.6283333333, 0.655, 0.6645833333, 0.6375, 0.6104166667,
         0.5833333333], # TEK10
        name='small_measure',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years], names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.small_measure, expected_small_measure)


def test_calculate_s_curves_return_correct_renovation(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_renovation = pd.Series(
        data=
        [0.04142857, 0.03916667, 0.03690476, 0.03464286, 0.03238095, 0.03011905, 0.02785714, 0.02559524, 0.02333333, 0.02107143,
         0.01880952,
         0.01654762, 0.01428571, 0.01202381, 0.0097619, 0.0075, 0.0052381, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08,
         0.09, 0.1,
         0.11, 0.12, 0.13, 0.14, 0.15, 0.17708333, 0.20416667, 0.23125, 0.25833333, 0.26833333, 0.24166667, 0.215,
         0.18833333], # TEK10
        name='renovation',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years], names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.renovation, expected_renovation)
    
    
def test_calculate_s_curves_return_correct_renovation_and_small_measure(
        scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_renovation_and_small_measure = pd.Series(
        data=
        [0.6231548, 0.6525, 0.6818452, 0.7111905, 0.7405357, 0.769881, 0.7779121, 0.7859432, 0.7939744, 0.8020055,
         0.8100366, 0.8180678, 0.8260989, 0.83413, 0.8421612, 0.8501923, 0.8582234, 0.8692308, 0.875, 0.8807692,
         0.8865385, 0.8875, 0.875, 0.8625, 0.85, 0.8375, 0.825, 0.8075, 0.79, 0.7725,
         0.755] + # TEK69
        [0.0] * 27 + [0.0170833, 0.0708333, 0.1245833, 0.1783333], # TEK10
        name='renovation_and_small_measure',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years], names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.renovation_and_small_measure, expected_renovation_and_small_measure)


def test_calculate_s_curves_return_correct_demolition(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_demolition = pd.Series(
        data=
        [0.0] * 17 + [0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1425, 0.16, 0.1775, 0.195] + # TEK69
         [0.0] * 31,  # TEK10
        name='demolition',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years],
                                         names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.demolition, expected_demolition)


def test_calculate_s_curves_return_columns(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurves_parameters_house, tek_parameters, years)

    assert 'original_condition' in result.columns
    assert 'small_measure' in result.columns
    assert 'renovation' in result.columns
    assert 'renovation_and_small_measure' in result.columns
    assert 'demolition' in result.columns

    assert 's_curve_demolition' in result.columns


def test_calculate_s_curves_conditions_sums_to_one(scurves_parameters_house, tek_parameters, years):
    result = s_curve.calculate_s_curves(scurves_parameters_house, tek_parameters, years)

    assert pd.Series(result.s_curve_sum.round(5) == 1.0).all()


def test_calculate_s_curves_just_demolition(tek_parameters, years):
    scurve_parameters_house_csv = """
building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
house,small_measure,3,23,30,80,0.0,1.0
house,renovation,10,37,24,75,0.0,1.0
house,demolition,60,90,40,150,0.7,0.05""".strip()
    scurves_parameters_house = pd.read_csv(io.StringIO(scurve_parameters_house_csv))

    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(['TEK1969', 'TEK2010'])],
                                        years=years)

    expected_demolition = pd.Series(
        data=
        [0.0] * 17 + [0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1425, 0.16, 0.1775,
                      0.195] +  # TEK69
        [0.0] * 31,  # TEK10
        name='demolition',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years],
                                         names=['building_category', 'TEK', 'year'])
    )

    pd.testing.assert_series_equal(result.demolition, expected_demolition)

    expected_original_condition = pd.Series(
        data=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] +
             [0.9875, 0.975, 0.9625, 0.95, 0.9375, 0.925, 0.9125, 0.9, 0.8875, 0.875] +
             [0.8574999999999999, 0.84, 0.8225, 0.8049999999999999] + # TEK69
             [1.0]*31, # TEK10

        name='original_condition',
        index=pd.MultiIndex.from_product([['house'], ['TEK1969', 'TEK2010'], years],
                                         names=['building_category', 'TEK', 'year'])
    )
    pd.testing.assert_series_equal(result.original_condition, expected_original_condition)

    assert (result.original_condition + result.demolition == 1.0).all()


def test_calculate_s_curves_cuts_off_non_demolition_after_2030(scurves_parameters_house, tek_parameters, years):
    use_tek = ['TEK1969']
    tek_parameters = tek_parameters[tek_parameters.TEK.isin(use_tek)]
    s_curves = s_curve.scurve_parameters_to_scurve(scurves_parameters_house)
    df_never_share = s_curve.scurve_parameters_to_never_share(s_curves, scurves_parameters_house)

    s_curves_with_tek = s_curve.merge_s_curves_and_tek(s_curves, df_never_share, tek_parameters)
    from_2030 = list(years.subset(10))

    s_curves_with_tek.loc[(slice(None), 'TEK1969', from_2030), ['small_measure_acc', 'renovation_acc']] = (
    0.931190, 0.828846)
    # s_curves_with_tek.loc[(slice(None), 'TEK2010', from_2030), ['small_measure_acc', 'renovation_acc']] = (0.228333, 0.030000)

    result = s_curve.calculate_s_curves(scurve_parameters=scurves_parameters_house,
                                        tek_parameters=tek_parameters[tek_parameters.TEK.isin(use_tek)],
                                        years=years)

    building_category_building_condition_year = pd.MultiIndex.from_product([['house'], use_tek, years],
                                                                           names=['building_category', 'TEK', 'year'])
    expected_original_condition = pd.Series(
        data=[0.050000000000000044, 0.050000000000000044, 0.050000000000000044, 0.050000000000000044,
              0.050000000000000044, 0.050000000000000044, 0.050000000000000044, 0.050000000000000044,
              0.050000000000000044, 0.050000000000000044, 0.050000000000000044, 0.050000000000000044,
              0.050000000000000044, 0.050000000000000044, 0.050000000000000044, 0.050000000000000044,
              0.050000000000000044, 0.040476190475299156, 0.025714285713399065, 0.010952380951499086,
              0.010000000000000009, 0.010000000000000009, 0.010000000000000009, 0.010000000000000009,
              0.010000000000000009, 0.010000000000000009, 0.010000000000000009, 0.010000000000000009,
              0.010000000000000009, 0.010000000000000009, 0.010000000000000009],  # TEK69
        name='original_condition', index=building_category_building_condition_year)
    assert (
                result.original_condition + result.small_measure + result.renovation + result.renovation_and_small_measure + result.demolition == 1.0).all()

    pd.testing.assert_series_equal(result.original_condition, expected_original_condition)

    expected_demolition = pd.Series(
        data=[0.0] * 17 + [0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1425, 0.16, 0.1775,
                           0.195]  # TEK69
        , name='demolition', index=building_category_building_condition_year)

    pd.testing.assert_series_equal(result.demolition, expected_demolition)

    expected_small_measure = pd.Series(
        data=[0.2854166667, 0.2583333333, 0.23125, 0.2041666667, 0.1770833333, 0.15, 0.1442307692, 0.1384615385,
              0.1326923077, 0.1269230769, 0.1211538462] +
             [0.11538461538559963, 0.10961538461639964, 0.10384615384719964, 0.09807692307799964,
              0.09230769230879965, 0.08653846153959965, 0.07779304029510059, 0.07428571428780062,
              0.07077838828050065, 0.05346153846279966] + [0.04] * 10,
        name='small_measure', index=building_category_building_condition_year)
    pd.testing.assert_series_equal(result.small_measure, expected_small_measure)

    expected_renovation = pd.Series(
        data=[0.04142857, 0.03916667, 0.03690476, 0.03464286, 0.03238095, 0.03011905, 0.02785714, 0.02559524,
                 0.02333333, 0.02107143, 0.01880952] + [0.016547619046699213, 0.01428571428479919, 0.012023809522899165,
                                                        0.00976190476099914, 0.007499999999099116,
                                                        0.005238095237199092] + [0.0] * 14, name='renovation',
        index=building_category_building_condition_year)
    pd.testing.assert_series_equal(result.renovation, expected_renovation)

    expected_renovation_and_small_measure = pd.Series(
        data=[0.6231548, 0.6525, 0.6818452, 0.7111905, 0.7405357, 0.769881, 0.7779121, 0.7859432, 0.7939744, 0.8020055,
              0.8100366] + [0.8180677655677011, 0.8260989010988011, 0.8341300366299012, 0.8421611721610012,
                            0.8501923076921012, 0.8582234432232012, 0.8692307692296003, 0.8749999999988003,
                            0.8807692307680003, 0.8865384615372003, 0.8875, 0.875, 0.8624999999999999, 0.85,
                            0.8374999999999999, 0.825, 0.8074999999999999, 0.7899999999999999, 0.7725,
                            0.7549999999999999], name='renovation_and_small_measure',
        index=building_category_building_condition_year)
    pd.testing.assert_series_equal(result.renovation_and_small_measure, expected_renovation_and_small_measure)


if __name__ == "__main__":
    import sys
    pytest.main([sys.argv[0]])
