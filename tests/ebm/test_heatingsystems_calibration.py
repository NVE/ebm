import io
import os
import pathlib

import pandas as pd
import pytest

from ebm.energy_consumption import calibrate_heating_systems


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


def test_heating_system_calibration_reduce_other_type():
    df = pd.read_csv(io.StringIO("""building_category,TEK,TEK_shares,heating_systems,year
apartment_block,TEK07,0.5,Electricity,2023
apartment_block,TEK07,0.5,Gas,2023
house,TEK07,0.5,DH,2023
house,TEK07,0.5,DH-Bio,2023
house,TEK07,1.0,Electrical boiler,2023
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
apartment_block,Electricity,1.1,Gas
apartment_block,Electricity,1,Electrical boiler
house,DH-Bio,2,DH
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
apartment_block,TEK07,2023,Electricity,0.55
apartment_block,TEK07,2023,Gas,0.45
house,TEK07,2023,DH,0.0
house,TEK07,2023,DH-Bio,1.0
house,TEK07,2023,Electrical boiler,1.0
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


@pytest.mark.skipif(not pathlib.Path('C:/Users/kenord/pyc/workspace').is_dir(), reason='Require special environment')
def test_heating_system_calibration_round_values_within_specification():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """
    pd.set_option('display.precision', 15)
    os.chdir('C:/Users/kenord/pyc/workspace')
    df = pd.read_csv('kalibrering/heating_systems_shares_start_year.csv')
    cal = pd.read_csv('kalibrering/calibrate_energy_consumption.csv')
    # cal = pd.DataFrame(data=[['heis', 'DH', 100.0, 'DH - Bio']], columns=['building_category', 'to', 'factor', 'from'])
    df = df[df['building_category'] == 'house']
    df_shares = df.groupby(by=['building_category', 'TEK', 'year']).sum().TEK_shares
    for idx, tek_share in df_shares.items():
        assert tek_share == 1.0, f'{idx} {tek_share=} expected=1.0'

    cal = cal[cal['building_category'] == 'house']
    result = calibrate_heating_systems(df, cal)
    #assert isinstance(result, pd.DataFrame)

    summed_result = result.groupby(by=['building_category', 'TEK']).sum()

    for idx, tek_share in summed_result.TEK_shares.items():
        assert tek_share == 1.0, f'{idx} {tek_share=} expected=1.0'


def test_heating_system_calibration_preserve_tek():
    """

    """
    df = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH-Ingen,0.50
house,TEK07,2023,DH-Bio,0.25
house,TEK10,2023,DH-Ingen,0.50
house,TEK10,2023,DH-Bio,0.25
house,TEK10,2024,DH-Bio,0.25
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
house,DH-Ingen,1.1,DH-Bio
    """.strip()))
    # house,DH-Ingen,1.1,DH-Gas
    result = calibrate_heating_systems(df, cal).reset_index(drop=True)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,DH-Ingen,0.55
house,TEK07,2023,DH-Bio,0.2
house,TEK10,2023,DH-Ingen,0.55
house,TEK10,2023,DH-Bio,0.2
house,TEK10,2024,DH-Bio,0.25
""".strip()))

    # Alternative/correct non-parallel result:
    # Bolig, house, TEK07, 0.30, DH, 0.95, Elec, 0.05
    # Bolig, house, TEK07, 0.15, DH, 0.95, Gas, 0.05

    pd.testing.assert_frame_equal(result, expected, check_like=True)


@pytest.mark.skipif(not pathlib.Path('C:/Users/kenord/pyc/workspace').is_dir(), reason='Require special environment')
def test_heating_system_calibration_add_5_percent():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """
    os.chdir('C:/Users/kenord/pyc/workspace')
    df = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
house,TEK07,Electricity,2023,0.05219849068043661
house,TEK07,Electric boiler,2023,0.01305000630802345
house,TEK07,DH,2023,0.02133151135658332
house,TEK07,DH - Bio,2023,0.007658006683126974
house,TEK07,Electric boiler - Solar,2023,0.0003008594060781025
house,TEK07,Electricity - Bio,2023,0.2247326376682366
house,TEK07,Gas,2023,0.008896825922106484
house,TEK07,HP - Bio - Electricity,2023,0.5649908788840202
house,TEK07,HP - Electricity,2023,0.09929473189808154
house,TEK07,HP Central heating - Electric boiler,2023,0.003815290330247105
house,TEK07,HP Central heating - Gas,2023,0.00373076086305975
"""))
    cal = pd.read_csv(io.StringIO("""building_category,to,from,factor
house,Electric boiler,Electricity,1.05"""))

    df = df[df['building_category'] == 'house']
    cal = cal[cal['building_category'] == 'house']
    result = calibrate_heating_systems(df, cal)
    # assert df.sum().TEK_shares == 1.0
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
house,TEK07,2023,Electricity,0.05154599036503544
house,TEK07,2023,Electric boiler,0.013702506623424622
house,TEK07,2023,DH,0.02133
house,TEK07,2023,DH - Bio,0.00766
house,TEK07,2023,Electric boiler - Solar,0.00030
house,TEK07,2023,Electricity - Bio,0.22473
house,TEK07,2023,Gas,0.008896825922106484
house,TEK07,2023,HP - Bio - Electricity,0.5649908788840202
house,TEK07,2023,HP - Electricity,0.09929473189808154
house,TEK07,2023,HP Central heating - Electric boiler,0.003815290330247105
house,TEK07,2023,HP Central heating - Gas,0.00373076086305975""".strip()))

    assert 0.9999999 < float(result.groupby(by=['building_category', 'TEK']).sum().TEK_shares) < 1.000001
    pd.testing.assert_frame_equal(result, expected, check_like=True, atol=1e-5)


def test_heating_system_calibration_reduce_single_building_category():
    df = pd.read_csv(io.StringIO("""building_category,TEK,TEK_shares,heating_systems,year
apartment_block,TEK07,1.0,Electric boiler,2023
apartment_block,TEK07,2.0,Electricity,2023
apartment_block,TEK07,3.0,Gas,2023
apartment_block,TEK07,4.0,DH,2023
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
apartment_block,Electric boiler,1.5,Electricity
apartment_block,Electricity,1.0,Electricity
apartment_block,Gas,1.0,Electricity
apartment_block,DH,1.0,Electricity
apartment_block,Bio,1.0,Electricity
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,TEK_shares
apartment_block,TEK07,2023,Electric boiler,1.5
apartment_block,TEK07,2023,Electricity,1.5
apartment_block,TEK07,2023,Gas,3.0
apartment_block,TEK07,2023,DH,4.0
""".strip()))

    pd.testing.assert_frame_equal(result, expected)
