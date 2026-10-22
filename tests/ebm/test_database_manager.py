import io
import itertools
import pathlib
from io import StringIO
from unittest.mock import MagicMock, Mock

import numpy as np
import pandas as pd
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.defaults import default_calibrate_heating_rv
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.file_handler import FileHandler


@pytest.mark.parametrize('floor_area_column_name',[
    'flood_area_new_apartment_block',
    'floor_area_new_apartment_block',
])
def test_get_new_buildings_category_share_renames_flood_area_new_apartment_block(floor_area_column_name):
    new_buildings_residential_csv = pd.DataFrame({
        'year': {0: 2020, 1: 2021},
        'new_house_share': {0: 0.44, 1: 0.43},
        'new_apartment_block_share': {0: 0.56, 1: 0.57},
        'floor_area_new_house': {0: 154, 1: 154},
        floor_area_column_name: {0: 69, 1: 69}})

    fh = FileHandler()
    fh.get_construction_building_category_share = Mock(return_value=new_buildings_residential_csv)
    dm = DatabaseManager(file_handler=fh)

    actual = dm.get_new_buildings_category_share()

    expected = pd.DataFrame({
        'new_house_share': {2020: 0.44, 2021: 0.43},
        'new_apartment_block_share': {2020: 0.56, 2021: 0.57},
        'floor_area_new_house': {2020: 154, 2021: 154},
        'floor_area_new_apartment_block': {2020: 69, 2021: 69}},
    index=pd.Index([2020, 2021], name='year'))

    pd.testing.assert_frame_equal(actual, expected)


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


def test_get_energy_need_yearly_improvements():

    mock_fh = MagicMock(spec=FileHandler)

    energy_need_improvements_csv = pd.read_csv(
        StringIO(
            """building_category,building_code,purpose,function,start_year,value,end_year
house+apartment_block,TEK69,lighting,yearly_reduction,2022,0.02,2023
office,PRE_TEK49+TEK69,lighting,improvement_at_end_year,2022,0.3,2023""".strip()
        )
    )

    mock_fh.get_energy_need_yearly_improvements.return_value = energy_need_improvements_csv
    mock_fh.get_building_category.return_value = pd.DataFrame({
        'building_category': ['apartment_block', 'house', 'office'],
        'building_group': ['residential', 'residential', 'non_residential']
    })

    mock_fh.get_building_code.return_value = pd.DataFrame({
        'building_code': ['PRE_TEK49',  'TEK69',]
    })

    dm = DatabaseManager(file_handler=mock_fh)
    actual = dm.get_energy_need_yearly_improvements().reset_index(drop=True)[[
        'building_category',
        'building_code',
        'purpose',
        'function',
        'start_year',
        'value',
        'end_year',
        'lineno',
        'dupe']]

    expected = pd.DataFrame(
        {
            'building_category': ['apartment_block', 'house', 'office', 'office'],
            'building_code': ['TEK69', 'TEK69', 'PRE_TEK49', 'TEK69'],
            'purpose': ['lighting'] * 4,
            'function': ['yearly_reduction', 'yearly_reduction', 'improvement_at_end_year', 'improvement_at_end_year'],
            'start_year': [2022] * 4,
            'value': [0.02, 0.02, 0.3, 0.3],
            'end_year': [2023] * 4,
            'lineno': [2, 2, 3, 3],
            'dupe': [False] * 4,
        }
    )

    assert 'improvement_at_end_year' not in actual.columns, 'improvement_at_end_year should be merged into value'
    assert 'yearly_efficiency_improvement' not in actual.columns, 'yearly_efficiency_improvement should be renamed to value'
    assert 'value' in actual.columns

    pd.testing.assert_frame_equal(actual, expected)


