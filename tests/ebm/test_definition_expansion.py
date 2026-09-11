import io
import re
import typing

import pandas as pd
import pytest

from ebm.definition_expansion import (
    build_grouping,
    collapse_years,
    expand_definitions,
    group_dupes_on_dupes,
    group_duplicated_lineno_summary,
    select_groups_with_lowest_lineno_count,
    summarize_energy_need_improvement_conflicts,
)
from ebm.validators import add_lineno, expanded_energy_need_improvements_schema

ENERGY_NEED_IMPROVEMENT_DTYPES: dict[str, str] = {
        'building_category': str,
        'building_code': str,
        'purpose': str,
        'function': str,
        'start_year': int,
        'value': float,
        'end_year': int,
}


ALL_BUILDING_CATEGORIES: set[str] = (
    'apartment_block',
    'culture',
    'hospital',
    'hotel',
    'house',
    'kindergarten',
    'nursing_home',
    'office',
    'retail',
    'school',
    'sports',
    'storage_repairs',
    'university',
)

DEFAULT_BUILDING_CODE: set[str] = (
    'PRE_TEK49',
    'TEK07',
    'TEK10',
    'TEK17',
    'TEK49',
    'TEK69',
    'TEK87',
    'TEK97',)

DEFAULT_PURPOSE: set[str] = (
    'cooling',
    'electrical_equipment',
    'fans_and_pumps',
    'heating_dhw',
    'heating_rv',
    'lighting',)

house_tek17_electrical_equipment = """building_category,building_code,purpose,function,start_year,value,end_year
house,TEK17,electrical_equipment,yearly_reduction,2020,0.02,2022
""".strip()

house_2tek_electrical_equipment = """building_category,building_code,purpose,function,start_year,value,end_year
apartment_block,TEK17,electrical_equipment,yearly_reduction,2020,0.02,2021
apartment_block,TEK10,electrical_equipment,yearly_reduction,2020,0.03,2021
""".strip()

university_plus_school = """building_category,building_code,purpose,function,start_year,value,end_year
university+school,TEK07,electrical_equipment,yearly_reduction,2021,0.04,2022
    """.strip()

tek87_plus_tek97 = """building_category,building_code,purpose,function,start_year,value,end_year
office,TEK87+TEK97,cooling,yearly_reduction,2021,0.05,2022
    """.strip()

lighting_plus_electrical_equipment = """building_category,building_code,purpose,function,start_year,value,end_year
retail,TEK69,electrical_equipment+lighting,yearly_reduction,2021,0.06,2022
""".strip()

house_tek17_electrical_equipment_dupe = """building_category,building_code,purpose,function,start_year,value,end_year
house,TEK17,electrical_equipment,yearly_reduction,2022,0.071,2023
house,TEK17,electrical_equipment,yearly_reduction,2022,0.072,2023
""".strip()

nursing_home_2_periods = """building_category,building_code,purpose,function,start_year,value,end_year
nursing_home,TEK49,lighting,yearly_reduction,2022,0.02,2023
nursing_home,TEK49,lighting,yearly_reduction,2024,0.03,2025
""".strip()

dupe_tek_with_clear_winners = """building_category,building_code,purpose,function,start_year,value,end_year
house,TEK49+TEK69,lighting,yearly_reduction,2022,0.02,2023
house,TEK49,lighting,yearly_reduction,2022,0.03,2023"""

input_with_lineno = """lineno,building_category,building_code,purpose,function,start_year,value,end_year
42,storage_repair,PRE_TEK49,lighting,yearly_reduction,2023,0.02,2023
""".strip()

single_year = """building_category,building_code,purpose,function,start_year,value,end_year
kindergarten,TEK87,lighting,yearly_reduction,2023,0.02,2023
""".strip()

default_building_category = """building_category,building_code,purpose,function,start_year,value,end_year
default,TEK87,lighting,yearly_reduction,2030,0.02,2030
""".strip()

residential_building_category = """building_category,building_code,purpose,function,start_year,value,end_year
residential,TEK87,lighting,yearly_reduction,2030,0.02,2030
""".strip()

residential_office = """building_category,building_code,purpose,function,start_year,value,end_year
office+residential+office,TEK87,lighting,yearly_reduction,2022,0.02,2022
""".strip()

non_residential_building_category = """building_category,building_code,purpose,function,start_year,value,end_year
non_residential,TEK97,lighting,yearly_reduction,2030,0.02,2030
""".strip()

default_building_code = """building_category,building_code,purpose,function,start_year,value,end_year
hotel,default,lighting,yearly_reduction,2030,0.02,2030
""".strip()

default_purpose = """building_category,building_code,purpose,function,start_year,value,end_year
hospital,TEK87,default,yearly_reduction,2030,0.02,2030
""".strip()


