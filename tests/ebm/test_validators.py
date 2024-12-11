import io
import itertools
import warnings

import numpy as np
import pandas as pd
import pandera as pa
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.validators import (tek_parameters,
                            area_parameters,
                            construction_building_category_yearly,
                            new_buildings_house_share,
                            population,
                            scurve_parameters,
                            energy_requirement_original_condition,
                            energy_requirement_reduction_per_condition,
                            energy_requirement_yearly_improvements,
                            heating_systems,
                            energy_requirement_policy_improvements, 
                            area_per_person,
                            check_overlapping_tek_periods,
                            heating_systems_shares_start_year,
                            heating_systems_projection,
                            heating_systems_efficiencies,
                            check_sum_of_tek_shares_equal_1)


@pytest.fixture
def ok_tek_parameters() -> pd.DataFrame:
    return pd.DataFrame({
        'TEK': ['PRE_TEK49_1940', 'TEK69_COM', 'TEK07'],
        'building_year': [1940, 1978, 1990],
        'period_start_year': [0, 1956, 2014],
        'period_end_year': [1955, 2013, 2050]
    })


def test_tek_overlapping_periods():
    df = pd.DataFrame({
        'TEK': ['PRE_TEK49_1940', 'TEK07'],
        'building_year': [1940, 1990],
        'period_start_year': [0, 2014],
        'period_end_year': [1955, 2050]
    })
    
    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(df)


def test_tek_overlapping_periods_when_tek_parameters_are_unsorted():
    df = pd.DataFrame([{'TEK':'TEK3', 'building_year': 1955, 'period_start_year': 1951, 'period_end_year': 2050},
                       {'TEK':'TEK2', 'building_year': 1945, 'period_start_year': 1940, 'period_end_year': 1950}])
    
    pd.testing.assert_series_equal(
        check_overlapping_tek_periods(df),
        pd.Series([True, True]), check_index=False)
    

def test_tek_parameters_when_all_are_correct(ok_tek_parameters: pd.DataFrame):
    tek_parameters.validate(ok_tek_parameters)


def test_tek_parameters_require_tek(ok_tek_parameters: pd.DataFrame):
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['', 2030, 2025, 2071]

    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(ok_tek_parameters)


@pytest.mark.parametrize('building_year', [-1, None, 'building_year', 2071])
def test_tek_parameters_building_year(ok_tek_parameters: pd.DataFrame, building_year):
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['TEK10', building_year, 2007, 2025]

    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(ok_tek_parameters)


@pytest.mark.parametrize('start_year', ['period_start_year', -1, 2071])
def test_tek_parameters_period_start_year(ok_tek_parameters: pd.DataFrame, start_year):
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['TEK10', 2011, start_year, 2070]

    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(ok_tek_parameters)


@pytest.mark.parametrize('start_year,end_year', [(2007, -1), (2007, None), (2007, 'period_end_year'), (2024, 2007)])
def test_tek_parameters_period_end_year(ok_tek_parameters: pd.DataFrame, start_year, end_year):
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['TEK10', 2011, start_year, end_year]

    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(ok_tek_parameters)


def test_tek_parameters_duplicate_tek(ok_tek_parameters):
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['TEK10', 2011, 2000, 2020]
    ok_tek_parameters.loc[len(ok_tek_parameters)] = ['TEK10', 2012, 2001, 2021]

    with pytest.raises(pa.errors.SchemaError):
        tek_parameters.validate(ok_tek_parameters)


def test_area_parameters_building_categories():
    rows = [[str(building_category), 'TEK10', 10000] for building_category in BuildingCategory]
    df = pd.DataFrame(data=rows, columns=['building_category', 'TEK', 'area'])

    area_parameters.validate(df)


def test_area_parameters_raises_schema_error_on_unknown_building_category():
    rows = [['CASTLE', 'TEK10', 10000]]
    df = pd.DataFrame(data=rows, columns=['building_category', 'TEK', 'area'])

    with pytest.raises(pa.errors.SchemaError):
        area_parameters.validate(df)


def test_area_parameters_raises_schema_error_on_illegal_area():
    rows = [[BuildingCategory.HOUSE, 'TEK10', -1]]
    df = pd.DataFrame(data=rows, columns=['building_category', 'TEK', 'area'])

    with pytest.raises(pa.errors.SchemaError):
        area_parameters.validate(df)


