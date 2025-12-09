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
from ebm.model.dataframemodels import PolicyImprovement
from ebm.validators import (
    area,
    area_new_residential_buildings,
    area_per_person,
    building_code_parameters,
    check_overlapping_building_code_periods,
    energy_need_behaviour_factor,
    energy_need_improvements,
    energy_need_original_condition,
    heating_system_efficiencies,
    heating_system_forecast,
    heating_system_initial_shares,
    improvement_building_upgrade,
    new_buildings_residential,
    population_forecast,
    s_curve,
)


@pytest.fixture
def ok_building_code() -> pd.DataFrame:
    return pd.DataFrame({
        'building_code': ['PRE_TEK49_1940', 'TEK69_COM', 'TEK07'],
        'building_year': [1940, 1978, 1990],
        'period_start_year': [0, 1956, 2014],
        'period_end_year': [1955, 2013, 2050]
    })


def test_building_code_overlapping_periods():
    df = pd.DataFrame({
        'building_code': ['PRE_TEK49_1940', 'TEK07'],
        'building_year': [1940, 1990],
        'period_start_year': [0, 2014],
        'period_end_year': [1955, 2050]
    })
    
    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(df)


def test_building_code_overlapping_periods_when_building_code_are_unsorted():
    df = pd.DataFrame([{'building_code':'TEK3', 'building_year': 1955, 'period_start_year': 1951, 'period_end_year': 2050},
                       {'building_code':'TEK2', 'building_year': 1945, 'period_start_year': 1940, 'period_end_year': 1950}])
    
    pd.testing.assert_series_equal(
        check_overlapping_building_code_periods(df),
        pd.Series([True, True]), check_index=False)
    

def test_building_code_when_all_are_correct(ok_building_code: pd.DataFrame):
    building_code_parameters.validate(ok_building_code)


def test_building_code_require_building_code(ok_building_code: pd.DataFrame):
    ok_building_code.loc[len(ok_building_code)] = ['', 2030, 2025, 2071]

    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(ok_building_code)


@pytest.mark.parametrize('building_year', [-1, None, 'building_year', 2071])
def test_building_code_building_year(ok_building_code: pd.DataFrame, building_year):
    ok_building_code.loc[len(ok_building_code)] = ['TEK10', building_year, 2007, 2025]

    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(ok_building_code)


@pytest.mark.parametrize('start_year', ['period_start_year', -1, 2071])
def test_building_code_period_start_year(ok_building_code: pd.DataFrame, start_year):
    ok_building_code.loc[len(ok_building_code)] = ['TEK10', 2011, start_year, 2070]

    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(ok_building_code)


@pytest.mark.parametrize('start_year,end_year', [(2007, -1), (2007, None), (2007, 'period_end_year'), (2024, 2007)])
def test_building_code_period_end_year(ok_building_code: pd.DataFrame, start_year, end_year):
    ok_building_code.loc[len(ok_building_code)] = ['TEK10', 2011, start_year, end_year]

    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(ok_building_code)


def test_building_code_duplicate_building_code(ok_building_code):
    ok_building_code.loc[len(ok_building_code)] = ['TEK10', 2011, 2000, 2020]
    ok_building_code.loc[len(ok_building_code)] = ['TEK10', 2012, 2001, 2021]

    with pytest.raises(pa.errors.SchemaError):
        building_code_parameters.validate(ok_building_code)


def test_area_parameters_building_categories():
    rows = [[str(building_category), 'TEK10', float(10000)] for building_category in BuildingCategory]
    df = pd.DataFrame(data=rows, columns=['building_category', 'building_code', 'area'])

    area.validate(df)


def test_area_parameters_raises_schema_error_on_unknown_building_category():
    rows = [['CASTLE', 'TEK10', 10000]]
    df = pd.DataFrame(data=rows, columns=['building_category', 'building_code', 'area'])

    with pytest.raises(pa.errors.SchemaError):
        area.validate(df)


