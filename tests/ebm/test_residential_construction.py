import numpy as np
import pandas as pd
import pytest

from ebm.model.area import (
    calculate_building_growth,
    calculate_household_change,
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
    building_change = pd.Series({y: 1 for y in years}, index=years.to_index())
    expected_values = [0.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=100).tolist()

    average_floor_area = pd.Series({y: 100 for y in YearRange(2010, 2060)})
    average_floor_area.index.name='year'
    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=average_floor_area).tolist()

    assert expected_values == calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=average_floor_area).tolist()


def test_calculate_yearly_floor_area_change() -> None:
    """Test that building_change and average_floor_area are multiplied."""
    years = YearRange(2010, 2015)
    building_change = pd.Series(data=[i for i in range(1, 7)], index=years.to_index())
    expected_values = pd.Series([0, 0, 6, 8, 10, 12],
                                name='yearly_floor_area_change',
                                index=years.to_index())

    yearly_floor_area_change = calculate_yearly_floor_area_change(building_change=building_change, average_floor_area=2)

    pd.testing.assert_series_equal(yearly_floor_area_change, expected_values)


def test_calculate_yearly_floor_area_change_with_building_category() -> None:
    """Test that building_change and average_floor_area are multiplied."""
    years = YearRange(2011, 2016)
    building_change = pd.DataFrame(data={
        'year': years.range(),
        'building_category': ['category1'] * 6,
        'building_change': [i for i in range(1, 7)],

    })

    average_floor_area = pd.DataFrame(
        data={
            'year': years.range() + years.range(),
            'building_category': ['category1'] * 6 + ['category2'] * 6,
            'average_floor_area': [2]*6 + [1]*6,
        })

    index_columns = ['building_category', 'year']

    expected_values = pd.DataFrame(
        data={
            'year': years.range(),
            'building_category': ['category1'] * 6,
            'yearly_floor_area_change': [0, 0, 6, 8, 10, 12],
        }).set_index(index_columns).yearly_floor_area_change

    actual = calculate_yearly_floor_area_change(
        building_change=building_change.set_index(index_columns),
        average_floor_area=average_floor_area.set_index(index_columns)
    )
    pd.testing.assert_series_equal(actual, expected_values)


def test_calculate_yearly_new_building_floor_area_sum() -> None:
    yearly_new_building_floor_area_house = pd.Series([100, 200, 300, 400], index=[2009, 2010, 2011, 2012])

    expected_accumulated_floor_area = pd.Series([100, 300, 600, 1000],
                                                name='accumulated_constructed_floor_area',
                                                index=[2009, 2010, 2011, 2012])
    result = calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house)

    pd.testing.assert_series_equal(result, expected_accumulated_floor_area)


def test_calculate_yearly_constructed_floor_area_build_area_sum_replace_calculated() -> None:
    """Any value in build_area_sum should replace calculated values."""
    build_area_sum = pd.Series([100, 200, 300], index=YearRange(2010, 2012).to_index())
    yearly_floor_area_change = pd.Series([10, 20, 30], index=YearRange(2010, 2012).to_index())

    expected_constructed_floor_area = pd.Series([100.0, 200.0, 300.0], name='constructed_floor_area', index=YearRange(2010, 2012).to_index())

    result = calculate_yearly_constructed_floor_area(build_area_sum, yearly_floor_area_change)

    pd.testing.assert_series_equal(result, expected_constructed_floor_area)

@pytest.mark.skip('Test not working properly')
def test_calculate_yearly_constructed_floor_area_build_area_sum_with_building_category() -> None:
    """Any value in build_area_sum should replace calculated values."""
    build_area_sum = pd.DataFrame({
        'building_category': ['category1', 'category1', 'category1'],
        'year': [100, 200, 300],
        'build_area_sum': [100, 200, 300],
    })
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



def test_calculate_building_growth_with_dataframe() -> None:
    building_category_share = pd.DataFrame({'share': [1, 2, 3, 4, 5]}, index=[2010, 2011, 2012, 2013, 2014])
    households_change = pd.Series([0.5, 0.6, 0.8, 1, 1], index=[2010, 2011, 2012, 2013, 2014])
    household_change = calculate_building_growth(
        building_category_share=building_category_share,
        households_change=households_change)

    expected_growth = pd.Series([0.5, 1.2, 2.4, 4, 5],
                                index=[2010, 2011, 2012, 2013, 2014],
                                name='building_growth')
    pd.testing.assert_series_equal(household_change, expected_growth)



