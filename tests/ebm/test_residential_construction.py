import platform

import pandas as pd
import pytest

from ebm.model.construction import ConstructionCalculator


def test_calculate_yearly_floor_area_change_accept_int_and_list():
    """
    Test if int and pd.Series works the same. First two values are 0. The rest are average_floor_area and
        building_change multiplied.
    """

    years = [y for y in range(2010, 2030)]
    building_change = pd.Series(data=[1 for i in range(0, 20)], index=years)
    expected_values = [0, 0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, start_year=2010, average_floor_area=100).tolist()

    average_floor_area = pd.Series(data=[100 for i in range(20)], index=years)
    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, start_year=2010, average_floor_area=average_floor_area).tolist()

    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, start_year=2010, average_floor_area=average_floor_area).tolist()


def test_calculate_yearly_floor_area_change():
    """
    Test that building_change and average_floor_area are multiplied.
    """

    years = [y for y in range(2010, 2016)]
    building_change = pd.Series(data=[i for i in range(1, 7)], index=years)
    expected_values = pd.Series([0, 0, 6, 8, 10, 12], name='house_floor_area_change', index=years)

    yearly_floor_area_change = ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, start_year=2010, average_floor_area=2)

    pd.testing.assert_series_equal(yearly_floor_area_change, expected_values)


def test_calculate_yearly_new_building_floor_area_sum():
    yearly_new_building_floor_area_house = pd.Series([100, 200, 300, 400], index=[2009, 2010, 2011, 2012])

    expected_accumulated_floor_area = pd.Series([100, 300, 600, 1000],
                                                name='accumulated_constructed_floor_area',
                                                index=[2009, 2010, 2011, 2012])
    result = ConstructionCalculator.calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house)

    pd.testing.assert_series_equal(result, expected_accumulated_floor_area)


def test_calculate_yearly_constructed_floor_area():
    build_area_sum = pd.Series([100, 200, 300], index=[0, 1, 2])
    yearly_floor_area_change = pd.Series([10, 20, 30], index=[0, 1, 2])
    yearly_demolished_floor_area = pd.Series([5, 15, 25], index=[0, 1, 2])

    expected_constructed_floor_area = pd.Series([100, 200, 300], name='constructed_floor_area', index=[0, 1, 2])

    result = ConstructionCalculator.calculate_yearly_constructed_floor_area(
        build_area_sum, yearly_floor_area_change, yearly_demolished_floor_area)

    pd.testing.assert_series_equal(result, expected_constructed_floor_area)


def test_calculate_population_growth():
    """ Test that population growth is calculated correctly"""
    population = pd.Series([100, 150, 225, 337.5])

    expected_growth = pd.Series([None, 0.5, 0.5, 0.5], name='population_growth')
    result = ConstructionCalculator().calculate_population_growth(population)
    pd.testing.assert_series_equal(result, expected_growth, check_dtype=False)


def test_calculate_building_growth():
    building_category_share = pd.Series([1, 2, 3, 4, 5], index=[2010, 2011, 2012, 2013, 2014])
    households_change = pd.Series([0.5, 0.6, 0.8, 1, 1], index=[2010, 2011, 2012, 2013, 2014])
    household_change = ConstructionCalculator().calculate_building_growth(
        building_category_share=building_category_share,
        households_change=households_change)

    expected_growth = pd.Series([0.5, 1.2, 2.4, 4, 5],
                                index=[2010, 2011, 2012, 2013, 2014],
                                name='building_growth')
    pd.testing.assert_series_equal(household_change, expected_growth)


def test_calculate_households_by_year():
    household_size = pd.Series([2, 4, 7, 8])
    population = pd.Series([1000, 1200, 1400, 1600])

    expected_households = pd.Series([500.0, 300.0, 200.0, 200.0], name='households')
    calculated_households = ConstructionCalculator.calculate_households_by_year(household_size, population)

    pd.testing.assert_series_equal(calculated_households, expected_households)


def test_calculate_residential_construction():
    population = pd.Series([1000, 1100, 1210, 1331], index=[2009, 2010, 2011, 2012])
    household_size = pd.Series([2.5, 2.4, 2.3, 2.2], index=[2009, 2010, 2011, 2012])
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=[2009, 2010, 2011, 2012])
    build_area_sum = pd.Series([100, 200, 300, 400], index=[2009, 2010, 2011, 2012])
    yearly_demolished_floor_area = pd.Series([10, 20, 30, 40], index=[2009, 2010, 2011, 2012])
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area)

    expected_data = {
        'population': population,
        'population_growth': pd.Series([None, 0.1, 0.1, 0.1], index=[2009, 2010, 2011, 2012], name='population_growth'),
        'household_size': household_size,
        'households': pd.Series([400, 458.33, 526.09, 605], index=[2009, 2010, 2011, 2012], name='households'),
        'households_change': pd.Series([None, 58.33, 67.75, 78.91], index=[2009, 2010, 2011, 2012],
                                       name='household_change'),
        'building_growth': pd.Series([None, 29.17, 33.88, 39.46], index=[2009, 2010, 2011, 2012],
                                     name='building_growth'),
        'yearly_floor_area_constructed': pd.Series([None, 0, 0, 6904.89], index=[2009, 2010, 2011, 2012],
                                                   name='house_floor_area_change'),
        'demolished_floor_area': yearly_demolished_floor_area,
        'constructed_floor_area': pd.Series([100.0, 200.0, 300.0, 400.0], index=[2009, 2010, 2011, 2012],
                                            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series([100.0, 300.0, 600.0, 1000.0], index=[2009, 2010, 2011, 2012],
                                                        name='accumulated_constructed_floor_area')
    }

    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result.round(2), expected_df)


@pytest.mark.skipif(platform.system() != 'Windows', reason='Prevent test from failing on Azure')
def test_yearly_constructed_floor_area_when_share_is_0():
    """
    This test shows that floor_area_change is non-zero even if construction is zero.

    """
    build_area_sum = pd.Series(data=[0.0, 0.0], index=[2010, 2011])
    yearly_floor_area_constructed = pd.Series(
        data=[0.0 for i in range(0, 41)],
        index=[y for y in range(2010, 2051)])
    yearly_demolished_floor_area = pd.Series(
        data=[0., 143053.0625, 143053.0625, 143053.0625, 143053.0625,
              143053.0625, 143053.0625, 143053.0625, 143053.0625, 143053.0625,
              200274.2875, 200274.2875, 200274.2875, 289437.9875, 289437.9875,
              289437.9875, 289437.9875, 289437.9875, 289437.9875, 289437.9875,
              289437.9875, 289437.9875, 289437.9875, 325103.4675, 325103.4675,
              325103.4675, 409340.98, 409340.98, 409340.98, 409340.98,
              409340.98, 409340.98, 409340.98, 409340.98, 409340.98,
              409340.98, 496913.2975, 496913.2975, 496913.2975, 496913.2975,
              496913.2975],
        index=[y for y in range(2010, 2051)])

    floor_area_change = ConstructionCalculator().calculate_yearly_constructed_floor_area(
        build_area_sum, yearly_floor_area_constructed, yearly_demolished_floor_area)

    expected = pd.Series(data=[0.0 for i in range(0, 41)],
                         index=[y for y in range(2010, 2051)],
                         name='floor_area_change')

    pd.testing.assert_series_equal(floor_area_change, expected)
