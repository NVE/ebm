import io
import os

import pandas as pd

from ebm.energy_consumption import calibrate_heating_systems


def test_heating_system_calibration_reduce_other_type():
    df = pd.read_csv(io.StringIO("""building_category,TEK,TEK_shares,heating_systems,year
apartment_block,TEK07,0.5,Electricity,2023
apartment_block,TEK07,0.5,Gas,2023
house,TEK07,0.5,DH,2023
house,TEK07,0.5,DH-Bio,2023
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
apartment_block,Electricity,1.1,Gas
house,DH-Bio,2,DH
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
apartment_block,TEK07,2023,Electricity,0.55
apartment_block,TEK07,2023,Gas,0.45
house,TEK07,2023,DH,0.0
house,TEK07,2023,DH-Bio,1.0
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_keep_uncalibrated_heating_systems_in_frame():
    """
    Make sure any heating system value in the original dataframe remains untouched when no related calibration is
    present. In this case DH - Gas should be kept as is in the result.

    """
    df = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH,0.5
house,TEK07,2023,DH-Bio,0.25
house,TEK07,2023,DH-Gas,0.25
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
house,DH,1.1,DH-Bio
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH,0.55
house,TEK07,2023,DH-Bio,0.20
house,TEK07,2023,DH-Gas,0.25
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_can_add_to_duplicate_to_value():
    """

    """
    df = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH-Ingen,0.50
house,TEK07,2023,DH-Bio,0.25
house,TEK07,2023,DH-Gas,0.25
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
house,DH-Ingen,1.1,DH-Bio
house,DH-Ingen,1.1,DH-Gas
    """.strip()))

    result = calibrate_heating_systems(df, cal).reset_index(drop=True)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH-Ingen,0.6
house,TEK07,2023,DH-Bio,0.2
house,TEK07,2023,DH-Gas,0.2
""".strip()))

    # Alternative/correct non-parallel result:
    # Bolig, house, TEK07, 0.30, DH, 0.95, Elec, 0.05
    # Bolig, house, TEK07, 0.15, DH, 0.95, Gas, 0.05

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_works_with_no_calibration():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """

    df = pd.read_csv(io.StringIO("""building_category,TEK,TEK_shares,heating_systems,year
house,TEK07,0.5,DH-Ingen,0.0,2023
house,TEK07,0.25,DH-Bio,0.05,2023
house,TEK07,0.25,DH-Gas,0.05,2023
""".strip()))

    cal = pd.DataFrame(data=[], columns=['building_category', 'to', 'factor', 'from'])

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,TEK_shares,heating_systems,year
house,TEK07,0.5,DH-Ingen,0.0,2023
house,TEK07,0.25,DH-Bio,0.05,2023
house,TEK07,0.25,DH-Gas,0.05,2023
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)
    assert result is df


def test_heating_system_calibration_does_not_produce_duplicate_values():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """
    os.chdir('C:/Users/kenord/pyc/workspace')
    df = pd.read_csv('kalibrering/heating_systems_shares_start_year.csv')
    cal = pd.read_csv('kalibrering/calibrate_energy_consumption.csv')

    df = df[df['building_category'] == 'house']
    cal = cal[cal['building_category'] == 'house']
    result = calibrate_heating_systems(df, cal)

    assert isinstance(result, pd.DataFrame)
