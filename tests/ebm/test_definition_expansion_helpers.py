import numpy as np
import pandas as pd
import pytest

from ebm.definition_expansion import (
    _replace_alias,
    explode_building_category,
    explode_building_code,
    explode_on_plus,
    explode_purpose,
    explode_years,
    replace_building_category_default,
    replace_building_code_default,
    replace_purpose_default,
)


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


@pytest.mark.parametrize(('building_categories', 'expected_building_categories'),[
    pytest.param('kindergarten+school+university', ['kindergarten', 'school', 'university'], id='explode_on_plus'),
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


@pytest.mark.parametrize(('building_code', 'expected_building_codes'),[
    pytest.param('TEK10', ['TEK10'], id='single_building_code'),
    pytest.param('+TEK10', ['TEK10'], id='leading_plus'),
    pytest.param('TEK10+', ['TEK10'], id='trailing_plus'),
    pytest.param('TEK10+TEK17+TEK10', ['TEK10', 'TEK17'], id='duplicate_building_code'),
    pytest.param('TEK07+TEK10+TEK17', ['TEK07', 'TEK10','TEK17'], id='explode_on_plus'),
    pytest.param('TEK07++TEK10+TEK17', ['TEK07', 'TEK10','TEK17'], id='explode_on_double_plus'),
    pytest.param('default', ['default'], id='default_no_replace'),
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

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


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
    #pytest.param('lighting+default+cooling', ['lighting', 'heating_rv', 'heating_dhw', 'cooling', 'electrical_equipment', 'fans_and_pumps'],
    # id='default_with_additional'),
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


@pytest.mark.parametrize(('building_category', 'expected_building_categories'),
    [
    pytest.param('house',
                     ['house'],
                     id='not_replacing_house'),
    pytest.param('residential',
                     ['house+apartment_block'],
                     id='replace_residential'),
    pytest.param('non_residential',
                     ['kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs'],
                     id='replace_non_residential'),
    pytest.param('non_residential+residential',
                     ['kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs+house+apartment_block'],
                     id='replace_non_residential_and_residential'),
    pytest.param('default',
                     ['house+apartment_block+kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs'],
                     id='replace_default'),
    pytest.param('default+other',
                     ['house+apartment_block+kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs+other'],
                     id='replace_default_and_other'),
    pytest.param('residential+office',
                     ['house+apartment_block+office'],
                     id='replace_residential_and_keep_office'),
    pytest.param('retail+residential+school',
                     ['retail+house+apartment_block+school'],
                     id='replace_residential_and_keep_retail_and_school'),
    pytest.param('UNresidentialUN',
                     ['UNresidentialUN'],
                     id='replace_residential_with_non_matching'),
    ])
def test_replace_building_category_replace_residential(building_category, expected_building_categories):
    df = pd.DataFrame({'building_category': building_category, 'lineno': [2], 'value': [0.5]})
    result = replace_building_category_default(df.copy())

    assert result.building_category.to_list() == expected_building_categories


@pytest.mark.parametrize(('building_code', 'expected_building_codes'),[
    pytest.param('TEK17', ['TEK17'], id='not_replacing_tek17'),
    pytest.param('TEK10', ['TEK10'], id='not_replacing_tek10'),
    pytest.param('PRE_TEK49', ['PRE_TEK49'], id='not_replacing_pretek49'),
    pytest.param('default', ['PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17'], id='replace_default'),
    pytest.param('TEK00+default+TEK27', ['TEK00+PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17+TEK27'], id='replace_default_when_surrounded'),
])
def test_replace_building_category_replace_default(building_code, expected_building_codes):
    df = pd.DataFrame({'building_category': ['house'], 'building_code': [building_code], 'lineno': [2], 'value': [0.5]})
    result = replace_building_code_default(df.copy())

    assert result['building_code'].to_list() == expected_building_codes


@pytest.mark.parametrize(('purpose', 'expected_purpose'),[
    pytest.param('heating_rv', ['heating_rv'], id='not_replacing_heating_rv'),
    pytest.param('heating_dhw', ['heating_dhw'], id='not_replacing_heating_dhw'),
    pytest.param('cooling', ['cooling'], id='not_replacing_cooling'),
    pytest.param('lighting', ['lighting'], id='not_replacing_lighting'),
    pytest.param('electrical_equipment', ['electrical_equipment'], id='not_replacing_electrical_equipment'),
    pytest.param('fans_and_pumps', ['fans_and_pumps'], id='not_replacing_fans_and_pumps'),
    pytest.param('default', ['heating_rv+heating_dhw+cooling+lighting+electrical_equipment+fans_and_pumps'], id='replace_default'),
    pytest.param('not_default', ['not_default'], id='do_not_replace_not_default'),
    pytest.param('FOO+default+BAR', ['FOO+heating_rv+heating_dhw+cooling+lighting+electrical_equipment+fans_and_pumps+BAR'],
                 id='replace_default_when_surrounded'),
])
def test_replace_purpose_replace_default(purpose, expected_purpose):
    df = pd.DataFrame({'building_category': ['house'], 'purpose': [purpose], 'lineno': [2], 'value': [0.5]})
    result = replace_purpose_default(df.copy())

    assert result['purpose'].to_list() == expected_purpose


def test_replace_purpose_default_returns_df_if_column_missing():
    df = pd.DataFrame({"lineno": [2], "value": [0.5]})
    result = replace_purpose_default(df.copy())
    pd.testing.assert_frame_equal(result, df)


@pytest.mark.parametrize(('column_value', 'alias', 'replacement', 'expected'), [
    pytest.param(['residential'], 'residential', 'house+apartment_block', 'house+apartment_block', id='single_match'),
    pytest.param(['house'], 'residential', 'house+apartment_block', 'house', id='no_match'),
    pytest.param(['office', 'residential', 'school'], 'residential', 'house+apartment_block', 'office+house+apartment_block+school', id='match_in_middle'),
    pytest.param(['default', 'other'], 'default', 'a+b', 'a+b+other', id='match_at_start'),
    pytest.param(['other', 'default'], 'default', 'a+b', 'other+a+b', id='match_at_end'),
    pytest.param(['default', 'default'], 'default', 'a+b', 'a+b+a+b', id='multiple_matches'),
    pytest.param(['x', 'y', 'z'], 'default', 'a+b', 'x+y+z', id='no_matches_multiple_tokens'),
    pytest.param([], 'default', 'a+b', '', id='empty_list'),
])
def test_replace_alias(column_value, alias, replacement, expected):
    assert _replace_alias(column_value, alias, replacement) == expected


@pytest.mark.parametrize('non_iterable_value', [
    np.nan,
    None,
    123,
])
def test_replace_alias_handles_non_iterable_input(non_iterable_value):
    result = _replace_alias(non_iterable_value, 'default', 'house+apartment_block')
    if pd.isna(non_iterable_value):
        assert pd.isna(result)
    else:
        assert result == non_iterable_value


