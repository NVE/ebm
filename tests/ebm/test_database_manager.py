import io
import itertools
import pathlib
from unittest.mock import Mock, MagicMock

import numpy as np
import pandas as pd
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.defaults import default_calibrate_heating_rv
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.file_handler import FileHandler
from ebm.validators import behaviour_factor_parser


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
    fh = FileHandler(directory=pathlib.Path(__file__).parent / 'data' / 'ebm')
    dm = DatabaseManager(fh)

    cal_df = pd.DataFrame({
        'building_category': ['apartment_block', 'culture', 'school'],
        'purpose': ['heating_rv'] * 3,
        'heating_rv_factor': [0.5, 2.0, 3.0]})

    cal_mock = Mock()
    cal_mock.return_value = cal_df
    dm.get_calibrate_heating_rv = cal_mock
    dm.get_tek_list = Mock(return_value=pd.Series(['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17'], name='TEK'))

    oc_df = pd.read_csv(io.StringIO("""building_category,TEK,purpose,kwh_m2
apartment_block,TEK87,heating_rv,100
apartment_block,TEK97,cooling,0.0
apartment_block,TEK97,electrical_equipment,17.52
apartment_block,TEK97,fans_and_pumps,0.43
apartment_block,TEK97,heating_dhw,29.76
apartment_block,TEK97,heating_rv,200
culture,PRE_TEK49,heating_rv,400"""))

    get_original_condition = Mock()
    get_original_condition.return_value = oc_df
    fh.get_energy_req_original_condition = get_original_condition

    behaviour_factors = itertools.product(['apartment_block', 'culture', 'school'], ['TEK87', 'TEK97', 'PRE_TEK49'],
                      ['heating_rv', 'cooling', 'electrical_equipment', 'fans_and_pumps', 'heating_dhw'],
                      [y for y in range(2020, 2051)], [1.0])

    dm.get_behaviour_factor = Mock(return_value=pd.DataFrame(
        data=behaviour_factors,
        columns='building_category,TEK,purpose,behaviour_factor,year'.split(',')))

    result = dm.get_energy_req_original_condition()

    apartment_block = result.query('building_category=="apartment_block"')
    culture = result.query('building_category=="culture"')
    # Check heating_rv
    assert apartment_block.query("TEK=='TEK87' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 50
    assert apartment_block.query("TEK=='TEK97' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 100
    assert culture.query("TEK=='PRE_TEK49' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 800

    # Check non-heating_rv
    assert apartment_block[(apartment_block['TEK'] == 'TEK97') & (apartment_block['purpose'] == 'heating_dhw')].iloc[0].kwh_m2 == 29.76
    assert apartment_block[(apartment_block['TEK'] == 'TEK97') & (apartment_block['purpose'] == 'fans_and_pumps')].iloc[0].kwh_m2 == 0.43

    # Any non apartment_block+culture should be NaNs
    assert result.query('building_category not in ["apartment_block", "culture"]')['kwh_m2'].isna().any()


def test_get_get_energy_req_original_condition_expand_unique_columns():
    """
    About this test: Expansion is currently done inside behaviour_factor_parser. This test is probably redundant.
    The test is kept around in case a refactor of tests or behaviour_factor_parser makes it useful again.
    """
    mock_file_handler = Mock(spec=FileHandler)
    mock_file_handler.get_energy_req_original_condition = Mock(
        return_value=pd.DataFrame(data=[
            ['residential', 'default', 'lighting', 100.0, 1.1],
            ['house', 'TEK03', 'lighting', 300.0, 1.3]
        ],
                                  columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor']))
    mock_file_handler.get_calibrate_heating_rv = Mock(return_value=default_calibrate_heating_rv())

    behaviour_factors = itertools.product(['apartment_block', 'house'],
                                          ['TEK01', 'TEK02', 'TEK03'],
                                          ['lighting'],
                                          [y for y in range(2020, 2051)], [1.0])

    dm = DatabaseManager(file_handler=mock_file_handler)
    dm.get_tek_list = Mock(return_value=pd.DataFrame(['TEK01', 'TEK02', 'TEK03'], columns=['TEK']).TEK.unique())
    dm.get_behaviour_factor = Mock(return_value=pd.DataFrame(data=itertools.chain.from_iterable([[['apartment_block', 'TEK01', 'lighting', 1.1, y], ['apartment_block', 'TEK02', 'lighting', 1.1, y], ['apartment_block', 'TEK03', 'lighting', 1.1, y], ['house', 'TEK01', 'lighting', 1.1, y], ['house', 'TEK02', 'lighting', 1.1, y], ['house', 'TEK03', 'lighting', 1.3, y]] for y in range(2020, 2050+1)]),
                                       columns='building_category,TEK,purpose,behaviour_factor,year'.split(',')))


    df = dm.get_energy_req_original_condition()
    result = df.query('building_category in ["house", "apartment_block"] and purpose=="lighting" and year==2020')
    result = result.sort_values(by=['building_category', 'TEK', 'purpose', 'year']).reset_index(drop=True)

    expected = pd.DataFrame(
        data=[
            ['apartment_block', 'lighting', 'TEK01', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['apartment_block', 'lighting', 'TEK02', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['apartment_block', 'lighting', 'TEK03', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK01', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK02', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK03', 2020, 300.0, 1.3, 1.0, 300.0, 300.0],],
        columns=['building_category', 'purpose', 'TEK', 'year', 'kwh_m2', 'behaviour_factor', 'heating_rv_factor', 'uncalibrated_kwh_m2', 'calibrated_kwh_m2'])

    pd.testing.assert_frame_equal(result, expected, check_like=True)


@pytest.mark.parametrize('simple_get,unique_columns',[
    ('get_energy_req_policy_improvements', ('building_category', 'TEK', 'purpose')),
    ('get_energy_req_reduction_per_condition', ('building_category', 'TEK', 'purpose', 'building_condition'))])
def test_method_use_and_return_through_expand_unique_columns(simple_get, unique_columns):
    file_handler_df = pd.DataFrame(data=[['default', 'default', 'lighting', 2010, 2040, 0.6], ],
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end'])
    exploded_df = pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2010, 2040, 0.6],
        ['kindergarten', 'TEK01', 'lighting', 2010, 2040, 0.6], ],
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end'])

    def call_explode_unique_columns(df, columns):
        if tuple(columns) == unique_columns:
            return exploded_df
        return df

    mock_file_handler = Mock(spec=FileHandler)
    setattr(mock_file_handler, simple_get, Mock(return_value=file_handler_df))
    mock_file_handler.get_calibrate_heating_rv = Mock(return_value=default_calibrate_heating_rv())

    dm = DatabaseManager(file_handler=mock_file_handler)
    dm.explode_unique_columns = call_explode_unique_columns

    df = getattr(dm, simple_get)()

    pd.testing.assert_frame_equal(df, exploded_df)

def test_get_calibrate_heating_rv():
    mock_fh = Mock()
    dm = DatabaseManager(mock_fh)

    calibrated_heating_rv = pd.DataFrame({'building_category': ['kindergarten', 'non_residential', 'residential'],
                                          'purpose': ['heating_rv'] * 3,
                                          'heating_rv_factor': [1.2, 1.2, 3.4]})
    mock_fh.get_calibrate_heating_rv = Mock()
    mock_fh.get_calibrate_heating_rv.return_value = calibrated_heating_rv

    result = dm.get_calibrate_heating_rv().set_index(['building_category', 'purpose'], drop=True)

    residential = [BuildingCategory.HOUSE, BuildingCategory.APARTMENT_BLOCK]
    non_residential = [bc for bc in BuildingCategory if not bc.is_residential()]
    expected = pd.DataFrame({
        'purpose': ['heating_rv']*13,
        'building_category': non_residential + residential,
        'heating_rv_factor': [1.2]*11 + [3.4] * 2,

    }).set_index(['building_category', 'purpose'])

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_expand_unique_columns_building_category_and_tek():
    residential = pd.DataFrame(data=[
        ['residential', 'default', 'lighting', 'residential-default-lighting'],
        ['house', 'TEK03', 'lighting', 'house-tek03-lighting'],
        ['house', 'TEK01+TEK02', 'lighting', 'house-tek01+tek02-lighting'],
        ['apartment_block', 'TEK01', 'lighting', 'apartment_block-tek01-lighting'],
        ['residential', 'default', 'lighting', 'residential-default-lighting-2'],
    ],
        columns=['building_category', 'TEK', 'purpose', 'v'])
    dm = DatabaseManager(Mock())
    dm.get_tek_list = Mock(return_value=pd.DataFrame(['TEK01', 'TEK02', 'TEK03'], columns=['TEK']).TEK.unique())

    result = dm.explode_unique_columns(residential, unique_columns=['building_category', 'TEK', 'purpose'])
    r = result.set_index(['building_category', 'TEK', 'purpose'])

    assert r.loc[('house', 'TEK01', 'lighting'), 'v'] == 'house-tek01+tek02-lighting'
    assert r.loc[('house', 'TEK02', 'lighting'), 'v'] == 'house-tek01+tek02-lighting'
    assert r.loc[('house', 'TEK03', 'lighting'), 'v'] == 'house-tek03-lighting'
    assert r.loc[('apartment_block', 'TEK01', 'lighting'), 'v'] == 'apartment_block-tek01-lighting'
    assert r.loc[('apartment_block', 'TEK02', 'lighting'), 'v'] == 'residential-default-lighting'
    assert r.loc[('apartment_block', 'TEK03', 'lighting'), 'v'] == 'residential-default-lighting'
    assert len(r) == 6


def test_expand_building_category_column_default_and_groups():
    residential = pd.DataFrame(data=[
        ['residential', 'TEK01', 'residential-tek01'],
        ['non_residential', 'TEK01', 'non_residential-tek01'],
        ['default', 'TEK02', 'default-tek02'],
        ['house+hotel', 'TEK03', 'house+hotel-tek03']
    ],
        columns=['building_category', 'TEK', 'v'])
    dm = DatabaseManager(Mock())

    dm.get_tek_list = Mock(return_value=['TEK01', 'TEK02', 'TEK03'])
    # explode_tek_column does not change the dataframe
    dm.explode_tek_column = lambda df,c: df
    result = dm.explode_unique_columns(residential, unique_columns=['building_category', 'TEK'])
    r = result.set_index(['building_category', 'TEK'])

    assert r.loc[(BuildingCategory.HOUSE, 'TEK01'), 'v'] == 'residential-tek01'
    assert r.loc[(BuildingCategory.APARTMENT_BLOCK, 'TEK01'), 'v'] == 'residential-tek01'
    assert r.loc[(BuildingCategory.KINDERGARTEN, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.SCHOOL, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.UNIVERSITY, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.OFFICE, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.RETAIL, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.HOTEL, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.HOSPITAL, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.NURSING_HOME, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.CULTURE, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.SPORTS, 'TEK01'), 'v'] == 'non_residential-tek01'
    assert r.loc[(BuildingCategory.STORAGE_REPAIRS, 'TEK01'), 'v'] == 'non_residential-tek01'

    for bc in BuildingCategory:
        assert r.loc[(bc, 'TEK02'), 'v'] == 'default-tek02'

    assert r.loc[(BuildingCategory.HOUSE, 'TEK03'), 'v'] == 'house+hotel-tek03'
    assert r.loc[(BuildingCategory.HOTEL, 'TEK03'), 'v'] == 'house+hotel-tek03'

    assert len(r) == 28


def test_make_building_purpose_with_year():
    mock_fh = MagicMock(spec=FileHandler)

    all_teks = ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17']
    mock_fh.get_tek_id = lambda: pd.DataFrame(data=all_teks, columns=['TEK'])
    dm = DatabaseManager(file_handler=mock_fh)

    year_range = YearRange(2020, 2030)
    result = dm.make_building_purpose(years=year_range)
    expected_conditions = ['original_condition']

    assert isinstance(result, pd.DataFrame)
    assert result.columns.to_list() == ['building_category', 'TEK', 'building_condition', 'purpose', 'year']

    for bc in BuildingCategory:
        assert bc in result['building_category'].unique(), f'{bc} missing from make_building_purpose()'
    for tek in all_teks:
        assert tek in result['TEK'].unique(), f'{tek} missing from make_building_purpose()'
    for condition in expected_conditions:
        assert condition in result['building_condition'].unique(), f'{condition} missing from make_building_purpose()'
    for purpose in EnergyPurpose:
        assert purpose in result['purpose'].unique(), f'{purpose} missing from make_building_purpose()'
    for year in year_range:
        assert year in result['year'].unique(), f'{year} missing from make_building_purpose()'

    assert len(result) == len(BuildingCategory) * len(all_teks) * len(expected_conditions) * len(EnergyPurpose) * len(year_range)


def test_make_building_purpose():
    mock_fh = MagicMock(spec=FileHandler)

    all_teks = ['PRE_TEK49', 'TEK49']
    mock_fh.get_tek_id = lambda: pd.DataFrame(data=all_teks, columns=['TEK'])
    dm = DatabaseManager(file_handler=mock_fh)

    result = dm.make_building_purpose()
    expected_conditions = ['original_condition']

    assert isinstance(result, pd.DataFrame)
    assert result.columns.to_list() == ['building_category', 'TEK', 'building_condition', 'purpose']

    for bc in BuildingCategory:
        assert bc in result['building_category'].unique(), f'{bc} missing from make_building_purpose()'
    for tek in all_teks:
        assert tek in result['TEK'].unique(), f'{tek} missing from make_building_purpose()'
    for condition in expected_conditions:
        assert condition in result['building_condition'].unique(), f'{condition} missing from make_building_purpose()'
    for purpose in EnergyPurpose:
        assert purpose in result['purpose'].unique(), f'{purpose} missing from make_building_purpose()'

    assert len(result) == len(BuildingCategory) * len(all_teks) * len(expected_conditions) * len(EnergyPurpose)