def test_area_parameters_raises_schema_error_on_illegal_area():
    rows = [[BuildingCategory.HOUSE, 'TEK10', -1]]
    df = pd.DataFrame(data=rows, columns=['building_category', 'building_code', 'area'])

    with pytest.raises(pa.errors.SchemaError):
        area.validate(df)


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

    result: pd.DataFrame = area_new_residential_buildings.validate(ok_construction_building_category_yearly)
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
    [b for b in [BuildingCategory.HOUSE, BuildingCategory.APARTMENT_BLOCK]],
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
        area_new_residential_buildings.validate(ok_construction_building_category_yearly)
    


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
    area_new_residential_buildings.validate(df1)

    df1.loc[last_row, building_category] = 1
    with pytest.raises(pa.errors.SchemaError):
        area_new_residential_buildings.validate(df1)


@pytest.fixture
def new_buildings_residential_df():
    return pd.DataFrame(
        data=[[2010, 0.6131112606550, 0.3868887393450, 175, 75], [2011, 0.6284545545246, 0.3715454454754, 175, 75]],
        columns=['year',
                 'new_house_share',
                 'new_apartment_block_share',
                 'floor_area_new_house',
                 'flood_area_new_apartment_block']
    )


def test_new_buildings_residential_ok(new_buildings_residential_df):
    new_buildings_residential.validate(new_buildings_residential_df)


@pytest.mark.parametrize('column, too_low, too_high',
                         [('year', 2009, 2071),
                          ('new_house_share', -0.01, 1.01),
                          ('new_apartment_block_share', -0.01, 1.01),
                          ('floor_area_new_house', 0, 1001),
                          ('flood_area_new_apartment_block', 0, 1001)])
def test_new_buildings_residential_value_ranges(new_buildings_residential_df, column, too_low, too_high):
    new_buildings_residential.validate(new_buildings_residential_df)

    new_buildings_residential_df.loc[0, column] = too_low
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_residential.validate(new_buildings_residential_df)

    new_buildings_residential_df.loc[0, column] = too_high
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_residential.validate(new_buildings_residential_df)


def test_new_buildings_residential_sum_of_share_should_be_1(new_buildings_residential_df):
    new_buildings_residential_df.loc[0, 'new_apartment_block_share'] = 1.0
    new_buildings_residential_df.loc[0, 'new_house_share'] = 1.0

    with pytest.raises(pa.errors.SchemaError):
        new_buildings_residential.validate(new_buildings_residential_df)


def test_population_coerce_values():
    rows = [(y, 4858199, 2) for y in YearRange(2010, 2070)]
    df = pd.DataFrame(data=rows,
                      columns=['year', 'population', 'household_size'])

    population_forecast.validate(df, lazy=True)


def test_population_ok(new_buildings_residential_df):
    standard_years = [(y, 4858199, 2.22) for y in YearRange(2001, 2070)]

    df = pd.DataFrame(data=[(2000, 4000000, np.nan, )] + standard_years,
                      columns=['year', 'population', 'household_size'])

    population_forecast.validate(df)

    household_df = df.copy()
    household_df.loc[0, 'household_size'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        population_forecast.validate(household_df)

    population_df = df.copy()
    population_df.loc[0, 'population'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        population_forecast.validate(population_df)



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
    s_curve.validate(s_curves)


def test_scurve_parameters_reject_invalid_building_category(s_curves):
    s_curves.loc[0, 'building_category'] = 'småhus'

    with pytest.raises(pa.errors.SchemaError):
        s_curve.validate(s_curves)


def test_scurve_parameters_reject_invalid_condition(s_curves):
    s_curves.loc[0, 'condition'] = 'INVALID'
    with pytest.raises(pa.errors.SchemaError):
        s_curve.validate(s_curves)


@pytest.mark.parametrize('attribute', ('earliest_age_for_measure',
                                       'average_age_for_measure',
                                       'rush_period_years',
                                       'last_age_for_measure'))
def test_scurve_parameters_reject_invalid_age(s_curves, attribute):
    s_curves.loc[0, attribute] = 0
    with pytest.raises(pa.errors.SchemaError):
        s_curve.validate(s_curves)


@pytest.mark.parametrize('attribute', ('rush_share', 'never_share'))
def test_scurve_parameters_reject_invalid_share(s_curves, attribute):
    s_curves.loc[0, attribute] = 0
    with pytest.raises(pa.errors.SchemaError):
        s_curve.validate(s_curves)
    s_curves.loc[0, attribute] = 1.01
    with pytest.raises(pa.errors.SchemaError):
        s_curve.validate(s_curves)


@pytest.fixture
def energy_by_floor_area_df():
    return pd.DataFrame(
        data=[['house', 'TEK69', 'lighting', 0.0],
              ['apartment_block', 'TEK69', 'lighting', 1.234]],
        columns=['building_category', 'building_code', 'purpose', 'kwh_m2'])


def test_energy_by_floor_area(energy_by_floor_area_df):
    energy_need_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_building_category(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[:, 'building_category'] = 'småhus'

    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_building_code(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[:, 'building_code'] = 'TAKK'

    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_illegal_kwhm(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[0, 'kwh_m2'] = -0.1

    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(energy_by_floor_area_df)


def test_energy_by_floor_area_raise_schema_error_on_unknown_purpose(energy_by_floor_area_df):
    energy_by_floor_area_df.loc[0, 'purpose'] = 'lys og varme'

    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(energy_by_floor_area_df)


@pytest.fixture
def original_condition_df():
    return pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'kwh_m2'],
                        data=[
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'electrical_equipment', 2.2],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'fans_and_pumps', 3.3],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'heating_dhw', 4.4],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'heating_rv', 5.5],
                            ['apartment_block', 'PRE_TEK49_RES_1950', 'lighting', 5.5],
                            ['default', 'default', 'default', 0]
                        ])


