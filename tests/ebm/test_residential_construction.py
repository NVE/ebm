import numpy as np
import pandas as pd
import pytest

from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from .test_industrial_construction import default_input


def test_calculate_yearly_floor_area_change_accept_int_and_list():
    """
    Test if int and pd.Series works the same. First two values are 0. The rest are average_floor_area and
        building_change multiplied.
    """

    years = YearRange(2010, 2029)
    building_change = pd.Series({y: 1 for y in years})
    expected_values = [0, 0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, period=years, average_floor_area=100).tolist()

    average_floor_area = pd.Series({y: 100 for y in YearRange(2009, 2060)})
    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, period=years, average_floor_area=average_floor_area).tolist()

    assert expected_values == ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, period=years, average_floor_area=average_floor_area).tolist()


def test_calculate_yearly_floor_area_change():
    """
    Test that building_change and average_floor_area are multiplied.
    """

    years = YearRange(2010, 2015)
    building_change = pd.Series(data=[i for i in range(1, 7)], index=years.range())
    expected_values = pd.Series([0, 0, 6, 8, 10, 12],
                                name='house_floor_area_change',
                                index=[2010, 2011, 2012, 2013, 2014, 2015])

    yearly_floor_area_change = ConstructionCalculator().calculate_yearly_floor_area_change(
        building_change=building_change, period=years, average_floor_area=2)

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
    period = YearRange(2010, 2013)
    population = pd.Series([1000, 1100, 1210, 1331], index=period.range())
    household_size = pd.Series([2.5, 2.4, 2.3, 2.2], index=period.range())
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.range())
    build_area_sum = pd.Series([100, 200, 300, 400], index=period.range())
    yearly_demolished_floor_area = pd.Series([10, 20, 30, 40], index=period.range())
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area,
                                                                         period=period)

    expected_data = {
        'population': population,
        'population_growth': pd.Series([None, 0.1, 0.1, 0.1], index=[2010, 2011, 2012, 2013], name='population_growth'),
        'household_size': household_size,
        'households': pd.Series([400, 458.33, 526.09, 605], index=[2010, 2011, 2012, 2013], name='households'),
        'households_change': pd.Series([None, 58.33, 67.75, 78.91], index=[2010, 2011, 2012, 2013],
                                       name='household_change'),
        'building_growth': pd.Series([None, 29.17, 33.88, 39.46], index=[2010, 2011, 2012, 2013],
                                     name='building_growth'),
        'yearly_floor_area_constructed': pd.Series([0, 0, 5928.44, 6904.89], index=[2010, 2011, 2012, 2013],
                                                   name='house_floor_area_change'),
        'demolished_floor_area': yearly_demolished_floor_area,
        'constructed_floor_area': pd.Series([100.0, 200.0, 300.0, 400.0], index=[2010, 2011, 2012, 2013],
                                            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series([100.0, 300.0, 600.0, 1000.0], index=[2010, 2011, 2012, 2013],
                                                        name='accumulated_constructed_floor_area')
    }

    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result.round(2), expected_df)


def test_calculate_residential_construction_2011():
    period = YearRange(2011, 2014)
    population = pd.Series([1000, 1100, 1210, 1331], index=period.range())
    household_size = pd.Series([2.5, 2.4, 2.3, 2.2], index=period.range())
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.range())
    build_area_sum = pd.Series([100, 200, 300, 400], index=period.range())
    yearly_demolished_floor_area = pd.Series([10, 20, 30, 40], index=period.range())
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area,
                                                                         period=period)

    expected_data = {
        'population': population,
        'population_growth': pd.Series([None, 0.1, 0.1, 0.1], index=period.to_index(),
                                       name='population_growth'),
        'household_size': household_size,
        'households': pd.Series([400, 458.33, 526.09, 605], index=period.to_index(), name='households'),
        'households_change': pd.Series([None, 58.33, 67.75, 78.91], index=period.to_index(),
                                       name='household_change'),
        'building_growth': pd.Series([None, 29.17, 33.88, 39.46], index=period.to_index(),
                                     name='building_growth'),
        'yearly_floor_area_constructed': pd.Series([0, 0, 5928.44, 6904.89], index=period.to_index(),
                                                   name='house_floor_area_change'),
        'demolished_floor_area': yearly_demolished_floor_area,
        'constructed_floor_area': pd.Series([100.0, 200.0, 300.0, 400.0], index=period.to_index(),
                                            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series([100.0, 300.0, 600.0, 1000.0],
                                                        index=period.to_index(),
                                                        name='accumulated_constructed_floor_area')
    }

    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result.round(2), expected_df)