def test_get_energy_req_original_condition():
    oc_df = pd.read_csv(io.StringIO("""building_category,building_code,purpose,kwh_m2
apartment_block,TEK87,heating_rv,100
apartment_block,TEK97,cooling,0.0
apartment_block,TEK97,electrical_equipment,17.52
apartment_block,TEK97,fans_and_pumps,0.43
apartment_block,TEK97,heating_dhw,29.76
apartment_block,TEK97,heating_rv,200
culture,PRE_TEK49,heating_rv,400"""))

    fh = FileHandler(directory=pathlib.Path(__file__).parent / 'data' / 'ebm')
    get_original_condition = Mock()
    get_original_condition.return_value = oc_df
    fh.get_energy_req_original_condition = get_original_condition
    fh.get_building_category = Mock(return_value = pd.DataFrame(
        {'building_category': ['apartment_block', 'culture', 'school'],
         'building_group': ['residential', 'non_residential', 'non_residential']})
    )
    fh.get_building_code = Mock(return_value=pd.DataFrame(['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17'], columns=['building_code']))

    dm = DatabaseManager(fh)

    cal_df = pd.DataFrame({
        'building_category': ['apartment_block', 'culture', 'school'],
        'purpose': ['heating_rv'] * 3,
        'heating_rv_factor': [0.5, 2.0, 3.0]})

    cal_mock = Mock()
    cal_mock.return_value = cal_df
    dm.get_calibrate_heating_rv = cal_mock

    behaviour_factors = itertools.product(['apartment_block', 'culture', 'school'], ['TEK87', 'TEK97', 'PRE_TEK49'],
                      ['heating_rv', 'cooling', 'electrical_equipment', 'fans_and_pumps', 'heating_dhw'],
                      [y for y in range(2020, 2051)], [1.0])

    dm.get_behaviour_factor = Mock(return_value=pd.DataFrame(
        data=behaviour_factors,
        columns='building_category,building_code,purpose,behaviour_factor,year'.split(',')))

    result = dm.get_energy_req_original_condition()

    apartment_block = result.query('building_category=="apartment_block"')
    culture = result.query('building_category=="culture"')
    # Check heating_rv
    assert apartment_block.query("building_code=='TEK97' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 100
    assert apartment_block.query("building_code=='TEK87' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 50
    assert culture.query("building_code=='PRE_TEK49' and purpose=='heating_rv' and year==2020").iloc[0].kwh_m2 == 800

    # Check non-heating_rv
    assert apartment_block[(apartment_block['building_code'] == 'TEK97') & (apartment_block['purpose'] == 'heating_dhw')].iloc[0].kwh_m2 == 29.76
    assert apartment_block[(apartment_block['building_code'] == 'TEK97') & (apartment_block['purpose'] == 'fans_and_pumps')].iloc[0].kwh_m2 == 0.43

    # Any non apartment_block+culture should be NaNs
    assert len(result.query('building_category not in ["apartment_block", "culture"]')) == 0


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
                                  columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor']))
    mock_file_handler.get_calibrate_heating_rv = Mock(return_value=default_calibrate_heating_rv())
    mock_file_handler.get_building_category = Mock(
        return_value=pd.DataFrame(
            {'building_category': ['apartment_block', 'house'], 'building_group': ['residential', 'residential']}
        )
    )
    mock_file_handler.get_building_code = Mock(
        return_value=pd.DataFrame(['TEK01', 'TEK02', 'TEK03'], columns=['building_code'])
    )

    behaviour_factors = itertools.product(['apartment_block', 'house'],
                                          ['TEK01', 'TEK02', 'TEK03'],
                                          ['lighting'],
                                          [y for y in range(2020, 2051)], [1.0])

    dm = DatabaseManager(file_handler=mock_file_handler)
    dm.get_building_code_list = Mock(return_value=pd.DataFrame(['TEK01', 'TEK02', 'TEK03'], columns=['building_code']).building_code.unique())
    dm.get_behaviour_factor = Mock(return_value=pd.DataFrame(data=itertools.chain.from_iterable([[['apartment_block', 'TEK01', 'lighting', 1.1, y], ['apartment_block', 'TEK02', 'lighting', 1.1, y], ['apartment_block', 'TEK03', 'lighting', 1.1, y], ['house', 'TEK01', 'lighting', 1.1, y], ['house', 'TEK02', 'lighting', 1.1, y], ['house', 'TEK03', 'lighting', 1.3, y]] for y in range(2020, 2050+1)]),
                                       columns='building_category,building_code,purpose,behaviour_factor,year'.split(',')))


    df = dm.get_energy_req_original_condition()
    rs = df.query('building_category in ["house", "apartment_block"] and purpose=="lighting" and year==2020')
    rs = rs.sort_values(by=['building_category', 'building_code', 'purpose', 'year']).reset_index(drop=True)
    result = rs[['building_category', 'purpose', 'building_code', 'year', 'kwh_m2', 'behaviour_factor', 'heating_rv_factor', 'uncalibrated_kwh_m2', 'calibrated_kwh_m2']]

    expected = pd.DataFrame(
        data=[
            ['apartment_block', 'lighting', 'TEK01', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['apartment_block', 'lighting', 'TEK02', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['apartment_block', 'lighting', 'TEK03', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK01', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK02', 2020, 100.0, 1.1, 1.0, 100.0, 100.0],
            ['house', 'lighting', 'TEK03', 2020, 300.0, 1.3, 1.0, 300.0, 300.0],],
        columns=['building_category', 'purpose', 'building_code', 'year', 'kwh_m2', 'behaviour_factor', 'heating_rv_factor', 'uncalibrated_kwh_m2', 'calibrated_kwh_m2'])

    pd.testing.assert_frame_equal(result, expected, check_like=True)

@pytest.fixture
def simple_file_handler():
    mock_file_handler = Mock(spec=FileHandler)
    mock_file_handler.get_building_category.return_value=pd.DataFrame(
        {
            'building_category': ['big_house', 'house', 'jail', 'kindergarten'],
            'building_group': ['residential', 'residential', 'non_residential', 'non_residential'],
        })

    mock_file_handler.get_building_code.return_value = pd.DataFrame(
        {
            'building_code': ['TEK01', 'TEK02']
        }
    )
    mock_file_handler.get_energy_req_reduction_per_condition = Mock()
    mock_file_handler.get_calibrate_heating_rv = Mock(return_value=default_calibrate_heating_rv())
    return mock_file_handler


def test_get_energy_req_reduction_per_condition_expands_default_aliases_and_conditions(simple_file_handler):
    file_handler_df = pd.DataFrame(
        data=[
            ['default', 'default', 'lighting', 'default', 0.0],
            ['default', 'TEK01+TEK02', 'lighting', 'small_measure', 0.1],
            ['kindergarten', 'TEK01+TEK02', 'lighting', 'renovation+renovation', 0.2],
            ['residential', 'TEK01', 'lighting', 'renovation', 0.25],
            ['non_residential+residential', 'TEK01', 'electrical_equipment', 'small_measure', 0.15],
            ['house+kindergarten', 'TEK01+TEK02', 'lighting', 'renovation_and_small_measure', 0.3],
        ],
        columns=[
            'building_category',
            'building_code',
            'purpose',
            'building_condition',
            'reduction_share',
        ],
    )
    expected_df = pd.DataFrame(
        data=[
            [ 0, 'big_house', 'TEK01', 'electrical_equipment', 'small_measure', 0.15],
            [ 1, 'big_house', 'TEK01', 'lighting', 'original_condition', 0.0],
            [ 2, 'big_house', 'TEK01', 'lighting', 'renovation', 0.25],
            [ 3, 'big_house', 'TEK01', 'lighting', 'renovation_and_small_measure', 0.0],
            [ 4, 'big_house', 'TEK01', 'lighting', 'small_measure', 0.1],
            [ 5, 'big_house', 'TEK02', 'lighting', 'original_condition', 0.0],
            [ 6, 'big_house', 'TEK02', 'lighting', 'renovation', 0.0],
            [ 7, 'big_house', 'TEK02', 'lighting', 'renovation_and_small_measure', 0.0],
            [ 8, 'big_house', 'TEK02', 'lighting', 'small_measure', 0.1],
            [ 9, 'house', 'TEK01', 'electrical_equipment', 'small_measure', 0.15],
            [10, 'house', 'TEK01', 'lighting', 'original_condition', 0.0],
            [11, 'house', 'TEK01', 'lighting', 'renovation', 0.25],
            [12, 'house', 'TEK01', 'lighting', 'renovation_and_small_measure', 0.3],
            [13, 'house', 'TEK01', 'lighting', 'small_measure', 0.1],
            [14, 'house', 'TEK02', 'lighting', 'original_condition', 0.0],
            [15, 'house', 'TEK02', 'lighting', 'renovation', 0.0],
            [16, 'house', 'TEK02', 'lighting', 'renovation_and_small_measure', 0.3],
            [17, 'house', 'TEK02', 'lighting', 'small_measure', 0.1],
            [18, 'jail', 'TEK01', 'electrical_equipment', 'small_measure', 0.15],
            [19, 'jail', 'TEK01', 'lighting', 'original_condition', 0.0],
            [20, 'jail', 'TEK01', 'lighting', 'renovation', 0.0],
            [21, 'jail', 'TEK01', 'lighting', 'renovation_and_small_measure', 0.0],
            [22, 'jail', 'TEK01', 'lighting', 'small_measure', 0.1],
            [23, 'jail', 'TEK02', 'lighting', 'original_condition', 0.0],
            [24, 'jail', 'TEK02', 'lighting', 'renovation', 0.0],
            [25, 'jail', 'TEK02', 'lighting', 'renovation_and_small_measure', 0.0],
            [26, 'jail', 'TEK02', 'lighting', 'small_measure', 0.1],
            [27, 'kindergarten', 'TEK01', 'electrical_equipment', 'small_measure', 0.15],
            [28, 'kindergarten', 'TEK01', 'lighting', 'original_condition', 0.0],
            [29, 'kindergarten', 'TEK01', 'lighting', 'renovation', 0.2],
            [30, 'kindergarten', 'TEK01', 'lighting', 'renovation_and_small_measure', 0.3],
            [31, 'kindergarten', 'TEK01', 'lighting', 'small_measure', 0.1],
            [32, 'kindergarten', 'TEK02', 'lighting', 'original_condition', 0.0],
            [33, 'kindergarten', 'TEK02', 'lighting', 'renovation', 0.2],
            [34, 'kindergarten', 'TEK02', 'lighting', 'renovation_and_small_measure', 0.3],
            [35, 'kindergarten', 'TEK02', 'lighting', 'small_measure', 0.1],
        ],
        columns=[
            'index',
            'building_category',
            'building_code',
            'purpose',
            'building_condition',
            'reduction_share',
        ],
    )

    simple_file_handler.get_energy_req_reduction_per_condition = Mock(return_value=file_handler_df)
    dm = DatabaseManager(file_handler=simple_file_handler)
    df = dm.get_energy_req_reduction_per_condition().reset_index()

    pd.testing.assert_frame_equal(df, expected_df)


def test_get_calibrate_heating_rv(simple_file_handler):
    dm = DatabaseManager(simple_file_handler)

    simple_file_handler.get_calibrate_heating_rv.return_value = pd.DataFrame([
            ('kindergarten', 'heating_rv', 1.1),
            ('jail+big_house', 'heating_rv', 3.4),
            ('residential', 'heating_rv', 1.2),
            ('kindergarten', 'heating_dhw', 0.0),
            ('kindergarten', 'electrical_equipment', 0.0),
        ],
        columns=['building_category', 'purpose', 'heating_rv_factor'],
    )

    result = dm.get_calibrate_heating_rv().reset_index()

    expected = pd.DataFrame(
        [
            (0, 'big_house', 'heating_rv', 3.4),
            (1, 'house', 'heating_rv', 1.2),
            (2, 'jail', 'heating_rv', 3.4),
            (3, 'kindergarten', 'heating_rv', 1.1),
        ],
        columns=['index', 'building_category', 'purpose', 'heating_rv_factor'],
    )

    pd.testing.assert_frame_equal(result, expected, check_like=True)


@pytest.mark.parametrize(
    'query, expected_start_years, expected_end_years, expected_behaviour_factor',
    [
        (('apartment_block', 'TEK49',  'heating_rv'), [2021]*4, [2024]*4, [.9]*4),
        (('house', 'PRE_TEK49',  'heating_rv'), [2021]*4, [2024]*4, [0.8]*4),
        (('kindergarten', 'TEK49',  'heating_rv'), [2021]*4, [2024]*4, [.7]*4),
        (('university', 'TEK07',  'lighting'), [2021]*4, [2024]*4, [1.0]*4),
    ],
)
def test_behaviour_factor_add_model_return_expected_columns(query, expected_start_years, expected_end_years, expected_behaviour_factor):
    behaviour_factor_df = pd.DataFrame(
        [
            ['apartment_block', 'TEK49', 'heating_rv', 0.9, None, None],
            ['house', 'PRE_TEK49', 'heating_rv', 0.8, 2022, None],
            ['kindergarten', 'TEK49', 'heating_rv', 0.7, None, 2023],
        ],
        columns=['building_category', 'building_code', 'purpose', 'behaviour_factor', 'start_year', 'end_year',],
    )

    mock_fh = Mock()
    mock_fh.get_file = Mock()
    mock_fh.get_file.return_value = behaviour_factor_df
    mock_fh.get_building_category.return_value = pd.DataFrame(
        [{'building_category': 'apartment_block', 'building_group': 'residential'},
        {'building_category': 'house', 'building_group': 'residential'}] + [{'building_category': c, 'building_group': 'non_residential'} for c in BuildingCategory if c.is_non_residential()]
    )
    mock_fh.get_building_code.return_value = pd.DataFrame({'building_code': ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17']})

    dm = DatabaseManager(mock_fh, years=YearRange(2021, 2024))
    result = dm.get_behaviour_factor()

    actual = result.query(f'building_category=="{query[0]}" and building_code=="{query[1]}" and purpose=="{query[2]}"')
    assert list(actual['start_year']) == expected_start_years
    assert list(actual['end_year']) == expected_end_years
    assert list(actual['behaviour_factor']) == expected_behaviour_factor
    assert list(actual['year']) == [2021, 2022, 2023, 2024]
    assert list(actual['function']) == ['behaviour_factor'] * len(expected_behaviour_factor)



def test_behaviour_factor(simple_file_handler):
    behaviour_factor_df = pd.DataFrame(
        [
            ['residential', 'TEK01', 'heating_rv', 0.91, None, None],
            ['kindergarten', 'default', 'heating_rv', 0.92, None, None],
            ['default', 'default', 'heating_rv', 1.0, None, None],
            ['jail', 'TEK01', 'heating_rv', 1.0, None, None],
        ],
        columns=['building_category', 'building_code', 'purpose', 'behaviour_factor', 'start_year', 'end_year',],
    )
    simple_file_handler.get_file.return_value = behaviour_factor_df
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2023))

    actual = dm.get_behaviour_factor()
    assert isinstance(actual, pd.DataFrame)

    heating_rv_actual = actual.query('purpose=="heating_rv"').reset_index(drop=True)

    expected_columns = ['building_category', 'building_code', 'purpose', 'year',
                        'function', 'model_start_year', 'model_end_year', 'start_year', 'end_year', 'behaviour_factor']
    assert set(expected_columns).symmetric_difference(heating_rv_actual.columns) == set()
    expected_df = pd.DataFrame(
        data=[
            ['big_house', 'TEK01', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['big_house', 'TEK01', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['big_house', 'TEK01', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['big_house', 'TEK02', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['big_house', 'TEK02', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['big_house', 'TEK02', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['house', 'TEK01', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['house', 'TEK01', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['house', 'TEK01', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.91],
            ['house', 'TEK02', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['house', 'TEK02', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['house', 'TEK02', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK01', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK01', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK01', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK02', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK02', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['jail', 'TEK02', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 1.0],
            ['kindergarten', 'TEK01', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
            ['kindergarten', 'TEK01', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
            ['kindergarten', 'TEK01', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
            ['kindergarten', 'TEK02', 'heating_rv', 2021, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
            ['kindergarten', 'TEK02', 'heating_rv', 2022, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
            ['kindergarten', 'TEK02', 'heating_rv', 2023, 'behaviour_factor', 2021, 2023, 2021, 2023, 0.92],
        ],
        columns=expected_columns,
    )
    pd.testing.assert_frame_equal(heating_rv_actual, expected_df, check_like=True)


def test_get_heating_system_forecast(simple_file_handler):
    heating_system_forecast_csv = pd.DataFrame(
        [
            ['residential', 'TEK01', 'DH', 'Electricity', 0.1, 0.2, 0.3,],
            ['residential', 'TEK02', 'DH', 'Electricity', 0.2, 0.2, 0.2,],
            ['kindergarten', 'default', 'DH', 'Electricity', 0.3, 0.3, 0.3,],
            ['jail', 'TEK01+TEK02', 'DH', 'Electricity', 0.4, 0.4, 0.4,],

        ],
        columns=['building_category', 'building_code', 'heating_systems', 'new_heating_systems', 2024, 2025, 2026],
    )
    simple_file_handler.get_heating_system_forecast.return_value = heating_system_forecast_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_heating_system_forecast()
    assert isinstance(actual, pd.DataFrame)

    expected_columns = ['building_category', 'building_code', 'heating_systems', 'new_heating_systems', 2024, 2025, 2026, 'lineno']
    assert set(expected_columns).symmetric_difference(actual.columns) == set()
    expected_df = pd.DataFrame(
        data=[
            ['big_house', 'TEK01', 'DH', 'Electricity', 0.1, 0.2, 0.3,2,],
            ['big_house', 'TEK02', 'DH', 'Electricity', 0.2, 0.2, 0.2,3,],
            ['house', 'TEK01', 'DH', 'Electricity', 0.1, 0.2, 0.3,2,],
            ['house', 'TEK02', 'DH', 'Electricity', 0.2, 0.2, 0.2,3,],
            ['jail', 'TEK01', 'DH', 'Electricity', 0.4, 0.4, 0.4,5,],
            ['jail', 'TEK02', 'DH', 'Electricity', 0.4, 0.4, 0.4,5,],
            ['kindergarten', 'TEK01', 'DH', 'Electricity', 0.3, 0.3, 0.3,4,],
            ['kindergarten', 'TEK02', 'DH', 'Electricity', 0.3, 0.3, 0.3,4,],
        ],
        columns=expected_columns,
    )
    pd.testing.assert_frame_equal(actual, expected_df, check_like=True)


def test_get_calibrate_heating_systems(simple_file_handler):
    heating_system_forecast_csv = pd.DataFrame(
        [
            ['residential', 'DH', 'Electricity', 0.1, ],
            ['non_residential', 'DH', 'Electricity', 0.2, ],
            ['big_house+house+non_residential', 'Electric boiler', 'Electricity', 0.3, ],
            ['default', 'Electricity - Bio', 'Electricity', 0.4, ],
            ['default', 'Electricity - Bio', 'Electricity', 0.4, ],
        ],
        columns=['building_category', 'to', 'from', 'factor'],
    )
    simple_file_handler.get_calibrate_heating_systems.return_value = heating_system_forecast_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_calibrate_heating_systems()
    assert 'lineno' in actual.columns
    assert 'building_category' in actual.columns
    assert isinstance(actual, pd.DataFrame)

    expected_columns = ['building_category', 'to', 'from', 'factor', 'lineno']
    assert set(expected_columns).symmetric_difference(actual.columns) == set()
    expected_df = pd.DataFrame(
        data=[
            [2, 'big_house'],
            [4, 'big_house'],
            [6, 'big_house'],
            [2, 'house'],
            [4, 'house'],
            [6, 'house'],
            [3, 'jail'],
            [4, 'jail'],
            [6, 'jail'],
            [3, 'kindergarten'],
            [4, 'kindergarten'],
            [6, 'kindergarten'],
        ],
        columns=['lineno', 'building_category'],
    )
    pd.testing.assert_frame_equal(actual[['lineno', 'building_category']], expected_df[['lineno', 'building_category']], check_like=True)


def test_get_heating_system_initial_shares(simple_file_handler):
    heating_system_initial_shares_csv = pd.DataFrame(
        [
            ['house', 'TEK01', 'DH', 2021, 0.1, ],
            ['house', 'TEK01', 'Electricity', 2021, 0.2, ],
            ['house', 'TEK01', 'Electricity - Bio', 2021, 0.3, ],
            ['house', 'TEK01', 'DH - Bio', 2021, 0.4, ],
        ],
        columns=['building_category',  'building_code', 'heating_systems', 'year', 'heating_system_share', ],
    )
    simple_file_handler.get_heating_systems_shares_start_year.return_value = heating_system_initial_shares_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_heating_system_initial_shares()
    assert 'lineno' in actual.columns
    assert 'building_category' in actual.columns
    assert isinstance(actual, pd.DataFrame)

    expected_columns = {'building_category', 'building_code', 'heating_systems', 'year', 'heating_system_share', 'lineno', 'dupe'}
    assert expected_columns.symmetric_difference(actual.columns) == set()
    expected_df = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'DH', 2021, 0.1, 2, False],
            ['house', 'TEK01', 'DH - Bio', 2021, 0.4, 5, False],
            ['house', 'TEK01', 'Electricity', 2021, 0.2, 3, False],
            ['house', 'TEK01', 'Electricity - Bio', 2021, 0.3, 4, False],
        ],
        columns=['building_category', 'building_code', 'heating_systems', 'year', 'heating_system_share', 'lineno', 'dupe'],
    )
    pd.testing.assert_frame_equal(actual, expected_df, check_like=True)


@pytest.mark.parametrize(
    ('column', 'column_value', 'expected_values',),
    [
        pytest.param('building_category',
                     'residential',
                     ['big_house', 'big_house', 'big_house', 'big_house', 'house', 'house', 'house', 'house', ],
                     id='building_category_residential'),
        pytest.param('building_category',
                     'house+kindergarten',
                     ['house', 'house', 'house', 'house', 'kindergarten', 'kindergarten', 'kindergarten', 'kindergarten',],
                     id='building_category_house_kindergarten'),
        pytest.param('building_category',
                     'non_residential',
                     ['jail', 'jail', 'jail', 'jail', 'kindergarten', 'kindergarten', 'kindergarten', 'kindergarten', ],
                     id='building_category_non_residential'),
        pytest.param('building_code',
                     'TEK01+TEK02',
                     ['TEK01', 'TEK01', 'TEK01', 'TEK01', 'TEK02', 'TEK02', 'TEK02', 'TEK02'],
                     id='building_code_TEK01_TEK02'),
        pytest.param('building_code',
                     'default',
                     ['TEK01', 'TEK01', 'TEK01', 'TEK01', 'TEK02', 'TEK02', 'TEK02', 'TEK02'],
                     id='building_code_default'),
        pytest.param('building_category',
                     'residential+house+big_house',
                     ['big_house', 'big_house', 'big_house', 'big_house', 'house', 'house', 'house', 'house', ],
                     id='building_category_residential_house_big_house'),
    ]
)
def test_get_heating_system_initial_shares_expand_columns(simple_file_handler, column, column_value, expected_values):
    heating_system_initial_shares_csv = pd.DataFrame(
        [
            ['house', 'TEK01', 'DH', 2021, 0.1, 2],
            ['house', 'TEK01', 'DH - Bio', 2021, 0.4, 3],
            ['house', 'TEK01', 'Electricity', 2021, 0.2, 4],
            ['house', 'TEK01', 'Electricity - Bio', 2021, 0.3, 5],
        ],
        columns=['building_category',  'building_code', 'heating_systems', 'year', 'heating_system_share', 'lineno'],
    )

    heating_system_initial_shares_csv[column] = column_value

    simple_file_handler.get_heating_systems_shares_start_year.return_value = heating_system_initial_shares_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_heating_system_initial_shares()[[column, 'lineno']]

    expected_df = pd.DataFrame(
        data={
            column: expected_values,
            'lineno': [2, 3, 4, 5, 2, 3, 4, 5],
        },
        columns=[column, 'lineno'],
    )
    pd.testing.assert_frame_equal(actual, expected_df, check_like=True)


def test_get_heating_system_initial_shares_split_heating_systems_on_plus(simple_file_handler):
    heating_system_initial_shares_csv = pd.DataFrame(
        [
            ['kindergarten', 'TEK01', 'DH+Electricity', 2021, 0.1, 2],
        ],
        columns=['building_category',  'building_code', 'heating_systems', 'year', 'heating_system_share', 'lineno'],
    )

    simple_file_handler.get_heating_systems_shares_start_year.return_value = heating_system_initial_shares_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_heating_system_initial_shares()[['building_category', 'building_code', 'heating_systems', 'lineno']]

    expected_df = pd.DataFrame(
        data={
            'building_category': ['kindergarten', 'kindergarten'],
            'building_code': ['TEK01', 'TEK01'],
            'heating_systems': ['DH', 'Electricity'],
            'lineno': [2, 2],
        },
    )
    pd.testing.assert_frame_equal(actual, expected_df, check_like=True)


def test_get_heating_system_initial_shares_dedupes_and_score_by_lineno(simple_file_handler):
    heating_system_initial_shares_csv = pd.DataFrame(
        [
            ['residential', 'TEK01', 'DH', 2021, 1.0, 2],
            ['residential', 'default', 'DH', 2021, 1.0, 3],
            ['house', 'TEK01', 'DH', 2021, 1.0, 4],
            ['jail', 'TEK01', 'DH', 2021, 1.0, 5],
            ['jail', 'TEK01', 'DH', 2021, 1.0, 6],
        ],
        columns=['building_category',  'building_code', 'heating_systems', 'year', 'heating_system_share', 'lineno'],
    )

    simple_file_handler.get_heating_systems_shares_start_year.return_value = heating_system_initial_shares_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))

    actual = dm.get_heating_system_initial_shares()[['building_category', 'building_code', 'lineno', 'dupe']]
    expected_df = pd.DataFrame(
        data=[
            {'building_category': 'big_house', 'building_code': 'TEK01', 'lineno': 2, 'dupe': False, },
            {'building_category': 'big_house', 'building_code': 'TEK02', 'lineno': 3, 'dupe': False,},
            {'building_category': 'house', 'building_code': 'TEK01', 'lineno': 4, 'dupe': False,},
            {'building_category': 'house', 'building_code': 'TEK02', 'lineno': 3, 'dupe': False,},
            {'building_category': 'jail', 'building_code': 'TEK01', 'lineno': 5, 'dupe': True,},
            {'building_category': 'jail', 'building_code': 'TEK01', 'lineno': 6, 'dupe': True,},
        ]
    )
    pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected_df, check_like=True)


def test_get_heating_system_forecast_drop_duplicates_when_heating_systems_are_different(simple_file_handler):
    """
    There can be multiple unique combinations of heating_systems and new_heating_systems.

    This test makes sure expand_building_category_building_code does not drop unique combinations.
    """

    heating_system_forecast_csv = pd.read_csv(io.StringIO("""
kindergarten,TEK01,DH,Gas,0.2,0.1
kindergarten,TEK01,Gas,DH,1.0,1.0
kindergarten,TEK01,Gas,Electric boiler,0.05,0.075
kindergarten,TEK01,Gas,DH,0.05,0.075
""".strip()), names=['building_category', 'building_code', 'heating_systems', 'new_heating_systems', 2021, 2022], skipinitialspace=True)

    simple_file_handler.get_heating_system_forecast.return_value = heating_system_forecast_csv
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2026))
    actual = dm.get_heating_system_forecast()

    expected = pd.DataFrame(
        data=[
            ['kindergarten', 'TEK01', 'DH', 'Gas', 0.2, 0.1, 2],
            ['kindergarten', 'TEK01', 'Gas', 'DH', 0.05, 0.075, 5],
            ['kindergarten', 'TEK01', 'Gas', 'Electric boiler', 0.05, 0.075, 4],
        ],
        columns=['building_category', 'building_code', 'heating_systems', 'new_heating_systems', 2021, 2022, 'lineno'])

    pd.testing.assert_frame_equal(actual.reset_index(drop=True), expected)


def test_behaviour_factor_explode_on_plus(simple_file_handler):
    behaviour_factor_df = pd.DataFrame(
        [
            ['default', 'default', 'default', 0.42, None, None],
            ['kindergarten+house', 'TEK01+TEK02', 'heating_rv+lighting', 0.24, None, None],
        ],
        columns=['building_category', 'building_code', 'purpose', 'behaviour_factor', 'start_year', 'end_year',],
    )
    simple_file_handler.get_file.return_value = behaviour_factor_df
    dm = DatabaseManager(simple_file_handler, years=YearRange(2021, 2023))

    actual = dm.get_behaviour_factor()
    assert isinstance(actual, pd.DataFrame)

    actual_42 = actual.query('building_category not in ["kindergarten", "house"] and building_code not in ["TEK01", "TEK02"] and purpose not in ["heating_rv", "lighting"]')
    assert actual_42.behaviour_factor.tolist() == [0.42] * len(actual_42)

    actual_24 = actual.query('building_category in ["kindergarten", "house"] and building_code in ["TEK01", "TEK02"] and purpose in ["heating_rv", "lighting"]')
    assert actual_24.behaviour_factor.tolist() == [0.24] * len(actual_24)


def test_make_building_purpose_with_year():
    mock_fh = MagicMock(spec=FileHandler)

    all_building_codes = ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17']
    mock_fh.get_building_code = lambda: pd.DataFrame(data=all_building_codes, columns=['building_code'])
    dm = DatabaseManager(file_handler=mock_fh)

    year_range = YearRange(2020, 2030)
    result = dm.make_building_purpose(years=year_range)
    expected_conditions = ['original_condition']

    assert isinstance(result, pd.DataFrame)
    assert result.columns.to_list() == ['building_category', 'building_code', 'building_condition', 'purpose', 'year']

    for bc in BuildingCategory:
        assert bc in result['building_category'].unique(), f'{bc} missing from make_building_purpose()'
    for tek in all_building_codes:
        assert tek in result['building_code'].unique(), f'{tek} missing from make_building_purpose()'
    for condition in expected_conditions:
        assert condition in result['building_condition'].unique(), f'{condition} missing from make_building_purpose()'
    for purpose in EnergyPurpose:
        assert purpose in result['purpose'].unique(), f'{purpose} missing from make_building_purpose()'
    for year in year_range:
        assert year in result['year'].unique(), f'{year} missing from make_building_purpose()'

    assert len(result) == len(BuildingCategory) * len(all_building_codes) * len(expected_conditions) * len(EnergyPurpose) * len(year_range)


def test_make_building_purpose():
    mock_fh = MagicMock(spec=FileHandler)

    all_building_codes = ['PRE_TEK49', 'TEK49']
    mock_fh.get_building_code = lambda: pd.DataFrame(data=all_building_codes, columns=['building_code'])
    dm = DatabaseManager(file_handler=mock_fh)

    result = dm.make_building_purpose()
    expected_conditions = ['original_condition']

    assert isinstance(result, pd.DataFrame)
    assert result.columns.to_list() == ['building_category', 'building_code', 'building_condition', 'purpose']

    for bc in BuildingCategory:
        assert bc in result['building_category'].unique(), f'{bc} missing from make_building_purpose()'
    for tek in all_building_codes:
        assert tek in result['building_code'].unique(), f'{tek} missing from make_building_purpose()'
    for condition in expected_conditions:
        assert condition in result['building_condition'].unique(), f'{condition} missing from make_building_purpose()'
    for purpose in EnergyPurpose:
        assert purpose in result['purpose'].unique(), f'{purpose} missing from make_building_purpose()'

    assert len(result) == len(BuildingCategory) * len(all_building_codes) * len(expected_conditions) * len(EnergyPurpose)


def test_get_building_code_list():
    mock_fh = MagicMock(spec=FileHandler)

    all_building_codes = pd.read_csv(StringIO("""
building_code,building_year,period_start_year,period_end_year
PRE_TEK49,1945,0,1948
TEK49,1962,1949,1968
TEK69,1977,1969,1986""".strip()))

    mock_fh.get_building_code.return_value = all_building_codes

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_building_code_list()

    assert (result == ['PRE_TEK49', 'TEK49', 'TEK69']).all()


def test_get_building_category():
    """Test that get_building_category returns the expected dataframe with building categories and descriptions.
    building_group is deliberately uses non-standard values residentials and non_residentials.
    """
    mock_fh = MagicMock(spec=FileHandler)

    all_building_categories = pd.read_csv(StringIO("""building_category,building_group
house,residentials
retail,non_residentials
småhus,residentials
""".strip()))

    mock_fh.get_building_category.return_value = all_building_categories

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_building_category()

    expected_building_category = pd.DataFrame(
        {
            'building_category': [
                'house',
                'retail',
                'småhus',
            ],
            'building_group': [
                'residentials',
                'non_residentials',
                'residentials',
            ],
        },
    )
    pd.testing.assert_frame_equal(result, expected_building_category)

def test_get_purpose_alias():
    """Test that get_purpose_alias returns the expected dataframe with purposes and aliases.
    """
    mock_fh = MagicMock(spec=FileHandler)

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_purpose_alias()

    expected_purpose_alias = pd.DataFrame(
        {
            'purpose': [
                'heating_rv',
                'heating_dhw',
                'fans_and_pumps',
                'lighting',
                'electrical_equipment',
                'cooling',
                'heating_rv',
                'heating_dhw',
                'fans_and_pumps',
                'lighting',
                'electrical_equipment',
                'cooling',
            ],
            'purpose_alias': [
                'heating_rv',
                'heating_dhw',
                'fans_and_pumps',
                'lighting',
                'electrical_equipment',
                'cooling',
                'default',
                'default',
                'default',
                'default',
                'default',
                'default',
            ],
        },
    )
    pd.testing.assert_frame_equal(result, expected_purpose_alias)


def test_get_building_code_alias():
    """Test that get_building_code_alias returns the expected dataframe with building codes and aliases.
    """
    mock_fh = MagicMock(spec=FileHandler)

    all_building_codes = pd.read_csv(StringIO("""building_code
PRE_TEK49
TEK49
TEK69
""".strip()))

    mock_fh.get_building_code.return_value = all_building_codes

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_building_code_alias()

    expected_building_code_alias = pd.DataFrame(
        {
            'building_code': [
                'PRE_TEK49',
                'TEK49',
                'TEK69',
                'PRE_TEK49',
                'TEK49',
                'TEK69',
            ],
            'building_code_alias': [
                'PRE_TEK49',
                'TEK49',
                'TEK69',
                'default',
                'default',
                'default',
            ],
        },
    )
    pd.testing.assert_frame_equal(result, expected_building_code_alias)


def test_get_building_category_alias():
    """Test that get_building_category returns the expected dataframe with building categories and descriptions.
    building_group is deliberately uses non-standard values residentials and non_residentials.
    """
    mock_fh = MagicMock(spec=FileHandler)

    all_building_categories = pd.read_csv(StringIO("""building_category,building_group
house,residentials
retail,non_residentials
småhus,residentials
""".strip()))

    mock_fh.get_building_category.return_value = all_building_categories

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_building_category_alias()

    expected_building_category = pd.DataFrame(
        {
            'building_category': [
                'house',
                'retail',
                'småhus',
                'house',
                'retail',
                'småhus',
                'house',
                'retail',
                'småhus',
            ],
            'building_category_alias': [
                'house',
                'retail',
                'småhus',
                'residentials',
                'non_residentials',
                'residentials',
                'default',
                'default',
                'default',
            ],
        },
    )
    pd.testing.assert_frame_equal(result, expected_building_category)


def test_get_building_category_code_purpose():
    dm = DatabaseManager(file_handler=MagicMock(spec=FileHandler))
    dm.get_building_category_alias = Mock(
        return_value=pd.DataFrame(
            {
                'building_category': ['house', 'house'],
                'building_category_alias': ['house', 'default'],
            },
        ),
    )
    dm.get_building_code_alias = Mock(
        return_value=pd.DataFrame(
            {
                'building_code': ['TEK17', 'TEK17'],
                'building_code_alias': ['TEK17', 'default'],
            },
        ),
    )
    dm.get_purpose_alias = Mock(
        return_value=pd.DataFrame(
            {
                'purpose': ['heating_rv', 'heating_rv'],
                'purpose_alias': ['heating_rv', 'default'],
            },
        ),
    )

    result = dm.get_building_category_code_purpose()

    expected = pd.DataFrame(
        {
            'building_category': ['house'] * 8,
            'building_category_alias': ['house'] * 4 + ['default'] * 4,
            'building_code': ['TEK17'] * 8,
            'building_code_alias': ['TEK17', 'TEK17', 'default', 'default'] * 2,
            'purpose': ['heating_rv'] * 8,
            'purpose_alias': ['heating_rv', 'default'] * 4,
        },
    )

    pd.testing.assert_frame_equal(result, expected)
    dm.get_building_category_alias.assert_called_once_with()
    dm.get_building_code_alias.assert_called_once_with()
    dm.get_purpose_alias.assert_called_once_with()


def test_get_energy_need_policy_improvement():
    mock_fh = MagicMock(spec=FileHandler)

    energy_need_improvements_csv = pd.read_csv(StringIO("""building_category,building_code,purpose,function,start_year,value,end_year,lineno
house,TEK69,lighting,yearly_reduction,2022,0.02,2023,3
house,PRE_TEK49+TEK49,lighting,improvement_at_end_year,2022,0.3,2023,4""".strip()))

    mock_fh.get_energy_need_yearly_improvements.return_value = energy_need_improvements_csv
    mock_fh.get_building_category.return_value = pd.DataFrame(
        {'building_category': ['house'], 'building_group': ['residential']}
    )

    mock_fh.get_building_code.return_value = pd.DataFrame(
        {
            'building_code': [
                'TEK69',
                'PRE_TEK49',
                'TEK49'
            ]
        }
    )

    dm = DatabaseManager(file_handler=mock_fh)

    expected = pd.DataFrame(
        {
            'building_category': ['house'] * 2,
            'building_code': ['PRE_TEK49', 'TEK49'],
            'purpose': ['lighting'] * 2,
            'function': ['improvement_at_end_year'] * 2,
            'start_year': [2022] * 2,
            'value': [0.3] * 2,
            'end_year': [2023] * 2,
            'lineno': [4] * 2,
            'dupe': [False] * 2,
        }
    )

    actual = dm.get_energy_need_policy_improvement().reset_index(drop=True)[[
        'building_category',
        'building_code',
        'purpose',
        'function',
        'start_year',
        'value',
        'end_year',
        'lineno',
        'dupe'
    ]]

    

    assert 'improvement_at_end_year' not in actual.columns
    assert 'value' in actual.columns
    pd.testing.assert_frame_equal(actual, expected)



def test_get_population_forecast_end_year():
    """Test that get_population_forecast_end_year return the actual end_year

    Does not assume the source file is sorted. Does not attempt to validate any of the other columns in the dataframe with
    the assumption that validation is handled elsewhere.
    """
    mock_fh = MagicMock(spec=FileHandler)

    all_building_codes = pd.read_csv(StringIO("""
year,population,household_size
2020,5367580,2.15
2021,5391369,2.14
2023,5488984,2.12
2019,5488984,2.12
""".strip()))

    mock_fh.get_construction_population.return_value = all_building_codes

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_population_forecast_end_year()

    assert result == 2023


@pytest.mark.parametrize(
    'building_category, building_code, purpose, building_condition, expected_reduction_share',
    [
        ('kindergarten', 'TEK17', 'heating_rv', 'small_measure', 0.17),
        ('kindergarten', 'TEK07', 'heating_rv', 'small_measure', 0.07),
        ('kindergarten', 'TEK10', 'heating_rv', 'small_measure', 0.07),
        ('house', 'TEK17', 'heating_rv', 'small_measure', 0.07),
        ('house', 'TEK07', 'heating_rv', 'small_measure', 0.07),
        ('house', 'TEK10', 'heating_rv', 'renovation_and_small_measure', 0.099),
        ('house', 'TEK10', 'heating_dhw', 'renovation_and_small_measure', 0.099),
        ('retail', 'TEK17', 'heating_rv', 'renovation', 0.042),
        ('retail', 'TEK07', 'heating_rv', 'renovation', 0.042),
        ('house', 'TEK10', 'heating_rv', 'renovation', 0.0108),
        ('retail', 'TEK10', 'heating_rv', 'renovation', 0.0108),
    ],
)
def test_get_energy_req_reduction_per_condition(
    building_category,
    building_code,
    purpose,
    building_condition,
    expected_reduction_share,
):
    mock_fh = MagicMock(spec=FileHandler)

    improvement_building_upgrade = pd.read_csv(StringIO("""building_category,building_code,purpose,building_condition,reduction_share,lineno
default,default,heating_rv,original_condition,0.0,2
default,default,heating_rv,small_measure,0.07,3
default,default,heating_rv,renovation,0.2,4
default,default,heating_rv,renovation_and_small_measure,0.25,5
non_residential,TEK17,heating_rv,small_measure,0.17,6
retail,TEK07+TEK17,heating_rv,renovation,0.042,7
retail+house,TEK10,heating_rv,renovation,0.0108,8
house,TEK10,heating_rv+heating_dhw,renovation_and_small_measure,0.099,9"""))

    mock_fh.get_energy_req_reduction_per_condition.return_value = improvement_building_upgrade

    mock_fh.get_building_category.return_value = pd.DataFrame({
        'building_category': ['house', 'kindergarten', 'retail'],
        'building_group': ['residential', 'non_residential', 'non_residential']
    })
    mock_fh.get_building_code.return_value = pd.DataFrame({'building_code': ['TEK07', 'TEK10', 'TEK17']})

    dm = DatabaseManager(file_handler=mock_fh)
    result = dm.get_energy_req_reduction_per_condition()

    matching_reduction_shares = result.query(
        'building_category == @building_category and building_code == @building_code and purpose == @purpose and building_condition == @building_condition'
    ).reduction_share

    assert matching_reduction_shares.to_list() == [expected_reduction_share]