def test_energy_need_original_condition(original_condition_df):
    energy_need_original_condition.validate(original_condition_df)


def test_energy_need_original_condition_require_valid_building_cat(original_condition_df):
    original_condition_df.loc[0, 'building_category'] = 'not_a_building_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(original_condition_df)


def test_energy_need_original_condition_require_valid_building_code(original_condition_df):
    original_condition_df.loc[0, 'building_code'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(original_condition_df)


def test_energy_need_original_condition_require_valid_purpose(original_condition_df):
    original_condition_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(original_condition_df)


def test_energy_need_original_condition_require_value_greater_than_or_equal_to_zero(original_condition_df):
    original_condition_df.loc[0, 'kwh_m2'] = -1
    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(original_condition_df)


def test_energy_need_original_condition_require_unique_rows():
    duplicate_df = pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'kwh_m2'],
                                data=[
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 1.1],
                                    ['apartment_block', 'PRE_TEK49_RES_1950', 'cooling', 2.1],
                                ])
    with pytest.raises(pa.errors.SchemaError):
        energy_need_original_condition.validate(duplicate_df)


# TODO: add test for special case with conditions
@pytest.fixture
def reduction_per_condition_df():
    return pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share'],
                        data=[['house', 'default', 'heating_rv', 'original_condition', 0.1],
                              ['house', 'default', 'heating_rv', 'small_measure', 0.2],
                              ['house', 'default', 'heating_rv', 'renovation', 0.3],
                              ['house', 'default', 'heating_rv', 'renovation_and_small_measure', 0.4],
                              ['house', 'TEK21', 'heating_rv', 'original_condition', 0.5],
                              ['house', 'TEK21', 'heating_rv', 'small_measure', 0.6],
                              ['house', 'TEK21', 'heating_rv', 'renovation', 0.7],
                              ['house', 'TEK21', 'heating_rv', 'renovation_and_small_measure', 0.8]])


