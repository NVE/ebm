import pandas as pd
import pytest

from ebm.model.bema import sort_lookup


def test_sort_lookup_by_tek():
    """
    BEMA TEK must be chronological ordered
        PRE_TEK49, TEK49, TEK69, TEK87, TEK97, TEK07, TEK17, (TEK21), default, all
    """
    df = pd.DataFrame(
        data=[
            ('all', 11),
            ('default', 10),
            ('TEK97', 5),
            ('TEK69', 3),
            ('TEK10', 7),
            ('PRE_TEK49', 1),
            ('TEK87', 4),
            ('TEK07', 6),
            ('TEK49', 2),
            ('TEK17', 8),
            ('TEK21', 9),
        ], columns=['TEK', 'value'])

    result = df.sort_values(by=['TEK'], key=sort_lookup)
    expected = ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17', 'TEK21', 'default', 'all']
    assert result['TEK'].tolist() == expected

def test_sort_lookup_by_building_category():
    """
    sort_lookup return building_category in expected order:
    ```[
        'house', 'apartment_block', 'retail', 'office', 'kindergarten', 'school', 'university', 'hospital',
        'nursing_home', 'hotel', 'sports', 'culture', 'storage_repairs']
    ```

    """
    df = pd.DataFrame(
        data=[
            ('default', 12),
            ('apartment_block', -1),
            ('culture', 10),
            ('all', 13),
            ('hotel', 8),
            ('house', -2),
            ('kindergarten', 3),
            ('nursing_home', 7),
            ('retail', 1),
            ('office', 2),
            ('university', 5),
            ('storage', 11),
            ('storage_repairs', 11),
            ('sports', 9),
            ('school', 4),
            ('hospital', 6),
        ],
        columns=['building_category', 'value'])

    result = df.sort_values(by=['building_category'], key=sort_lookup)
    expected = [
        'house', 'apartment_block', 'retail', 'office', 'kindergarten', 'school', 'university', 'hospital',
        'nursing_home', 'hotel', 'sports', 'culture', 'storage', 'storage', 'default', 'all']
    assert result['building_category'].tolist() == expected


def test_sort_lookup_by_building_group():
    """
    sort_lookup map building_group order as residential, holiday_home, non_residential, all
    """
    df = pd.DataFrame(
        data=[
            ('non_residential', 11),
            ('holiday_home', 1),
            ('all', 3),
            ('residential', 2),
        ],
        columns=['building_group', 'value'])

    result = df.sort_values(by=['building_group'], key=sort_lookup)
    expected = ['residential', 'holiday_home', 'non_residential', 'all']
    assert result['building_group'].tolist() == expected


def test_sort_lookup_by_building_condition():
    """
    sort_lookup return bema order of building conditions
    `['original_condition', 'small_measure', 'renovation', 'renovation_and_small_measure', 'demolition']`
    """
    df = pd.DataFrame(
        data=[
            ('small_measure', 2),
            ('renovation_and_small_measure', 4),
            ('renovation', 3),
            ('demolition', 5),
            ('original_condition', 1),
        ],
        columns=['building_condition', 'value'])

    result = df.sort_values(by=['building_condition'], key=sort_lookup)
    expected = ['original_condition', 'small_measure', 'renovation', 'renovation_and_small_measure', 'demolition']
    assert result['building_condition'].tolist() == expected


def test_sort_lookup_by_purpose():
    """
sort_lookup return bema order of purpose
`['heating_rv', 'heating_dhw', 'fans_and_pumps', 'lighting', 'electrical_equipment', 'cooling']` + default
    """
    df = pd.DataFrame(
        data=[
            ('heating_dhw', 2),
            ('lighting', 4),
            ('fans_and_pumps', 3),
            ('electrical_equipment', 5),
            ('heating_rv', 1),
            ('cooling', 6),
            ('default', 7),
        ],
        columns=['purpose', 'value'])

    result = df.sort_values(by=['purpose'], key=sort_lookup)
    expected = ['heating_rv', 'heating_dhw', 'fans_and_pumps', 'lighting', 'electrical_equipment', 'cooling', 'default']
    assert result['purpose'].tolist() == expected


def test_sort_lookup_multiple_columns_including_year():
    """
    Make sure sort_lookup return the correct order when ordering by building_category, TEK, purpose and year
    """
    df = pd.DataFrame(
        data=[
            ('storage', 'PRE_TEK49', 'heating_rv', 2021, 8),
            ('storage', 'PRE_TEK49', 'heating_rv', 2020, 7),
            ('kindergarten', 'TEK97', 'cooling', 2020, 6),
            ('kindergarten', 'TEK49', 'cooling', 2020, 5),
            ('apartment_block', 'TEK07', 'cooling', 2020, 4),
            ('apartment_block', 'TEK07', 'heating_rv', 2020, 3),
            ('apartment_block', 'TEK69', 'cooling', 2020, 2),
            ('house', 'TEK17', 'cooling', 2020, 1),
            ('default', 'default', 'default', 1814, 99)
        ],
        columns=['building_category', 'TEK', 'purpose', 'year', 'value'])

    result = df.sort_values(by=['building_category', 'TEK', 'purpose', 'year'], key=sort_lookup)
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 99]
    assert result['value'].tolist() == expected

    indexed = df.set_index(['building_category', 'TEK', 'purpose', 'year']).sort_index(key=sort_lookup)
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 99]
    assert indexed['value'].tolist() == expected


def test_sort_lookup_by_faulty_tek():
    """
    Non-existing TEK should be sorted last
    """
    df = pd.DataFrame(
        data=[
            ('TEK25', 2),
            ('TEK29', 3),
            ('TEK97', 1),
        ], columns=['TEK', 'value'])

    result = df.sort_values(by=['TEK'], key=sort_lookup)

    expected = ['TEK97', 'TEK25', 'TEK29']

    assert result['TEK'].tolist() == expected


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
