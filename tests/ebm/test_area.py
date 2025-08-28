# noinspection PyTypeChecker
import io
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest

from ebm.model.area import (transform_area_forecast_to_area_change,
                            transform_construction_by_year,
                            transform_cumulative_demolition_to_yearly_demolition, building_condition_scurves,
                            calculate_construction_by_building_category)
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager


def test_transform_area_forecast_to_area_change():
    """
    Test that construction is the change in sum of area, demolition is a negative value. When no
    building_code_parameters are provided, construction is assumed to be of TEK17.
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'original_condition', y, m2) for y, m2 in [(2020, 100), (2021, 90), (2022, 80)]]+
             [('house', 'TEK97', 'renovation', y, m2 ) for y, m2 in [(2020, 0), (2021, 6), (2022, 12)]]+
             [('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0), (2021, 4), (2022, 9)]]+
             [('house', 'TEK17', 'renovation', y, m2 ) for y, m2 in [(2020, 0), (2021, 0), (2022, 4)]]+
             [('house', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 100), (2021, 120), (2022, 135)]]+
             [('house', 'TEK17', 'small_measure', y, m2 ) for y, m2 in [(2020, 1), (2021, 2), (2022, 3)]]+
             [('office', 'TEK17', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 1.0)]] +
             [('office', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 20), (2021, 22), (2022, 25)]]
        ,columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    result  = transform_area_forecast_to_area_change(area, None).reset_index(drop=True)

    expected = pd.DataFrame(
        [('house', 'TEK97', y, 'demolition', m2) for y, m2 in enumerate((0.0, -4.0, -5.0), start=2020)]+
        [('office', 'TEK17', y, 'demolition', m2) for y, m2 in enumerate((0.0, 0.0, -1.0), start=2020)]+
        [('house', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 21.0, 20.0), start=2020)]+
        [('office', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 2.0, 3.0), start=2020)]
    , columns=['building_category', 'building_code', 'year', 'demolition_construction', 'm2'])

    assert len(result) == 12

    pd.testing.assert_frame_equal(result, expected)


def test_transform_area_forecast_to_area_change_raises_value_error():
    """
    transform_area_forecast_to_area_change raise ValueError when area_forecast is None
    """

    building_code_parameters = pd.DataFrame(data=[['TEK17', 2017, 2011, 2019]],
                                  columns=['building_code', 'building_year', 'period_start_year', 'period_end_year'])
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_area_forecast_to_area_change(None, building_code_parameters=building_code_parameters)


def test_transform_construction_by_year():
    """
    Test that building_code_parameters is used to figure out the correct TEK for construction In this case we expect that TEK21
    is used.
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'original_condition', y, m2) for y, m2 in [(2020, 100), (2021, 90), (2022, 80)]]+
             [('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0), (2021, 10), (2022, 20)]]+
             [('house', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 100), (2021, 100), (2022, 100)]]+
             [('house', 'TEK17', 'demolition', y, m2 ) for y, m2 in [(2020, 0.0), (2021, 0.0), (2022, 0.0)]]+
             [('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]] +
             [('house', 'TEK21', 'renovation', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 1.0)]] +
             [('house', 'TEK21', 'original_condition', y, m2 ) for y, m2 in [(2020, 10.0), (2021, 20.0), (2022, 33.0)]]
        ,columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    building_code_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2019], ['TEK21', 2021, 2020, 2050]],
        columns=['building_code', 'building_year', 'period_start_year', 'period_end_year'])

    result  = transform_construction_by_year(area, building_code_parameters).reset_index().set_index(
        ['building_category', 'building_code', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=[('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 10.0, 14.0), start=2020)],
        columns=['building_category', 'building_code', 'year', 'm2']).set_index(['building_category', 'building_code', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_construction_by_year_expect_columns():
    """
    transform_construction_by_year should raise ValueError when expected columns are missing
    """
    area = pd.DataFrame(
        data=[('house', 'TEK21', 'construction', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]],
        columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])
    building_code_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2019], ['TEK21', 2021, 2020, 2050]],
        columns=['building_code', 'building_year', 'period_start_year', 'period_end_year'])

    for expected_column in area.columns:
        with pytest.raises(ValueError):
            transform_construction_by_year(area.drop(columns=[expected_column]))

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_construction_by_year(area_forecast=None)

    for expected_column in building_code_parameters.columns:
        with pytest.raises(ValueError):
            transform_construction_by_year(area, building_code_parameters.drop(columns=[expected_column]))


def test_transform_accumulated_to_yearly_demolition():
    """
    Test transform_cumulative_demolition_to_yearly_demolition. Make sure any other condition is ignored. Input accumulated demolition, output
    yearly demolition
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'original_condition', y, m2) for y, m2 in [(2020, 100), (2021, 90), (2022, 80)]]+
             [('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0), (2021, 10), (2022, 21)]]+
             [('house', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 100), (2021, 100), (2022, 100)]]+
             [('house', 'TEK17', 'demolition', y, m2 ) for y, m2 in [(2020, 0.0), (2021, 2.0), (2022, 4.0)]]+
             [('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]] +
             [('house', 'TEK21', 'renovation', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 1.0)]] +
             [('house', 'TEK21', 'original_condition', y, m2 ) for y, m2 in [(2020, 10.0), (2021, 20.0), (2022, 33.0)]]
        ,columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    result  = transform_cumulative_demolition_to_yearly_demolition(area).reset_index().set_index(
        ['building_category', 'building_code', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=
             [('house', 'TEK17', y, m2) for y, m2 in enumerate((np.nan, 2.0, 2.0), start=2020)]+
             [('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 0.0, 0.0), start=2020)]+
             [('house', 'TEK97', y, m2) for y, m2 in enumerate((np.nan, 10.0, 11), start=2020)],
        columns=['building_category', 'building_code', 'year', 'm2']).set_index(['building_category', 'building_code', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_accumulated_to_yearly_demolition_handle_disorganized_area():
    """
    Make sure transform_cumulative_demolition_to_yearly_demolition handle disorganized input
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0),  (2022, 21), (2021, 10)]]+
             [('house', 'TEK17', 'demolition', y, m2 ) for y, m2 in [(2021, 2.0), (2020, 0.0), (2022, 4.0)]]+
             [('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2022, 0.0), (2021, np.nan), (2020, np.nan)]]
        ,columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    result  = transform_cumulative_demolition_to_yearly_demolition(area).reset_index().set_index(
        ['building_category', 'building_code', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=[('house', 'TEK17', y, m2) for y, m2 in enumerate((np.nan, 2.0, 2.0), start=2020)]+
             [('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 0.0, 0.0), start=2020)]+
             [('house', 'TEK97', y, m2) for y, m2 in enumerate((np.nan, 10.0, 11), start=2020)]
        , columns=['building_category', 'building_code', 'year', 'm2']).set_index(['building_category', 'building_code', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_accumulated_to_yearly_demolition_expect_columns():
    """
    transform_cumulative_demolition_to_yearly_demolition should raise ValueError when expected columns are missing
    """
    area = pd.DataFrame(
        data=[('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]],
        columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    for expected_column in area.columns:
        with pytest.raises(ValueError):
            transform_cumulative_demolition_to_yearly_demolition(area.copy().drop(columns=[expected_column]))

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_cumulative_demolition_to_yearly_demolition(None)


def test_building_condition_scurves():
    house_csv = io.StringIO("""building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share
    house,small_measure,3,23,30,80,0.8,0.01
    house,renovation,10,37,24,75,0.65,0.05
    house,demolition,60,90,40,150,0.7,0.05""".strip())

    house_parameters = pd.read_csv(house_csv)

    res = building_condition_scurves(house_parameters)

    assert isinstance(res, pd.DataFrame)


@patch('ebm.model.construction.ConstructionCalculator.calculate_all_construction')
def test_house(mock_calculator):
    demolition = pd.DataFrame({'demolition': [0.0, 864644.3575, 1754542.5575, 1754542.5575, 1754542.5575, 1754542.5575,
                                              1754542.5575, 1754542.5575, 1754542.5575, 1754542.5575, 1754542.5575,
                                              1754542.5575, 2110501.8375000004, 2110501.8375000004, 2110501.8375000004,
                                              2110501.8375000004, 2110501.8375000004, 3048130.0, 3048130.0, 3048130.0,
                                              3048130.0, 3048130.0, 3048130.0, 3048130.0, 3048130.0, 3048130.0,
                                              3048130.0, 3423181.2650000006, 3423181.2650000006, 3423181.2650000006,
                                              3423181.2650000006]},
                              index=pd.Index([('house', y) for y in range(2020, 2051)],
                                             name=('building_category', 'year')))
    building_code = pd.DataFrame({'building_code': {0: 'PRE_TEK49', 1: 'TEK49', 2: 'TEK69', 3: 'TEK87', 4: 'TEK97',
                                                    5: 'TEK07', 6: 'TEK10', 7: 'TEK17', 8: 'TEK30'},
                                  'building_year': {0: 1945.0, 1: 1962.0, 2: 1977.0, 3: 1991.0, 4: 2002.0, 5: 2012.0,
                                                    6: 2018.0, 7: 2025.0, 8: 2032.0},
                                  'period_start_year': {0: 0.0, 1: 1949.0, 2: 1969.0, 3: 1987.0, 4: 1997.0, 5: 2007.0,
                                                        6: 2011.0, 7: 2020.0, 8: 2031.0},
                                  'period_end_year': {0: 1948.0, 1: 1968.0, 2: 1986.0, 3: 1996.0, 4: 2006.0, 5: 2010.0,
                                                      6: 2019.0, 7: 2030.0, 8: 2050.0}})
    mock_database_manager = DatabaseManager()
    mock_database_manager.get_building_codes = MagicMock(return_value=building_code)

    mock_construction = pd.DataFrame({'year': {0: 2020.0, 1: 2021.0, 2: 2022.0, 3: 2023.0, 4: 2024.0, 5: 2025.0,
                                               6: 2026.0, 7: 2027.0, 8: 2028.0, 9: 2029.0, 10: 2030.0, 11: 2031.0,
                                               12: 2032.0, 13: 2033.0, 14: 2034.0, 15: 2035.0, 16: 2036.0, 17: 2037.0,
                                               18: 2038.0, 19: 2039.0, 20: 2040.0, 21: 2041.0, 22: 2042.0, 23: 2043.0,
                                               24: 2044.0, 25: 2045.0, 26: 2046.0, 27: 2047.0, 28: 2048.0, 29: 2049.0,
                                               30: 2050.0},
                                      'population': {0: 5367580.0, 1: 5391369.0, 2: 5425270.0, 3: 5488984.0,
                                                     4: 5550203.0, 5: 5600121.0, 6: 5638838.0, 7: 5666689.0,
                                                     8: 5694657.0, 9: 5722427.0, 10: 5749712.0, 11: 5776723.0,
                                                     12: 5803284.0, 13: 5829350.0, 14: 5855072.0, 15: 5880318.0,
                                                     16: 5905184.0, 17: 5928866.0, 18: 5951491.0, 19: 5973100.0,
                                                     20: 5993766.0, 21: 6013501.0, 22: 6032325.0, 23: 6050194.0,
                                                     24: 6067121.0, 25: 6083032.0, 26: 6097893.0, 27: 6111684.0,
                                                     28: 6124356.0, 29: 6135899.0, 30: 6146321.0},
                                      'population_growth': {0: np.nan, 1: 0.004431978657048363, 2: 0.006288013304227569,
                                                            3: 0.011743931638425353, 4: 0.01115306584970921,
                                                            5: 0.008993905267969504, 6: 0.0069136006168437625,
                                                            7: 0.004939138169956392, 8: 0.004935509960048989,
                                                            9: 0.0048765009025126815, 10: 0.004768081794665147,
                                                            11: 0.004697800515921502, 12: 0.004597935542348219,
                                                            13: 0.004491594759105322, 14: 0.004412498820623334,
                                                            15: 0.004311817173213273, 16: 0.004228682870552225,
                                                            17: 0.004010374613221179, 18: 0.003816075451865464,
                                                            19: 0.0036308548563712684, 20: 0.003459844971622772,
                                                            21: 0.003292587665250757, 22: 0.0031302896598837116,
                                                            23: 0.0029622077722935014, 24: 0.0027977615263246047,
                                                            25: 0.0026224959086855737, 26: 0.0024430251229978772,
                                                            27: 0.0022616008513105523, 28: 0.002073405627647018,
                                                            29: 0.0018847695986321522, 30: 0.001698528610069916},
                                      'household_size': {0: 2.15, 1: 2.14, 2: 2.13, 3: 2.12, 4: 2.115, 5: 2.11,
                                                         6: 2.105, 7: 2.1, 8: 2.095, 9: 2.09, 10: 2.085, 11: 2.081,
                                                         12: 2.077, 13: 2.073, 14: 2.07, 15: 2.067, 16: 2.064,
                                                         17: 2.062, 18: 2.06, 19: 2.059, 20: 2.058, 21: 2.057,
                                                         22: 2.056, 23: 2.055, 24: 2.054, 25: 2.053, 26: 2.052,
                                                         27: 2.051, 28: 2.05, 29: 2.05, 30: 2.05},
                                      'households': {0: 2496548.8372093025, 1: 2519331.308411215, 2: 2547075.1173708923,
                                                     3: 2589143.396226415, 4: 2624209.4562647752, 5: 2654085.7819905216,
                                                     6: 2678782.8978622328, 7: 2698423.333333333, 8: 2718213.365155131,
                                                     9: 2738003.349282297, 10: 2757655.635491607,
                                                     11: 2775936.0884190295, 12: 2794070.2936928263,
                                                     13: 2812035.697057405, 14: 2828537.198067633,
                                                     15: 2844856.3134978227, 16: 2861038.7596899224,
                                                     17: 2875298.739088264, 18: 2889073.300970874,
                                                     19: 2900971.3453132585, 20: 2912422.7405247814,
                                                     21: 2923432.6689353427, 22: 2934010.214007782,
                                                     23: 2944133.333333333, 24: 2953807.6923076925,
                                                     25: 2962996.5903555774, 26: 2971682.7485380117,
                                                     27: 2979855.6801560214, 28: 2987490.7317073173,
                                                     29: 2993121.4634146346, 30: 2998205.365853659},
                                      'households_change': {0: np.nan, 1: 22782.4712019125, 2: 27743.80895967735,
                                                            3: 42068.27885552263, 4: 35066.0600383603,
                                                            5: 29876.32572574634, 6: 24697.11587171117,
                                                            7: 19640.435471100267, 8: 19790.031821798068,
                                                            9: 19789.98412716575, 10: 19652.28620930994,
                                                            11: 18280.45292742271, 12: 18134.205273796804,
                                                            13: 17965.403364578728, 14: 16501.50101022795,
                                                            15: 16319.115430189762, 16: 16182.446192099713,
                                                            17: 14259.979398341384, 18: 13774.561882609967,
                                                            19: 11898.044342384674, 20: 11451.395211522933,
                                                            21: 11009.92841056129, 22: 10577.545072439127,
                                                            23: 10123.119325551204, 24: 9674.358974359464,
                                                            25: 9188.898047884926, 26: 8686.158182434272,
                                                            27: 8172.931618009694, 28: 7635.05155129591,
                                                            29: 5630.731707317289, 30: 5083.902439024299},
                                      'building_growth': {0: np.nan, 1: 10285.183370024104, 2: 12475.764416060289,
                                                          3: 18842.517803515962, 4: 15643.987430018115,
                                                          5: 13275.689899102475, 6: 10930.465476125311,
                                                          7: 8657.630668147845, 8: 8688.462357892317,
                                                          9: 8653.330156248836, 10: 8558.25367179544,
                                                          11: 7928.40934223303, 12: 7832.806729553463,
                                                          13: 7728.021092473165, 14: 7069.03011018808,
                                                          15: 6961.945211750204, 16: 6874.929559675597,
                                                          17: 6032.891284168806, 18: 5803.08961893119,
                                                          19: 4991.421505571876, 20: 4783.727999652654,
                                                          21: 4579.775059812689, 22: 4381.150926778047,
                                                          23: 4174.970341199004, 24: 3972.728701406103,
                                                          25: 3757.073637320366, 26: 3536.106976203467,
                                                          27: 3312.673734848439, 28: 3081.112738926385,
                                                          29: 2262.2826907948092, 30: 2033.56097560972},
                                      'net_constructed_floor_area': {0: 0.0, 1: 0.0, 2: 2183258.7728105504,
                                                                     3: 3297440.6156152934, 4: 2737697.80025317,
                                                                     5: 2323245.7323429333, 6: 1912831.4583219294,
                                                                     7: 1515085.3669258729, 8: 1520480.9126311555,
                                                                     9: 1514332.7773435463, 10: 1497694.3925642022,
                                                                     11: 1387471.6348907803, 12: 1370741.177671856,
                                                                     13: 1352403.6911828038, 14: 1237080.269282914,
                                                                     15: 1218340.4120562857, 16: 1203112.6729432296,
                                                                     17: 1055755.974729541, 18: 1015540.6833129582,
                                                                     19: 873498.7634750783, 20: 837152.3999392145,
                                                                     21: 801460.6354672204, 22: 766701.4121861581,
                                                                     23: 730619.8097098257, 24: 695227.5227460681,
                                                                     25: 657487.886531064, 26: 618818.7208356068,
                                                                     27: 579717.9035984768, 28: 539194.7293121174,
                                                                     29: 395899.4708890916, 30: 355873.17073170096},
                                      'demolished_floor_area': {0: 0.0, 1: 864644.3575, 2: 1754542.5575,
                                                                3: 1754542.5575, 4: 1754542.5575, 5: 1754542.5575,
                                                                6: 1754542.5575, 7: 1754542.5575, 8: 1754542.5575,
                                                                9: 1754542.5575, 10: 1754542.5575, 11: 1754542.5575,
                                                                12: 2110501.8375000004, 13: 2110501.8375000004,
                                                                14: 2110501.8375000004, 15: 2110501.8375000004,
                                                                16: 2110501.8375000004, 17: 3048130.0, 18: 3048130.0,
                                                                19: 3048130.0, 20: 3048130.0, 21: 3048130.0,
                                                                22: 3048130.0, 23: 3048130.0, 24: 3048130.0,
                                                                25: 3048130.0, 26: 3048130.0, 27: 3423181.2650000006,
                                                                28: 3423181.2650000006, 29: 3423181.2650000006,
                                                                30: 3423181.2650000006},
                                      'constructed_floor_area': {0: 0.0, 1: 2733711.49774, 2: 3937801.3303105505,
                                                                 3: 5051983.1731152935, 4: 4492240.357753171,
                                                                 5: 4077788.2898429334, 6: 3667374.0158219296,
                                                                 7: 3269627.924425873, 8: 3275023.4701311556,
                                                                 9: 3268875.334843546, 10: 3252236.9500642023,
                                                                 11: 3142014.1923907804, 12: 3481243.0151718566,
                                                                 13: 3462905.528682804, 14: 3347582.106782914,
                                                                 15: 3328842.2495562863, 16: 3313614.51044323,
                                                                 17: 4103885.9747295408, 18: 4063670.683312958,
                                                                 19: 3921628.763475078, 20: 3885282.3999392143,
                                                                 21: 3849590.6354672206, 22: 3814831.412186158,
                                                                 23: 3778749.8097098256, 24: 3743357.522746068,
                                                                 25: 3705617.8865310643, 26: 3666948.7208356066,
                                                                 27: 4002899.1685984773, 28: 3962375.994312118,
                                                                 29: 3819080.735889092, 30: 3779054.4357317016},
                                      'accumulated_constructed_floor_area': {0: 0.0, 1: 2733711.49774,
                                                                             2: 6671512.82805055, 3: 11723496.001165845,
                                                                             4: 16215736.358919015,
                                                                             5: 20293524.64876195, 6: 23960898.66458388,
                                                                             7: 27230526.589009754,
                                                                             8: 30505550.05914091, 9: 33774425.39398445,
                                                                             10: 37026662.34404866,
                                                                             11: 40168676.53643943,
                                                                             12: 43649919.55161129,
                                                                             13: 47112825.080294095,
                                                                             14: 50460407.18707701,
                                                                             15: 53789249.4366333,
                                                                             16: 57102863.94707653,
                                                                             17: 61206749.92180607,
                                                                             18: 65270420.60511903,
                                                                             19: 69192049.36859411,
                                                                             20: 73077331.76853332,
                                                                             21: 76926922.40400054,
                                                                             22: 80741753.8161867,
                                                                             23: 84520503.62589653,
                                                                             24: 88263861.1486426,
                                                                             25: 91969479.03517367,
                                                                             26: 95636427.75600928,
                                                                             27: 99639326.92460775,
                                                                             28: 103601702.91891988,
                                                                             29: 107420783.65480897,
                                                                             30: 111199838.09054068},
                                      'building_category': {0: 'house', 1: 'house', 2: 'house', 3: 'house', 4: 'house',
                                                            5: 'house', 6: 'house', 7: 'house', 8: 'house', 9: 'house',
                                                            10: 'house', 11: 'house', 12: 'house', 13: 'house',
                                                            14: 'house', 15: 'house', 16: 'house', 17: 'house',
                                                            18: 'house', 19: 'house', 20: 'house', 21: 'house',
                                                            22: 'house', 23: 'house', 24: 'house', 25: 'house',
                                                            26: 'house', 27: 'house', 28: 'house', 29: 'house',
                                                            30: 'house'}})
    mock_calculator.return_value = mock_construction
    r = calculate_construction_by_building_category(demolition.demolition, mock_database_manager, YearRange(2020, 2050))

    expected = pd.Series({('house', 'TEK17', 2020.0): 0.0,
                          ('house', 'TEK17', 2021.0): 2733711.49774,
                ('house', 'TEK17', 2022.0): 6671512.82805055,
                          ('house', 'TEK17', 2023.0): 11723496.001165845,
                ('house', 'TEK17', 2024.0): 16215736.358919015,
                          ('house', 'TEK17', 2025.0): 20293524.64876195,
                ('house', 'TEK17', 2026.0): 23960898.66458388,
                          ('house', 'TEK17', 2027.0): 27230526.589009754,
                          ('house', 'TEK17', 2028.0): 30505550.05914091,
                          ('house', 'TEK17', 2029.0): 33774425.39398445,
                          ('house', 'TEK17', 2030.0): 37026662.34404866,
                          ('house', 'TEK17', 2031): 37026662.34404866,
                          ('house', 'TEK17', 2032): 37026662.34404866,
                          ('house', 'TEK17', 2033): 37026662.34404866,
                          ('house', 'TEK17', 2034): 37026662.34404866,
                          ('house', 'TEK17', 2035): 37026662.34404866,
                          ('house', 'TEK17', 2036): 37026662.34404866,
                          ('house', 'TEK17', 2037): 37026662.34404866,
                          ('house', 'TEK17', 2038): 37026662.34404866,
                          ('house', 'TEK17', 2039): 37026662.34404866,
                          ('house', 'TEK17', 2040): 37026662.34404866,
                          ('house', 'TEK17', 2041): 37026662.34404866,
                          ('house', 'TEK17', 2042): 37026662.34404866,
                          ('house', 'TEK17', 2043): 37026662.34404866,
                          ('house', 'TEK17', 2044): 37026662.34404866,
                          ('house', 'TEK17', 2045): 37026662.34404866,
                          ('house', 'TEK17', 2046): 37026662.34404866,
                          ('house', 'TEK17', 2047): 37026662.34404866,
                          ('house', 'TEK17', 2048): 37026662.34404866,
                          ('house', 'TEK17', 2049): 37026662.34404866,
                          ('house', 'TEK17', 2050): 37026662.34404866,
                          ('house', 'TEK30', 2020): 0.0,
                          ('house', 'TEK30', 2021): 0.0,
                          ('house', 'TEK30', 2022): 0.0,
                          ('house', 'TEK30', 2023): 0.0,
                          ('house', 'TEK30', 2024): 0.0,
                          ('house', 'TEK30', 2025): 0.0,
                          ('house', 'TEK30', 2026): 0.0,
                          ('house', 'TEK30', 2027): 0.0,
                          ('house', 'TEK30', 2028): 0.0,
                          ('house', 'TEK30', 2029): 0.0,
                          ('house', 'TEK30', 2030): 0.0,
                ('house', 'TEK30', 2031.0): 3142014.1923907804,
                ('house', 'TEK30', 2032.0): 6623257.207562637,
                          ('house', 'TEK30', 2033.0): 10086162.736245442,
                          ('house', 'TEK30', 2034.0): 13433744.843028355,
                ('house', 'TEK30', 2035.0): 16_762_587.092584642,
                          ('house', 'TEK30', 2036.0): 20076201.603027873,
                ('house', 'TEK30', 2037.0): 24_180_087.57775741,
                          ('house', 'TEK30', 2038.0): 28243758.26107037,
                ('house', 'TEK30', 2039.0): 32165387.02454545,
                          ('house', 'TEK30', 2040.0): 36050669.42448466,
                ('house', 'TEK30', 2041.0): 39900260.05995189,
                          ('house', 'TEK30', 2042.0): 43715091.47213804,
                ('house', 'TEK30', 2043.0): 47493841.281847864,
                          ('house', 'TEK30', 2044.0): 51237198.804593936,
                ('house', 'TEK30', 2045.0): 54942816.691125,
                          ('house', 'TEK30', 2046.0): 58609765.41196061,
                ('house', 'TEK30', 2047.0): 62612664.58055908,
                          ('house', 'TEK30', 2048.0): 66575040.5748712,
                ('house', 'TEK30', 2049.0): 70394121.31076029,
                ('house', 'TEK30', 2050.0): 74173175.746492,
                          })
    expected.name = 'area'
    expected.index.names=['building_category', 'building_code', 'year']

    df = r.sort_index().to_frame()
    df['left'] = expected
    pd.testing.assert_series_equal(r.sort_index(), expected)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