def test_energy_req_reduction_per_condition(reduction_per_condition_df):
    improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_building_cat(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_category'] = 'not_a_building_category'
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_building_cat(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('building_category')] = 'default'
    improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_building_code(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_code'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_building_code(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('building_code')] = 'default'
    improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_purpose(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_allows_default_purpose(reduction_per_condition_df):
    reduction_per_condition_df.iloc[0:4, reduction_per_condition_df.columns.get_loc('purpose')] = 'default'
    improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_valid_building_condition(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_condition'] = 'not_a_condition'
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_exisiting_building_condition(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'building_condition'] = 'demolition'
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_value_between_zero_and_one(reduction_per_condition_df):
    reduction_per_condition_df.loc[0, 'reduction_share'] = -1
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)

    reduction_per_condition_df.loc[0, 'reduction_share'] = 1.01
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(reduction_per_condition_df)


def test_energy_req_reduction_per_condition_require_unique_rows():
    duplicate_df = pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'building_condition',
                                         'reduction_share'],
                                data=[['house', 'default', 'heating_rv', 'original_condition', 0.1],
                                      ['house', 'default', 'heating_rv', 'original_condition', 0.2],
                                      ['house', 'default', 'heating_rv', 'original_condition', 0.2]
                                      ])
    with pytest.raises(pa.errors.SchemaError):
        improvement_building_upgrade.validate(duplicate_df)


def test_energy_req_reduction_per_condition_allow_missing_building_conditions(reduction_per_condition_df):
    reduction_per_condition_df.drop(index=0, inplace=True)
    improvement_building_upgrade.validate(reduction_per_condition_df)


@pytest.fixture
def yearly_improvements_df():
    return pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'value'],
                        data=[
                            ['default', 'default', 'cooling', 0.0],
                            ['default', 'default', 'electrical_equipment', 0.1],
                            ['default', 'default', 'fans_and_pumps', 0.0],
                            ['default', 'default', 'heating_dhw', 0.0],
                            ['default', 'default', 'lighting', 0.05],
                            ['house', 'TEK01', 'heating_rv', 0.0]
                        ])


def test_energy_need_yearly_improvements(yearly_improvements_df):
    energy_need_improvements.validate(yearly_improvements_df)


@pytest.mark.parametrize(('building_group', 'expected_category'), [
    ('residential', 'residential'),('non_residential', 'non_residential'), ('default', 'default')])
def test_energy_need_yearly_improvements_allow_building_groups(building_group, expected_category):
    df = pd.DataFrame(columns=['building_category', 'building_code', 'purpose', 'function', 'value'],
                 data=[
                     [building_group, 'default', 'cooling', 'yearly_improvements', 0.0],])

    result = energy_need_improvements.validate(df)
    assert (result.building_category == expected_category).all()


def test_energy_need_yearly_improvements_require_valid_building_cat(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'building_category'] = 'not_a_category'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements.validate(yearly_improvements_df)