def test_calculate_household_change() -> None:
    """Test that the yearly difference is returned and the first year is NaN."""
    period = YearRange(2010, 2014)
    households = pd.Series([400.0, 450.0, 525.0, 525.0, 500.0], index=period.to_index())

    result = calculate_household_change(households)

    expected = pd.Series([np.nan, 50.0, 75.0, 0.0, -25.0],
                         index=period.to_index(),
                         name='household_change')
    pd.testing.assert_series_equal(result, expected)



def test_calculate_household_change_with_building_category() -> None:
    """Test that the yearly difference is returned and the first year is NaN."""
    period = YearRange(2010, 2014)
    households = pd.DataFrame(
        {
            'building_category': ['category1'] * 5,
            'year': period.range(),
            'households': [400.0, 450.0, 525.0, 525.0, 500.0]}
    )

    result = calculate_household_change(households)

    expected = pd.DataFrame({
            'building_category': ['category1'] * 5,
            'year': period.range(),
            'household_change': [np.nan, 50.0, 75.0, 0.0, -25.0],
        },
    ).set_index(['building_category', 'year']).household_change
    pd.testing.assert_series_equal(result, expected)


def test_calculate_household_change_with_more_than_one_building_category() -> None:
    """The change should be calculated per building_category, not across categories."""
    years = YearRange(2010, 2013)
    index_columns = ['building_category', 'year']
    households = pd.DataFrame(
        data={
            'year': years.range() + years.range(),
            'building_category': ['category1'] * 4 + ['category2'] * 4,
            'households': [400.0, 450.0, 525.0, 500.0, 100.0, 125.0, 125.0, 200.0],
        }).set_index(index_columns).households

    result = calculate_household_change(households)

    expected = pd.DataFrame(
        data={
            'year': years.range() + years.range(),
            'building_category': ['category1'] * 4 + ['category2'] * 4,
            'household_change': [np.nan, 50.0, 75.0, -25.0, np.nan, 25.0, 0.0, 75.0],
        }).set_index(index_columns).household_change

    pd.testing.assert_series_equal(result, expected)


def test_calculate_household_change_single_year() -> None:
    """A single value has no previous year and should give NaN."""
    households = pd.Series([400.0], index=pd.Index([2010], name='year'))

    result = calculate_household_change(households)

    expected = pd.Series([np.nan], index=pd.Index([2010], name='year'), name='household_change')
    pd.testing.assert_series_equal(result, expected)


def test_calculate_households_by_year() -> None:
    household_size = pd.Series([2, 4, 7, 8])
    population = pd.Series([1000, 1200, 1400, 1600])

    expected_households = pd.Series([500.0, 300.0, 200.0, 200.0], name='households')
    calculated_households = calculate_households_by_year(household_size, population)

    pd.testing.assert_series_equal(calculated_households, expected_households)


def test_calculate_residential_construction() -> None:
    period = YearRange(2010, 2013)
    households_by_year = pd.Series([400.0, 458.33333333333337, 526.0869565217391, 605.0], index=period.to_index())
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.to_index())
    build_area_sum = pd.Series([0, 200, 300, 400], index=period.to_index())
    average_floor_area = 175

    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])[[
        'net_constructed_floor_area', 'constructed_floor_area', 'accumulated_constructed_floor_area']]

    expected_data = {
        'net_constructed_floor_area': pd.Series(
            data=[0, 200.0, 300, 400], index=period.to_index(), name='house_floor_area_change'),
        'constructed_floor_area': pd.Series(
            data=[0, 200.0, 300.0, 400.0],
            index=period.to_index(),
            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series(
            data=[0, 200.0, 500.0, 900.0],
            index=period.to_index(),
            name='accumulated_constructed_floor_area'),
    }

    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result.round(2), expected_df)



