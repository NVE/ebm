# noinspection PyTypeChecker
import numpy as np
import pandas as pd
import pytest

from ebm.model.area import (transform_area_forecast_to_area_change,
                            transform_construction_by_year,
                            transform_cumulative_demolition_to_yearly_demolition)


def test_transform_area_forecast_to_area_change():
    """
    Test that construction is the change in sum of area, demolition is a negative value. When no
    tek_parameters are provided, construction is assumed to be of TEK17.
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
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    result  = transform_area_forecast_to_area_change(area, None).reset_index(drop=True)

    expected = pd.DataFrame(
        [('house', 'TEK97', y, 'demolition', m2) for y, m2 in enumerate((0.0, -4.0, -5.0), start=2020)]+
        [('office', 'TEK17', y, 'demolition', m2) for y, m2 in enumerate((0.0, 0.0, -1.0), start=2020)]+
        [('house', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 21.0, 20.0), start=2020)]+
        [('office', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 2.0, 3.0), start=2020)]
    , columns=['building_category', 'TEK', 'year', 'demolition_construction', 'm2'])

    assert len(result) == 12

    pd.testing.assert_frame_equal(result, expected)


def test_transform_area_forecast_to_area_change_raises_value_error():
    """
    transform_area_forecast_to_area_change raise ValueError when area_forecast is None
    """

    tek_parameters = pd.DataFrame(data=[['TEK17', 2017, 2011, 2019]],
                                  columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_area_forecast_to_area_change(None, tek_parameters=tek_parameters)


def test_transform_construction_by_year():
    """
    Test that tek_parameters is used to figure out the correct TEK for construction In this case we expect that TEK21
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
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    tek_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2019], ['TEK21', 2021, 2020, 2050]],
        columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])

    result  = transform_construction_by_year(area, tek_parameters).reset_index().set_index(
        ['building_category', 'TEK', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=[('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 10.0, 14.0), start=2020)],
        columns=['building_category', 'TEK', 'year', 'm2']).set_index(['building_category', 'TEK', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_construction_by_year_expect_columns():
    """
    transform_construction_by_year should raise ValueError when expected columns are missing
    """
    area = pd.DataFrame(
        data=[('house', 'TEK21', 'construction', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]],
        columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])
    tek_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2019], ['TEK21', 2021, 2020, 2050]],
        columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])

    for expected_column in area.columns:
        with pytest.raises(ValueError):
            transform_construction_by_year(area.drop(columns=[expected_column]))

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_construction_by_year(area_forecast=None)

    for expected_column in tek_parameters.columns:
        with pytest.raises(ValueError):
            transform_construction_by_year(area, tek_parameters.drop(columns=[expected_column]))


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
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    result  = transform_cumulative_demolition_to_yearly_demolition(area).reset_index().set_index(
        ['building_category', 'TEK', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=
             [('house', 'TEK17', y, m2) for y, m2 in enumerate((np.nan, 2.0, 2.0), start=2020)]+
             [('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 0.0, 0.0), start=2020)]+
             [('house', 'TEK97', y, m2) for y, m2 in enumerate((np.nan, 10.0, 11), start=2020)],
        columns=['building_category', 'TEK', 'year', 'm2']).set_index(['building_category', 'TEK', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_accumulated_to_yearly_demolition_handle_disorganized_area():
    """
    Make sure transform_cumulative_demolition_to_yearly_demolition handle disorganized input
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0),  (2022, 21), (2021, 10)]]+
             [('house', 'TEK17', 'demolition', y, m2 ) for y, m2 in [(2021, 2.0), (2020, 0.0), (2022, 4.0)]]+
             [('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2022, 0.0), (2021, np.nan), (2020, np.nan)]]
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    result  = transform_cumulative_demolition_to_yearly_demolition(area).reset_index().set_index(
        ['building_category', 'TEK', 'year'])[['m2']]

    expected = pd.DataFrame(
        data=[('house', 'TEK17', y, m2) for y, m2 in enumerate((np.nan, 2.0, 2.0), start=2020)]+
             [('house', 'TEK21', y, m2) for y, m2 in enumerate((np.nan, 0.0, 0.0), start=2020)]+
             [('house', 'TEK97', y, m2) for y, m2 in enumerate((np.nan, 10.0, 11), start=2020)]
        , columns=['building_category', 'TEK', 'year', 'm2']).set_index(['building_category', 'TEK', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_transform_accumulated_to_yearly_demolition_expect_columns():
    """
    transform_cumulative_demolition_to_yearly_demolition should raise ValueError when expected columns are missing
    """
    area = pd.DataFrame(
        data=[('house', 'TEK21', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 0.0)]],
        columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    for expected_column in area.columns:
        with pytest.raises(ValueError):
            transform_cumulative_demolition_to_yearly_demolition(area.copy().drop(columns=[expected_column]))

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        transform_cumulative_demolition_to_yearly_demolition(None)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
