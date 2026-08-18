import io

import pandas as pd
import pytest

from ebm import input_filter
from ebm.input_filter import de_dupe_dataframe, explode_dataframe, dedupe_and_merge_by_priority
from ebm.model.energy_purpose import EnergyPurpose


@pytest.mark.parametrize('missing_column', [
    'lineno',
    'building_category_org',
    'building_code_org',
    'purpose',
    'function',
    'year',
    'score',
])
def test_detect_conflicts_raise_value_error_for_missing_column(missing_column):
    df = pd.DataFrame({
        'lineno': [1],
        'building_category_org': ['house'],
        'building_code_org': ['TEK17'],
        'purpose': ['lighting'],
        'function': ['foo'],
        'year': [2020],
        'score': [0.5],
    }).drop(columns=[missing_column])

    with pytest.raises(ValueError, match=f'Missing required columns: .*{missing_column}'):
        input_filter.detect_conflicts(df)


@pytest.mark.parametrize(
    'missing_column',
    [
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'year',
        'score',
        'definition_lineno',
        'conflict_lineno',
    ],
)
def test_make_energy_need_improvements_periodical(missing_column):
    conflicts = pd.DataFrame({
        'conflict_lineno': [1],
        'definition_lineno': [1],
        'building_category_org': ['house'],
        'building_code_org': ['TEK17'],
        'purpose': ['lighting'],
        'function': ['foo'],
        'year': [2020],
        'score': [0.5],
    }).drop(columns=[missing_column])

    energy_need_improvements_csv = pd.DataFrame({
        'building_category': ['house'],
        'building_code': ['TEK17'],
        'purpose': ['lighting'],
        'function': ['foo'],
        'start_year': [2020],
        'end_year': [2025],
        'value': [0.5],
    })

    with pytest.raises(ValueError, match=f'Missing required columns: .*{missing_column}'):
        input_filter.make_energy_need_improvements_periodical(conflicts, energy_need_improvements_csv)

@pytest.fixture
def score_energy_need_improvement():
    df = pd.DataFrame(
        {
            'building_category_org': ['cat', 'cat', 'cat', 'cat', 'cat'],
            'building_code_org': ['cod', 'cod', 'cod', 'cod', 'cod'],
            'purpose': ['pur', 'pur', 'pur', 'pur', 'pur'],
            'function': ['func_a', 'func_b', 'func_b', 'func_b', 'func_b'],
            'start_year': [2020, 2031, 2031, 2031, 2031],
            'end_year': [2030, 2050, 2050, 2050, 2050],
            '_energy_need_improvements_csv': [6, 7, 8, 9, 10],
            'score': [0.015, 0.015, 0.15, 1.0, 1.0],
        }
    )
    return df


@pytest.mark.parametrize(
    'missing_column',
    [
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'score',
    ],
)
def test_input_filter_mark_high_score_raise_value_error_on_missing_columns(missing_column, score_energy_need_improvement):
    with pytest.raises(ValueError):
        input_filter.mark_high_score(score_energy_need_improvement.drop(columns=[missing_column]))


@pytest.fixture
def building_categories():
    return pd.DataFrame({'building_category': ['SmallHouse', 'Apartment', 'Office']})


def test_score_building_group_default_assigns_default_building_group(building_categories):
    result = input_filter.score_building_group_default(building_categories)
    assert (result['building_group'] == 'default').all()


def test_score_building_group_default_assigns_score(building_categories):
    result = input_filter.score_building_group_default(building_categories)
    assert (result['score'] == 0.1).all()


def test_score_building_group_default_assigns_num_equal_to_row_count(building_categories):
    result = input_filter.score_building_group_default(building_categories)
    assert (result['num'] == len(building_categories)).all()


def test_score_building_group_default_preserves_building_category(building_categories):
    result = input_filter.score_building_group_default(building_categories)
    assert result['building_category'].tolist() == building_categories['building_category'].tolist()


def test_score_building_group_default_single_row():
    df = pd.DataFrame({'building_category': ['SmallHouse']})
    result = input_filter.score_building_group_default(df)
    assert result['num'].iloc[0] == 1
    assert result['building_group'].iloc[0] == 'default'
    assert result['score'].iloc[0] == 0.1


def test_score_building_group_default_empty_dataframe():
    df = pd.DataFrame({'building_category': []})
    result = input_filter.score_building_group_default(df)
    assert len(result) == 0
    assert 'building_group' in result.columns
    assert 'score' in result.columns
    assert 'num' in result.columns


def test_score_building_category_specific_building_group_equals_building_category():
    df = pd.DataFrame({'building_category': ['house', 'office', 'school']})
    result = input_filter.score_building_category_specific(df)
    assert result['building_group'].tolist() == ['house', 'office', 'school']