def test_energy_need_yearly_improvements_require_valid_building_code(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'building_code'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements.validate(yearly_improvements_df)


def test_energy_need_yearly_improvements_require_valid_purpose(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements.validate(yearly_improvements_df)


def test_energy_need_yearly_improvements_value_between_zero_and_one(yearly_improvements_df):
    yearly_improvements_df.loc[0, 'value'] = -1
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements.validate(yearly_improvements_df)

    yearly_improvements_df.loc[0, 'value'] = 2
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements.validate(yearly_improvements_df)


def test_energy_need_yearly_improvements_require_unique_rows():
    duplicate_df = pd.DataFrame(
        columns='building_category,building_code,purpose,yearly_efficiency_improvement,start_year,function,end_year'.split(','),
        data=[['default', 'default', 'cooling', 0.0, 2020, 'yearly_reduction', 2050],
              ['default', 'default', 'cooling', 0.1, 2020, 'yearly_reduction', 2050],
              ['default', 'default', 'cooling', 0.0, 2020, 'yearly_reduction', 2050]])
    with pytest.raises(pa.errors.SchemaError):
        energy_need_improvements(duplicate_df)


@pytest.mark.skip
def test_energy_req_policy_improvements_require_valid_building_cat(policy_improvements_df):
    policy_improvements_df.loc[0, 'building_category'] = 'not_a_category'
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


@pytest.mark.skip
def test_energy_req_policy_improvements_require_valid_building_code(policy_improvements_df):
    policy_improvements_df.loc[0, 'building_code'] = 'TAKK'
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


@pytest.mark.skip
def test_energy_req_policy_improvements_require_valid_purpose(policy_improvements_df):
    policy_improvements_df.loc[0, 'purpose'] = 'not_a_purpose'
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


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


def test_heating_system_initial_shares_ok():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,year,heating_system_share
apartment_block,TEK17,DH,2023,0.2067590404511288
apartment_block,TEK17,DH - Bio,2023,0.0033946606308616
apartment_block,TEK17,Electric boiler,2023,0.0340346740470787
apartment_block,TEK17,Electric boiler - Solar,2023,0.0003390668680222
apartment_block,TEK17,Electricity,2023,0.4560101624930742
apartment_block,TEK17,Electricity - Bio,2023,0.1128016818166627
apartment_block,TEK17,Gas,2023,0.0205424237443141
apartment_block,TEK17,HP - Electricity,2023,0.0073046316982173
apartment_block,TEK17,HP Central heating - Bio,2023,0.0086647944512573
apartment_block,TEK17,HP Central heating - Electric boiler,2023,0.1487089355849942
apartment_block,TEK17,HP Central heating - Gas,2023,0.0014399282143885
university,TEK97,DH,2023,0.3182453573763764
university,TEK97,DH - Bio,2023,0.0002142250969049
university,TEK97,Electric boiler,2023,0.1177376992297113
university,TEK97,Electric boiler - Solar,2023,0.0002493794096936
university,TEK97,Electricity,2023,0.1413637792376423
university,TEK97,Electricity - Bio,2023,0.0216740945571909
university,TEK97,Gas,2023,0.0331300895188176
university,TEK97,HP - Electricity,2023,0.0030762755043380
university,TEK97,HP Central heating - Bio,2023,0.0001936265574100
university,TEK97,HP Central heating - Electric boiler,2023,0.3640435119049470
university,TEK97,HP Central heating - Gas,2023,0.0000719616069676                                                                                                                                             
""".strip()), skipinitialspace=True) 
    
    heating_system_initial_shares.validate(shares_start_year)


def test_heating_systems_shares_require_same_start_year():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,year,heating_system_share
apartment_block,TEK07,DH,2020,0.3316670026630616
apartment_block,TEK07,DH - Bio,2021,0.003305887353335002                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_system_initial_shares.validate(shares_start_year)


def test_heating_systems_shares_between_zero_and_one():
    shares_start_year = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,year,heating_system_share
apartment_block,TEK07,DH,2020,-1                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_system_initial_shares.validate(shares_start_year)

    shares_start_year = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,year,heating_system_share
apartment_block,TEK07,DH,2020,2                                               
""".strip()), skipinitialspace=True) 
    
    with pytest.raises(pa.errors.SchemaError):
        heating_system_initial_shares.validate(shares_start_year)


def test_heating_system_initial_shares_sum_shares_equal_1():

    df = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,year,heating_system_share
apartment_block,TEK17,DH,2023,0.5
apartment_block,TEK17,DH - Bio,2023,0.5
university,TEK97,Electricity,2023,0.5
university,TEK97,Electricity - Bio,2023,0.4                                                                                                                         
""".strip()), skipinitialspace=True) 
    
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        validated_df = heating_system_initial_shares.validate(df, lazy=True)
        expected_in_error="<Check check_sum_of_heating_system_shares_equal_1:"
        for warning in caught_warnings:
            assert expected_in_error in str(warning.message)

        assert caught_warnings


def test_heating_system_forecast_ok():
    projection = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,new_heating_systems,2024,2025
apartment_block,default,Electricity - Bio,HP Central heating - Bio,0.1,0.1
default,default,Gas,Electric boiler,0.1,0.2
default,default,Gas,HP Central heating - Electric boiler,0.1,0.2
house,default,Electricity - Bio,HP - Bio - Electricity,0.1,0.1
kindergarten,TEK87,Electricity,DH,0.1,0.1
kindergarten,TEK97,Electricity,DH,0.1,0.1
non_residential,TEK69,HP Central heating - Gas,HP Central heating - Electric boiler,0.2,0.3
office,TEK87,Electricity,DH,0.1,0.1
office,TEK97,Electricity,DH,0.1,0.1
residential,default,HP - Electricity,HP - Bio - Electricity,0.1,0.1                                                                                                                                                                                                                                                                             
""".strip()), skipinitialspace=True) 

    heating_system_forecast.validate(projection)


