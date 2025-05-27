import numpy as np
import pandas as pd

from ebm.model.area import transform_area_forecast_to_area_change


def test_transform_area_forecast_to_area_change():
    """
    Test that construction is the change in sum of area, demolition is a negative value. When no
    tek_parameters are provided, construction is assumed to be of TEK17.
    """
    area = pd.DataFrame(
        data=[('house', 'TEK97', 'original_condition', y, m2) for y, m2 in [(2020, 100), (2021, 90), (2022, 80)]]+
             [('house', 'TEK97', 'renovation', y, m2 ) for y, m2 in [(2020, 0), (2021, 6), (2022, 12)]]+
             [('house', 'TEK97', 'demolition', y, m2 ) for y, m2 in [(2020, 0), (2021, 4), (2022, 8)]]+
             [('house', 'TEK17', 'renovation', y, m2 ) for y, m2 in [(2020, 0), (2021, 0), (2022, 4)]]+
             [('house', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 100), (2021, 120), (2022, 135)]]+
             [('house', 'TEK17', 'small_measure', y, m2 ) for y, m2 in [(2020, 1), (2021, 2), (2022, 3)]]+
             [('office', 'TEK17', 'demolition', y, m2) for y, m2 in [(2020, np.nan), (2021, np.nan), (2022, 1.0)]] +
             [('office', 'TEK17', 'original_condition', y, m2 ) for y, m2 in [(2020, 20), (2021, 22), (2022, 25)]]
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])
    result  = transform_area_forecast_to_area_change(area, None).reset_index(drop=True)

    expected = pd.DataFrame(
        [('house', 'TEK97', y, 'demolition', m2) for y, m2 in enumerate((0.0, -4.0, -8.0), start=2020)]+
        [('office', 'TEK17', y, 'demolition', m2) for y, m2 in enumerate((0.0, 0.0, -1.0), start=2020)]+
        [('house', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 21.0, 20.0), start=2020)]+
        [('office', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((0.0, 2.0, 3.0), start=2020)]
    , columns=['building_category', 'TEK', 'year', 'demolition_construction', 'm2'])

    assert len(result) == 12

    pd.testing.assert_frame_equal(result, expected)


def test_transform_area_forecast_to_area_change_use_correct_tek_for_construction():
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
             [('house', 'TEK21', 'original_condition', y, m2 ) for y, m2 in [(2020, 10.0), (2021, 20.0), (2022, 33.0)]]
        ,columns=['building_category', 'TEK', 'building_condition', 'year', 'm2'])

    tek_parameters = pd.DataFrame(
        data=[['TEK97', 2012, 0, 2010], ['TEK17', 2017, 2011, 2019], ['TEK21', 2021, 2020, 2050]],
        columns=['TEK', 'building_year', 'period_start_year', 'period_end_year'])

    result  = transform_area_forecast_to_area_change(area, tek_parameters).reset_index(drop=True)

    expected = pd.DataFrame(
        [('house', 'TEK97', y, 'demolition', m2) for y, m2 in enumerate((0.0, -10.0, -20.0), start=2020)]+
        [('house', 'TEK17', y, 'demolition', m2) for y, m2 in enumerate((0.0, 0.0, 0.0), start=2020)]+
        [('house', 'TEK21', y, 'demolition', m2) for y, m2 in enumerate((0.0, 0.0, 0.0), start=2020)]+
        [('house', 'TEK21', y, 'construction', m2) for y, m2 in enumerate((0.0, 10.0, 13.0), start=2020)]
    , columns=['building_category', 'TEK', 'year', 'demolition_construction', 'm2'])

    pd.testing.assert_frame_equal(result, expected)