def test_score_building_category_specific_score_is_one():
    df = pd.DataFrame({'building_category': ['house', 'office', 'school']})
    result = input_filter.score_building_category_specific(df)
    assert (result['score'] == 1.0).all()


def test_score_building_category_specific_num_is_one():
    df = pd.DataFrame({'building_category': ['house', 'office', 'school']})
    result = input_filter.score_building_category_specific(df)
    assert (result['num'] == 1).all()


def test_score_building_category_specific_preserves_building_category():
    df = pd.DataFrame({'building_category': ['house', 'office', 'school']})
    result = input_filter.score_building_category_specific(df)
    assert result['building_category'].tolist() == ['house', 'office', 'school']


def test_score_building_category_specific_preserves_row_count():
    df = pd.DataFrame({'building_category': ['house', 'office', 'school']})
    result = input_filter.score_building_category_specific(df)
    assert len(result) == len(df)


def test_score_building_category_specific_empty_dataframe():
    df = pd.DataFrame({'building_category': []})
    result = input_filter.score_building_category_specific(df)
    assert len(result) == 0
    assert 'building_group' in result.columns
    assert 'score' in result.columns
    assert 'num' in result.columns


@pytest.fixture
def score_building_category_all_inputs():
    specific = pd.DataFrame({'building_category': ['house', 'office'], 'building_group': ['house', 'office'], 'score': [1.0, 1.0], 'num': [1, 1]})
    groups = pd.DataFrame({'building_category': ['house', 'office'], 'building_group': ['residential', 'non_residential'], 'score': [0.5, 0.75], 'num': [2, 1]})
    default = pd.DataFrame({'building_category': ['house', 'office'], 'building_group': ['default', 'default'], 'score': [0.1, 0.1], 'num': [2, 2]})
    return specific, groups, default


def test_score_building_category_row_count(score_building_category_all_inputs):
    specific, groups, default = score_building_category_all_inputs
    building_categories = pd.DataFrame({'building_category': ['house', 'office']})
    
    result = input_filter.score_building_category(building_categories)
    assert len(result) == len(specific) + len(groups) + len(default)


def test_score_building_category_all_contains_all_rows_from_specific(score_building_category_all_inputs):
    building_categories = pd.DataFrame({'building_category': ['house', 'office']})

    result = input_filter.score_building_category(building_categories)
    assert (result['building_group'] == 'house').any()
    assert (result['building_group'] == 'office').any()


def test_score_building_category_contains_all_rows_from_groups(score_building_category_all_inputs):
    building_categories = pd.DataFrame({'building_category': ['house', 'office']})
    result = input_filter.score_building_category(building_categories)
    assert (result['building_group'] == 'residential').any()
    assert (result['building_group'] == 'non_residential').any()


def test_score_building_category_contains_all_rows_from_default(score_building_category_all_inputs):
    building_categories = pd.DataFrame({'building_category': ['house', 'office']})
    result = input_filter.score_building_category(building_categories)
    assert (result['building_group'] == 'default').any()


def test_score_building_category_all_empty_inputs():
    empty = pd.DataFrame({'building_category': []})
    result = input_filter.score_building_category(empty)
    assert len(result) == 0


@pytest.fixture
def building_codes():
    return pd.DataFrame({'building_code': ['TEK10', 'TEK17', 'TEK87']})


# --- score_building_code_specific ---

def test_score_building_code_specific_code_group_equals_building_code(building_codes):
    result = input_filter.score_building_code_specific(building_codes)
    assert result['code_group'].tolist() == building_codes['building_code'].tolist()


def test_score_building_code_specific_score_is_one(building_codes):
    result = input_filter.score_building_code_specific(building_codes)
    assert (result['score'] == 1.0).all()


def test_score_building_code_specific_num_is_one(building_codes):
    result = input_filter.score_building_code_specific(building_codes)
    assert (result['num'] == 1).all()


def test_score_building_code_specific_preserves_row_count(building_codes):
    result = input_filter.score_building_code_specific(building_codes)
    assert len(result) == len(building_codes)


# --- score_building_code_group_default ---

def test_score_building_code_group_default_assigns_default_code_group(building_codes):
    result = input_filter.score_building_code_group_default(building_codes)
    assert (result['code_group'] == 'default').all()


def test_score_building_code_group_default_assigns_score(building_codes):
    result = input_filter.score_building_code_group_default(building_codes)
    assert (result['score'] == 0.15).all()


def test_score_building_code_group_default_assigns_num_eight(building_codes):
    result = input_filter.score_building_code_group_default(building_codes)
    assert (result['num'] == 8).all()


def test_score_building_code_group_default_preserves_building_code(building_codes):
    result = input_filter.score_building_code_group_default(building_codes)
    assert result['building_code'].tolist() == building_codes['building_code'].tolist()