def test_heating_system_forecast_unique_columns():
    projection = pd.read_csv(io.StringIO("""
building_category,building_code,heating_systems,new_heating_systems,2021,2022
default,default,Gas,Electric boiler,0.05,0.06
default,default,Gas,Electric boiler,0.05,0.05
""".strip()), skipinitialspace=True) 

    with pytest.raises(pa.errors.SchemaError):
        heating_system_forecast.validate(projection)


def test_heating_systems_efficiencies_ok():
    efficiencies = pd.read_csv(io.StringIO("""
heating_systems,Grunnlast,Spisslast,Ekstralast,base_load_energy_product,peak_load_energy_product,tertiary_load_energy_product,tertiary_load_coverage,base_load_coverage,peak_load_coverage,base_load_efficiency,peak_load_efficiency,tertiary_load_efficiency,Tappevann,domestic_hot_water_energy_product,domestic_hot_water_efficiency,Spesifikt elforbruk,cooling_efficiency
Electric boiler,Electric boiler,Ingen,Ingen,Electricity,Ingen,Ingen,0.0,1.0,0.0,0.98,1.0,1,Electric boiler,Electricity,0.98,1,4
DH,DH,Ingen,Ingen,DH,Ingen,Ingen,0.0,1.0,0.0,0.99,1.0,1,DH,DH,0.99,1,4
Electricity,Electricity,Ingen,Ingen,Electricity,Ingen,Ingen,0.0,1.0,0.0,1.0,1.0,1,Electricity,Electricity,0.98,1,4
Gas,Gas,Ingen,Ingen,Fossil,Ingen,Ingen,0.0,1.0,0.0,0.96,0.96,1,Gas,Fossil,0.96,1,4
Electricity - Bio,Electricity,Bio,Ingen,Electricity,Bio,Ingen,0.0,0.7,0.3,1.0,0.65,1,Electricity,Electricity,0.98,1,4
DH - Bio,DH,Bio,Ingen,DH,Bio,Ingen,0.0,0.95,0.050000000000000044,0.99,0.65,1,DH,DH,0.99,1,4
HP - Bio - Electricity,HP,Bio,Electricity,Electricity,Bio,Electricity,0.4,0.5,0.1,2.5,0.65,1,Electricity,Electricity,0.98,1,4
HP - Electricity,HP,Electricity,Ingen,Electricity,Electricity,Ingen,0.0,0.5,0.5,2.5,1.0,1,Electricity,Electricity,0.98,1,4
HP Central heating - Electric boiler,HP Central heating,Electric boiler,Ingen,Electricity,Electricity,Ingen,0.0,0.85,0.15000000000000002,3.0,0.99,1,HP Central heating,Electricity,3.0,1,4
HP Central heating - Gas,HP Central heating,Gas,Ingen,Electricity,Fossil,Ingen,0.0,0.85,0.15000000000000002,3.0,0.96,1,HP Central heating,Electricity,3.0,1,4
Electric boiler - Solar,Electric boiler,Solar,Ingen,Electricity,Solar,Ingen,0.0,0.85,0.15000000000000002,0.98,0.7,1,Electric boiler,Electricity,0.98,1,4
HP Central heating - Bio,HP Central heating,Bio,Ingen,Electricity,Bio,Ingen,0.0,0.85,0.15000000000000002,3.0,0.65,1,HP Central heating,Electricity,3.0,1,4
""".strip()), skipinitialspace=True) 
    
    heating_system_efficiencies.validate(efficiencies)

def test_behaviour_factor_validate_and_parse():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,default,1.0,,,,
house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.85,,,,
house,default,lighting,0.85,,,,
non_residential,default,default,1.15,,,,
retail,default,electrical_equipment,2.0,,,,""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category=="house" and purpose=="lighting"')
    assert (house_lighting['behaviour_factor'] == 0.85).all()

    old_house = res.query('building_category=="house" and building_code in ["PRE_TEK49","TEK69","TEK87","TEK49","TEK97"]')
    assert (old_house['behaviour_factor'] == 0.85).all()

    new_house = res.query('building_category=="house" and building_code in ["TEK07","TEK10","TEK17"] and purpose!="lighting"')
    assert (new_house['behaviour_factor'] == 1.0).all()

    retail_electrical_equipment = res.query('building_category=="retail" and purpose=="electrical_equipment"')
    assert (retail_electrical_equipment['behaviour_factor'] == 2.0).all()

    non_residential_non_electrical_equipment = res.query(
        'building_category not in ["house", "apartment_block"] and purpose!="electrical_equipment"')
    assert (non_residential_non_electrical_equipment['behaviour_factor'] == 1.15).all()