@pytest.mark.parametrize(('input_data', 'column', 'expected'), [
    pytest.param(house_tek17_electrical_equipment, 'building_category', ('house', 'house', 'house'), id='house_tek17_elt_building_category'),
    pytest.param(house_tek17_electrical_equipment, 'building_code', ('TEK17', 'TEK17', 'TEK17'), id='house_tek17_elt_building_code'),
    pytest.param(house_tek17_electrical_equipment, 'purpose', ('electrical_equipment', ) * 3, id='house_tek17_elt_purpose'),
    pytest.param(house_tek17_electrical_equipment, 'year', (2020, 2021, 2022), id='house_tek17_elt_year'),
    pytest.param(house_tek17_electrical_equipment, 'lineno', (2, 2, 2), id='house_tek17_elt_lineno'),
    pytest.param(house_tek17_electrical_equipment, 'lineno_count', (1, 1, 1), id='house_tek17_elt_lineno_count'),
    pytest.param(house_tek17_electrical_equipment, 'function', ('yearly_reduction', 'yearly_reduction', 'yearly_reduction'), id='house_tek17_elt_function'),
    pytest.param(house_tek17_electrical_equipment, 'value', (0.02, 0.02, 0.02), id='house_tek17_elt_value'),
    pytest.param(house_tek17_electrical_equipment, 'dupe', (False, False, False), id='house_tek17_elt_dupe'),

    pytest.param(house_2tek_electrical_equipment, 'building_code', ('TEK10', 'TEK10', 'TEK17', 'TEK17'), id='house_2tek_elt_building_code'),
    pytest.param(house_2tek_electrical_equipment, 'lineno', (3, 3, 2, 2), id='house_2tek_elt_lineno'),
    pytest.param(house_2tek_electrical_equipment, 'lineno_count', (1, 1, 1, 1), id='house_2tek_elt_lineno_count'),
    pytest.param(house_2tek_electrical_equipment, 'year', (2020, 2021, 2020, 2021), id='house_2tek_elt_year'),
    pytest.param(house_2tek_electrical_equipment, 'dupe', (False, False, False, False), id='house_2tek_elt_dupe'),
    pytest.param(house_2tek_electrical_equipment, 'value', (0.03, 0.03, 0.02, 0.02), id='house_2tek_elt_value'),

    pytest.param(university_plus_school, 'value', (0.04, 0.04, 0.04, 0.04), id='university_plus_school_value'),
    pytest.param(university_plus_school, 'year', (2021, 2022, 2021, 2022), id='university_plus_school_year'),
    pytest.param(university_plus_school, 'dupe', (False, False, False, False), id='university_plus_school_dupe'),
    pytest.param(university_plus_school, 'building_category', ('school', 'school', 'university', 'university'), id='university_plus_school_building_category'),

    pytest.param(tek87_plus_tek97, 'building_code', ('TEK87', 'TEK87', 'TEK97', 'TEK97'), id='tek87_plus_tek97_building_code'),
    pytest.param(tek87_plus_tek97, 'year', (2021, 2022, 2021, 2022), id='tek87_plus_tek97_year'),

    pytest.param(lighting_plus_electrical_equipment, 'purpose', ('electrical_equipment', 'electrical_equipment', 'lighting', 'lighting'),
                 id='purpose_lig_plus_elt'),
    pytest.param(lighting_plus_electrical_equipment, 'year', (2021, 2022, 2021, 2022), id='lighting_plus_elt_year'),
    pytest.param(lighting_plus_electrical_equipment, 'lineno', (2, 2, 2, 2), id='lighting_plus_elt_lineno'),

    pytest.param(house_tek17_electrical_equipment_dupe, 'building_category', ('house', 'house', 'house', 'house'), id='house_tek17_elt_dupe_building_category'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'building_code', ('TEK17', 'TEK17', 'TEK17', 'TEK17'), id='house_tek17_elt_dupe_building_code'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'purpose', ('electrical_equipment', ) * 4, id='house_tek17_elt_dupe_purpose'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'function', ('yearly_reduction', ) * 4, id='house_tek17_elt_dupe_function'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'dupe', (True, True, True, True), id='house_tek17_elt_dupe_dupe'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'year', (2022, 2023, 2022, 2023), id='house_tek17_elt_dupe_year'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'value', (0.071, 0.071, 0.072, 0.072), id='house_tek17_elt_dupe_value'),
    pytest.param(house_tek17_electrical_equipment_dupe, 'lineno_count', (1, 1, 1, 1), id='house_tek17_elt_dupe_lineno_count'),

    pytest.param(nursing_home_2_periods, 'lineno', (2, 2, 3, 3), id='nursing_home_2_periods_lineno'),
    pytest.param(nursing_home_2_periods, 'dupe', (False, False, False, False), id='nursing_home_2_periods_dupe'),

    pytest.param(single_year, 'year', (2023,), id='single_year_year'),

    pytest.param(dupe_tek_with_clear_winners, 'building_code', ('TEK49', 'TEK49', 'TEK69', 'TEK69'), id='dupe_tek_with_clear_winners_building_code'),
    pytest.param(dupe_tek_with_clear_winners, 'year', (2022, 2023,2022, 2023), id='dupe_tek_with_clear_winners_year'),
    pytest.param(dupe_tek_with_clear_winners, 'value', (0.03, 0.03, 0.02, 0.02), id='dupe_tek_with_clear_winners_value'),
    pytest.param(dupe_tek_with_clear_winners, 'dupe', (False, False, False, False), id='dupe_tek_with_clear_winners_dupe'),

    pytest.param(input_with_lineno, 'lineno', (42,), id='keep_existing_lineno'),

    pytest.param(residential_building_category, 'building_category', ('apartment_block', 'house'), id='replace_residential_building_category'),
    pytest.param(non_residential_building_category, 'building_code', ('TEK97', ) * 11, id='replace_non_residential_building_category'),
    pytest.param(default_building_category, 'building_category', ALL_BUILDING_CATEGORIES, id='replace_default_building_category'),
    pytest.param(default_building_category, 'building_code', ('TEK87',)*13, id='replace_default_building_category_building_code'),
    pytest.param(default_building_category, 'lineno', (2,)*13, id='replace_default_building_category_lineno'),

    pytest.param(default_building_code, 'building_code', DEFAULT_BUILDING_CODE, id='replace_default_building_code'),
    pytest.param(default_building_code, 'building_category', ('hotel',)*8, id='replace_default_building_code_building_category'),

    pytest.param(default_purpose, 'purpose', DEFAULT_PURPOSE, id='replace_default_purpose'),
    pytest.param(default_purpose, 'building_category', ('hospital',)*6, id='replace_default_purpose_building_category'),
    pytest.param(residential_office, 'building_category', ('apartment_block', 'house', 'office',), id='combine_residential_and_building_category'),
])
def test_expand_definitions_on_energy_need_improvements_columns_have_expected_values(input_data, column, expected):
    single_csv = io.StringIO(input_data)

    input_data = pd.read_csv(single_csv, dtype=ENERGY_NEED_IMPROVEMENT_DTYPES)

    result = expand_definitions(input_data, drop_helper_columns=False)
    assert column in result.columns, f"Column '{column}' not found in result DataFrame"
    actual = result[column].tolist()
    assert tuple(actual) == expected


