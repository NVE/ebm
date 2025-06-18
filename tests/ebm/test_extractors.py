import socket

import pandas as pd
import pytest

from ebm.extractors import extract_area_forecast
from ebm.model.bema import map_sort_order
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler


@pytest.mark.skipif(socket.gethostname()!='JDJSBS3', reason='Test is only useable locally')
def test_extract_area_forecast():
    """
    Integration test to keep area working while doing refactor.

    This test will not run on azure, currently.
    """

    dm: DatabaseManager = DatabaseManager(FileHandler(directory=r'C:\Users\kenord\pyc\workspace\t2734_input'))
    years: YearRange = YearRange(2020, 2050)
    scurve_parameters: pd.DataFrame = dm.get_scurve_params()
    tek_parameters: pd.DataFrame = dm.file_handler.get_tek_params()
    area_parameters: pd.DataFrame = dm.get_area_parameters()

    result = (extract_area_forecast(years, scurve_parameters, tek_parameters, area_parameters, dm)
           .set_index(['building_category', 'TEK', 'year', 'building_condition'], drop=True)
           .sort_index(key=map_sort_order))

    expected = (pd.read_csv(r'C:\Users\kenord\pyc\workspace\output\area_dataframes.csv', sep=';')
                .set_index(['building_category', 'TEK', 'year', 'building_condition'], drop=True)
                .sort_index(key=map_sort_order))

    assert isinstance(result, pd.DataFrame)
    # assert result.m2.sum() == expected.m2.sum()
    # assert len(result) == len(expected)

    pd.testing.assert_index_equal(result.index, expected.index)
    pd.testing.assert_frame_equal(result, expected)