def test_behaviour_factor_validate_and_parse_add_year():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,default,2.4,2024,noop,2042,
non_residential,default,default,4.2,2024,noop,2042,""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category in ["house", "apartment_block"] and 2024 <= year <=2042')
    assert (house_lighting.behaviour_factor == 2.4).all()

    non_residential = res.query('building_category not in ["house", "apartment_block"] and 2024 <= year <=2042')
    assert (non_residential.behaviour_factor == 4.2).all()

    outside_range = res.query('year < 2024 and year < 2042')
    assert (outside_range.behaviour_factor == 1.0).all()


def test_behaviour_factor_validate_and_parse_with_empty_start_year_or_end_year():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,default,2.4,2021,noop,,
non_residential,default,default,4.2,,noop,2049,
non_residential,default,default,0.99,2050,noop,2050,
residential,default,default,0.98,2020,noop,2020
""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    residential_after_2021 = res.query('building_category in ["house", "apartment_block"] and year >= 2021')
    assert (residential_after_2021.behaviour_factor == 2.4).all()

    non_residential_before_2050 = res.query('building_category not in ["house", "apartment_block"] and year <= 2049')
    assert (non_residential_before_2050.behaviour_factor == 4.2).all()

    residential_in_2020 = res.query('building_category in ["house", "apartment_block"] and year==2020')
    assert (residential_in_2020.behaviour_factor == 0.98).all()

    non_residential_in_2050 = res.query('building_category not in ["house", "apartment_block"] and year==2050')
    assert (non_residential_in_2050.behaviour_factor == 0.99).all()


def test_behaviour_factor_validate_and_parse_missing_years():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor
residential,default,default,2.4
non_residential,default,default,4.2""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category in ["house", "apartment_block"]')
    assert (house_lighting.behaviour_factor == 2.4).all()

    non_residential = res.query('building_category not in ["house", "apartment_block"]')
    assert (non_residential.behaviour_factor == 4.2).all()


def test_behaviour_factor_validate_and_parse_calculate_yearly_reduction():
        df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,lighting,1.0,2031,yearly_reduction,2050,0.02