def test_calculate_residential_construction_2052(default_input):
    """
    Test that accumulated_constructed_floor_area has a correct index from 2010 to 2052 when YearRange is longer than
        normal
    """
    period = YearRange(2010, 2052)
    population = pd.Series(default_input.get('population'), name='period').loc[period]
    household_size = pd.Series(default_input.get('household_size'), name='household_size').loc[period]
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000, 30_000, 31_000], index=[2010, 2011, 2012, 2013])
    yearly_demolished_floor_area = pd.Series([500 + y for y in period], index=period.range())
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area,
                                                                         period=period)
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.range(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()


def test_calculate_residential_construction_from_2020(default_input):
    """
    Test that accumulated_constructed_floor_area has a correct index from 2011 to 2052
    """
    period = YearRange(2011, 2051)
    population = pd.Series(default_input.get('population'), name='period').loc[period]
    household_size = pd.Series(default_input.get('household_size'), name='household_size').loc[period]
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000], index=[2011, 2012])
    yearly_demolished_floor_area = pd.Series([500 + y for y in period], index=period.range())
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area,
                                                                         period=period)
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.range(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()


def test_calculate_residential_construction_for_ten_years(default_input):
    """
    Test that accumulated_constructed_floor_area has a correct index from 2011 to 2020
    """
    period = YearRange(2011, 2020)
    population = pd.Series(default_input.get('population'), name='period')
    household_size = pd.Series(default_input.get('household_size'), name='household_size')
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000], index=[2011, 2012])
    yearly_demolished_floor_area = pd.Series([500 + y for y in period], index=period.range())
    average_floor_area = 175

    result = ConstructionCalculator().calculate_residential_construction(population, household_size,
                                                                         building_category_share, build_area_sum,
                                                                         yearly_demolished_floor_area,
                                                                         average_floor_area,
                                                                         period=period)

    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(
        data=[10000.0, 30000.0, 4420349.59, 6720971.5, 8980429.70, 11846230.1,
              13620002.80, 17062970.79715203, 19520260.74, 21983008.85], index=period.range(),
        name='accumulated_constructed_floor_area')

    pd.testing.assert_series_equal(accumulated_constructed_floor_area, expected)


def test_calculate_residential_construction_raise_value_error_on_missing_build_area_sum(default_input):
    """
    Test that accumulated_constructed_floor_area has a correct index from 2011 to 2052
    """
    period = YearRange(2011, 2051)
    population = pd.Series(default_input.get('population'), name='period').loc[period]
    household_size = pd.Series(default_input.get('household_size'), name='household_size').loc[period]
    building_category_share = pd.Series({y: 0.5 for y in period})
    yearly_demolished_floor_area = pd.Series([500 + y for y in period], index=period.range())
    average_floor_area = 175

    with pytest.raises(ValueError, match='missing constructed floor area for 2012'):
        ConstructionCalculator().calculate_residential_construction(
            population, household_size, building_category_share,
            pd.Series([10_000, np.nan], index=YearRange(2011, 2012).to_index()),
            yearly_demolished_floor_area,
            average_floor_area,
            period=period)

    with pytest.raises(ValueError, match='missing constructed floor area for 2012'):
        ConstructionCalculator().calculate_residential_construction(
            population, household_size, building_category_share,
            pd.Series([10_000, 11_000], index=YearRange(2010, 2011).to_index()),
            yearly_demolished_floor_area,
            average_floor_area,
            period=period)



#@pytest.mark.skipif(platform.system() != 'Windows', reason='Prevent test from failing on Azure')
@pytest.mark.skip('Test not working properly')
def test_yearly_constructed_floor_area_when_share_is_0():
    """
    This test shows that floor_area_change is non-zero even if construction is zero.

    """
    build_area_sum = pd.Series(data=[0.0, 0.0], index=[2010, 2011])
    yearly_floor_area_constructed = pd.Series({y: 0.0 for y in range(2010, 2051)})
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


if __name__ == '__main__':
    default_input()
    pytest.main()