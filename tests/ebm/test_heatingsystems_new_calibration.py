import io

import pandas as pd

from ebm.energy_consumption import calibrate_heating_systems_adder


def test_heating_system_calibration_keep_uncalibrated_heating_systems_in_frame():
    """
    Make sure any heating system value in the original dataframe remains untouched when no related calibration is
    present. In this case DH - Gas should be kept as is in the result.

    """
    df = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,heating_system_share
house,TEK07,2023,DH,0.5
house,TEK07,2023,DH-Bio,0.25
house,TEK07,2023,DH-Gas,0.25
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,to,factor,from
house,DH,0.25,DH-Bio
house,DH,0.1,DH-Gas
    """.strip()))

    result = calibrate_heating_systems_adder(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,year,heating_systems,heating_system_share
house,TEK07,2023,DH,0.85
house,TEK07,2023,DH-Bio,0.0
house,TEK07,2023,DH-Gas,0.15
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_works_with_no_calibration():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """

    df = pd.read_csv(io.StringIO("""building_category,TEK,heating_system_share,heating_systems,year
house,TEK07,0.5,DH-Ingen,0.0,2023
house,TEK07,0.25,DH-Bio,0.05,2023
house,TEK07,0.25,DH-Gas,0.05,2023
""".strip()))

    cal = pd.DataFrame(data=[('house', 'DH', 0.0,'DH - Bio')], columns=['building_category', 'to', 'factor', 'from'])

    result = calibrate_heating_systems_adder(df, cal)
    expected = pd.read_csv(io.StringIO("""building_category,TEK,heating_system_share,heating_systems,year
house,TEK07,0.5,DH-Ingen,0,2023
house,TEK07,0.25,DH-Bio,0.05,2023
house,TEK07,0.25,DH-Gas,0.05,2023
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)
    assert result is df