@pytest.mark.parametrize(('selection', 'expected_years', 'expected_lineno'), [
    pytest.param(('house', 'TEK49', 'heating_rv', 'yearly_reduction'), (2021, 2022), (2, 2), id='house-t49-hrv'),
    pytest.param(('house', 'PRE_TEK49', 'lighting', 'yearly_reduction'), (2021, 2022), (3, 3), id='house-p49-lig'),
    pytest.param(('house', 'PRE_TEK49', 'heating_rv', 'yearly_reduction'), (2021, 2022), (4, 4), id='house-p49-hrv'),
    pytest.param(('house', 'TEK17', 'heating_rv', 'yearly_reduction'), (2021, 2022), (5, 5), id='house-t17-hrv'),
    pytest.param(('house', 'TEK10', 'heating_rv', 'yearly_reduction'), (2021, 2022), (6, 6), id='house-t10-hrv'),
    pytest.param(('house', 'TEK07', 'heating_rv', 'yearly_reduction'), (2021, 2022), (7, 7), id='house-t07-hrv'),
    pytest.param(('house', 'TEK97', 'heating_rv', 'yearly_reduction'), (2021, 2022), (8, 8), id='house-t97-hrv'),
    pytest.param(('house', 'TEK87', 'heating_rv', 'yearly_reduction'), (2021, 2022), (9, 9), id='house-t87-hrv'),
    pytest.param(('apartment_block', 'TEK87', 'electrical_equipment', 'yearly_reduction'), (2021, 2022), (10, 10), id='apart-t87-elt'),
    pytest.param(('hotel', 'TEK87', 'heating_rv', 'yearly_reduction'), (2030,), (11,), id='hotel-t87-hrv'),
    pytest.param(('hotel', 'PRE_TEK49', 'heating_rv', 'yearly_reduction'), (2031, 2033), (12, 13), id='hotel-p49-hrv'),
    pytest.param(('house', 'TEK69', 'fans_and_pumps', 'yearly_reduction'), (2022, ), (14, ), id='house-69-fas'),
    pytest.param(('house', 'TEK87', 'heating_dhw', 'yearly_reduction'), (2022,), (14, ), id='house-t87-hhw'),
    pytest.param(('house', 'TEK10', 'cooling', 'yearly_reduction'), (2023, 2024, 2025, 2026, ), (17, 17, 17, 17) , id='house-t10-cog'),
    pytest.param(('house', 'TEK27', 'heating_rv', 'yearly_reduction'), (2027,), (15,), id='house-t27-hrv'),
    pytest.param(('house', 'TEK27', 'lighting', 'yearly_reduction'), (2027,), (15,), id='house-t27-lig'),
    pytest.param(('sports', 'TEK17', 'cooling', 'yearly_reduction'), (2023,), (16,), id='sports-t17-cog'),
    pytest.param(('sports', 'PRE_TEK49', 'cooling', 'yearly_reduction'), (2023,), (18,), id='sports-p49-cog'),
    pytest.param(('sports', 'TEK49', 'cooling', 'yearly_reduction'), (2023,), (19,), id='sports-t49-cog'),
    pytest.param(('sports', 'TEK10', 'cooling', 'yearly_reduction'), (2023,), (20,), id='sports-t10-cog'),
])
def test_expand_definitions_keeps_expected_definitions(selection, expected_years, expected_lineno):
    input_csv = io.StringIO("""building_category,building_code,purpose,function,start_year,value,end_year,lineno
residential,default,heating_rv,yearly_reduction,2021,0.8,2022,2
default,PRE_TEK49,lighting,yearly_reduction,2021,0.7,2022,3
default,PRE_TEK49,heating_rv,yearly_reduction,2021,0.6,2022,4
residential,TEK17,heating_rv,yearly_reduction,2021,0.5,2022,5
residential,TEK10+TEK17,heating_rv,yearly_reduction,2021,0.4,2022,6
residential,TEK07,heating_rv,yearly_reduction,2021,0.3,2022,7
house,TEK97,heating_rv,yearly_reduction,2021,0.2,2022,8
house,TEK87,heating_rv,yearly_reduction,2021,0.1,2022,9
default,default,default,yearly_reduction,2021,0.0,2022,10
hotel,default,default,yearly_reduction,2030,0.11,2030,11
hotel,PRE_TEK49,default,yearly_reduction,2031,0.031,2031,12
hotel,PRE_TEK49,default,yearly_reduction,2033,0.033,2033,13
house,default,default,yearly_reduction,2022,0.022,2022,14
default,TEK27,default,yearly_reduction,2027,0.027,2027,15
default,default,cooling,yearly_reduction,2023,0.0,2023,16
house,default,cooling,yearly_reduction,2023,0.0,2026,17
default,PRE_TEK49,cooling,yearly_reduction,2023,0.0,2023,18
default,PRE_TEK49+TEK49,cooling,yearly_reduction,2023,0.0,2023,19
default,TEK49+TEK69+TEK87+TEK97+TEK07+TEK10,cooling,yearly_reduction,2023,0.0,2023,20
default,default,cooling,improvement_at_end_year,2023,0.0,2023,21
""".strip())

    input_data = pd.read_csv(input_csv, dtype=ENERGY_NEED_IMPROVEMENT_DTYPES)

    building_category, building_code, purpose, function =selection

    result = expand_definitions(input_data, drop_helper_columns=False)
    query = f"building_category == '{building_category}' and building_code == '{building_code}' and purpose == '{purpose}' and function == '{function}'"

    actual_years = tuple(result.query(query).year)
    actual_lineno = tuple(result.query(query).lineno)

    assert actual_lineno == expected_lineno, f"Expected value for {building_category}, {building_code}, {purpose} not found in result DataFrame"
    assert actual_years == expected_years, f"Expected row count for {building_category}, {building_code}, {purpose} not found in result DataFrame"


def test_expand_definitions_does_not_change_the_definitions_parameter():
    input_data = pd.read_csv(io.StringIO(house_2tek_electrical_equipment), dtype=ENERGY_NEED_IMPROVEMENT_DTYPES)

    original_copy = input_data.copy()

    expand_definitions(input_data, drop_helper_columns=False)

    pd.testing.assert_frame_equal(input_data, original_copy)


@pytest.mark.parametrize(('selection', 'expected_years', 'expected_lineno'), [
    pytest.param(('apartment_block', 'TEK49', 'cooling'), (2020, 2021, 2022,), (2, 2, 2,), id='apartment_block-t49-cog'),
    pytest.param(('house', 'TEK49', 'heating_rv'), (2020, 2021, 2022, ), (3, 3, 3,), id='house-t49-hrv'),
    pytest.param(('house', 'PRE_TEK49', 'lighting'), (2020, 2021, 2022, ), (3, 3, 3,), id='house-p49-lig'),
    pytest.param(('house', 'TEK17', 'lighting'), (2020, 2021, 2022), (4, 4, 4,), id='house-t17-lig'),
    pytest.param(('office', 'TEK17', 'lighting'), (2020, 2021, 2022), (5, 5, 5,), id='office-t17-lig'),
    pytest.param(('retail', 'TEK17', 'lighting'), (2020, 2021, 2022), (5, 5, 5,), id='retail-t17-lig'),
    pytest.param(('retail', 'TEK17', 'electrical_equipment'), (2020, 2021, 2022), (6, 6, 6,), id='retail-t17-elt'),
])
def test_expand_definitions_keeps_expected_behaviour_factor_definitions(selection, expected_years, expected_lineno):
    input_csv = io.StringIO("""building_category,building_code,purpose,behaviour_factor
residential,default,default,1
house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.85
house,TEK07+TEK10+TEK17,lighting,0.85
non_residential,default,default,1.15
retail,default,electrical_equipment,2
""")

    input_data = pd.read_csv(input_csv, dtype={'building_category': str, 'building_code': str, 'purpose': str, 'behaviour_factor': float,})
    input_data = input_data.assign(start_year=2020, end_year=2022)

    building_category, building_code, purpose =selection

    result = expand_definitions(input_data, drop_helper_columns=False)
    query = f"building_category == '{building_category}' and building_code == '{building_code}' and purpose == '{purpose}'"

    actual_years = tuple(result.query(query).year)
    actual_lineno = tuple(result.query(query).lineno)

    assert actual_lineno == expected_lineno, f"Expected value for {building_category}, {building_code}, {purpose} not found in result DataFrame"
    assert actual_years == expected_years, f"Expected row count for {building_category}, {building_code}, {purpose} not found in result DataFrame"


