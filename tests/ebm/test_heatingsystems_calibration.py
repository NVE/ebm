import io

import pandas as pd
import pytest

from ebm.heating_systems import calibrate_heating_systems


@pytest.mark.skip(reason='Incorrect data type, in the middle of refactor')
def test_heating_system_calibration():
    df = pd.read_csv(io.StringIO("""building_group,building_category,TEK,TEK_shares,Grunnlast,Grunnlast andel,Spisslast,Spisslast andel
Bolig,apartment_block,TEK07,0.3316670026630616,DH,1.0,Ingen,0.0
Bolig,apartment_block,TEK07,0.003305887353335,DH,0.95,Bio,0.05
Bolig,apartment_block,TEK07,0.0002415945163788,Electric boiler,0.8,Solar,0.1999999999999999
Bolig,apartment_block,TEK07,0.0075495428952456,HP Central heating,0.85,DH,0.15
Bolig,apartment_block,TEK07,0.0047049853428493,HP Central heating,0.85,Gas,0.15
Bolig,apartment_block,TEK07,0.00634805343290627,Electric boiler,1.0,Ingen,0.0
Bolig,apartment_block,TEK07,0.058887285441004904,Electricity,0.7,Bio,0.3
Bolig,apartment_block,TEK07,0.02944238792648616,Gas,1.0,Ingen,0.0
Bolig,apartment_block,TEK07,0.5493419585433096,HP Central heating,0.85,Electric boiler,0.15
Bolig,apartment_block,TEK07,0.008511301885422498,HP Central heating,0.85,Bio,0.15"""))

    cal = pd.read_csv(io.StringIO("""building_group,c_type,to,factor,from
Bolig,Heating system ,DH,1.1,Electricity -Bio
Bolig,Heating system ,DH,0.9,Electricity -Bio
Bolig,Heating system ,DH,2,Electricity -Bio
Bolig,Heating system ,DH,1.0,Electricity -Bio
    """.strip()))

    assert calibrate_heating_systems(df, cal[cal['factor'] == 1.1]) == 0.3349728900163966
    assert calibrate_heating_systems(df, cal[cal['factor'] == 0.9]) == 0.29850030239675546
    assert calibrate_heating_systems(df, cal[cal['factor'] == 2]) == 0.3349728900163966
    assert calibrate_heating_systems(df, cal[cal['factor'] == 1]) == 0.3316670026630616
