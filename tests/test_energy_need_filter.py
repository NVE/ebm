import io

import pandas as pd
import pytest

from ebm.model.energy_need_filter import de_dupe_dataframe, explode_dataframe, dedupe_and_merge_by_priority
from ebm.model.energy_purpose import EnergyPurpose


def test_de_dupe_dataframe():
    settings = pd.read_csv(io.StringIO(
"""building_category,building_code,purpose,value,start_year,function,end_year
default,default,cooling,0.0,2020,yearly_reduction,
default,default,electrical_equipment,0.01,2021,yearly_reduction,
default,default,lighting,0.005,2031,yearly_reduction,2050
default,default,lighting,0.5555555555555556,2020,improvement_at_end_year,2030
""".strip()))

    df = de_dupe_dataframe(df=explode_dataframe(settings),
                           unique_columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year', 'function'])

    others = df.query('purpose not in ["lighting", "electrical_equipment"]')

    assert (others.value == 0.0).all()
    el_eq = df.query('purpose in ["electrical_equipment"]')
    assert len(el_eq) == 104
    assert (el_eq.value == 0.01).all()
    lighting_yearly_reduction = df.query('purpose in ["lighting"] and function=="yearly_reduction"')
    assert len(lighting_yearly_reduction) == 104
    assert (lighting_yearly_reduction.value == 0.005).all()
    lighting_improvement_at_end_year = df.query('function=="improvement_at_end_year"')
    assert len(lighting_improvement_at_end_year) == 104
    assert (lighting_improvement_at_end_year.value == 0.5555555555555556).all()


def test_explode_dataframe():
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,kwh_m2
    default,TEK07,cooling,0.1
    apartment_block,default,cooling,0.2                                                                                   
    apartment_block,TEK07,default,0.3
    default,default,default,0.99                                                                                                                                                                                                                                                                                          
    """.strip()), skipinitialspace=True)

    ex_df = explode_dataframe(
        df=original_condition,
        building_code_list='TEK49 PRE_TEK49 PRE_TEK49_RES_1950 TEK69 TEK87 TEK97 TEK07 TEK10 TEK17 TEK21 TEK01'.split(' '))
    cooling = ex_df.query('building_category=="apartment_block" and building_code=="TEK07" and purpose=="cooling"')

    assert len(cooling) == 4
    assert cooling.iloc[0].kwh_m2 == 0.3


@pytest.mark.parametrize(
    "column,expected",
    [
        pytest.param('_categories', [
            'house+apartment_block+kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs',
            'apartment_block',
            'apartment_block+house',
            'house+apartment_block+kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs',
        ], id="building_category-plus-set"),
        pytest.param('_building_category', ['default', 'apartment_block', 'residential', 'default',], id='original building_category'),
        pytest.param('bc_priority', [13, 0, 2, 13], id='bc_priority'),
        pytest.param('_purps', ['cooling', 'cooling', '+'.join([p for p in EnergyPurpose]), 'cooling+fans_and_pumps'], id='purpose-plus-set'),
        pytest.param('_building_code', ['TEK_C+TEK_A', 'default', 'TEK_C', 'default',], id='original building_code'),
        pytest.param('t_priority', [2, 3, 0, 3], id='t_priority'),
        pytest.param('_purpose', ['cooling', 'cooling', 'default', 'cooling+fans_and_pumps',], id='original purpose'),
        pytest.param('p_priority', [0, 0, 6, 2], id='p_priority'),
        pytest.param('_row', [1, 2, 3, 4], id='_row'),
        pytest.param('_codes', ['TEK_A+TEK_C', 'TEK_A+TEK_B+TEK_C', 'TEK_C', 'TEK_A+TEK_B+TEK_C'], id='building_code-plus-set'),
        #pytest.param(0, 0, 0, marks=pytest.mark.slow),
    ],
)
def test_explode_dataframe_columns(column, expected):
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,kwh_m2
    default,TEK_C+TEK_A,cooling,0.1
    apartment_block,default,cooling,0.2                                                                                   
    residential,TEK_C,default,0.3
    default,default,cooling+fans_and_pumps,0.99                                                                                                                                                                                                                                                                                          
    """.strip()), skipinitialspace=True)

    ex_df = explode_dataframe(
        df=original_condition,
        building_code_list='TEK_A TEK_B TEK_C'.split(' '))

    cooling = ex_df.query('building_category=="apartment_block" and building_code=="TEK_C" and purpose=="cooling"').sort_values(['kwh_m2'])
    assert column in ex_df.columns, f'{column} not in dataframe'

    if isinstance(expected[0], str):
        actual = cooling[column].str.split('+').apply(lambda r: set(r)).to_list()
        expected = [set(c.split('+')) for c in expected]
        assert actual == expected, f'expected values: {expected}, got: {actual}'
    else:
        assert cooling[column].to_list() == expected