@pytest.mark.parametrize(('selection', 'expected_years', 'expected_lineno'), [
    pytest.param(('apartment_block', 'PRE_TEK49', 'cooling'), (2020, 2021,), (2, 2, ), id='apartment_block-p49-cog'),
    pytest.param(('apartment_block', 'PRE_TEK49', 'electrical_equipment'), (2020, 2021,), (3, 3, ), id='apartment_block-p49-elt'),
    pytest.param(('apartment_block', 'PRE_TEK49', 'fans_and_pumps'), (2020, 2021,), (4, 4, ), id='apartment_block-p49-fas'),
    pytest.param(('apartment_block', 'PRE_TEK49', 'heating_dhw'), (2020, 2021,), (5, 5, ), id='apartment_block-p49-hhw'),
    pytest.param(('apartment_block', 'PRE_TEK49', 'heating_rv'), (2020, 2021,), (6, 6, ), id='apartment_block-p49-hrv'),
    pytest.param(('apartment_block', 'TEK49', 'lighting'), (2020, 2021,), (7, 7, ), id='apartment_block-t49-lig'),
    pytest.param(('apartment_block', 'TEK07', 'heating_rv'), (2020, 2021,), (12, 12, ), id='apartment_block-p49-hrv'),
])
def test_expand_definitions_keeps_expected_energy_need_original_condition_definitions(selection, expected_years, expected_lineno):
    input_csv = io.StringIO("""building_category,building_code,purpose,kwh_m2
apartment_block,PRE_TEK49,cooling,0.0
apartment_block,PRE_TEK49,electrical_equipment,17.52
apartment_block,PRE_TEK49,fans_and_pumps,0.5788888888888889
apartment_block,PRE_TEK49,heating_dhw,29.76888888888889
apartment_block,PRE_TEK49,heating_rv,126.739738913315
apartment_block,default,lighting,8.196800000000001
apartment_block,TEK07,cooling,0.0
apartment_block,TEK07,electrical_equipment,17.52
apartment_block,TEK07,fans_and_pumps,9.455555555555556
apartment_block,TEK07,heating_dhw,29.76888888888889
apartment_block,TEK07,heating_rv,39.52794604570375
default,default,default,-99
""")

    input_data = pd.read_csv(input_csv, dtype={'building_category': str, 'building_code': str, 'purpose': str, 'behaviour_factor': float,})
    input_data = input_data.assign(start_year=2020, end_year=2021)

    building_category, building_code, purpose =selection

    result = expand_definitions(input_data, drop_helper_columns=False)
    query = f"building_category == '{building_category}' and building_code == '{building_code}' and purpose == '{purpose}'"

    actual_years = tuple(result.query(query).year)
    actual_lineno = tuple(result.query(query).lineno)

    assert actual_lineno == expected_lineno, f"Expected value for {building_category}, {building_code}, {purpose} not found in result DataFrame"
    assert actual_years == expected_years, f"Expected row count for {building_category}, {building_code}, {purpose} not found in result DataFrame"


@pytest.mark.parametrize(('selection', 'expected_years', 'expected_lineno'), [
    pytest.param(('retail', 'PRE_TEK49', 'Gas', 'HP Central heating - Electric boiler'), (2024, 2030,), 2, id='retail-p49-g2hpeb'),
    pytest.param(('retail', 'PRE_TEK49', 'Gas', 'Electric boiler'), (2024, 2030,), 3, id='retail-p49-g2eb'),
    pytest.param(('sports', 'TEK49', 'Electricity', 'HP - Electricity'), (2024, 2040,), 4, id='sports-t49-el2hpel'),
    pytest.param(('house', 'TEK49', 'Electricity - Bio', 'HP - Bio - Electricity'), (2024, 2040,), 7, id='house-t49-elbio2hpelbio'),
    pytest.param(('house', 'TEK17', 'Electricity - Bio', 'HP - Bio - Electricity'), (2024, 2040,), 7, id='house-t17-elbio2hpelbio'),
    pytest.param(('apartment_block', 'TEK17', 'Electricity', 'DH'), (2024, 2050,), 8, id='house-t17-el2dh'),
    pytest.param(('apartment_block', 'TEK17', 'Electricity', 'HP Central heating - Electric boiler'), (2024, 2050,), 9, id='house-t17-el2hpceb'),
])
def test_expand_definitions_keeps_expected_heating_system_forecast_definitions(selection, expected_years, expected_lineno):
    input_csv = io.StringIO("""building_category,building_code,heating_systems,new_heating_systems,start_year,end_year,start_value,end_value
non_residential,default,Gas,HP Central heating - Electric boiler,2024,2030,0.1,0.5
non_residential,default,Gas,Electric boiler,2024,2030,0.1,0.5
non_residential,default,Electricity,HP - Electricity,2024,2040,0.05,0.5
non_residential,default,HP Central heating - Gas,HP Central heating - Electric boiler,2024,2030,0.2,1.0
house,default,HP Central heating - Gas,HP Central heating - Electric boiler,2024,2030,0.2,1.0
house,default,Electricity - Bio,HP - Bio - Electricity,2024,2040,0.03,0.6
apartment_block,default,Electricity,DH,2024,2050,0.029,0.161
apartment_block,default,Electricity,HP Central heating - Electric boiler,2024,2050,0.029,0.161""")

    input_data = pd.read_csv(input_csv, dtype={'building_category': str, 'building_code': str,
                                               'heating_systems': str, 'new_heating_systems': str,
                                               'start_year': int, 'end_year': int, 'start_value': float, 'end_value': float})

    building_category, building_code, heating_systems, new_heating_systems =selection

    result = expand_definitions(input_data, drop_helper_columns=False,
                                grouping_columns=['building_category', 'building_code', 'heating_systems', 'new_heating_systems'])
    selection_query = f"""
    building_category == '{building_category}'
    and building_code == '{building_code}'
    and heating_systems == '{heating_systems}'
    and new_heating_systems == '{new_heating_systems}'""".replace('\n', ' ').strip()

    expected_years = tuple(range(expected_years[0], expected_years[1]+1))
    actual_years = tuple(result.query(selection_query).year)
    actual_lineno = tuple(result.query(selection_query).lineno)

    assert actual_lineno == tuple(expected_lineno for _ in expected_years), \
        f"Expected value for {building_category}, {building_code}, {heating_systems} {new_heating_systems} not found in result DataFrame"
    assert actual_years == expected_years, \
        f"Expected row count for {building_category}, {building_code}, {heating_systems} {new_heating_systems} not found in result DataFrame"


