import io
from pathlib import Path

import pandas as pd


def test_area_new_residential_buildings():
    """Make sure area_new_residential_buildings is correct."""
    ebm_data = Path(__file__).parent.parent.parent.parent / 'ebm' / 'data'
    df: pd.DataFrame = pd.read_csv(ebm_data / 'area_new_residential_buildings.csv')

    assert 'year' in df.columns
    assert 'house' in df.columns
    assert 'apartment_block' in df.columns

    expected = pd.read_csv(io.StringIO("""
year,house,apartment_block
2020,"0.0","0.0"
2021,"2733711.49774",1152796""".strip()))

    pd.testing.assert_frame_equal(df, expected)
