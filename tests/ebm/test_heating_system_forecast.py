import io
import re

import pandas as pd
import pytest
from loguru import logger

from ebm.heating_system_forecast import (
    HeatingSystemsForecast,
    add_existing_heating_system_shares_to_projection,
    add_missing_heating_systems,
    check_sum_of_shares,
    project_heating_systems,
)
from ebm.model.data_classes import YearRange

BUILDING_CATEGORY = 'building_category'
BUILDING_CODE = 'building_code'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
HEATING_SYSTEM_SHARE = 'heating_system_share'


@pytest.fixture
def building_code_list():
    return ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17']


def test_validate_years_require_one_start_year():
    """ValueError if there is more than one start year in the 'shares_start_year' dataframe."""
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2021,1
kindergarten,TEK97,Gas,2020,1
""".strip()),
                                    names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    with pytest.raises(ValueError, match=re.escape('More than one start year in dataframe.')):
        HeatingSystemsForecast(shares_start_year=shares_start_year,
                               efficiencies=pd.DataFrame(),
                               forecast=pd.DataFrame(),
                               building_code_list=[],
                               period=YearRange(2020,2022))


def test_validate_years_require_match_on_start_year():
    """ValueError if the start_year of the period is not equal to the start year in the 'shares_start_year' dataframe."""
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5
""".strip()),
                                    names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    with pytest.raises(ValueError, match=re.escape("Start year in dataframe doesn't match start year for given period.")):
        HeatingSystemsForecast(shares_start_year=shares_start_year,
                               efficiencies=pd.DataFrame(),
                               forecast=pd.DataFrame(),
                               building_code_list=[],
                               period=YearRange(2021,2023))


def test_validate_years_require_matching_years_between_dataframes():
    """ValueError if the start_year in 'projection' is not equal to one year after the start year in 'shares_start_year'."""
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5
""".strip()),
                                    names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.55
house,TEK97,Electricity,DH,0.25,0.5,0.55
apartment_block,TEK07,Electricity,DH,0.25,0.5,0.55
""".strip()),
                             names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS, 2020, 2021, 2022], skipinitialspace=True)


    with pytest.raises(ValueError, match=re.escape("Years don't match between dataframes.")):
        HeatingSystemsForecast(shares_start_year=shares_start_year,
                               efficiencies=pd.DataFrame(),
                               forecast=projection,
                               building_code_list=[],
                               period=YearRange(2020,2022))


def test_validate_years_require_period_years_present_in_projection():
    """ValueError if the years in the given 'period' is not present in the years col of the 'projection' dataframe."""
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5
""".strip()),
                                    names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.55
house,TEK97,Electricity,DH,0.25,0.5,0.55
apartment_block,TEK07,Electricity,DH,0.25,0.5,0.55
""".strip()),
                             names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS, 2021, 2022, 2023], skipinitialspace=True)

    with pytest.raises(ValueError, match=re.escape("Years in dataframe not present in given period.")):
        HeatingSystemsForecast(shares_start_year=shares_start_year,
                               efficiencies=pd.DataFrame(),
                               forecast=projection,
                               building_code_list=[],
                               period=YearRange(2020,2030))


def test_add_missing_heating_systems_ok():
    """Test that missing heating systems are added with default value = 0."""
    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5
""".strip()),
                         names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    result = add_missing_heating_systems(shares)

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5
kindergarten,TEK97,Electric boiler,2020,0.0
kindergarten,TEK97,Electricity,2020,0.0
kindergarten,TEK97,Gas,2020,0.0
kindergarten,TEK97,Electricity - Bio,2020,0.0
kindergarten,TEK97,DH - Bio,2020,0.0
kindergarten,TEK97,HP - Bio - Electricity,2020,0.0
kindergarten,TEK97,HP - Electricity,2020,0.0
kindergarten,TEK97,HP Central heating - Electric boiler,2020,0.0
kindergarten,TEK97,HP Central heating - Gas,2020,0.0
kindergarten,TEK97,Electric boiler - Solar,2020,0.0
kindergarten,TEK97,HP Central heating - Bio,2020,0.0
""".strip()),
                           names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS])
    result = result.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS])
    expected.reset_index(drop=True, inplace=True) # noqa: PD002
    result.reset_index(drop=True, inplace=True) # noqa: PD002

    pd.testing.assert_frame_equal(result, expected)


def test_add_missing_heating_systems_require_start_year_match():
    """Raise ValueError if given start year doesn't match year in input file."""
    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5
""".strip()),
                         names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    with pytest.raises(ValueError): # noqa: PT011
        add_missing_heating_systems(shares, start_year=2023)


def test_project_heating_systems_ok():
    shares_start_year_all_systems = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,DH,2020,0.0
""".strip()),
                                                names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    projected_shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5
""".strip()),
                                   names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS, 2021, 2022], skipinitialspace=True)

    result = project_heating_systems(shares_start_year_all_systems, projected_shares, YearRange(2020,2022))

    expected = pd.read_csv(io.StringIO("""
2021,kindergarten,TEK97,DH,0.25
2022,kindergarten,TEK97,DH,0.5
2021,kindergarten,TEK97,Electricity,0.75
2022,kindergarten,TEK97,Electricity,0.5
""".strip()),
                           names=[YEAR, BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    expected.reset_index(drop=True, inplace=True) # noqa: PD002
    result.reset_index(drop=True, inplace=True) # noqa: PD002

    pd.testing.assert_frame_equal(result, expected)


def test_project_heating_systems_different_years_in_data():
    shares_start_year_all_systems = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2022,1
kindergarten,TEK97,DH,2022,0.0
""".strip()),
                                                names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    projected_shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.75