def test_expand_definitions_drop_helper_columns_expected_columns():
    result = expand_definitions(pd.read_csv(io.StringIO(nursing_home_2_periods)), drop_helper_columns=True)
    expected_columns = {'building_category', 'building_code', 'purpose', 'function', 'start_year', 'value', 'end_year',
                        'lineno', 'year', 'dupe'}
    assert set(result.columns) == expected_columns, f"Expected columns {expected_columns}, but got {set(result.columns)}"


def test_expand_definitions_raise_value_error_on_empty_definitions():
    with pytest.raises(ValueError, match=f'Dataframe `definitions` is empty. Cannot expand grouped definitions.'):
        expand_definitions(pd.DataFrame(), drop_helper_columns=True)

@pytest.mark.parametrize(('columns', ), [
    pytest.param(('building_category',), ),
    pytest.param(('start_year',), ),
    pytest.param(('end_year',), ),
    pytest.param(('start_year', 'end_year'), ),
])
def test_expand_definitions_raise_value_error_when_missing_required_columns(columns: tuple[str]):
    definitions = pd.read_csv(io.StringIO(nursing_home_2_periods))

    expected_message = f'DataFrame `definitions` does not contain all required columns. Missing column: {columns[0]}'
    if len(columns) > 1:
        expected_message = f'DataFrame `definitions` does not contain all required columns. Missing columns: {", ".join(columns)}'
    with pytest.raises(ValueError, match=expected_message):
        expand_definitions(definitions.drop(columns=list(columns)), drop_helper_columns=True)


def test_expand_definitions_raise_value_error_when_missing_grouping_columns():
    definitions = pd.DataFrame({
        'building_category': ['house', 'apartment_block'],
        'column_a': ['a', 'a'],
        'start_year': [2020, 2020],
        'end_year': [2020, 2020],
        'value': [1, 2],
        'lineno': [2, 3],
    })

    expected_singular = 'DataFrame `definitions` does not contain all columns specified in `grouping_columns`. Missing columns: column_b.'
    with pytest.raises(ValueError, match=expected_singular):
        expand_definitions(definitions, grouping_columns=['building_category', 'column_a', 'column_b'])

    expected_plural = re.escape('DataFrame `definitions` does not contain all columns specified in `grouping_columns`. Missing columns: column_a, column_b.')

    with pytest.raises(ValueError, match=expected_plural):
        expand_definitions(definitions.drop(columns=['column_a']), grouping_columns=['building_category', 'column_a', 'column_b'])


nan_building_category = """building_category,building_code,purpose,function,start_year,value,end_year
,TEK87,lighting,yearly_reduction,2022,0.02,2022
""".strip()

nan_and_valid_building_category = """building_category,building_code,purpose,function,start_year,value,end_year
,TEK87,lighting,yearly_reduction,2022,0.02,2022
house,TEK87,lighting,yearly_reduction,2022,0.03,2022
""".strip()


@pytest.mark.parametrize(('input_data', 'expected_dtype', 'expected_message'), [
    pytest.param(nan_building_category, 'float64',
                 re.escape('DataFrame `definitions` column `building_category`(float64). Expected dtype string.'),
                 id='all_values_nan_column_is_float'),
    pytest.param(nan_and_valid_building_category, 'str', re.escape("Dataframe 'building_category' cannot be empty"),
                 id='some_values_nan_column_is_str'),
])
def test_expand_definitions_raises_on_nan_building_category(
        input_data: str, expected_dtype: str, expected_message: str):
    """A missing building_category always raises ValueError, with a message that depends on dtype.

    When every value is missing pandas types the column as float64, which is
    rejected by the dtype check. A mix of missing and present values gives a
    string column, which reaches the emptiness guard in `explode_on_plus`.
    """
    definitions = pd.read_csv(io.StringIO(input_data))
    assert definitions['building_category'].dtype == expected_dtype
    assert definitions['building_category'].isna().any()

    with pytest.raises(ValueError, match=expected_message):
        expand_definitions(definitions)


nan_function = """building_category,building_code,purpose,function,start_year,value,end_year
house,TEK87,lighting,,2022,0.02,2022
""".strip()

nan_and_valid_function = """building_category,building_code,purpose,function,start_year,value,end_year
house,TEK87,lighting,,2022,0.02,2022
apartment_block,TEK87,lighting,yearly_reduction,2022,0.03,2022
""".strip()


def test_expand_definitions_raises_when_all_function_values_are_nan():
    """An all NaN `function` column is typed float64 and rejected by the dtype check."""
    definitions = pd.read_csv(io.StringIO(nan_function))
    assert definitions['function'].dtype == 'float64'

    expected_message = re.escape('DataFrame `definitions` column `function`(float64). Expected dtype string.')
    with pytest.raises(ValueError, match=expected_message):
        expand_definitions(definitions)


def test_expand_definitions_keep_rows_with_nan_function():
    definitions = pd.read_csv(io.StringIO(nan_and_valid_function))
    assert definitions['function'].dtype == 'str'
    assert definitions['function'].isna().sum() == 1

    result = expand_definitions(definitions)

    assert result['building_category'].tolist() == ['apartment_block', 'house']

    assert result['value'].tolist() == [0.03, 0.02]