def test_dedupe_and_merge_by_priority():
    csv="""building_category,building_code,purpose,function,start_year,end_year,value,priority
house,TEK17,cooling,yearly_reduction,2020,2050,0.0,21
house,TEK17,electrical_equipment,yearly_reduction,2021,2050,0.01,21
house,TEK17,fans_and_pumps,yearly_reduction,2020,2050,0.0,21
house,TEK17,heating_dhw,yearly_reduction,2020,2050,0.0,21
house,TEK17,lighting,improvement_at_end_year,2020,2025,0.555555556,8
house,TEK17,lighting,yearly_reduction,2030,2050,0.2,10
house,TEK17,lighting,yearly_reduction,2026,2030,0.05,8
house,TEK17,lighting,yearly_reduction,2031,2050,0.005,8
house,TEK17,lighting,yearly_reduction,2020,2050,0.0,21
""".strip()
    df = pd.read_csv(io.StringIO(csv))

    actual = dedupe_and_merge_by_priority(df)

    expected = pd.read_csv(io.StringIO("""building_category,building_code,purpose,function,start_year,end_year,value
house,TEK17,cooling,yearly_reduction,2020,2050,0.0
house,TEK17,electrical_equipment,yearly_reduction,2021,2050,0.01
house,TEK17,fans_and_pumps,yearly_reduction,2020,2050,0.0
house,TEK17,heating_dhw,yearly_reduction,2020,2050,0.0
house,TEK17,lighting,improvement_at_end_year,2020,2025,0.555555556
house,TEK17,lighting,yearly_reduction,2026,2030,0.05
house,TEK17,lighting,yearly_reduction,2031,2050,0.005
""".strip()))

    pd.testing.assert_frame_equal(expected, actual)


@pytest.mark.parametrize('columns', [['building_category'], ['building_code', 'function'], ['priority', 'purpose']])
def test_dedupe_and_merge_by_priority_raise_value_error_on_missing_columns(columns):
    csv = """building_category,building_code,purpose,function,start_year,end_year,value,priority
    house,TEK17,cooling,yearly_reduction,2020,2050,0.0,21
    """.strip()
    df = pd.read_csv(io.StringIO(csv))

    msg = f'Column {", ".join(columns)} not in DataFrame'
    with pytest.raises(ValueError, match=msg):
        dedupe_and_merge_by_priority(df.drop(columns=columns))


def test_dedupe_and_merge_by_priority_keep_unknown_columns():
    csv = """building_category,building_code,purpose,function,start_year,_underscore_prefix,CHANGE,priority
    house,TEK17,cooling,yearly_reduction,2020,2050,0.0,21
    """.strip()
    df = pd.read_csv(io.StringIO(csv))

    actual = dedupe_and_merge_by_priority(df)

    assert 'CHANGE' in actual.columns, 'Lost column CHANGE while deduplicating'
    assert '_underscore_prefix' in actual.columns, 'dedupe_and_merge_by_priority did not filter skip _skip_underscore_prefix'


def test_dedupe_and_merge_by_priority_drop_dupes():
    csv="""building_category,building_code,purpose,function,start_year,end_year,value,priority
house,TEK17,lighting,yearly_reduction,2026,2030,0.05,8
house,TEK17,lighting,yearly_reduction,2031,2050,0.005,8
house,TEK17,lighting,yearly_reduction,2030,2050,0.2,10
house,TEK17,lighting,yearly_reduction,2026,2030,0.05,8
house,TEK17,lighting,yearly_reduction,2030,2050,0.2,10
""".strip()
    df = pd.read_csv(io.StringIO(csv))
    # house,TEK17,lighting,yearly_reduction,2026,2030,0.05,8

    actual = dedupe_and_merge_by_priority(df)

    expected = pd.read_csv(io.StringIO("""building_category,building_code,purpose,function,start_year,end_year,value
house,TEK17,lighting,yearly_reduction,2026,2030,0.05
house,TEK17,lighting,yearly_reduction,2031,2050,0.005
""".strip()))

    pd.testing.assert_frame_equal(expected, actual)


if __name__ == "__main__":
    pytest.main()
