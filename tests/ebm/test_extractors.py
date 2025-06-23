import pathlib

import pandas as pd
import pytest

from ebm.extractors import extract_area_forecast
from ebm.model.bema import map_sort_order
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.s_curve import calculate_s_curves

test_data = pathlib.Path(__file__).parent / 'data'

@pytest.fixture
def extract_area_forecast_csv():
    """
    Load and decompress (revert column merge) extract_area_forecast.csv
    """
    df = pd.read_csv(test_data / 'extract_area_forecast.csv', sep=';')
    df = df.ffill()
    df['TEK'] = df['TEK'].str.replace('T', 'TEK').str.replace('P', 'PRE_')
    df['year'] = df['year'].astype(int)

    return df


def test_extract_area_forecast(extract_area_forecast_csv: pd.DataFrame):
    """
    Integration test to keep area working while doing refactor.
    """

    input_directory = test_data / 'kalibrert'

    dm: DatabaseManager = DatabaseManager(FileHandler(directory=input_directory))
    years: YearRange = YearRange(2020, 2050)
    scurve_parameters: pd.DataFrame = dm.get_scurve_params()
    tek_parameters: pd.DataFrame = dm.file_handler.get_tek_params()
    area_parameters: pd.DataFrame = dm.get_area_parameters()

    s_curves_by_condition = calculate_s_curves(scurve_parameters, tek_parameters, years)
    index_columns = ['year', 'building_category', 'building_condition', 'TEK']
    result = extract_area_forecast(years, s_curves_by_condition, tek_parameters, area_parameters, dm)
    result = result.set_index(index_columns, drop=True).sort_index(key=map_sort_order)

    expected = extract_area_forecast_csv.set_index(index_columns, drop=True).sort_index(key=map_sort_order) # type: ignore

    assert isinstance(result, pd.DataFrame)
    # assert result.m2.sum() == expected.m2.sum()
    # assert len(result) == len(expected)

    pd.testing.assert_index_equal(result.index, expected.index)
    pd.testing.assert_frame_equal(result, expected)


def decompress(expected):

    return expected