def test_transform_with_clear_winner():
    csv_content = """building_category,building_code,purpose,function,start_year,value,end_year
house+apartment_block,TEK49,lighting,yearly_reduction,2022,0.02,2023
house,TEK49,lighting,yearly_reduction,2022,0.03,2023
house+apartment_block,TEK49,lighting,yearly_reduction,2022,0.04,2023"""

    df = pd.read_csv(io.StringIO(csv_content), dtype=ENERGY_NEED_IMPROVEMENT_DTYPES)

    actual = expand_definitions(df)
    assert len(actual) == 6, 'Expected 6 rows in result'  # 3 rows expanded to 2 years each
    assert not actual.query("lineno==3").dupe.all()


def expanded(energy_need_improvements_csv):
    single_csv = io.StringIO(energy_need_improvements_csv)
    input_data = pd.read_csv(single_csv, dtype=ENERGY_NEED_IMPROVEMENT_DTYPES)

    return {'input': input_data.pipe(add_lineno).reset_index(drop=True),
            'expanded': expand_definitions(input_data, drop_helper_columns=True)}


@pytest.mark.parametrize(('input_data', 'column', 'expected'), [
    pytest.param(expanded(single_year), 'lineno', tuple(), id='single_year_no_duplicates_lineno'),
    pytest.param(expanded(single_year), 'duplicate_lineno', tuple(), id='single_year_duplicate_lineno'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'lineno', (2, ), id='single_year_lineno'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'duplicate_lineno', (3, ), id='house_t17_elt_dupe_lineno'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_codes', ('TEK17', ), id='house_t17_elt_dupe_building_codes'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_codes_cnt', (1, ), id='house_t17_elt_dupe_building_codes_cnt'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_categories', ('house', ), id='house_t17_elt_dupe_building_categories'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_categories_cnt', (1, ), id='house_t17_elt_dupe_building_categories_cnt'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_category_original', ('house', ), id='house_t17_building_category_original'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), 'building_code_original', ('TEK17', ), id='house_t17_elt_building_code_original'),
])
def test_summarize_energy_need_improvement_conflicts(input_data: pd.DataFrame, column: str, expected: tuple[typing.Any]):
    conflicts = summarize_energy_need_improvement_conflicts(input_data.get('expanded'), input_data.get('input'))

    assert column in conflicts.columns, f"Column '{column}' not found in conflicts DataFrame"
    actual = conflicts[column]
    assert tuple(actual) == expected


@pytest.mark.parametrize(('input_data', 'columns', 'expected_message'), [
    pytest.param(expanded(single_year), ('lineno', ),
                 'Dataframe exploded_definition is missing lineno column(s)', id='single_year_no_duplicates_lineno'),
    pytest.param(expanded(single_year), ( 'building_category', 'lineno'),
                 'Dataframe exploded_definition is missing building_category, lineno column(s)', id='missing_building_category'),
    pytest.param(expanded(single_year), ( 'building_code', 'purpose', 'function','year'),
                 'Dataframe exploded_definition is missing building_code, purpose, function, year column(s)', id='missing_multiple_columns'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), ('lineno', ), 'Dataframe exploded_definition is missing lineno column(s)',
                 id='house_tek17_electrical_equipment_dupe_lineno'),
])
def test_summarize_energy_need_improvement_raise_value_error_on_missing_columns_in_exploded_definition(
        input_data: dict[str, pd.DataFrame], columns: tuple[str], expected_message: str):
    expanded_definition = input_data.get('expanded').drop(columns=list(columns))
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        summarize_energy_need_improvement_conflicts(expanded_definition, input_data.get('input'))


@pytest.mark.parametrize(('input_data', 'columns', 'expected_message'), [
    pytest.param(expanded(single_year), ('lineno', ), 'Dataframe original_definition is missing lineno column(s)', id='input_missing_lineno'),
    pytest.param(expanded(single_year), ('purpose', ), 'Dataframe original_definition is missing purpose column(s)', id='input_missing_purpose'),
    pytest.param(expanded(single_year), ('function', ), 'Dataframe original_definition is missing function column(s)', id='input_missing_function'),
    pytest.param(expanded(single_year), ('building_category', 'lineno', ),
                'Dataframe original_definition is missing building_category, lineno column(s)', id='input_missing_multiple'),
    pytest.param(expanded(single_year), ('building_code', 'lineno', ),
                 'Dataframe original_definition is missing building_code, lineno column(s)', id='input_missing_building_code'),
    pytest.param(expanded(house_tek17_electrical_equipment_dupe), ('lineno', ),
                 'Dataframe original_definition is missing lineno column(s)', id='house_tek17_electrical_equipment_dupe'),
])
def test_summarize_energy_need_improvement_raise_value_error_on_missing_columns_in_original_definition(
        input_data: dict[str, pd.DataFrame], columns: tuple[str], expected_message: str):
    original = input_data.get('input').drop(columns=list(columns))
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        summarize_energy_need_improvement_conflicts(input_data.get('expanded'), original)


def test_build_grouping_prefers_available_group_columns():
    df = pd.DataFrame(
        {
            "lineno": [2],
            "building_category": ["house"],
            "building_code": ["TEK17"],
            "purpose": ["lighting"],
        },
    )

    assert build_grouping(df) == ["building_category", "building_code", "purpose"]


def test_build_grouping_includes_building_group_when_present():
    df = pd.DataFrame(
        {
            "lineno": [2],
            "building_group": ["residential"],
            "building_category": ["house"],
            "building_code": ["TEK17"],
            "purpose": ["lighting"],
        },
    )

    assert build_grouping(df) == ["building_category", "building_code", "purpose"]


def test_select_groups_with_lowest_lineno_count_require_lineno():
    df = pd.DataFrame({
        'building_category': ['house'],
        'building_code': ['TEK17'],
        'purpose': ['lighting'],
        'function': ['yearly_reduction'],
        'value': [0.2],
        'start_year': [2010],
        'end_year': [2030],
    })

    with pytest.raises(KeyError, match=r'Dataframe must contain a "lineno" column \(building_category, building_code, purpose, function\)'):
        df.pipe(select_groups_with_lowest_lineno_count)


@pytest.mark.parametrize(('lineno', 'lineno_count', 'building_categories', 'value'),
[
        (2, 11, {'culture', 'hospital', 'hotel', 'kindergarten', 'nursing_home', 'office', 'retail', 'school', 'sports', 'storage_repairs', 'university'}, 0.2),
        (3, 1, {'apartment_block'}, 0.3),
        (4, 1, {'house'}, 0.4),
    ])
