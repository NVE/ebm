import numpy as np
import pandas as pd
import pytest

from ebm.model.area import (
    calculate_building_growth,
    calculate_households_by_year,
    calculate_residential_construction,
    calculate_yearly_constructed_floor_area,
    calculate_yearly_floor_area_change,
    calculate_yearly_new_building_floor_area_sum,
)
from ebm.model.construction import (
    calculate_population_growth,
)
from ebm.model.data_classes import YearRange

from .test_industrial_construction import default_input


def test_calculate_yearly_floor_area_change_accept_int_and_list() -> None:
    """Test if int and pd.Series works the same. First two values are 0. The rest are average_floor_area and building_change multiplied."""
    years = YearRange(2010, 2029)
    building_change = pd.Series({y: 1 for y in years})
    expected_values = [0.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=100).tolist()

    average_floor_area = pd.Series({y: 100 for y in YearRange(2010, 2060)})
    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=average_floor_area).tolist()

    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=average_floor_area).tolist()


def test_calculate_yearly_floor_area_change() -> None:
    """Test that building_change and average_floor_area are multiplied."""
    years = YearRange(2010, 2015)
    building_change = pd.Series(data=[i for i in range(1, 7)], index=years.range())
    expected_values = pd.Series([0, 0, 6, 8, 10, 12],
                                name='house_floor_area_change',
                                index=[2010, 2011, 2012, 2013, 2014, 2015])

    yearly_floor_area_change = calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=2)

    pd.testing.assert_series_equal(yearly_floor_area_change, expected_values)


def test_calculate_yearly_new_building_floor_area_sum() -> None:
    yearly_new_building_floor_area_house = pd.Series([100, 200, 300, 400], index=[2009, 2010, 2011, 2012])

    expected_accumulated_floor_area = pd.Series([100, 300, 600, 1000],
                                                name='accumulated_constructed_floor_area',
                                                index=[2009, 2010, 2011, 2012])
    result = calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house)

    pd.testing.assert_series_equal(result, expected_accumulated_floor_area)


def test_calculate_yearly_constructed_floor_area_build_area_sum_replace_calculated() -> None:
    """Any value in build_area_sum should replace calculated values."""
    build_area_sum = pd.Series([100, 200, 300], index=[0, 1, 2])
    yearly_floor_area_change = pd.Series([10, 20, 30], index=[0, 1, 2])

    expected_constructed_floor_area = pd.Series([100, 200, 300], name='constructed_floor_area', index=[0, 1, 2])

    result = calculate_yearly_constructed_floor_area(build_area_sum, yearly_floor_area_change)

    pd.testing.assert_series_equal(result, expected_constructed_floor_area)


def test_calculate_population_growth() -> None:
    """Test that population growth is calculated correctly."""
    population = pd.Series([100, 150, 225, 337.5])

    expected_growth = pd.Series([None, 0.5, 0.5, 0.5], name='population_growth')
    result = calculate_population_growth(population)
    pd.testing.assert_series_equal(result, expected_growth, check_dtype=False)


def test_calculate_building_growth() -> None:
    building_category_share = pd.Series([1, 2, 3, 4, 5], index=[2010, 2011, 2012, 2013, 2014])
    households_change = pd.Series([0.5, 0.6, 0.8, 1, 1], index=[2010, 2011, 2012, 2013, 2014])
    household_change = calculate_building_growth(
        building_category_share=building_category_share,
        households_change=households_change)

    expected_growth = pd.Series([0.5, 1.2, 2.4, 4, 5],
                                index=[2010, 2011, 2012, 2013, 2014],
                                name='building_growth')
    pd.testing.assert_series_equal(household_change, expected_growth)


def test_calculate_households_by_year() -> None:
    household_size = pd.Series([2, 4, 7, 8])
    population = pd.Series([1000, 1200, 1400, 1600])

    expected_households = pd.Series([500.0, 300.0, 200.0, 200.0], name='households')
    calculated_households = calculate_households_by_year(household_size, population)

    pd.testing.assert_series_equal(calculated_households, expected_households)