@pytest.fixture
def ok_construction_building_category_yearly():
    return pd.DataFrame(data=[
        {'year': 2010, 'house': 1.1, 'apartment_block': 1.2, 'kindergarten': 1.3, 'school': 1.4,
         'university': 1.5, 'office': 1.6, 'retail': 1.7, 'hotel': 1.8, 'hospital': 1.9, 'nursing_home': 1.11,
         'culture': 1.12, 'sports': 1.13, 'storage_repairs': 1.14},
        {'year': 2011, 'house': 2, 'apartment_block': 3, 'kindergarten': 4, 'school': 5,
         'university': 6, 'office': 7, 'retail': 8, 'hotel': 9, 'hospital': 10, 'nursing_home': 11,
         'culture': 12, 'sports': 13, 'storage_repairs': 14},
        {'year': 2012, 'house': None, 'apartment_block': None, 'kindergarten': 4, 'school': 5,
         'university': 6, 'office': 7, 'retail': 8, 'hotel': 9, 'hospital': 10, 'nursing_home': 11,
         'culture': 12, 'sports': 13, 'storage_repairs': 14},
        {'year': 2013, 'house': None, 'apartment_block': None, 'kindergarten': 4.2, 'school': 4.3,
         'university': 4.4, 'office': 4.5, 'retail': 4.6, 'hotel': 4.7, 'hospital': 4.8, 'nursing_home': 4.9,
         'culture': 4.1, 'sports': 4.11, 'storage_repairs': 4.12}])


def test_construction_building_category_yearly(ok_construction_building_category_yearly):
    """
    Test that construction_building_category_yearly supports:
        - float
        - int to float
        - empty value for house and apartment_block
    """

    result: pd.DataFrame = construction_building_category_yearly.validate(ok_construction_building_category_yearly)
    assert result['year'].dtype == np.int64
    pd.testing.assert_series_equal(left=result['year'],
                                   right=pd.Series([2010, 2011, 2012, 2013]),
                                   check_names=False,
                                   check_index=False)

    assert result['house'].dtype == np.float64
    pd.testing.assert_series_equal(left=result['house'],
                                   right=pd.Series([1.1, 2.0, np.nan, np.nan]),
                                   check_names=False,
                                   check_index=False)

    assert result['kindergarten'].dtype == np.float64
    pd.testing.assert_series_equal(left=result['kindergarten'],
                                   right=pd.Series([1.3, 4.0, 4.0, 4.2]),
                                   check_names=False,
                                   check_index=False)


@pytest.mark.parametrize('building_category,row', itertools.product(
    [b for b in [BuildingCategory.HOUSE, BuildingCategory.APARTMENT_BLOCK, BuildingCategory.STORAGE_REPAIRS]], 
    [0, 1, 2, 3]))
def test_construction_building_category_yearly_commercial_area(ok_construction_building_category_yearly,
                                                               building_category: BuildingCategory,
                                                               row: int):
    """ Test that building category raises SchemaError when area is empty or less than zero"""
    if building_category.is_residential() and row > 1:
        # Skip test. The rows 2 to 5 are supposed to be empty for residential.
        return

    # Prevent this test running on a non-existing row
    if ok_construction_building_category_yearly.loc[row].empty:
        raise ValueError(f'Row {row} was not found in ok_construction_building_category_yearly')

    ok_construction_building_category_yearly.loc[row, building_category] = -0.1
    with pytest.raises(pa.errors.SchemaError):
        construction_building_category_yearly.validate(ok_construction_building_category_yearly)
    ok_construction_building_category_yearly.loc[row, building_category] = None
    with pytest.raises(pa.errors.SchemaError):
        construction_building_category_yearly.validate(ok_construction_building_category_yearly)
    ok_construction_building_category_yearly.loc[row, building_category] = ''
    with pytest.raises(pa.errors.SchemaError):
        construction_building_category_yearly.validate(ok_construction_building_category_yearly)