def test_select_groups_with_lowest_lineno_count(lineno, lineno_count, building_categories, value):
    df = pd.DataFrame({
        'lineno': [2, 3, 4],
        'building_category': ['default', 'residential', 'house'],
        'building_code': ['TEK17', 'TEK17', 'TEK17'],
        'purpose': ['lighting', 'lighting', 'lighting'],
        'function': ['yearly_reduction', 'yearly_reduction', 'yearly_reduction'],
        'value': [0.2, 0.3, 0.4],
        'start_year': [2010, 2010, 2010],
        'end_year': [2030, 2030, 2030],
    })

    df_expanded = expanded_energy_need_improvements_schema().validate(df)
    result = df_expanded.pipe(select_groups_with_lowest_lineno_count, filter_columns=False)

    query_line = f'lineno=={lineno}'
    assert list(result.query(query_line).value) == [value]  * lineno_count
    assert set(result.query(query_line).building_category) == building_categories


def test_select_groups_with_lowest_lineno_count_return_dataframe_with_expected_columns():
    df = pd.DataFrame(
        {
            'lineno': [2],
            'building_category': ['kindergarten'],
            'building_code': ['TEK17'],
            'purpose': ['lighting'],
            'function': ['yearly_reduction'],
            'value': [0.2],
            'start_year': [2010],
            'end_year': [2030],
        },
    )

    expected = pd.DataFrame(
        {
            'lineno': [2],
            'building_category': ['kindergarten'],
            'building_code': ['TEK17'],
            'purpose': ['lighting'],
            'function': ['yearly_reduction'],
            'value': [0.2],
            'start_year': [2010],
            'end_year': [2030],
        },
    )
    result = df.pipe(select_groups_with_lowest_lineno_count)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_select_groups_with_lowest_lineno_count_honours_by_grouping():
    grouping = ['building_category', 'building_code', 'heating_systems', 'new_heating_systems']
    df = pd.DataFrame(
        [
            ('office', 'TEK17', 'Gas', 'X', 2, 0.1),
            ('hotel', 'TEK17', 'Gas', 'X', 2, 0.1),
            ('office', 'TEK17', 'Gas', 'X', 3, 0.2),
            ('office', 'TEK17', 'Electricity', 'Y', 4, 0.3),
            ('hotel', 'TEK17', 'Electricity', 'Y', 4, 0.3),
        ],
        columns=[*grouping, 'lineno', 'value'],
    )

    result = select_groups_with_lowest_lineno_count(df, grouping_columns=grouping, filter_columns=False)

    office_gas = result.query("building_category == 'office' and heating_systems == 'Gas'")
    assert tuple(office_gas.lineno) == (3,), 'the most specific line must win its own group'

    hotel_electricity = result.query("building_category == 'hotel' and heating_systems == 'Electricity'")
    assert tuple(hotel_electricity.lineno) == (4,)

    office_electricity = result.query("building_category == 'office' and heating_systems == 'Electricity'")
    assert tuple(office_electricity.lineno) == (4,), 'office lost its Electricity -> Y definition'