# --- score_building_code_all ---

def test_score_building_code_row_count(building_codes):
    specific = input_filter.score_building_code_specific(building_codes)
    default = input_filter.score_building_code_group_default(building_codes)
    result = input_filter.score_building_code(building_codes)
    assert len(result) == len(specific) + len(default)


def test_score_building_code_order_is_specific_then_default(building_codes):
    specific = input_filter.score_building_code_specific(building_codes)
    default = input_filter.score_building_code_group_default(building_codes)
    result = input_filter.score_building_code(building_codes)
    scores = result['score'].tolist()
    assert scores[:len(specific)] == specific['score'].tolist()
    assert scores[len(specific):] == default['score'].tolist()


def test_score_building_code_contains_specific_code_groups(building_codes):
    result = input_filter.score_building_code(building_codes)
    assert set(building_codes['building_code']).issubset(set(result['code_group'].dropna()))


def test_score_building_code_contains_default_code_group(building_codes):
    result = input_filter.score_building_code(building_codes)
    assert (result['code_group'] == 'default').any()


@pytest.fixture
def mixed_building_categories():
    """3 residential, 2 non-residential, 1 holiday_home — covers all group branches."""
    return pd.DataFrame({'building_category': [
        'house', 'apartment_block', 'house',  # residential (3)
        'office', 'school',                   # non_residential (2)
        'holiday_home',                        # neither (1)
    ]})


def test_score_building_group_residential_residential_categories_get_residential_group(mixed_building_categories):
    result = input_filter.score_building_group_residential(mixed_building_categories)
    residential_rows = result[result['building_category'].isin(['house', 'apartment_block'])]
    assert (residential_rows['building_group'] == 'residential').all()


def test_score_building_group_residential_non_residential_categories_get_non_residential_group(mixed_building_categories):
    result = input_filter.score_building_group_residential(mixed_building_categories)
    non_residential_rows = result[result['building_category'].isin(['office', 'school'])]
    assert (non_residential_rows['building_group'] == 'non_residential').all()


def test_score_building_group_residential_holiday_home_keeps_own_name_as_group(mixed_building_categories):
    result = input_filter.score_building_group_residential(mixed_building_categories)
    holiday_rows = result[result['building_category'] == 'holiday_home']
    assert (holiday_rows['building_group'] == 'holiday_home').all()


def test_score_building_group_residential_num_is_per_group_count(mixed_building_categories):
    result = input_filter.score_building_group_residential(mixed_building_categories)
    residential_num = result[result['building_group'] == 'residential']['num'].iloc[0]
    non_residential_num = result[result['building_group'] == 'non_residential']['num'].iloc[0]
    assert residential_num == 3
    assert non_residential_num == 2


def test_score_building_group_residential_score_formula(mixed_building_categories):
    # score = 1.0 - (num / total_count), total = 6
    result = input_filter.score_building_group_residential(mixed_building_categories)
    residential_score = result[result['building_group'] == 'residential']['score'].iloc[0]
    non_residential_score = result[result['building_group'] == 'non_residential']['score'].iloc[0]
    assert residential_score == pytest.approx(1.0 - 3 / 6)
    assert non_residential_score == pytest.approx(1.0 - 2 / 6)


def test_score_building_group_residential_only_residential():
    df = pd.DataFrame({'building_category': ['house', 'apartment_block']})
    result = input_filter.score_building_group_residential(df)
    assert (result['building_group'] == 'residential').all()
    assert result['score'].iloc[0] == pytest.approx(0.1)  # 1.0 - 2/2


def test_score_building_group_residential_only_non_residential():
    df = pd.DataFrame({'building_category': ['office', 'school', 'hospital']})
    result = input_filter.score_building_group_residential(df)
    assert (result['building_group'] == 'non_residential').all()
    assert result['score'].iloc[0] == pytest.approx(0.1)  # 1.0 - 3/3


def test_score_building_group_residential_preserves_all_rows(mixed_building_categories):
    result = input_filter.score_building_group_residential(mixed_building_categories)
    assert len(result) == len(mixed_building_categories)


def test_input_filter_mark_high_score_return_correct_columns_and_value(score_energy_need_improvement):
    """Make sure mark_high_score returns the correct columns and values for high_score.

    Include floating point differences to test that the function correctly identifies high scores even with floating
    point precision issues.
    """
    df = score_energy_need_improvement.assign(score=pd.Series([0.015, 0.015, 0.15, 0.99999999999999999, 1.000000000000001], name='score'))
    result = df.pipe(input_filter.mark_high_score)
    assert 'high_score' in result.columns
    assert result.high_score.tolist() == [True, False, False, True, True]
    assert 'max_score' not in result.columns


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