""".strip()))

        res = energy_need_behaviour_factor.validate(df)

        house_lighting = res.query('building_category=="house" and building_code=="TEK07" and purpose=="lighting"').set_index([
            'year'
        ])

        expected = pd.Series([1.0] * 11 +
                             [1.0, 0.98, 0.9603999999999999, 0.9411919999999999, 0.9223681599999999, 0.9039207967999999,
                              0.8858423808639999, 0.8681255332467199, 0.8507630225817855, 0.8337477621301498,
                              0.8170728068875467, 0.8007313507497958, 0.7847167237347998, 0.7690223892601038,
                              0.7536419414749017, 0.7385691026454038, 0.7237977205924956, 0.7093217661806457,
                              0.6951353308570327, 0.6812326242398921],
                             index=YearRange(2020, 2050).to_index(), name='behaviour_factor')


        pd.testing.assert_series_equal(house_lighting.behaviour_factor, expected)


def test_behaviour_factor_validate_and_parse_calculate_interpolate():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,lighting,1.0,2041,improvement_at_end_year,2050,2.0
retail,TEK17,electrical_equipment,1.0,2020,improvement_at_end_year,2050,0.5
""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category=="house" and building_code=="TEK07" and purpose=="lighting"').set_index(
        ['year'])

    expected = pd.Series(
        [1.0] * 21 + [1.0, 1.1111111111111112, 1.2222222222222223, 1.3333333333333333, 1.4444444444444444,
                      1.5555555555555556, 1.6666666666666665, 1.7777777777777777, 1.8888888888888888, 2.0],
        index=YearRange(2020, 2050).to_index(), name='behaviour_factor')

    pd.testing.assert_series_equal(house_lighting.behaviour_factor, expected)

    retail_electrical = res.query(
        'building_category=="retail" and building_code=="TEK17" and purpose=="electrical_equipment"').set_index(['year'])

    expected = pd.Series(
        [1., 0.98333333, 0.96666667, 0.95, 0.93333333, 0.91666667, 0.9, 0.88333333, 0.86666667, 0.85, 0.83333333,
         0.81666667, 0.8, 0.78333333, 0.76666667, 0.75, 0.73333333, 0.71666667, 0.7, 0.68333333, 0.66666667, 0.65,
         0.63333333, 0.61666667, 0.6, 0.58333333, 0.56666667, 0.55, 0.53333333, 0.51666667, 0.5],
        index=YearRange(2020, 2050).to_index(), name='behaviour_factor')

    pd.testing.assert_series_equal(retail_electrical.behaviour_factor, expected)


def test_behaviour_factor_set_default_start_year_and_end_year():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year
residential,default,default,1.0,2020,noop,2050
house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.85,,noop,
house,TEK07+TEK10+TEK17,lighting,0.85,2020,noop,2050
non_residential,default,default,1.15,,,
retail,default,electrical_equipment,2.0,,,
""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_heating_rv = res.query('building_category=="house" and building_code=="PRE_TEK49" and purpose=="heating_rv"').set_index(
        ['year']
    )

    expected = pd.Series([0.85]*31, index=YearRange(2020, 2050).to_index(), name='behaviour_factor')

    pd.testing.assert_series_equal(house_heating_rv.behaviour_factor, expected)


def test_behaviour_factor_with_start_year_and_end_year():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,default,1.0,2020,,2050,
house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.85,2020,noop,2050,0.02
house,default,lighting,0.85,2020,,2050,
non_residential,default,default,1.15,2020,,2050,
retail,default,electrical_equipment,2.0,2020,,2050,
""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_heating_rv = res.query('building_category=="house" and building_code=="PRE_TEK49" and purpose=="heating_rv"').set_index(
        ['year']
    )

    expected = pd.Series([0.85]*31, index=YearRange(2020, 2050).to_index(), name='behaviour_factor')

    pd.testing.assert_series_equal(house_heating_rv.behaviour_factor, expected)



def test_behaviour_factor_with_improvement_at_end_year_and_yearly_reduction():
    df = pd.read_csv(io.StringIO("""
building_category,building_code,purpose,behaviour_factor,start_year,function,end_year,parameter
default,default,electrical_equipment,1.0, 2020, yearly_reduction,2050,0.01
house,TEK49,lighting,1.0,2020,improvement_at_end_year,2030,0.5556
house,TEK49,lighting,0.5556,2031,yearly_reduction,2050,0.005
""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category=="house" and building_code=="TEK49" and purpose=="lighting"').set_index(
        ['year']
    )

    expected_policy_improvement = [
        1., 0.95556, 0.91112, 0.86668, 0.82224, 0.7778,
        0.73336, 0.68892, 0.64448, 0.60004, 0.5556]

    expected_yearly_reduction = [
        0.5556, 0.552822, 0.55005789, 0.5473076005499999, 0.54457106254725,
        0.5418482072345138, 0.5391389661983411, 0.5364432713673494, 0.5337610550105127, 0.5310922497354601,
        0.5284367884867829, 0.5257946045443489, 0.5231656315216271, 0.520549803364019, 0.5179470543471989,
        0.5153573190754629, 0.5127805324800856, 0.5102166298176851, 0.5076655466685968, 0.5051272189352537]

    expected = pd.Series(expected_policy_improvement + expected_yearly_reduction,
        index=YearRange(2020, 2050).to_index(), name='behaviour_factor')

    assert len(house_lighting) == 31, f'Got years: {house_lighting.values}'
    pd.testing.assert_series_equal(house_lighting.behaviour_factor, expected)


if __name__ == "__main__":
    pytest.main()