def test_calculate_residential_construction_with_building_categories() -> None:
    period = YearRange(2010, 2013)
    households_by_year = pd.Series([400.0, 458.33333333333337, 526.0869565217391, 605.0], index=period.to_index())

    building_category_share = pd.DataFrame(
        {'share': [0.5, 0.5, 0.5, 0.5]}, index=period.to_index())
    build_area_sum = pd.Series([0, 200, 300, 400], index=period.to_index())
    average_floor_area = 175

    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])[[
        'net_constructed_floor_area', 'constructed_floor_area', 'accumulated_constructed_floor_area']]

    expected_data = {
        'net_constructed_floor_area': pd.Series(
            data=[0, 200.0, 300, 400], index=pd.Series([2010, 2011, 2012, 2013], name='year'), name='house_floor_area_change'),
        'constructed_floor_area': pd.Series(
            data=[0, 200.0, 300.0, 400.0],
            index=pd.Series([2010, 2011, 2012, 2013], name='year'),
            name='constructed_floor_area'),
        'accumulated_constructed_floor_area': pd.Series(
            data=[0, 200.0, 500.0, 900.0],
            index=pd.Series([2010, 2011, 2012, 2013], name='year'),
            name='accumulated_constructed_floor_area'),
    }

    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result.round(2), expected_df)


def test_calculate_residential_construction_2011() -> None:
    period = YearRange(2011, 2014)
    building_category_share = pd.Series([0.5, 0.5, 0.5, 0.5], index=period.to_index())
    build_area_sum = pd.Series([0, 200, 300, 400], index=period.to_index())
    average_floor_area = 175

    households_by_year = pd.Series([400.0, 458.33333333333337, 526.0869565217391, 605.0], index=period.to_index(), name='households')
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])

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
    building_category_share = pd.Series([0.5]*len(period), index=period.to_index())
    build_area_sum = pd.Series([10_000, 20_000, 30_000, 31_000], index=pd.Index([2010, 2011, 2012, 2013], name='year'))
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    households_by_year.index.name = 'year'
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.to_index(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()


def test_calculate_residential_construction_from_2020(default_input) -> None:
    """Test that accumulated_constructed_floor_area has a correct index from 2011 to 2052."""
    period = YearRange(2011, 2051)
    building_category_share = pd.Series({y: 0.5 for y in period})
    build_area_sum = pd.Series([10_000, 20_000], index=pd.Index([2011, 2012], name='year'))
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    households_by_year.index.name = 'year'
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])
    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area
    expected = pd.Series(data=[1_000_000.0 + y for y in period],
                         index=period.to_index(),
                         name='accumulated_constructed_floor_area')

    assert accumulated_constructed_floor_area.index.to_list() == expected.index.to_list()

@pytest.mark.parametrize('build_sum_0', [0.0, 10_000.0])
def test_calculate_residential_construction_for_ten_years(default_input, build_sum_0):
    """Test that accumulated_constructed_floor_area has a correct index from 2011 to 2020."""
    period = YearRange(2011, 2020)
    building_category_share = pd.Series([0.5] * len(period), index=period.to_index())
    build_area_sum = pd.Series([build_sum_0, 20_000], index=pd.Series([2011, 2012], name='year'))
    average_floor_area = 175

    households_by_year = default_input.get('households_by_year').loc[period]
    households_by_year.index.name = 'year'
    result = calculate_residential_construction(households_by_year, building_category_share, build_area_sum,
                                                average_floor_area, period=period).set_index(['year'])

    accumulated_constructed_floor_area = result.accumulated_constructed_floor_area

    expected_values = [build_sum_0, 20000.0, 4407836.558149085, 6705944.512694532, 8962887.694512703,
                       11826172.096754318, 13597427.80451687, 17037877.79715203, 19492648.74249253,
                       21952876.859417602]
    expected = pd.Series(data=expected_values, index=period.to_index(), name='accumulated_constructed_floor_area')
    expected.iloc[1:] = expected.iloc[1:] + build_sum_0


    pd.testing.assert_series_equal(accumulated_constructed_floor_area, expected)


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


