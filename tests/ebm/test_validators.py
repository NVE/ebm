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
                            energy_need_behaviour_factor)
    
    
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
    rows = [[str(building_category), 'TEK10', float(10000)] for building_category in BuildingCategory]
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


def test_population_coerce_values():
    rows = [(y, 4858199, 2) for y in YearRange(2010, 2070)]
    df = pd.DataFrame(data=rows,
                      columns=['year', 'population', 'household_size'])

    population.validate(df, lazy=True)


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


def test_heating_systems_shares_start_year_sum_shares_equal_1():

    df = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,year,TEK_shares
apartment_block,TEK17,DH,2023,0.5
apartment_block,TEK17,DH - Bio,2023,0.5
university,TEK97,Electricity,2023,0.5
university,TEK97,Electricity - Bio,2023,0.4                                                                                                                         
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
building_category,TEK,heating_systems,new_heating_systems,2024,2025
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

    heating_systems_projection.validate(projection)


def test_heating_systems_projection_unique_columns():
    projection = pd.read_csv(io.StringIO("""
building_category,TEK,heating_systems,new_heating_systems,2021,2022
default,default,Gas,Electric boiler,0.05,0.06
default,default,Gas,Electric boiler,0.05,0.05
""".strip()), skipinitialspace=True) 

    with pytest.raises(pa.errors.SchemaError):
        heating_systems_projection.validate(projection)


def test_heating_systems_efficiencies_ok():
    efficiencies = pd.read_csv(io.StringIO("""
heating_systems,Grunnlast,Spisslast,Ekstralast,Grunnlast energivare,Spisslast energivare,Ekstralast energivare,Ekstralast andel,Grunnlast andel,Spisslast andel,Grunnlast virkningsgrad,Spisslast virkningsgrad,Ekstralast virkningsgrad,Tappevann,Tappevann energivare,Tappevann virkningsgrad,Spesifikt elforbruk,Kjoling virkningsgrad
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
    
    heating_systems_efficiencies.validate(efficiencies)

def test_behaviour_factor_validate_and_parse():
    df = pd.read_csv(io.StringIO("""
building_category,TEK,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,default,1.0,,,,
house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.85,,,,
house,default,lighting,0.85,,,,
non_residential,default,default,1.15,,,,
retail,default,electrical_equipment,2.0,,,,""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category=="house" and purpose=="lighting"')
    assert (house_lighting['behaviour_factor'] == 0.85).all()

    old_house = res.query('building_category=="house" and TEK in ["PRE_TEK49","TEK69","TEK87","TEK49","TEK97"]')
    assert (old_house['behaviour_factor'] == 0.85).all()

    new_house = res.query('building_category=="house" and TEK in ["TEK07","TEK10","TEK17"] and purpose!="lighting"')
    assert (new_house['behaviour_factor'] == 1.0).all()

    retail_electrical_equipment = res.query('building_category=="retail" and purpose=="electrical_equipment"')
    assert (retail_electrical_equipment['behaviour_factor'] == 2.0).all()

    non_residential_non_electrical_equipment = res.query(
        'building_category not in ["house", "apartment_block"] and purpose!="electrical_equipment"')
    assert (non_residential_non_electrical_equipment['behaviour_factor'] == 1.15).all()


def test_behaviour_factor_validate_and_parse_add_year():
    df = pd.read_csv(io.StringIO("""
building_category,TEK,purpose,behaviour_factor,start_year,function,end_year,parameter
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
building_category,TEK,purpose,behaviour_factor,start_year,function,end_year,parameter
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
building_category,TEK,purpose,behaviour_factor
residential,default,default,2.4
non_residential,default,default,4.2""".strip()))

    res = energy_need_behaviour_factor.validate(df)

    house_lighting = res.query('building_category in ["house", "apartment_block"]')
    assert (house_lighting.behaviour_factor == 2.4).all()

    non_residential = res.query('building_category not in ["house", "apartment_block"]')
    assert (non_residential.behaviour_factor == 4.2).all()


def test_behaviour_factor_validate_and_parse_calculate_yearly_reduction():
        df = pd.read_csv(io.StringIO("""
building_category,TEK,purpose,behaviour_factor,start_year,function,end_year,parameter
residential,default,lighting,1.0,2031,yearly_reduction,2050,0.02""".strip()))

        res = energy_need_behaviour_factor.validate(df)

        house_lighting = res.query('building_category=="house" and TEK=="TEK07" and purpose=="lighting"').set_index([
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


if __name__ == "__main__":
    pytest.main()
