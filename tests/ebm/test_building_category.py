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


def test_expand_building_categories_prefer_specific_over_general():
    residential = pd.DataFrame([['apartment_block', 1], ['residential', 2], ['house', 3]],
                               columns=['building_category', 'foo'])
    result = expand_building_categories(residential)

    expected = pd.DataFrame([['apartment_block', 1], ['house', 3]],
                            columns=['building_category', 'foo'], index=[0, 2])

    pd.testing.assert_frame_equal(result, expected, check_like=True)


def test_expand_building_categories_filter_duplicates():
    residential = pd.DataFrame([['residential', 1], ['residential', 2]],
                               columns=['building_category', 'foo'])
    result = expand_building_categories(residential)

    expected = pd.DataFrame([['house', 2], ['apartment_block', 2]],
                            columns=['building_category', 'foo'], index=[0, 1])

    pd.testing.assert_frame_equal(result, expected, check_like=True)