@pytest.mark.parametrize(
    ('column', 'expected_values'),
    [('household_change', [
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,
    ]),
     ('net_constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416,
         0.0, 1152796.0, 1052877.5500197378, 1770653.857028967, 1524321.629867502,
         1133806.561292109, 937255.5473314389, 758906.4266032964, 764686.8295942774, 764684.9866736847,
         759364.3391277362,
     ]),
     ('constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416,
         0.0, 1152796.0, 1052877.5500197378, 1770653.857028967, 1524321.629867502,
         1133806.561292109, 937255.5473314389, 758906.4266032964, 764686.8295942774, 764684.9866736847,
         759364.3391277362,

     ]),
      ('accumulated_constructed_floor_area', [
          0.0, 2733711.49774, 4656357.458645608, 7182978.286708325, 9181042.387694068,
          11251471.760488354, 12962981.890397938, 14293817.79791966, 15634790.354164697, 16975759.67862145,
          18307398.59216429,
          0.0, 1152796.0, 2205673.550019738, 3976327.407048705, 5500649.0369162075,
          6634455.598208317, 7571711.145539755, 8330617.572143052, 9095304.401737329, 9859989.388411013,
          10619353.72753875,
      ]),
     ],
)
def test_calculate_residential_construction_house_dataframe_with_two_building_categories(column, expected_values):
    """
    Test the calculation of residential construction for house using Dataframe parameters.
    Use building_category and year as index. Data from short_analysis_2025.
    """
    build_area_sum = pd.DataFrame({
            'year': [2020, 2021, 2020, 2021],
            'building_category': ['category_1', 'category_1', 'category_2', 'category_2'],
            'house': [0.0, 2733711.49774, 0.0, 1152796.0],
         }).set_index(['building_category', 'year'])

    households_by_year = pd.DataFrame({
        'building_category':['category_1'] * 11 + ['category_2'] * 11,
        'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] * 2,
        'households':[
            2496548.837209302,
            2519331.308411215,
            2547075.117370892,
            2589143.396226415,
            2624209.456264775,
            2654085.781990522,
            2678782.897862233,
            2698423.333333333,
            2718213.365155131,
            2738003.349282297,
            2757655.635491607,
        ] * 2},
    ).set_index(['building_category', 'year'])

    building_category_share = pd.DataFrame(
        {
            'building_category': ['category_1'] * 11 + ['category_2'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] * 2,
            'share': [0.44, 0.43, 0.45, 0.39, 0.37, 0.45, 0.45, 0.44, 0.44, 0.44, 0.44,
                      0.56, 0.57, 0.55, 0.61, 0.63, 0.55, 0.55, 0.56, 0.56, 0.56, 0.56],
        },
    ).set_index(['building_category', 'year'])

    average_floor_area = pd.DataFrame(
        {
            'building_category': ['category_1'] * 11 + ['category_2'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] * 2,
            'average_floor_area': [154.0] *11 + [69.0]* 11,

        },
    ).set_index(['building_category', 'year'])

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=YearRange(2020, 2030),
    )


    assert actual[column].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)


def test_calculate_residential_construction_house_dataframe_missing_building_category_in_households_by_year():
    """
    Test the calculation of residential construction for house using Dataframe parameters.
    Use building_category and year as index. Data from short_analysis_2025.
    """
    build_area_sum = pd.DataFrame({
            'year': [2020, 2021, 2020, 2021],
            'building_category': ['category_1', 'category_1', 'category_2', 'category_2'],
            'house': [0.0, 2733711.49774, 0.0, 1152796.0],
         }).set_index(['building_category', 'year'])

    households_by_year = pd.DataFrame({
        'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
        'households':[
            2496548.837209302,
            2519331.308411215,
            2547075.117370892,
            2589143.396226415,
            2624209.456264775,
            2654085.781990522,
            2678782.897862233,
            2698423.333333333,
            2718213.365155131,
            2738003.349282297,
            2757655.635491607,
        ]},
    ).set_index(['year'])

    building_category_share = pd.DataFrame(
        {
            'building_category': ['category_1'] * 11 + ['category_2'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] * 2,
            'share': [0.44, 0.43, 0.45, 0.39, 0.37, 0.45, 0.45, 0.44, 0.44, 0.44, 0.44,
                      0.56, 0.57, 0.55, 0.61, 0.63, 0.55, 0.55, 0.56, 0.56, 0.56, 0.56],
        },
    ).set_index(['building_category', 'year'])

    average_floor_area = pd.DataFrame(
        {
            'building_category': ['category_1'] * 11 + ['category_2'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] * 2,
            'average_floor_area': [154.0] *11 + [69.0]* 11,

        },
    ).set_index(['building_category', 'year'])

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=YearRange(2020, 2030),
    )
    expected_values = [np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
    29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
    19652.28620930994,
    np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
    29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
    19652.28620930994,]

    assert actual['household_change'].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)


