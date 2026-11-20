import pathlib
from importlib.resources import files

import pandas as pd
import pytest
from energibruksmodell.controllers import (
    calculate_area_forecast,
    calculate_energy_need,
    calculate_heating_systems,
    calculate_s_curves_by_condition,
)

from ebm import extractors
from ebm.areaforecast.s_curve import calculate_s_curves
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.model.heating_systems_parameter import heating_systems_parameter_from_projection


def controllers_s_curves_by_condition(input_directory, years: YearRange) -> pd.DataFrame:
    controller_scurves = calculate_s_curves_by_condition(input_directory=pathlib.Path(input_directory), years=years)
    return controller_scurves

EBM_TEST_DATA = pathlib.Path(__file__).parent.parent / 'ebm' / 'data'


@pytest.mark.parametrize(
    ('input_directory', 'years'),
    [
        pytest.param(EBM_TEST_DATA / 'kalibrert', YearRange(2020, 2050), id='kalibrert'),
        pytest.param(EBM_TEST_DATA / 'custom-building_category', YearRange(2020, 2030), id='custom-building_category'),
        pytest.param(files('ebm.data.short_analysis_2025'), YearRange(2020, 2030), id='data_short_analysis_2025'),
        pytest.param(files('ebm.data.long_analysis_2024'), YearRange(2020, 2050), id='data_long_analysis'),
    ],
)
def test_area_forecast(input_directory, years):
    """
    Test that area forecast calculated by the controller is equal to the area forecast calculated by the extractor.

    scurves_by_condition is calculated by the controller and passed to both the controller and the extractor to ensure
    s_curves_by_condition is the same for both calculations.
    """
    extractor_dm = DatabaseManager(FileHandler(input_directory))
    s_curves_by_condition = controllers_s_curves_by_condition(input_directory=input_directory, years=years)

    extractor_af = extractors.extract_area_forecast(
        years=years,
        s_curves_by_condition=s_curves_by_condition,
        building_code_parameters=extractor_dm.get_building_codes(),
        area_parameters=extractor_dm.get_area_parameters(),
        database_manager=extractor_dm,
    )

    controller_af = calculate_area_forecast(
        input_directory=pathlib.Path(input_directory),
        s_curves_by_condition=s_curves_by_condition,
        years=years,
    )

    pd.testing.assert_frame_equal(controller_af, extractor_af, check_dtype=False)


@pytest.mark.parametrize(
    ('input_directory', 'years'),
    [
        pytest.param(EBM_TEST_DATA / 'kalibrert', YearRange(2020, 2050), id='kalibrert'),
        pytest.param(EBM_TEST_DATA / 'custom-building_category', YearRange(2020, 2030), id='custom-building_category'),
        pytest.param(files('ebm.data.short_analysis_2025'), YearRange(2020, 2030), id='data_short_analysis_2025'),
        pytest.param(files('ebm.data.long_analysis_2024'), YearRange(2020, 2050), id='data_long_analysis'),
    ],
)
def test_scurves(input_directory, years):
    controller_scurves = calculate_s_curves_by_condition(input_directory=pathlib.Path(input_directory), years=years)

    extractor_dm = DatabaseManager(FileHandler(input_directory))
    extrator_scurves = calculate_s_curves(extractor_dm.get_scurve_params(), extractor_dm.get_building_codes(), years)

    pd.testing.assert_frame_equal(controller_scurves, extrator_scurves, check_dtype=False)
    pd.testing.assert_frame_equal(controller_scurves, controllers_s_curves_by_condition(input_directory=input_directory, years=years), check_dtype=False)


ENERGY_NEED_COLUMNS = [
    'building_category',
    'building_code',
    'purpose',
    'building_condition',
    'year',
    'kwh_m2',
    'reduction_condition',
    'factor_yearly_reduction_1',
    'reduction_yearly',
    'reduction_policy',
    'behavior_kwh_m2',
    'reduced_kwh_m2',
]


@pytest.mark.parametrize(
    ('input_directory', 'years'),
    [
        pytest.param(EBM_TEST_DATA / 'kalibrert', YearRange(2020, 2050), id='kalibrert'),
        pytest.param(EBM_TEST_DATA / 'custom-building_category', YearRange(2020, 2030), id='custom-building_category'),
        pytest.param(files('ebm.data.short_analysis_2025'), YearRange(2020, 2030), id='data_short_analysis_2025'),
    ],
)
def test_energy_need(input_directory, years):
    controller_energy_need = calculate_energy_need(
        years=years,
        input_directory=input_directory,
    )

    extractor_dm = DatabaseManager(FileHandler(input_directory))
    extractor_energy_need = extractors.extract_energy_need(
        years=years,
        dm=extractor_dm,
    )

    pd.testing.assert_frame_equal(
        left=controller_energy_need.reset_index()[ENERGY_NEED_COLUMNS],
        right=extractor_energy_need.reset_index()[ENERGY_NEED_COLUMNS],
        check_dtype=False,
    )


@pytest.mark.explicit
def test_energy_need_long_analysis_2024():
    """
    test_energy_need is slow. long analysis 2024 is makes it slower. The test will only run when explicitly requested.
    """
    input_directory = files('ebm.data.long_analysis_2024')
    years = YearRange(2020, 2050)

    controller_energy_need = calculate_energy_need(
        years=years,
        input_directory=input_directory,
    )

    extractor_dm = DatabaseManager(FileHandler(input_directory))
    extractor_energy_need = extractors.extract_energy_need(
        years=years,
        dm=extractor_dm,
    )

    pd.testing.assert_frame_equal(
        left=controller_energy_need.reset_index()[ENERGY_NEED_COLUMNS],
        right=extractor_energy_need.reset_index()[ENERGY_NEED_COLUMNS],
        check_dtype=False,
    )


@pytest.mark.parametrize(
    ('input_directory', 'years'),
    [
        pytest.param(EBM_TEST_DATA / 'kalibrert', YearRange(2020, 2050), id='tests_kalibrert'),
        pytest.param(EBM_TEST_DATA / 'custom-building_category', YearRange(2020, 2030), id='tests_custom-building_category'),
        pytest.param(files('ebm.data.short_analysis_2025'), YearRange(2020, 2030), id='data_short_analysis_2025'),
        pytest.param(files('ebm.data.long_analysis_2024'), YearRange(2020, 2050), id='data_long_analysis'),
    ],
)
def test_heating_systems(input_directory, years):
    controller_hs_projection = calculate_heating_systems(input_directory=input_directory, years=years)

    extractor_dm = DatabaseManager(FileHandler(input_directory))
    extractor_hs_forecast = extractors.extract_heating_systems_forecast(
        years=years,
        database_manager=extractor_dm,
    )
    extractor_hs_projection = heating_systems_parameter_from_projection(extractor_hs_forecast)

    pd.testing.assert_frame_equal(
        left=controller_hs_projection.reset_index(drop=True),
        right=extractor_hs_projection.reset_index(drop=True),
        check_dtype=False,
    )


if __name__ == '__main__':
    import sys

    pytest.main([sys.argv[0]])
