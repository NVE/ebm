import pandas as pd
import pytest

from ebm import input_filter


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