@pytest.mark.parametrize('building_category', [BuildingCategory.HOUSE, BuildingCategory.APARTMENT_BLOCK])
def test_construction_building_category_yearly_residential_area(
        ok_construction_building_category_yearly,
        building_category):
    """ Test that residential building categories raises SchemaError when
        - area is empty or less than zero after
        -
    """
    df1 = ok_construction_building_category_yearly.copy()
    last_row = len(df1)-1
    df1.loc[last_row, building_category] = None
    construction_building_category_yearly.validate(df1)

    df1.loc[last_row, building_category] = 1
    with pytest.raises(pa.errors.SchemaError):
        construction_building_category_yearly.validate(df1)


@pytest.fixture
def new_buildings_house_share_df():
    return pd.DataFrame(
        data=[[2010, 0.6131112606550, 0.3868887393450, 175, 75], [2011, 0.6284545545246, 0.3715454454754, 175, 75]],
        columns=['year',
                 'new_house_share',
                 'new_apartment_block_share',
                 'floor_area_new_house',
                 'flood_area_new_apartment_block']
    )


def test_new_buildings_house_share_ok(new_buildings_house_share_df):
    new_buildings_house_share.validate(new_buildings_house_share_df)


@pytest.mark.parametrize('column, too_low, too_high',
                         [('year', 2009, 2071),
                          ('new_house_share', -0.01, 1.01),
                          ('new_apartment_block_share', -0.01, 1.01),
                          ('floor_area_new_house', 0, 1001),
                          ('flood_area_new_apartment_block', 0, 1001)])
def test_new_buildings_house_share_value_ranges(new_buildings_house_share_df, column, too_low, too_high):
    new_buildings_house_share.validate(new_buildings_house_share_df)

    new_buildings_house_share_df.loc[0, column] = too_low
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_house_share.validate(new_buildings_house_share_df)

    new_buildings_house_share_df.loc[0, column] = too_high
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_house_share.validate(new_buildings_house_share_df)


def test_new_buildings_house_share_sum_of_share_should_be_1(new_buildings_house_share_df):
    new_buildings_house_share_df.loc[0, 'new_apartment_block_share'] = 1.0
    new_buildings_house_share_df.loc[0, 'new_house_share'] = 1.0

    with pytest.raises(pa.errors.SchemaError):
        new_buildings_house_share.validate(new_buildings_house_share_df)


