import numpy as np
import pandas as pd
import pytest

from ebm.validators4061 import (
    build_grouping,
    energy_need_improvements_yearly_schema,
    expanded_energy_need_improvements_schema,
    explode_building_category,
    explode_building_code,
    explode_purpose,
    explode_years,
    group_dupes_on_dupes,
    replace_building_category_default,
    replace_building_code_default,
    replace_purpose_default,
    select_groups_with_lowest_lineno_count,
    group_duplicated_lineno_summary,
    explode_on_plus,
)


def test_expanded_energy_need_improvements_schema():
    df = pd.DataFrame({
        'lineno': [2, 3, 4],
        'building_category': ['house', 'apartment_block', 'kindergarten'],
        'building_code': ['TEK17', 'TEK17', 'TEK17'],
        'purpose': ['lighting', 'lighting', 'lighting'],
        'value': [0.5, 0.7, 0.9],
    })
    schema = expanded_energy_need_improvements_schema().validate(df)
    assert schema.equals(df)


def test_expanded_energy_need_improvements_schema_expand_building_code():
    df = pd.DataFrame({
        'lineno': [2,3],
        'building_category': ['house', 'school'],
        'building_code': ['default', 'TEK49'],
        'purpose': ['lighting', 'lighting'],
        'value': [0.5, 0.5],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2]*8+[3],
        'building_category': ['house']*8+['school'],
        'building_code': ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17', 'TEK49'],
        'purpose': ['lighting']*9,
        'value': [0.5]*9,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_expanded_energy_need_improvements_schema_expand_explode_plus_in_building_code():
    df = pd.DataFrame({
        'lineno': [2, 3],
        'building_category': ['office', 'office'],
        'building_code': ['TEK07+TEK10+TEK17', 'TEK87'],
        'purpose': ['lighting', 'lighting'],
        'value': [0.5, 0.5],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2, 2, 2, 3],
        'building_category': ['office']*4,
        'building_code': ['TEK07', 'TEK10', 'TEK17', 'TEK87'],
        'purpose': ['lighting']*4,
        'value': [0.5]*4,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_expanded_energy_need_improvements_schema_expand_building_category():
    df = pd.DataFrame({
        'lineno': [2],
        'building_category': ['default'],
        'building_code': ['TEK17'],
        'purpose': ['lighting'],
        'value': [0.5],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2]*13,
        'building_category': [
            'house',
            'apartment_block',
            'kindergarten',
            'school',
            'university',
            'office',
            'retail',
            'hotel',
            'hospital',
            'nursing_home',
            'culture',
            'sports',
            'storage_repairs'],
        'building_code': ['TEK17'] * 13,
        'purpose': ['lighting']*13,
        'value': [0.5]*13,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_expanded_energy_need_improvements_schema_expand_explode_plus_in_building_category():
    df = pd.DataFrame({
        'lineno': [2],
        'building_category': ['kindergarten+school+university'],
        'building_code': ['TEK87'],
        'purpose': ['lighting'],
        'value': [0.5],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2]*3,
        'building_category': [
            'kindergarten',
            'school',
            'university'],
        'building_code': ['TEK87'] * 3,
        'purpose': ['lighting']*3,
        'value': [0.5]*3,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_expanded_energy_need_improvements_schema_expand_purpose():
    df = pd.DataFrame({
        'lineno': [2],
        'building_category': ['kindergarten'],
        'building_code': ['TEK07'],
        'purpose': ['default'],
        'value': [0.4],
        'start_year': [2020],
        'end_year': [2020],
        'function': ['yearly_reduction'],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2]*6,
        'building_category': ['kindergarten']*6,
        'building_code': ['TEK07'] * 6,
        'purpose': ['heating_rv', 'heating_dhw', 'cooling', 'lighting', 'electrical_equipment', 'fans_and_pumps'],
        'value': [0.4]*6,
        'start_year': [2020]*6,
        'end_year': [2020]*6,
        'function': ['yearly_reduction']*6,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_expanded_energy_need_improvements_schema_expand_explode_plus_in_purpose():
    df = pd.DataFrame({
        'lineno': [2],
        'building_category': ['kindergarten'],
        'building_code': ['TEK07'],
        'purpose': ['lighting+cooling+heating_rv+heating_dhw+electrical_equipment+fans_and_pumps'],
        'value': [0.1],
        'start_year': [2020],
        'end_year': [2030],
        'function': ['yearly_reduction'],
    })

    schema = expanded_energy_need_improvements_schema().validate(df)
    expected = pd.DataFrame({
        'lineno': [2]*6,
        'building_category': ['kindergarten']*6,
        'building_code': ['TEK07'] * 6,
        'purpose': [
            'lighting',
            'cooling',
            'heating_rv',
            'heating_dhw',
            'electrical_equipment',
            'fans_and_pumps',
        ],
        'value': [0.1]*6,
        'start_year': [2020]*6,
        'end_year': [2030]*6,
        'function': ['yearly_reduction']*6,
    })

    pd.testing.assert_frame_equal(schema, expected, check_like=True)


def test_explode_on_plus_splits_and_deduplicates_values():
    df = pd.DataFrame({
        "column_b": ["kindergarten+school+university", "office++office+"],
    })

    result = explode_on_plus(df.copy(), column_name="column_b")

    assert result["column_b"].tolist() == ["kindergarten", "school", "university", "office"]


@pytest.mark.parametrize(('value', 'message'), [
    (np.nan, r"Dataframe 'column_b' cannot be empty"),
    (None, r"Dataframe 'column_b' cannot be empty"),
])
def test_explode_on_plus_handles_missing_values_in_existing_column(value, message):
    df = pd.DataFrame({
        "column_a": ["TEK49", "TEK17", ""],
        "column_b": ["house", value, "retail"],
        "column_c": ["lighting", "heating_rv", ""],
    })

    with pytest.raises(ValueError, match=message):
        explode_on_plus(df.copy(), column_name="column_b")




@pytest.mark.parametrize(('building_categories', 'expected_building_categories'),[    pytest.param('kindergarten+school+university', ['kindergarten', 'school', 'university'], id='explode_on_plus'),
    pytest.param('kindergarten', ['kindergarten'], id='single'),
    pytest.param('hospital+hospital', ['hospital'], id='duplicate'),
    pytest.param('hospital++hospital', ['hospital'], id='explode_on_double_plus'),
    pytest.param('office+', ['office'], id='trailing_plus'),
    pytest.param('+office', ['office'], id='leading_plus'),
])
def test_explode_building_category(building_categories, expected_building_categories):
    df = pd.DataFrame({
        "lineno": [2],
        "building_category": [building_categories],
        "value": [0.5],
    })
    result = explode_building_category(df)
    expected = pd.DataFrame({
        "lineno": [2] * len(expected_building_categories),
        "building_category": expected_building_categories,
        "value": [0.5] * len(expected_building_categories),
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_explode_building_category_raise_value_error_on_missing_building_category_column():
    df = pd.DataFrame({
        "lineno": [2],
        "value": [0.5],
    })
    with pytest.raises(ValueError, match=r"Dataframe must contain a 'building_category' column"):
        explode_building_category(df)


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

@pytest.mark.parametrize(('building_code', 'expected_building_codes'),[
    pytest.param('TEK10', ['TEK10'], id='single_building_code'),
    pytest.param('+TEK10', ['TEK10'], id='leading_plus'),
    pytest.param('TEK10+', ['TEK10'], id='trailing_plus'),
    pytest.param('TEK10+TEK17+TEK10', ['TEK10', 'TEK17'], id='duplicate_building_code'),
    pytest.param('TEK07+TEK10+TEK17', ['TEK07', 'TEK10','TEK17'], id='explode_on_plus'),
    pytest.param('TEK07++TEK10+TEK17', ['TEK07', 'TEK10','TEK17'], id='explode_on_double_plus'),
    pytest.param('default', ['default'], id='default_no_replace'),
    #pytest.param('TEK17+default', ['TEK17', 'PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10'], id='single+default'),
    #pytest.param('default', ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17'], id='default'),
])
def test_explode_building_code(building_code, expected_building_codes):
    df = pd.DataFrame({
        "lineno": [2],
        "building_code": [building_code],
        "value": [0.5],
    })
    expected = pd.DataFrame({
        "lineno": [2] * len(expected_building_codes),
        "building_code": expected_building_codes,
        "value": [0.5] * len(expected_building_codes),
    })
    result = explode_building_code(df)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))# f'Expected {expected_building_codes} rows, got {result.building_code.to_list()}'


def test_explode_building_code_when_missing_building_code_column():
    df = pd.DataFrame({
        "lineno": [2],
        "value": [0.5],
    })
    result = explode_building_code(df)
    pd.testing.assert_frame_equal(result, df)


@pytest.mark.parametrize(('purpose', 'expected_purpose'),[
    pytest.param('lighting+cooling+heating_rv', ['lighting', 'cooling','heating_rv'], id='explode_on_plus'),
    pytest.param('lighting++heating_rv', ['lighting','heating_rv'], id='explode_on_double_plus'),
    pytest.param('cooling+cooling', ['cooling'], id='duplicate_purpose'),
    pytest.param('heating_dhw', ['heating_dhw'], id='single_purpose'),
    pytest.param('heating_dhw+', ['heating_dhw'], id='trailing_plus'),
    pytest.param('+heating_dhw+', ['heating_dhw'], id='leading_and_trailing_plus'),
    pytest.param('+++cooling', ['cooling'], id='leading_plus'),
    pytest.param('cooling++', ['cooling'], id='trailing_plus'),
    pytest.param('default', ['default'], id='default_no_replace'),
    #pytest.param('lighting+default+cooling', ['lighting', 'heating_rv', 'heating_dhw', 'cooling', 'electrical_equipment', 'fans_and_pumps'], id='default_with_additional'),
    #pytest.param('default', ['heating_rv', 'heating_dhw', 'cooling', 'lighting', 'electrical_equipment', 'fans_and_pumps'], id='default'),
                        ])
def test_explode_purpose(purpose, expected_purpose):
    df = pd.DataFrame({
        "lineno": [2],
        "purpose": [purpose],
        "value": [0.5],
    })

    result = explode_purpose(df)

    actual_purpose = result.purpose.to_list()
    assert len(result) == len(expected_purpose), f'Expected {expected_purpose} rows, got {actual_purpose}'
    assert actual_purpose == expected_purpose


def test_explode_purpose_ignore_missing_purpose():
    df = pd.DataFrame({
        "lineno": [2],
        "value": [0.5],
    })

    result = explode_purpose(df)

    assert len(result) == 1
    assert 'purpose' not in result.columns


def test_explode_years_raise_value_error_when_missing_start_year():
    with pytest.raises(ValueError, match=r"Dataframe must contain a 'start_year' column"):
        explode_years(pd.DataFrame({
        "lineno": [2],
        "end_year": [2010],
        "value": [0.5],
    }))

    with pytest.raises(ValueError, match=r"Dataframe must contain a 'end_year' column"):
        explode_years(pd.DataFrame({
        "lineno": [2],
        "start_year": [2010],
        "value": [0.5],
    }))


def test_explode_years_raise_value_error_when_start_year_gt_end_year():
    df = pd.DataFrame({
        "lineno": [2],
        "start_year": [2012],
        "end_year": [2010],
        "value": [0.5],
    })

    with pytest.raises(ValueError, match=r'start_year must be less than or equal to end_year'):
        explode_years(df)


def test_explode_years():
    df = pd.DataFrame({
        "lineno": [2],
        "start_year": [2020],
        "end_year": [2022],
        "value": [0.5],
    })
    result = explode_years(df)
    expected = pd.DataFrame({
        "lineno": [2, 2, 2],
        "start_year": [2020, 2020, 2020],
        "end_year": [2022, 2022, 2022],
        "value": [0.5, 0.5, 0.5],
        "year": [2020, 2021, 2022],
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_replace_building_code_default_returns_df_if_column_missing():
    df = pd.DataFrame({"lineno": [2], "value": [0.5]})
    result = replace_building_code_default(df.copy())
    pd.testing.assert_frame_equal(result, df)


def test_replace_building_category_default_returns_df_if_column_missing():
    df = pd.DataFrame({"lineno": [2], "value": [0.5]})
    result = replace_building_category_default(df.copy())
    pd.testing.assert_frame_equal(result, df)


def test_replace_purpose_default_returns_df_if_column_missing():
    df = pd.DataFrame({"lineno": [2], "value": [0.5]})
    result = replace_purpose_default(df.copy())
    pd.testing.assert_frame_equal(result, df)


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

    expanded = expanded_energy_need_improvements_schema().validate(df)
    result = expanded.pipe(select_groups_with_lowest_lineno_count, filter_columns=False)

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
    result = df.pipe(select_groups_with_lowest_lineno_count) # , filter_columns=True)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


@pytest.mark.parametrize(('category', 'code', 'function', 'start_year', 'duplicate_years'), [
    pytest.param('retail', 'TEK49', 'yearly_reduction', 2025, frozenset(), id='different building_category and start_year'),
    pytest.param('retail', 'TEK49', 'yearly_reduction', 2021, frozenset(), id='different building_category, same start_year'),
    pytest.param('office', 'TEK49', 'improvement_at_end_year', 2021, frozenset(), id='different function'),
    pytest.param('office', 'TEK69', 'yearly_reduction', 2021, frozenset(), id='different building_code'),
    pytest.param('office', 'TEK49', 'yearly_reduction', 2024, frozenset(), id='no overlapping years'),
    pytest.param('office', 'TEK49', 'yearly_reduction', 2023, frozenset({2023}), id='overlapping end_year'),
    pytest.param('office', 'TEK49', 'yearly_reduction', 2019, frozenset({2021}), id='overlapping start_year'),
    pytest.param('office', 'TEK49', 'yearly_reduction', 2021, frozenset({2021, 2022, 2023}), id='full overlap'),
])
def test_energy_need_improvements_yearly_schema_mark_all_duplicates(category: str, code: str, function: str, start_year: int, duplicate_years: frozenset[int]):
    purpose = 'lighting'

    preferred_energy_need_improvements = pd.DataFrame(
        [
            {
                'building_category': 'office',
                'building_code': 'TEK49',
                'purpose': 'lighting',
                'function': 'yearly_reduction',
                'start_year': 2021,
                'value': 0.02,
                'end_year': 2023,
                'lineno': 3,
            },
            {
                'building_category': category,
                'building_code': code,
                'purpose': purpose,
                'function': function,
                'start_year': start_year,
                'value': 0.03,
                'end_year': start_year + 2,
                'lineno': 4,
            },
        ]
    )
    result = energy_need_improvements_yearly_schema.validate(preferred_energy_need_improvements)

    assert frozenset(result.loc[result.dupe, 'year']) == duplicate_years
    assert result.dupe.sum() == 2 * len(duplicate_years), 'Expected duplicate years to be marked in both overlapping rows'


def test_energy_need_improvements_yearly_schema_expand_year():
    preferred_energy_need_improvements = pd.DataFrame({
            'building_category': ['office', 'house'],
            'building_code': ['TEK49', 'TEK49'],
            'purpose': ['lighting', 'lighting'],
            'function': ['yearly_reduction', 'improvement_at_end_year'],
            'start_year': [2021, 2019],
            'value': [0.02, 0.03],
            'end_year': [2023, 2024],
            'lineno': [2, 3],
        })

    result = energy_need_improvements_yearly_schema.validate(preferred_energy_need_improvements)

    expected_lineno = pd.Series([2, 2, 2, 3, 3, 3, 3, 3, 3], name='lineno')
    pd.testing.assert_series_equal(result.lineno, expected_lineno, check_index=False)

    expected_years = pd.Series([2021, 2022, 2023, 2019, 2020, 2021, 2022, 2023, 2024], name='year')
    pd.testing.assert_series_equal(result.year, expected_years, check_index=False)


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
        ]
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
        ]
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_group_duplicated_lineno_summary_accepts_lineno_y_and_lineno_x():
    df = pd.DataFrame([
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2021, 'year_y': 2021, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2022, 'year_y': 2022, 'lineno_x': 3, 'lineno_y': 4},
        {'building_category': 'retail', 'building_code': 'TEK17', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'year_x': 2023, 'year_y': 2023, 'lineno_x': 3, 'lineno_y': 4}]
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
        {'building_category': 'retail', 'building_code': 'TEK07', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'lineno': 3, 'duplicate_lineno': 4},
        {'building_category': 'retail', 'building_code': 'TEK10', 'purpose': 'electrical_equipment', 'function': 'yearly_reduction', 'lineno': 3, 'duplicate_lineno': 4},
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
        {'building_category': 'apartment_block', 'building_code': 'TEK69', 'purpose': 'lighting', 'function': 'improvement_and_end_year', 'lineno': 2, 'duplicate_lineno': 5},

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



if __name__ == "__main__":
    import sys
    pytest.main([sys.argv[0]])
