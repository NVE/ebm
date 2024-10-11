import itertools

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
                            new_buildings_population,
                            scurve_parameters,
                            energy_requirement_original_condition,
                            energy_requirement_reduction_per_condition,
                            energy_requirement_yearly_improvements,
                            energy_requirement_policy_improvements)


@pytest.fixture
def ok_tek_parameters() -> pd.DataFrame:
    return pd.DataFrame({
        'TEK': ['PRE_TEK49_1940', 'TEK69_COM', 'TEK07'],
        'building_year': [1940, 1978, 1990],
        'period_start_year': [0, 1971, 2014],
        'period_end_year': [1955, 1990, 2024]
    })


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
    [b for b in BuildingCategory], [0, 1, 2, 3]))
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


def test_new_buildings_population_ok(new_buildings_house_share_df):
    df = pd.DataFrame(data=[(y, 4858199, 2.22) for y in YearRange(2010, 2070)],
                      columns=['year', 'population', 'household_size'])

    new_buildings_population.validate(df)

    household_df = df.copy()
    household_df.loc[0, 'household_size'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_population.validate(household_df)

    population_df = df.copy()
    population_df.loc[0, 'population'] = -1.0
    with pytest.raises(pa.errors.SchemaError):
        new_buildings_population.validate(population_df)


def test_new_buildings_population_coerce_values(new_buildings_house_share_df):
    df = pd.DataFrame(data=[(float(y), 4858199.0, 2) for y in YearRange(2010, 2070)],
                      columns=['year', 'population', 'household_size'])

    new_buildings_population.validate(df)


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
def heating_reduction_df():
    return pd.DataFrame(columns=['building_category','TEK', 'purpose', 'building_condition', 'reduction_share'],
                        data=[['house','default', 'heating_rv','original_condition', 0.1],
                              ['house', 'default', 'heating_rv', 'small_measure', 0.2],
                              ['house', 'default', 'heating_rv', 'renovation', 0.3],
                              ['house', 'default', 'heating_rv', 'renovation_and_small_measure', 0.4],
                              ['house', 'TEK21', 'heating_rv', 'original_condition', 0.5],
                              ['house', 'TEK21', 'heating_rv', 'small_measure', 0.6],
                              ['house', 'TEK21', 'heating_rv', 'renovation', 0.7],
                              ['house', 'TEK21', 'heating_rv', 'renovation_and_small_measure', 0.8]])


def test_heating_reduction(heating_reduction_df):
    energy_requirement_reduction_per_condition.validate(heating_reduction_df)


def test_heating_reduction_require_tek(heating_reduction_df):
    heating_reduction_df.loc[0, 'TEK'] = 'TAKK'

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(heating_reduction_df)


def test_heating_reduction_allows_default_tek(heating_reduction_df):
    heating_reduction_df.loc[0, 'TEK'] = 'default'
    energy_requirement_reduction_per_condition.validate(heating_reduction_df)


def test_heating_reduction_require_building_condition(heating_reduction_df):
    heating_reduction_df.loc[0, 'building_condition'] = 'riving'

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(heating_reduction_df)


def test_heating_reduction_value_between_zero_and_one(heating_reduction_df):
    heating_reduction_df.loc[0, 'reduction_share'] = -1

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(heating_reduction_df)

    heating_reduction_df.loc[0, 'reduction_share'] = 1.01

    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_reduction_per_condition.validate(heating_reduction_df)


#TODO: add more test for energy requirement input data 
@pytest.fixture
def energy_req_policy_improv_df() -> pd.DataFrame:
    df = pd.DataFrame(
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year', 'improvement_at_period_end'],
        data=[['default', 'default', 'lighting', 2018, 2030, 0.6]])
    return df

def test_energy_req_policy_improv_ok(energy_req_policy_improv_df: pd.DataFrame):
    energy_requirement_policy_improvements.validate(energy_req_policy_improv_df)

def test_energy_req_policy_improv_wrong_year_range(energy_req_policy_improv_df: pd.DataFrame):
    energy_req_policy_improv_df['period_start_year'] = 2050
    energy_req_policy_improv_df['period_end_year'] = 2010
    
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(energy_req_policy_improv_df)

@pytest.mark.parametrize('start_year', [-1, ""])
def test_energy_req_policy_improv_wrong_start_year(energy_req_policy_improv_df: pd.DataFrame, start_year):
    energy_req_policy_improv_df['period_start_year'] = start_year
    
    with pytest.raises(pa.errors.SchemaError):
        energy_requirement_policy_improvements.validate(energy_req_policy_improv_df)