def test_group_dupes_on_dupes():
    df = pd.DataFrame(
        [
            {'building_category': 'office', 'lineno': 2, 'year': 2021, 'value': 0.02, 'dupe': False},
            {'building_category': 'office', 'lineno': 2, 'year': 2022, 'value': 0.02, 'dupe': False},
            {'building_category': 'retail', 'lineno': 3, 'year': 2021, 'value': 0.03, 'dupe': True},
            {'building_category': 'retail', 'lineno': 3, 'year': 2022, 'value': 0.03, 'dupe': True},
            {'building_category': 'retail', 'lineno': 4, 'year': 2021, 'value': 0.04, 'dupe': True},
            {'building_category': 'retail', 'lineno': 4, 'year': 2022, 'value': 0.04, 'dupe': True},
            {'building_category': 'house', 'lineno':5, 'year': 2021, 'value': 0.05, 'dupe': True},
            {'building_category': 'house', 'lineno': 6, 'year': 2021, 'value': 0.06, 'dupe': True},
        ],
    )
    result = df.pipe(group_dupes_on_dupes)

    expected = pd.DataFrame(
        [
            {'building_category': 'retail', 'lineno_x': 3, 'lineno_y': 4, 'year_x': 2021, 'year_y': 2021, 'value_x': 0.03, 'value_y': 0.04},
            {'building_category': 'retail', 'lineno_x': 3, 'lineno_y': 4, 'year_x': 2022, 'year_y': 2022, 'value_x': 0.03, 'value_y': 0.04},
            {'building_category': 'retail', 'lineno_x': 4, 'lineno_y': 3, 'year_x': 2021, 'year_y': 2021, 'value_x': 0.04, 'value_y': 0.03},
            {'building_category': 'retail', 'lineno_x': 4, 'lineno_y': 3, 'year_x': 2022, 'year_y': 2022, 'value_x': 0.04, 'value_y': 0.03},
            {'building_category': 'house', 'lineno_x': 5, 'lineno_y': 6, 'year_x': 2021, 'year_y': 2021, 'value_x': 0.05, 'value_y': 0.06},
            {'building_category': 'house', 'lineno_x': 6, 'lineno_y': 5, 'year_x': 2021, 'year_y': 2021, 'value_x': 0.06, 'value_y': 0.05},
        ],
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_group_duplicated_lineno_summary_accepts_lineno_y_and_lineno_x():
    df = pd.DataFrame([
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction',
            'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4}],
)

    result = df.pipe(group_duplicated_lineno_summary)
    expected = pd.DataFrame(
        [{
            'lineno': 3, 'duplicate_lineno': 4,
            'building_categories': 'retail',
            'building_categories_cnt': 1,
            'building_codes': 'TEK07+TEK10+TEK17',
            'building_codes_cnt': 3,
            'purposes': 'electrical_equipment',
            'purposes_cnt': 1,
            'functions': 'yearly_reduction',
            'functions_cnt': 1,
            'all_cnt': 6,
        },
        ],
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_group_duplicated_lineno_summary_merge_and_summarize_duplicates_on_building_code():
    df = pd.DataFrame([
        {'building_category': 'retail',
         'building_code': 'TEK07',
         'purpose': 'electrical_equipment',
         'function': 'yearly_reduction',
         'lineno': 3,
         'duplicate_lineno': 4},
        {'building_category': 'retail',
         'building_code': 'TEK10',
         'purpose': 'electrical_equipment',
         'function': 'yearly_reduction',
         'lineno': 3,
         'duplicate_lineno': 4},
    ])

    result = df.pipe(group_duplicated_lineno_summary)

    expected = pd.DataFrame([
        {
            'lineno': 3,
            'duplicate_lineno': 4,
            'building_categories': 'retail',
            'building_categories_cnt': 1,
            'building_codes': 'TEK07+TEK10',
            'building_codes_cnt': 2,
            'purposes': 'electrical_equipment',
            'purposes_cnt': 1,
            'functions': 'yearly_reduction',
            'functions_cnt': 1,
            'all_cnt': 5,
        },
    ])

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_group_duplicated_lineno_summary_merge_and_summarize_duplicates_on_building_category():
    df = pd.DataFrame([
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'lighting', 'function': 'yearly_reduction', 'lineno': 3, 'duplicate_lineno': 4},
        {'building_category': 'office', 'building_code': 'TEK07', 'purpose': 'lighting', 'function': 'yearly_reduction', 'lineno': 3, 'duplicate_lineno': 4},
        {'building_category': 'hotel', 'building_code': 'TEK07', 'purpose': 'lighting', 'function': 'yearly_reduction', 'lineno': 3, 'duplicate_lineno': 4},

    ])

    result = df.pipe(group_duplicated_lineno_summary)

    expected = pd.DataFrame([
        {
            'lineno': 3,
            'duplicate_lineno': 4,
            'building_categories': 'retail+office+hotel',
            'building_categories_cnt': 3,
            'building_codes': 'TEK07',
            'building_codes_cnt': 1,
            'purposes': 'lighting',
            'purposes_cnt': 1,
            'functions': 'yearly_reduction',
            'functions_cnt': 1,
            'all_cnt': 6,
        },
    ])

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_group_duplicated_lineno_summary_merge_and_summarize_basic_line():
    df = pd.DataFrame([
        {'building_category': 'apartment_block',
         'building_code': 'TEK69',
         'purpose': 'lighting',
         'function': 'improvement_and_end_year',
         'lineno': 2,
         'duplicate_lineno': 5,
         },
    ])

    result = group_duplicated_lineno_summary(df)

    expected = pd.DataFrame([
        {
            'lineno': 2,
            'duplicate_lineno': 5,
            'building_categories': 'apartment_block',
            'building_categories_cnt': 1,
            'building_codes': 'TEK69',
            'building_codes_cnt': 1,
            'purposes': 'lighting',
            'purposes_cnt': 1,
            'functions': 'improvement_and_end_year',
            'functions_cnt': 1,
            'all_cnt': 4,
        },
    ])

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_collapse_years():
    df = pd.DataFrame({
        'building_category': ['house', 'house', 'house', 'apartment_block'],
        'building_code': ['TEK07', 'TEK07', 'TEK07', 'TEK07'],
        'purpose': ['heating_rv', 'heating_rv', 'heating_rv', 'heating_rv'],
        "start_year": [2020, 2020, 2020, 2020],
        "end_year": [2022, 2022, 2022, 2020],
        'function': ['yearly_reduction', 'yearly_reduction', 'yearly_reduction', 'yearly_reduction'],
        "year": [2020, 2021, 2022, 2020],
        "value": [0.5, 0.5, 0.5, 0.3],
        "lineno": [2, 2, 2, 3],
    })
    result = collapse_years(df)
    expected = pd.DataFrame({
        'building_category': ['house', 'apartment_block'],
        'building_code': ['TEK07', 'TEK07'],
        'purpose': ['heating_rv', 'heating_rv'],
        "start_year": [2020, 2020],
        "end_year": [2022, 2020],
        'function': ['yearly_reduction', 'yearly_reduction'],
        "value": [0.5, 0.3],
        "lineno": [2, 3],
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_collapse_years_raise_value_error_on_duplicates():
    df = pd.DataFrame({
        'building_category': ['house', 'house', ],
        'building_code': ['TEK07', 'TEK07', ],
        'purpose': ['heating_rv', 'heating_rv', ],
        "start_year": [2020, 2020 ],
        "end_year": [2020, 2020 ],
        'function': ['yearly_reduction', 'yearly_reduction'],
        "year": [2020, 2020],
        "value": [0.5, 0.6],
        "lineno": [2, 3],
    })
    with pytest.raises(ValueError, match=r'Duplicate values found for the same group'):
        collapse_years(df)
    with pytest.raises(ValueError, match=r'Duplicate values found for the same group'):
        collapse_years(df.drop(columns=['start_year']))
    with pytest.raises(ValueError, match=r'Duplicate values found for the same group'):
        collapse_years(df.drop(columns=['end_year']))


@pytest.mark.parametrize('year', [
    pytest.param(2019, id='less_than_start_year'),
    pytest.param(2022, id='greater_than_end_year'),
])
def test_collapse_years_drop_years_outside_start_end_year(year):
    df = pd.DataFrame({
        'building_category': ['house', 'house', 'house', 'house', 'house'],
        "start_year": [2020, 2020, 2020, 2020, 2020],
        "end_year": [2023, 2023, 2023, 2021, 2021],
        'function': ['yearly_reduction', 'yearly_reduction', 'yearly_reduction', 'yearly_reduction', 'yearly_reduction'],
        "year": [2020, 2021, 2022, year , 0],
        "value": [0.2, 0.2, 0.2, 0.3, 0.3],
        "lineno": [2, 2, 2, 3, 3],
    })
    result = collapse_years(df)
    assert result.lineno.to_list() == [2]
    assert result.value.to_list() == [0.2]

@pytest.mark.parametrize('missing_column', [
    ('start_year',),
    ('end_year',),
    ('start_year', 'end_year')])
def test_collapse_years_accept_missing_start_or_end_year(missing_column):
    df = pd.DataFrame({
        'building_category': ['house', 'apartment_block'],
        "start_year": [2020, 2020],
        "end_year": [2022, 2020],
        'function': ['noop', 'noop'],
        "year": [2020, 2020],
        "value": [0.5, 0.3],
        "lineno": [2, 3],
    })
    result = collapse_years(df.drop(columns=list(missing_column)))
    expected = pd.DataFrame({
        'building_category': ['house', 'apartment_block'],
        "start_year": [2020, 2020],
        "end_year": [2022, 2020],
        'function': ['noop', 'noop'],
        "value": [0.5, 0.3],
        "lineno": [2, 3],
    }).drop(columns=list(missing_column))

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


if __name__ == "__main__":
    import sys

    pytest.main([sys.argv[0]])