@pytest.mark.parametrize(
    ('column', 'expected_values'),
    [('household_change', [
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,]),
     ('net_constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
     ('constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
      ('accumulated_constructed_floor_area', [
          0.0, 2733711.49774, 4656357.458645608, 7182978.286708325, 9181042.387694068,
          11251471.760488354, 12962981.890397938, 14293817.79791966, 15634790.354164697, 16975759.67862145,
          18307398.59216429,]),
     ],
)
def test_calculate_residential_construction_house_dataframe_with_building_category_and_year(column, expected_values):
    """
    Test the calculation of residential construction for house using Dataframe parameters.
    Use building_category and year as index. Data from short_analysis_2025.
    """
    build_area_sum = pd.DataFrame({
            'building_category': ['house', 'house'],
            'year': [2020, 2021],
            'house': [0.0, 2733711.49774],
         }).set_index(['building_category', 'year'])

    households_by_year = pd.DataFrame({
        'building_category':['house'] * 11,
        'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
        'households':[
            2496548.837209302,
            2519331.308411215,
            2547075.117370892,
            2589143.396226415,
            2624209.456264775,
            2654085.781990522,
            2678782.897862233,
            2698423.333333333,
            2718213.365155131,
            2738003.349282297,
            2757655.635491607,
        ]},
    ).set_index(['building_category', 'year'])

    building_category_share = pd.DataFrame(
        {
            'building_category': ['house'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
            'share': [0.44, 0.43, 0.45, 0.39, 0.37, 0.45, 0.45, 0.44, 0.44, 0.44, 0.44],
        },
    ).set_index(['building_category', 'year'])

    average_floor_area = pd.DataFrame(
        {
            'building_category': ['house'] * 11,
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
            'average_floor_area': [154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0],
        },
    ).set_index(['building_category', 'year'])

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=YearRange(2020, 2030),
    )

    assert actual[column].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)


@pytest.mark.parametrize(
    ('column', 'expected_values'),
    [('household_change', [
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,]),
     ('net_constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
     ('constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
     ('accumulated_constructed_floor_area', [
         0.0, 2733711.49774, 4656357.458645608, 7182978.286708325, 9181042.387694068,
         11251471.760488354, 12962981.890397938, 14293817.79791966, 15634790.354164697, 16975759.67862145,
         18307398.59216429,]),
     ],
)
def test_calculate_residential_construction_house_dataframe(column, expected_values):
    """
    Test the calculation of residential construction for house using Dataframe parameters. Use year as index.
    Data from short_analysis_2025.
    """
    build_area_sum = pd.DataFrame({
            'year': [2020, 2021],
            'house': [0.0, 2733711.49774],
         }).set_index(['year'])

    households_by_year = pd.DataFrame({
        'year':[2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
        'households':[
            2496548.837209302,
            2519331.308411215,
            2547075.117370892,
            2589143.396226415,
            2624209.456264775,
            2654085.781990522,
            2678782.897862233,
            2698423.333333333,
            2718213.365155131,
            2738003.349282297,
            2757655.635491607,
        ]},
    ).set_index(['year'])

    building_category_share = pd.DataFrame(
        {
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
            'share': [0.44, 0.43, 0.45, 0.39, 0.37, 0.45, 0.45, 0.44, 0.44, 0.44, 0.44],
        },
    ).set_index(['year'])

    average_floor_area = pd.DataFrame(
        {
            'year': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
            'average_floor_area': [154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0, 154.0],
        },
    ).set_index(['year'])

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=YearRange(2020, 2030),
    )

    assert actual[column].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)


@pytest.mark.parametrize(
    ('column', 'expected_values'),
    [('household_change', [
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,]),
     ('net_constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
     ('constructed_floor_area', [
         0.0, 2733711.49774, 1922645.9609056083, 2526620.8280627173, 1998064.1009857433,
         2070429.372794286, 1711510.1299095838, 1330835.9075217226, 1340972.5562450371, 1340969.3244567513,
         1331638.9135428416]),
     ('accumulated_constructed_floor_area', [
         0.0, 2733711.49774, 4656357.458645608, 7182978.286708325, 9181042.387694068,
         11251471.760488354, 12962981.890397938, 14293817.79791966, 15634790.354164697, 16975759.67862145,
         18307398.59216429,]),
     ],
)
def test_calculate_residential_construction_house_series(column, expected_values):
    """
    Test the calculation of residential construction for house using Series inputs.
    Data from short_analysis_2025.
    """
    build_area_sum = pd.Series({2020: 0.0, 2021: 2733711.49774})
    build_area_sum.index.name = 'year'
    households_by_year = pd.Series(
        {
            2020: 2496548.837209302,
            2021: 2519331.308411215,
            2022: 2547075.117370892,
            2023: 2589143.396226415,
            2024: 2624209.456264775,
            2025: 2654085.781990522,
            2026: 2678782.897862233,
            2027: 2698423.333333333,
            2028: 2718213.365155131,
            2029: 2738003.349282297,
            2030: 2757655.635491607,
        },
    )
    households_by_year.index.name = 'year'
    building_category_share = pd.Series(
        {
            2020: 0.44,
            2021: 0.43,
            2022: 0.45,
            2023: 0.39,
            2024: 0.37,
            2025: 0.45,
            2026: 0.45,
            2027: 0.44,
            2028: 0.44,
            2029: 0.44,
            2030: 0.44,
        },
    )
    building_category_share.index.name = "year"
    average_floor_area = pd.Series(
        {
            2020: 154.0,
            2021: 154.0,
            2022: 154.0,
            2023: 154.0,
            2024: 154.0,
            2025: 154.0,
            2026: 154.0,
            2027: 154.0,
            2028: 154.0,
            2029: 154.0,
            2030: 154.0,
        },
    )
    average_floor_area.index.name = "year"

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=YearRange(2020, 2030),
    )

    assert actual[column].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)


@pytest.mark.parametrize(
    ('column', 'expected_values'),
    [('household_change', [
        np.nan, 22782.471201912966, 27743.808959676884, 42068.278855523095, 35066.060038359836,
        29876.325725747272, 24697.11587171117, 19640.4354710998, 19790.031821798068, 19789.98412716575,
        19652.28620930994,]),
     ('net_constructed_floor_area', [
         0.0, 1152796.0, 1052877.5500197378, 1770653.857028967, 1524321.629867502,
         1133806.561292109, 937255.5473314389, 758906.4266032964, 764686.8295942774, 764684.9866736847,
         759364.3391277362]),
     ('constructed_floor_area', [
         0.0, 1152796.0, 1052877.5500197378, 1770653.857028967, 1524321.629867502,
         1133806.561292109, 937255.5473314389, 758906.4266032964, 764686.8295942774, 764684.9866736847,
         759364.3391277362]),
     ('accumulated_constructed_floor_area', [
         0.0, 1152796.0, 2205673.550019738, 3976327.407048705, 5500649.0369162075,
         6634455.598208317, 7571711.145539755, 8330617.572143052, 9095304.401737329, 9859989.388411013,
         10619353.72753875]),
     ],
)
def test_calculate_residential_construction_apartment_block_series(column, expected_values):
    """
    Test the calculation of residential construction for apartment blocks using Series inputs.
    Data from short_analysis_2025.
    """
    year_range = YearRange(2020, 2030)
    build_area_sum = pd.Series({2020: 0.0, 2021: 1152796.0}, name='apartment_block')
    build_area_sum.index.name = 'year'

    households_by_year = pd.Series(
        {
            2020: 2496548.837209302,
            2021: 2519331.308411215,
            2022: 2547075.117370892,
            2023: 2589143.396226415,
            2024: 2624209.456264775,
            2025: 2654085.781990522,
            2026: 2678782.897862233,
            2027: 2698423.333333333,
            2028: 2718213.365155131,
            2029: 2738003.349282297,
            2030: 2757655.635491607,
        },
    )
    households_by_year.index.name = 'year'

    building_category_share = pd.Series(
        {2020: 0.56, 2021: 0.57, 2022: 0.55, 2023: 0.61, 2024: 0.63, 2025: 0.55, 2026: 0.55, 2027: 0.56, 2028: 0.56, 2029: 0.56, 2030: 0.56},
    )
    building_category_share.index.name = 'year'

    average_floor_area = pd.Series(
        {
            2020: 69.0,
            2021: 69.0,
            2022: 69.0,
            2023: 69.0,
            2024: 69.0,
            2025: 69.0,
            2026: 69.0,
            2027: 69.0,
            2028: 69.0,
            2029: 69.0,
            2030: 69.0,
        },
    )
    average_floor_area.index.name = 'year'

    actual = calculate_residential_construction(
        households_by_year=households_by_year,
        building_category_share=building_category_share,
        average_floor_area=average_floor_area,
        build_area_sum=build_area_sum,
        period=year_range,
    )

    assert actual[column].tolist() == pytest.approx(expected_values, rel=1e-3, nan_ok=True)

if __name__ == '__main__':
    default_input()
    pytest.main()
