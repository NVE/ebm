import io

import pandas as pd

from ebm.energy_consumption import calibrate_heating_systems


def test_heating_system_calibration_reduce_other_type():
    df = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,apartment_block,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,apartment_block,TEK07,0.5,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.5,DH,0.95,Bio,0.05
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,c_type,to,factor,from
apartment_block,Heating system,DH,1.1,DH-Bio
house,Heating system,DH-Bio,2,DH
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,apartment_block,TEK07,0.55,DH,1.0,Ingen,0.0
Bolig,house,TEK07,1.0,DH,0.95,Bio,0.05
Bolig,apartment_block,TEK07,0.45,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.0,DH,1.0,Ingen,0.0
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_keep_uncalibrated_heating_systems_in_frame():
    """
    Make sure any heating system value in the original dataframe remains untouched when no related calibration is
    present. In this case DH - Gas should be kept as is in the result.

    """
    df = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.25,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.25,DH,0.95,Gas,0.05
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,c_type,to,factor,from
house,Heating system,DH,1.1,DH-Bio
    """.strip()))

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.55,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.20,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.25,DH,0.95,Gas,0.05
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_calibrate_multiple_values():
    """

    """
    df = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.25,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.25,DH,0.95,Gas,0.05
""".strip()))

    cal = pd.read_csv(io.StringIO("""building_category,c_type,to,factor,from
house,Heating system,DH,1.1,DH-Bio
house,Heating system,DH-Bio,1.5,DH-Gas
    """.strip()))

    result = calibrate_heating_systems(df, cal).reset_index(drop=True)
    expected = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.55,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.375,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.125,DH,0.95,Gas,0.05
""".strip()))

    # Alternative/correct non-parallel result:
    # Bolig, house, TEK07, 0.30, DH, 0.95, Bio, 0.05
    # Bolig, house, TEK07, 0.15, DH, 0.95, Gas, 0.05

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_heating_system_calibration_works_with_no_calibration():
    """
    When no factor are provided to calibrate_heating_system, simply return the original dataframe
    """

    df = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.25,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.25,DH,0.95,Gas,0.05
""".strip()))

    cal = pd.DataFrame(data=[], columns=['building_category', 'c_type' , 'to', 'factor', 'from'])

    result = calibrate_heating_systems(df, cal)
    expected = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,house,TEK07,0.5,DH,1.0,Ingen,0.0
Bolig,house,TEK07,0.25,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.25,DH,0.95,Gas,0.05
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)
    assert result is df
