# noinspection PyTypeChecker
import io
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from ebm.model.area import (
    building_condition_scurves,
    construction_with_building_code,
    transform_area_forecast_to_area_change,
    transform_construction_by_year,
    transform_cumulative_demolition_to_yearly_demolition,
)
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
        data=[('house', 'TEK97', 'original_condition', y, m2) for y, m2 in
                [(2020, 100), (2021, 90), (2022, 80), (2023,70)]]+
             [('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in
                [(2020, 0), (2021, 10), (2022, 20), (2023, 30)]]+
             [('house', 'TEK17', 'original_condition', y, m2 ) for y, m2 in
                [(2020, 100), (2021, 110), (2022, 110), (2023, 110)]]+
             [('house', 'TEK17', 'demolition', y, m2 ) for y, m2 in
                [(2020, 0.0), (2021, 0.0), (2022, 0.0), (2023, 0.0)]]+
             [('house', 'TEK22', 'demolition', y, m2) for y, m2 in
                [(2020, np.nan), (2021, np.nan), (2022, 0.0), (2023, 0.0)]] +
             [('house', 'TEK22', 'renovation', y, m2) for y, m2 in
                [(2020, np.nan), (2021, np.nan), (2022, 1.0), (2023, 1.5)]] +
             [('house', 'TEK22', 'original_condition', y, m2 ) for y, m2 in
                [(2020, 0), (2021, np.nan), (2022, 11.0), (2023, 22.0)]]
        ,columns=['building_category', 'building_code', 'building_condition', 'year', 'm2'])

    building_code_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2021], ['TEK22', 2022, 2022, 2050]],
        columns=['building_code', 'building_year', 'period_start_year', 'period_end_year'])

    result  = transform_construction_by_year(area, building_code_parameters).reset_index().set_index(
        ['building_category', 'building_code', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=[('house', 'TEK17', 2020, np.nan), ('house', 'TEK17', 2021, 10.0), #('house', 'TEK17', 2022, 0.0), ('house', 'TEK17', 2023, 0.0),
              ('house', 'TEK22', 2020, np.nan), ('house', 'TEK22', 2021, 0.0), ('house', 'TEK22', 2022, 12.0), ('house', 'TEK22', 2023, 11.5)],
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


def test_construction_with_building_code():
    years = YearRange(2020, 2024)
    demolition_by_year = [0.0, 1, 1, 1, 1] + [0.0, 2, 2, 2, 2]
    construction_by_year = [0.0, 1.0, 1.0, 1.0, 1.0] + [ 2.0, 2.0, 2.0, 2.0, 2.0]

    demolition = pd.DataFrame({'demolition': demolition_by_year},
                              index=pd.Index([('house', y) for y in years] + [('retail', y) for y in years]
                                             , name=('building_category', 'year')))
    building_code = pd.DataFrame(
        [{'building_code': 'TEK0X', 'building_year': 2010.0, 'period_start_year': 1945, 'period_end_year': years.start -1},
         {'building_code': 'TEKAA', 'building_year': years.start + 2, 'period_start_year': years.start, 'period_end_year': years.end}])

    mock_database_manager = DatabaseManager()
    mock_database_manager.get_building_codes = MagicMock(return_value=building_code)

    mock_construction = pd.DataFrame(
        {'year': list(years) + list(years), 'constructed_floor_area': construction_by_year,
         'building_category': ['house' for y in years] + ['retail' for y in years]})

    result = construction_with_building_code(building_category_demolition_by_year=demolition.demolition, construction_floor_area_by_year=mock_construction,
                                             building_code=building_code,
                                             years=years)

    expected_construction = pd.Series({('house', 'TEKAA', 2020): 0.0, ('house', 'TEKAA', 2021): 1.0, ('house', 'TEKAA', 2022): 2.0,
                          ('house', 'TEKAA', 2023): 3.0, ('house', 'TEKAA', 2024): 4.0,
                          ('retail', 'TEKAA', 2020): 2.0, ('retail', 'TEKAA', 2021): 4.0,
                          ('retail', 'TEKAA', 2022): 6.0, ('retail', 'TEKAA', 2023): 8.0, ('retail', 'TEKAA', 2024): 10.0})
    expected_construction.name = 'net_construction_acc'
    expected_construction.index.names = ['building_category', 'building_code', 'year']

    pd.testing.assert_series_equal(result.net_construction_acc, expected_construction)

    expected_net_construction = pd.Series({('house', 'TEKAA', 2020): 0.0, ('house', 'TEKAA', 2021): 1.0, ('house', 'TEKAA', 2022): 1.0,
                          ('house', 'TEKAA', 2023): 1.0, ('house', 'TEKAA', 2024): 1.0,
                          ('retail', 'TEKAA', 2020): 2.0, ('retail', 'TEKAA', 2021): 2.0,
                          ('retail', 'TEKAA', 2022): 2.0, ('retail', 'TEKAA', 2023): 2.0, ('retail', 'TEKAA', 2024): 2.0})
    expected_net_construction.name = 'net_construction'
    expected_net_construction.index.names = ['building_category', 'building_code', 'year']

    pd.testing.assert_series_equal(result.net_construction, expected_net_construction)


@pytest.mark.parametrize("years_parameter", [YearRange(2020, 2029), None])
def test_construction_with_building_code_more_than_one_building_code(years_parameter):
    years = YearRange(2020, 2029)
    demolition_by_year = [0.0, 1, 1, 1, 1] + [2, 2, 2, 2, 2]
    construction_by_year = [0.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    demolition = pd.Series(demolition_by_year, name='demolition',
                              index=pd.Index([('house', y) for y in years], name=('building_category', 'year')))
    building_code = pd.DataFrame(
        [{'building_code': 'TEK0X', 'building_year': 2010.0, 'period_start_year': 1945, 'period_end_year': 2019.0},
         {'building_code': 'TEK17', 'building_year': 2025.0, 'period_start_year': 2020.0, 'period_end_year': 2026.0},
         {'building_code': 'TEK21', 'building_year': 2027.0, 'period_start_year': 2027.0, 'period_end_year': 2029.0}])

    mock_database_manager = DatabaseManager()
    mock_database_manager.get_building_codes = MagicMock(return_value=building_code)

    mock_construction = pd.DataFrame(
        {'year': years, 'constructed_floor_area': construction_by_year, 'building_category': ['house'] * len(years)})

    r = construction_with_building_code(demolition, building_code=building_code,
                                        construction_floor_area_by_year=mock_construction,
                                        years=years_parameter).net_construction_acc

    expected = pd.Series({('house', 'TEK17', 2020): 0.0, ('house', 'TEK17', 2021): 1.0, ('house', 'TEK17', 2022): 2.0,
                          ('house', 'TEK17', 2023): 3.0, ('house', 'TEK17', 2024): 4.0, ('house', 'TEK17', 2025): 6.0,
                          ('house', 'TEK17', 2026): 8.0, ('house', 'TEK17', 2027): 8.0, ('house', 'TEK17', 2028): 8.0,
                          ('house', 'TEK17', 2029): 8.0, ('house', 'TEK21', 2020): 0.0, ('house', 'TEK21', 2021): 0.0,
                          ('house', 'TEK21', 2022): 0.0, ('house', 'TEK21', 2023): 0.0, ('house', 'TEK21', 2024): 0.0,
                          ('house', 'TEK21', 2025): 0.0, ('house', 'TEK21', 2026): 0.0, ('house', 'TEK21', 2027): 2.0,
                          ('house', 'TEK21', 2028): 4.0, ('house', 'TEK21', 2029): 6.0})
    expected.name = 'net_construction_acc'
    expected.index.names = ['building_category', 'building_code', 'year']

    pd.testing.assert_series_equal(r.sort_index(), expected)



if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
