import numpy as np
import pandas as pd

from ebm.model.area import transform_area_forecast_to_area_change


def test_transform_area_forecast_to_area_change():
    """Test that construction is the sum of area"""
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
    result  = transform_area_forecast_to_area_change(area).reset_index(drop=True)

    expected = pd.DataFrame(
        [('house', 'TEK97', y, 'demolition', m2) for y, m2 in enumerate((0.0, -4.0, -8.0), start=2020)]+
        [('office', 'TEK17', y, 'demolition', m2) for y, m2 in enumerate((np.nan, np.nan, -1.0), start=2020)]+
        [('house', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((np.nan, 21.0, 20.0), start=2020)]+
        [('office', 'TEK17', y, 'construction', m2) for y, m2 in enumerate((np.nan, 2.0, 3.0), start=2020)]
    , columns=['building_category', 'TEK', 'year', 'demolition_construction', 'm2'])

    assert len(result) == 12

    pd.testing.assert_frame_equal(result, expected)