def test_population_ok(new_buildings_house_share_df):
    standard_years = [(y, 4858199, 2.22) for y in YearRange(2001, 2070)]

    df = pd.DataFrame(data=[(2000, 4000000, np.nan, )] + standard_years,
                      columns=['year', 'population', 'household_size'])

    population.validate(df)

    household_df = df.copy()
    household_df.loc[0, 'household_size'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        population.validate(household_df)

    population_df = df.copy()
    population_df.loc[0, 'population'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        population.validate(population_df)


def test_population_coerce_values(new_buildings_house_share_df):
    df = pd.DataFrame(data=[(float(y), 4858199.0, 2) for y in YearRange(2010, 2070)],
                      columns=['year', 'population', 'household_size'])

    population.validate(df)


@pytest.fixture
def s_curves() -> pd.DataFrame:
    df = pd.DataFrame(
        columns=['building_category', 'condition', 'earliest_age_for_measure', 'average_age_for_measure',
                 'rush_period_years', 'last_age_for_measure', 'rush_share', 'never_share'],
        data=[[f'{BuildingCategory.HOUSE}', f'{BuildingCondition.SMALL_MEASURE}', 2, 23, 30, 80, 0.8, 0.01],
              [f'{BuildingCategory.HOUSE}', f'{BuildingCondition.RENOVATION}', 10, 37, 24, 750, 0.65, 0.05],
              [f'{BuildingCategory.HOUSE}', f'{BuildingCondition.DEMOLITION}', 60, 90, 40, 150, 0.7, 0.05]])
    return df


def test_scurve_parameters_ok(s_curves):
    scurve_parameters.validate(s_curves)


def test_scurve_parameters_reject_invalid_building_category(s_curves):
    s_curves.loc[0, 'building_category'] = 'småhus'

    with pytest.raises(pa.errors.SchemaError):
        scurve_parameters.validate(s_curves)


def test_scurve_parameters_reject_invalid_condition(s_curves):
    s_curves.loc[0, 'condition'] = 'INVALID'
    with pytest.raises(pa.errors.SchemaError):
        scurve_parameters.validate(s_curves)


@pytest.mark.parametrize('attribute', ('earliest_age_for_measure',
                                       'average_age_for_measure',
                                       'rush_period_years',
                                       'last_age_for_measure'))
def test_scurve_parameters_reject_invalid_age(s_curves, attribute):
    s_curves.loc[0, attribute] = 0
    with pytest.raises(pa.errors.SchemaError):
        scurve_parameters.validate(s_curves)


@pytest.mark.parametrize('attribute', ('rush_share', 'never_share'))
def test_scurve_parameters_reject_invalid_share(s_curves, attribute):
    s_curves.loc[0, attribute] = 0
    with pytest.raises(pa.errors.SchemaError):
        scurve_parameters.validate(s_curves)
    s_curves.loc[0, attribute] = 1.01
    with pytest.raises(pa.errors.SchemaError):
        scurve_parameters.validate(s_curves)


@pytest.fixture
def energy_by_floor_area_df():
    return pd.DataFrame(
        data=[['house', 'TEK69', 'lighting', 0.0],
              ['apartment_block', 'TEK69', 'lighting', 1.234]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2'])


def test_energy_by_floor_area(energy_by_floor_area_df):
    energy_requirement_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_building_category(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[:, 'building_category'] = 'småhus'

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_tek(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[:, 'TEK'] = 'TAKK'

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_illegal_kwhm(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[0, 'kwh_m2'] = -0.1

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_purpose(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[0, 'purpose'] = 'lys og varme'

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(energy_by_floor_area_df)


@pytest.fixture
def original_condition_df():
    return pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'kwh_m2'],
                        data=[
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'electrical_equipment', 2.2],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'fans_and_pumps', 3.3],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'heating_dhw', 4.4],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'heating_rv', 5.5],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'lighting', 5.5],
                            ['default', 'default', 'default', 0]
                        ])


def test_energy_req_original_condition(original_condition_df):
    energy_requirement_original_condition.validate(original_condition_df)


def test_energy_req_original_condition_require_valid_building_cat(original_condition_df):
    original_condition_df.loc[0, 'building_category'] = 'not_a_building_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(original_condition_df)


def test_energy_req_original_condition_require_valid_tek(original_condition_df):
    original_condition_df.loc[0, 'TEK'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(original_condition_df)


def test_energy_req_original_condition_require_valid_purpose(original_condition_df):
    original_condition_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(original_condition_df)


def test_energy_req_original_condition_require_value_greater_than_or_equal_to_zero(original_condition_df):
    original_condition_df.loc[0, 'kwh_m2'] = -1
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(original_condition_df)


def test_energy_req_original_condition_require_unique_rows():
    duplicate_df = pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'kwh_m2'],
                                data=[
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 2.1],
                                ])
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_original_condition.validate(duplicate_df)


# TODO: add test for special case with conditions
@pytest.fixture
def reduction_per_condition_df():
    return pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share'],
                        data=[['house', 'default', 'heating_rv', 'original_condition', 0.1],
                              ['house', 'default', 'heating_rv', 'small_measure', 0.2],
                              ['house', 'default', 'heating_rv', 'renovation', 0.3],
                              ['house', 'default', 'heating_rv', 'renovation_and_small_measure', 0.4],
                              ['house', 'TEK21', 'heating_rv', 'original_condition', 0.5],
                              ['house', 'TEK21', 'heating_rv', 'small_measure', 0.6],
                              ['house', 'TEK21', 'heating_rv', 'renovation', 0.7],
                              ['house', 'TEK21', 'heating_rv', 'renovation_and_small_measure', 0.8]])


def test_energy_req_reduction_per_condition(reduction_per_condition_df):
    energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_building_cat(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_category'] = 'not_a_building_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_building_cat(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('building_category')] = 'default'
    energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_tek(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'TEK'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_tek(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('TEK')] = 'default'
    energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_purpose(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_purpose(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('purpose')] = 'default'
    energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_building_condition(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_condition'] = 'not_a_condition'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_exisiting_building_condition(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_condition'] = 'demolition'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_value_between_zero_and_one(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'reduction_share'] = -1
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)

    reduction_per_condition_df.loc[0, 'reduction_share'] = 1.01
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_unique_rows():
    duplicate_df = pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'building_condition',
                                         'reduction_share'],
                                data=[['house', 'default', 'heating_rv', 'original_condition', 0.1],
                                      ['house', 'default', 'heating_rv', 'original_condition', 0.2],
                                      ['house', 'default', 'heating_rv', 'original_condition', 0.2]
                                      ])
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(duplicate_df)


