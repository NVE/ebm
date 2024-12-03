import io
import pathlib
from unittest.mock import Mock

import numpy as np
import pandas as pd

from ebm.model import DatabaseManager, FileHandler, BuildingCategory


def test_get_area_per_person():
    area_per_person = pd.DataFrame({
        'building_category': {0: 'kindergarten', 1: 'retail'},
        'area_per_person': {0: 0.6, 1: 6.0}})

    fh = FileHandler()
    fh.get_area_per_person = Mock(return_value=area_per_person)
    dm = DatabaseManager(file_handler=fh)

    result = dm.get_area_per_person()
    expected = pd.Series([0.6, 6.0],
                         name='area_per_person',
                         index=pd.Index(['kindergarten', 'retail'], name='building_category'))

    pd.testing.assert_series_equal(result, expected)

    expected = np.float64(6.0)

    retail = dm.get_area_per_person(building_category=BuildingCategory.RETAIL)
    assert retail == expected


def test_get_energy_req_original_condition():
    fh = FileHandler(directory=pathlib.Path(__file__).parent / 'data' / 'bema')
    dm = DatabaseManager(fh)

    cal_df = pd.DataFrame({
        'building_category': ['apartment_block', 'culture', 'school'],
        'purpose': ['heating_rv'] * 3,
        'heating_rv_factor': [0.5, 2.0, 3.0]}).set_index(['building_category', 'purpose'])

    cal_mock = Mock()
    cal_mock.return_value = cal_df.heating_rv_factor
    dm.get_calibrate_heating_rv = cal_mock

    oc_df = pd.read_csv(io.StringIO("""building_category,TEK,purpose,kwh_m2
apartment_block,TEK87,heating_rv,100
apartment_block,TEK97,cooling,0.0
apartment_block,TEK97,electrical_equipment,17.52
apartment_block,TEK97,fans_and_pumps,0.43
apartment_block,TEK97,heating_dhw,29.76
apartment_block,TEK97,heating_rv,200
culture,PRE_TEK49,heating_rv,400"""))

    original_condition = Mock()
    original_condition.return_value = oc_df
    fh.get_energy_req_original_condition = original_condition

    result = dm.get_energy_req_original_condition()

    # Check heating_rv
    assert result[(result['TEK'] == 'TEK87') & (result['purpose'] == 'heating_rv')].iloc[0].kwh_m2 == 50
    assert result[(result['TEK'] == 'TEK97') & (result['purpose'] == 'heating_rv')].iloc[0].kwh_m2 == 100
    assert result[(result['TEK'] == 'PRE_TEK49') & (result['purpose'] == 'heating_rv')].iloc[0].kwh_m2 == 800

    # Check non-heating_rv
    assert result[(result['TEK'] == 'TEK97') & (result['purpose'] == 'heating_dhw')].iloc[0].kwh_m2 == 29.76
    assert result[(result['TEK'] == 'TEK97') & (result['purpose'] == 'fans_and_pumps')].iloc[0].kwh_m2 == 0.43

    # There should not be any NaNs
    assert not result['kwh_m2'].isna().any()