""".strip()),
                                   names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS, 2021, 2022, 2023], skipinitialspace=True)

    result = project_heating_systems(shares_start_year_all_systems, projected_shares, YearRange(2022,2023))

    expected = pd.read_csv(io.StringIO("""
2023,kindergarten,TEK97,DH,0.75
2023,kindergarten,TEK97,Electricity,0.25
""".strip()),
                           names=[YEAR, BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    expected.reset_index(drop=True, inplace=True) # noqa: PD002
    result.reset_index(drop=True, inplace=True) # noqa: PD002

    pd.testing.assert_frame_equal(result, expected)


def test_add_existing_heating_system_shares_to_projection_ok():
    """Test that function returns expected result with ok input."""
    projected_shares = pd.read_csv(io.StringIO("""
2021,kindergarten,TEK97,DH,0.25
2022,kindergarten,TEK97,DH,0.5
2021,kindergarten,TEK97,Electricity,0.75
2022,kindergarten,TEK97,Electricity,0.5
""".strip()),
                                   names=[YEAR, BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,Gas,2020,1
""".strip()),
                         names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    result = add_existing_heating_system_shares_to_projection(projected_shares,
                                                   shares,
                                                   period=YearRange(2020,2022))

    #TODO: should DH = 0 in 2020 also be included in results?
    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,Electricity,2021,0.75
kindergarten,TEK97,Electricity,2022,0.5
kindergarten,TEK97,DH,2021,0.25
kindergarten,TEK97,DH,2022,0.5
kindergarten,TEK97,Gas,2020,1
kindergarten,TEK97,Gas,2021,1
kindergarten,TEK97,Gas,2022,1
""".strip()),
                           names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    expected.reset_index(drop=True, inplace=True) # noqa: PD002
    result.reset_index(drop=True, inplace=True) # noqa: PD002
    pd.testing.assert_frame_equal(result, expected)


def test_check_sum_of_shares_use_log_error():
    """Make sure that check_sum_of_share log error when the sum of heating_system_share is not equal to 1."""
    projected_shares = pd.read_csv(io.StringIO("""
house,TEK97,DH,2020,0.5
house,TEK97,Electricity,2020,0.5
house,TEK97,DH,2021,0.5
house,TEK97,Electricity,2021,0.5
house,TEK07,Gas,2020,0.5
house,TEK07,DH,2020,0.5
house,TEK07,Gas,2021,0.4
house,TEK07,DH,2021,0.5
kindergarten,TEK97,DH,2020,0.4
kindergarten,TEK97,Gas,2020,0.5
kindergarten,TEK97,DH,2021,0.5
kindergarten,TEK97,Gas,2021,0.5
""".strip()), names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    messages = []

    def sink(msg) -> None:
        messages.append(msg.split(' - ')[-1].strip())

    logger.add(sink, level="ERROR")
    check_sum_of_shares(projected_shares, precision=1)
    assert "('kindergarten', 'TEK97', 2020): {'heating_system_share': 0.9}" in messages
    assert "('house', 'TEK07', 2021): {'heating_system_share': 0.9}" in messages
    assert len(messages) > 2, 'Expected at least 2 messages in error log'
    logger.remove()


def test_check_sum_of_shares_ignore_tiny_deviations():
    """Make sure that check_sum_of_share does not log error when the sum of heating_system_share similar enough to 1."""
    projected_shares = pd.read_csv(io.StringIO("""
house,TEK97,DH,2020,0.50000001
house,TEK97,Electricity,2020,0.5
house,TEK97,DH,2021,0.5
house,TEK97,Electricity,2021,0.5
""".strip()), names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    messages = []

    def sink(msg) -> None:
        messages.append(msg.split(' - ')[-1].strip())

    logger.add(sink, level="ERROR")
    check_sum_of_shares(projected_shares, precision=5)
    assert len(messages) == 0, 'Expected empty error log when the difference is tiny'
    logger.remove()


def test_calculate_forecast_ok(building_code_list):
    """Test that calculate_forecast method runs ok with input that is correct."""
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5
""".strip()),
                                    names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE], skipinitialspace=True)

    efficiencies = pd.read_csv(io.StringIO("""
Electric boiler,0
DH,0
Electricity,0
Gas,0
Electricity - Bio,0
DH - Bio,0
HP - Bio,0
HP - Electricity,0
HP Central heating - DH,0
HP Central heating,0
HP Central heating - Gas,0
Electric boiler - Solar,0
HP Central heating - Bio,0
""".strip()),
names=[HEATING_SYSTEMS, 'Value'], skipinitialspace=True)

    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.5,0.5,1
""".strip()),
                             names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS, 2021, 2022, 2023, 2024, 'lineno'], skipinitialspace=True)

    hsp = HeatingSystemsForecast(shares_start_year=shares_start_year,
                                 efficiencies=efficiencies,
                                 forecast=projection,
                                 building_code_list=building_code_list,
                                 period=YearRange(2020,2022))

    result = hsp.calculate_forecast()

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5,0
kindergarten,TEK97,Electricity,2021,0.375,0
kindergarten,TEK97,Electricity,2022,0.25,0
kindergarten,TEK97,DH,2021,0.125,0
kindergarten,TEK97,DH,2022,0.25,0
kindergarten,TEK97,Gas,2020,0.5,0
kindergarten,TEK97,Gas,2021,0.5,0
kindergarten,TEK97,Gas,2022,0.5,0
""".strip()),
                           names=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR, HEATING_SYSTEM_SHARE, 'Value'], skipinitialspace=True)

    # dataframe formatting
    expected = expected.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY, BUILDING_CODE, HEATING_SYSTEMS, YEAR])
    expected.reset_index(drop=True, inplace=True) # noqa: PD002
    result.reset_index(drop=True, inplace=True) # noqa: PD002

    pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    pytest.main()