def test_energy_req_reduction_per_condition_allow_missing_building_conditions(reduction_per_condition_df):
    reduction_per_condition_df.drop(index=0, inplace=True)
    energy_requirement_reduction_per_condition.validate(reduction_per_condition_df)


@pytest.fixture
def yearly_improvements_df():
    return pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement'],
                        data=[
                            ['default', 'default', 'cooling', 0.0],
                            ['default', 'default', 'electrical_equipment', 0.1],
                            ['default', 'default', 'fans_and_pumps', 0.0],
                            ['default', 'default', 'heating_dhw', 0.0],
                            ['default', 'default', 'lighting', 0.05],
                            ['house', 'TEK01', 'heating_rv', 0.0]
                        ])


def test_energy_req_yearly_improvements(yearly_improvements_df):
    energy_requirement_yearly_improvements.validate(yearly_improvements_df)


def test_energy_req_yearly_improvements_require_valid_building_cat(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'building_category'] = 'not_a_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements.validate(yearly_improvements_df)


def test_energy_req_yearly_improvements_require_valid_tek(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'TEK'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements.validate(yearly_improvements_df)


def test_energy_req_yearly_improvements_require_valid_purpose(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements.validate(yearly_improvements_df)


def test_energy_req_yearly_improvements_value_between_zero_and_one(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'yearly_efficiency_improvement'] = -1
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements.validate(yearly_improvements_df)

    yearly_improvements_df.loc[0, 'yearly_efficiency_improvement'] = 2
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements.validate(yearly_improvements_df)


def test_energy_req_yearly_improvements_require_unique_rows():
    duplicate_df = pd.DataFrame(columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement'],
                                data=[['default', 'default', 'cooling', 0.0],
                                      ['default', 'default', 'cooling', 0.1],
                                      ['default', 'default', 'cooling', 0.0]])
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_yearly_improvements(duplicate_df)


@pytest.fixture
def policy_improvements_df():
    df = pd.DataFrame(
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end'],
        data=[['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['house', 'TEK01', 'default', 2020, 2040, 0.9]])
    return df


def test_energy_req_policy_improvements(policy_improvements_df):
    energy_requirement_policy_improvements.validate(policy_improvements_df)


def test_energy_req_policy_improvements_require_valid_building_cat(policy_improvements_df):
    policy_improvements_df.loc[0, 'building_category'] = 'not_a_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


def test_energy_req_policy_improvements_require_valid_tek(policy_improvements_df):
    policy_improvements_df.loc[0, 'TEK'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


def test_energy_req_policy_improvements_require_valid_purpose(policy_improvements_df):
    policy_improvements_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


def test_energy_req_policy_improvements_wrong_year_range(policy_improvements_df):
    policy_improvements_df.loc[0, 'period_start_year'] = 2050
    policy_improvements_df.loc[0, 'period_end_year'] = 2010
    
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


@pytest.mark.parametrize('start_year', [-1, ""])
def test_energy_req_policy_improvements_wrong_start_year(policy_improvements_df, start_year):
    policy_improvements_df['period_start_year'] = start_year
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


@pytest.mark.parametrize('end_year', [-1, ""])
def test_energy_req_policy_improvements_wrong_end_year(policy_improvements_df, end_year):
    policy_improvements_df['period_end_year'] = end_year
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


@pytest.mark.parametrize('improvement_value', [-1, 2])
def test_energy_req_policy_improvements_value_between_zero_and_one(policy_improvements_df, 
                                                                   improvement_value):
    policy_improvements_df.loc[0, 'improvement_at_period_end'] = improvement_value
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(policy_improvements_df)


def test_energy_req_policy_improvements_require_unique_rows():
    duplicate_df = pd.DataFrame(
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end'],
        data=[['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['default', 'default', 'lighting', 2018, 2030, 0.1]])
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements(duplicate_df)


def test_heating_systems_ok():
    heating_systems_csv = """building_category,TEK,Oppvarmingstyper,tek_share,Ekstralast andel,Grunnlast andel,Spisslast andel,Grunnlast virkningsgrad,Spisslast virkningsgrad,Ekstralast virkningsgrad,Tappevann virkningsgrad,Spesifikt elforbruk,Kjoling virkningsgrad
apartment_block,TEK07,Electricity,0.0,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4
retail,TEK97,Electricity,0.08158166937579898,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4
retail,PRE_TEK49,Electricity,0.07593898514970877,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4"""
    heating_systems.validate(pd.read_csv(io.StringIO(heating_systems_csv)))


def test_area_per_person_ok():
    area_per_person_csv = """building_category,area_per_person
kindergarten,0.6
retail,6.0
hotel,1.6
sports,1.3
office,5.5
culture,1.3
school,2.8
nursing_home,1.3
hospital,0.6
university,0.6"""
    area_per_person.validate(pd.read_csv(io.StringIO(area_per_person_csv)))


def test_area_per_person_raises_schema_error():
    area_per_person_csv = """building_category,area_per_person
invalid_category,0.6
"""
    with pytest.raises(pa.errors.SchemaError):
        area_per_person.validate(pd.read_csv(io.StringIO(area_per_person_csv)))


def test_heating_systems_shares_start_year_ok():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
apartment_block,TEK07,DH,2020,0.3316670026630616
apartment_block,TEK07,DH - Bio,2020,0.003305887353335002
apartment_block,TEK07,Electric boiler,2020,0.002667754942095502
apartment_block,TEK07,Electric boiler - Solar,2020,0.0002415945163788188
apartment_block,TEK07,Electricity - Bio,2020,0.06266384914026892
apartment_block,TEK07,Gas,2020,0.03680298490810775
apartment_block,TEK07,HP Central heating,2020,0.5456616600524988
apartment_block,TEK07,HP Central heating - Bio,2020,0.004734738186158519
apartment_block,TEK07,HP Central heating - DH,2020,0.007549542895245683
apartment_block,TEK07,HP Central heating - Gas,2020,0.0047049853428493
culture,PRE_TEK49,DH,2020,0.448808476036656
culture,PRE_TEK49,Electric boiler,2020,0.3532945191779804
culture,PRE_TEK49,Electricity,2020,0.0731295180790151
culture,PRE_TEK49,Electricity - Bio,2020,0.04554724481915243
culture,PRE_TEK49,Gas,2020,0.00796869432401196
culture,PRE_TEK49,HP Central heating,2020,0.06620268747246605
culture,PRE_TEK49,HP Central heating - Bio,2020,0.005048860090718066                                                                                                
""".strip()), skipinitialspace=True) 
    
    heating_systems_shares_start_year.validate(shares_start_year)


def test_heating_systems_shares_require_same_start_year():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
apartment_block,TEK07,DH,2020,0.3316670026630616
apartment_block,TEK07,DH - Bio,2021,0.003305887353335002                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_systems_shares_start_year.validate(shares_start_year)


def test_heating_systems_shares_between_zero_and_one():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
apartment_block,TEK07,DH,2020,-1                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_systems_shares_start_year.validate(shares_start_year)

    shares_start_year = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
apartment_block,TEK07,DH,2020,2                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_systems_shares_start_year.validate(shares_start_year)


def test_heating_systems_shares_start_year_equal_1():

    df = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
storage_repairs,TEK07,DH,2020,0.1513880769366867
storage_repairs,TEK07,DH - Bio,2020,0.01303276731750762
storage_repairs,TEK07,Electric boiler,2020,0.2258458963728039
storage_repairs,TEK07,Electricity - Bio,2020,0.0797465812036097
storage_repairs,TEK07,Gas,2020,0.2320505402244028
storage_repairs,TEK07,HP Central heating,2020,0.2850441643853094   
apartment_block,TEK07,DH,2020,0.3316670026630616
apartment_block,TEK07,DH - Bio,2020,0.003305887353335002
apartment_block,TEK07,Electric boiler,2020,0.002667754942095502
apartment_block,TEK07,Electric boiler - Solar,2020,0.0002415945163788188
apartment_block,TEK07,Electricity - Bio,2020,0.06266384914026892
apartment_block,TEK07,Gas,2020,0.03680298490810775
apartment_block,TEK07,HP Central heating,2020,0.5456616600524988
apartment_block,TEK07,HP Central heating - Bio,2020,0.004734738186158519
apartment_block,TEK07,HP Central heating - DH,2020,0.007549542895245683
apartment_block,TEK07,HP Central heating - Gas,2020,0.0047049853428493                                                                                           
""".strip()), skipinitialspace=True) 
    
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        validated_df = heating_systems_shares_start_year.validate(df, lazy=True)
        expected_in_error="<Check check_sum_of_tek_shares_equal_1:"
        for warning in caught_warnings:
            assert expected_in_error in str(warning.message)

        assert caught_warnings


def test_heating_systems_projection_ok():
    projection = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,new_heating_systems,2021,2022
default,default,Gas,HP Central heating,0.05,0.075
default,default,Gas,Electric boiler,0.05,0.075
non_residential,TEK69,HP Central heating - Gas,HP Central heating,0.1,0.15
house,default,Electricity - Bio,HP - Bio,0.05,0.054893999666245
residential,default,HP - Electricity,HP - Bio,0.05,0.0550163004472704
kindergarten,TEK87,Electricity,DH,0.05,0.0550163004472704                                                                                                                                                                                                                                                                                 
""".strip()), skipinitialspace=True) 

    heating_systems_projection.validate(projection)


def test_heating_systems_efficiencies_ok():
    efficiencies = pd.read_csv(io.StringIO("""
heating_systems,Grunnlast,Spisslast,Ekstralast,Ekstralast andel,Grunnlast energivare,Spisslast energivare,Ekstralast energivare,Grunnlast andel,Spisslast andel,Grunnlast virkningsgrad,Spisslast virkningsgrad,Ekstralast virkningsgrad,Tappevann,Tappevann virkningsgrad,Spesifikt elforbruk,Kjoling virkningsgrad
Electric boiler,Electric boiler,Ingen,Ingen,0.0,Electricity,Ingen,Ingen,1.0,0.0,0.98,1.0,1,Electric boiler,0.98,1,4
DH,DH,Ingen,Ingen,0.0,DH,Ingen,Ingen,1.0,0.0,0.99,1.0,1,DH,0.99,1,4
Electricity,Electricity,Ingen,Ingen,0.0,Electricity,Ingen,Ingen,1.0,0.0,1.0,1.0,1,Electricity,0.98,1,4
Gas,Gas,Ingen,Ingen,0.0,Fossil,Ingen,Ingen,1.0,0.0,0.96,1.0,1,Gas,0.96,1,4
Electricity - Bio,Electricity,Bio,Ingen,0.0,Electricity,Bio,Ingen,0.7,0.3,1.0,0.65,1,Electricity,0.98,1,4
DH - Bio,DH,Bio,Ingen,0.0,DH,Bio,Ingen,0.95,0.05,0.99,0.65,1,DH,0.99,1,4
HP - Bio,HP,Bio,Electricity,0.5,Electricity,Bio,Electricity,0.4,0.1,2.5,0.65,1,Electricity,0.98,1,4
HP - Electricity,HP,Electricity,Ingen,0.0,Electricity,Electricity,Ingen,0.4,0.6,2.5,1.0,1,Electricity,0.98,1,4
HP Central heating - DH,HP Central heating,DH,Ingen,0.0,Electricity,DH,Ingen,0.85,0.15,3.0,0.99,1,HP Central heating,3.0,1,4
HP Central heating,HP Central heating,Electric boiler,Ingen,0.0,Electricity,Electricity,Ingen,0.85,0.15,3.0,0.98,1,HP Central heating,3.0,1,4
HP Central heating - Gas,HP Central heating,Gas,Ingen,0.0,Electricity,Fossil,Ingen,0.85,0.15,3.0,0.96,1,HP Central heating,3.0,1,4
Electric boiler - Solar,Electric boiler,Solar,Ingen,0.0,Electricity,Solar,Ingen,0.8,0.1999999999999999,0.99,0.96,1,Electric boiler,0.99,1,4
HP Central heating - Bio,HP Central heating,Bio,Ingen,0.0,Electricity,Bio,Ingen,0.85,0.15,3.0,0.65,1,HP Central heating,3.0,1,4
""".strip()), skipinitialspace=True) 
    
    heating_systems_efficiencies.validate(efficiencies)