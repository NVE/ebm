import io

import pandas as pd
import pytest

from ebm.energy_consumption import calibrate_heating_systems, calibrate_heating_systems2


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

    result = calibrate_heating_systems2(df, cal)
    expected = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,apartment_block,TEK07,0.55,DH,1.0,Ingen,0.0
Bolig,apartment_block,TEK07,0.45,DH,0.95,Bio,0.05
Bolig,house,TEK07,0.0,DH,1.0,Ingen,0.0
Bolig,house,TEK07,1.0,DH,0.95,Bio,0.05
""".strip()))

    pd.testing.assert_frame_equal(result, expected, check_like=True)