def test_calculate_residential_construction() -> None:
    period = YearRange(2010, 2013)
    households_by_year = pd.Series([400.0, 458.33333333333337, 526.0869565217391, 605.0], index=period.range())
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.range())
    build_area_sum = pd.Series([0, 200, 300, 400], index=period.range())
    average_floor_area = 175

    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period)[[
        'net_constructed_floor_area', 'constructed_floor_area', 'accumulated_constructed_floor_area']]

    expected_data = {
        'net_constructed_floor_area': pd.Series(
            data=[0, 200.0, 300, 400], index=[2010, 2011, 2012, 2013], name='house_floor_area_change'),
        'constructed_floor_area': pd.Series(
            data=[0, 200.0, 300.0, 400.0],
            index=[2010, 2011, 2012, 2013],
            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series(
            data=[0, 200.0, 500.0, 900.0],
            index=[2010, 2011, 2012, 2013],
            name='accumulated_constructed_floor_area'),
    }

    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result.round(2), expected_df)


def test_calculate_residential_construction_2011() -> None:
    period = YearRange(2011, 2014)
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.range())
    build_area_sum = pd.Series([0, 200, 300, 400], index=period.range())
    average_floor_area = 175

    households_by_year = pd.Series([400.0, 458.33333333333337, 526.0869565217391, 605.0], index=period.range(), name='households')
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period)

    expected_data = {
        'net_constructed_floor_area': pd.Series(
            data=[0, 200.0, 300.0, 400.0],
            index=period.to_index(),
            name='house_floor_area_change'),
        'constructed_floor_area': pd.Series(
            data=[0, 200.0, 300.0, 400.0],
            index=period.to_index(),
            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series(
            data=[0.0, 200.0, 500.0, 900.0],
            index=period.to_index(),
            name='accumulated_constructed_floor_area'),
    }

    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result[expected_df.columns].round(2), expected_df, check_names=False)


def test_calculate_residential_construction_2052(default_input) -> None:
    """Test that accumulated_constructed_floor_area has a correct index from 2010 to 2052 when YearRange is longer than normal."""
    period = YearRange(2010, 2052)
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000, 30_000, 31_000], index=[2010, 2011, 2012, 2013])
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period)
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.range(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()


def test_calculate_residential_construction_from_2020(default_input) -> None:
    """Test that accumulated_constructed_floor_area has a correct index from 2011 to 2052."""
    period = YearRange(2011, 2051)
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000], index=[2011, 2012])
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period)
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.range(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()

@pytest.mark.parametrize('build_sum_0', [0.0, 10_000.0])
def test_calculate_residential_construction_for_ten_years(default_input, build_sum_0):
    """Test that accumulated_constructed_floor_area has a correct index from 2011 to 2020."""
    period = YearRange(2011, 2020)
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([build_sum_0, 20_000], index=[2011, 2012])
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period)

    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area

    expected_values = [build_sum_0, 20000.0, 4407836.558149085, 6705944.512694532, 8962887.694512703,
                       11826172.096754318, 13597427.80451687, 17037877.79715203, 19492648.74249253,
                       21952876.859417602]
    expected = pd.Series(data=expected_values, index=period.range(), name='accumulated_constructed_floor_area')
    expected.iloc[1:] = expected.iloc[1:] + build_sum_0


    pd.testing.assert_series_equal(accumulated_constructed_floor_area, expected)


def test_calculate_residential_construction_raise_value_error_on_missing_build_area_sum(default_input):
    """Test that accumulated_constructed_floor_area has a correct index from 2011 to 2052."""
    period = YearRange(2011, 2051)
    building_category_share = pd.Series({y: 0.5 for y in period})
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year')
    with pytest.raises(ValueError, match='missing constructed floor area for 2012'):
        calculate_residential_construction(households_by_year, building_category_share,
                                           pd.Series([10_000, np.nan], index=YearRange(2011, 2012).to_index()),
                                           average_floor_area, period=period)

    with pytest.raises(ValueError, match='missing constructed floor area for 2012'):
        calculate_residential_construction(households_by_year, building_category_share,
                                           pd.Series([10_000, 11_000], index=YearRange(2010, 2011).to_index()),
                                           average_floor_area, period=period)


@pytest.mark.skip('Test not working properly')
def test_yearly_constructed_floor_area_when_share_is_0():
    """Test that floor_area_change is non-zero even if construction is zero."""
    build_area_sum = pd.Series(data=[0.0, 0.0], index=[2010, 2011])
    yearly_floor_area_constructed = pd.Series({y: 0.0 for y in range(2010, 2051)})

    floor_area_change = calculate_yearly_constructed_floor_area(build_area_sum, yearly_floor_area_constructed)

    expected = pd.Series(data=[0.0 for i in range(0, 41)],
                         index=[y for y in range(2010, 2051)],
                         name='floor_area_change')

    pd.testing.assert_series_equal(floor_area_change, expected)


if __name__ == '__main__':
    default_input()
    pytest.main()
