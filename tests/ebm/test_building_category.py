import pandas as pd

from ebm.model.building_category import expand_building_category, BuildingCategory, expand_building_categories


def test_expand_building_category_expands_residential():
    residential = pd.DataFrame([['residential', 1, 'a']], columns=['building_category', 'foo', 'bar'])
    result = expand_building_category(residential.iloc[0])

    expected = pd.DataFrame([['house', 1, 'a'], ['apartment_block', 1, 'a']],
                            columns=['building_category', 'foo', 'bar'])

    pd.testing.assert_frame_equal(result, expected)


def test_expand_building_category_expands_non_residential():
    residential = pd.DataFrame([['non_residential', 2]], columns=['building_category', 'foo'])
    result = expand_building_category(residential.iloc[0])

    expected = pd.DataFrame([[bc, 2] for bc in BuildingCategory if bc.is_non_residential()],
                            columns=['building_category', 'foo'])

    pd.testing.assert_frame_equal(result, expected)


def test_expand_building_category_does_not_expand_house():
    residential = pd.DataFrame([['house', 1, 'a']], columns=['building_category', 'foo', 'bar'])
    result = expand_building_category(residential.iloc[0])

    expected = pd.DataFrame([['house', 1, 'a']],
                            columns=['building_category', 'foo', 'bar'])

    pd.testing.assert_frame_equal(result, expected)


def test_expand_building_categories_prefer_specific_over_general():
    residential = pd.DataFrame([['apartment_block', 1], ['residential', 2], ['house', 3]],
                               columns=['building_category', 'foo'])
    result = expand_building_categories(residential)

    expected = pd.DataFrame([['apartment_block', 1], ['house', 3]],
                            columns=['building_category', 'foo'], index=[0, 2])

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_expand_building_categories_filter_duplicates_with_extra_column():
    residential = pd.DataFrame([['residential', 'dupe', 1], ['residential', 'dupe', 2], ['residential', 'uniq', 3]],
                               columns=['building_category', 'other_index', 'foo'])
    result = expand_building_categories(residential, unique_columns=['building_category', 'other_index'])
    actual = result.reset_index(drop=True)

    expected = pd.DataFrame([['house', 'dupe', 2], ['apartment_block', 'dupe', 2],
                             ['house', 'uniq', 3], ['apartment_block', 'uniq', 3]],
                            columns=['building_category', 'other_index', 'foo'])

    pd.testing.assert_frame_equal(actual, expected)


def test_expand_building_categories_ignore_duplicates_by_default():
    residential = pd.DataFrame([['residential', 'dupe', 1], ['residential', 'dupe', 2], ['residential', 'uniq', 3]],
                               columns=['building_category', 'other_index', 'foo'])
    result = expand_building_categories(residential)
    actual = result.reset_index(drop=True)

    expected = pd.DataFrame([
        ['house', 'dupe', 1], ['apartment_block', 'dupe', 1],
        ['house', 'dupe', 2], ['apartment_block', 'dupe', 2],
        ['house', 'uniq', 3], ['apartment_block', 'uniq', 3]],
                            columns=['building_category', 'other_index', 'foo'])

    pd.testing.assert_frame_equal(actual, expected)
