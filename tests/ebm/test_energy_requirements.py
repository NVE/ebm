import io

import pandas as pd
import pytest

from ebm.model import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import (
    calculate_energy_requirement_reduction_by_condition,
    calculate_proportional_energy_change_based_on_end_year,
    calculate_energy_requirement_reduction,
    calculate_lighting_reduction, EnergyRequirementFilter)


def test_calculate_energy_requirement_reduction_by_condition():
    test_data = io.StringIO("""building_category,TEK,purpose, kwh_m2
                               apartment_block,PRE_TEK49,HeatingRV, 100
                               apartment_block,TEK07,HeatingRV,200
                               house,TEK07,HeatingRV,400""")
    energy_requirements = pd.read_csv(test_data, skipinitialspace=True)
    condition_reduction = pd.DataFrame(data=[[BuildingCondition.ORIGINAL_CONDITION, 0],
                                             [BuildingCondition.SMALL_MEASURE, 0.2],
                                             [BuildingCondition.RENOVATION, 0.4],
                                             [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.8]],
                                       columns=['building_condition', 'reduction'])

    df = calculate_energy_requirement_reduction_by_condition(energy_requirements, condition_reduction)

    pre_tek49 = df[(df.building_category == 'apartment_block') &
                   (df.TEK == 'PRE_TEK49') &
                   (df.purpose == 'HeatingRV')]

    expected_pre_tek49 = pd.Series([100.0], name='kwh_m2')
    pd.testing.assert_series_equal(pre_tek49[pre_tek49.building_condition == 'original_condition'].kwh_m2,
                                   expected_pre_tek49)

    pd.testing.assert_series_equal(
        pre_tek49.kwh_m2,
        pd.Series([100.0, 80.0, 60.0, 20.0], name='kwh_m2'),
        check_index=False)


def test_calculate_proportional_energy_change_based_on_end_year():
    kwh_m2 = pd.Series(data=[100.0]*8, index=YearRange(2010, 2017), name='kwh_m2')

    result = calculate_proportional_energy_change_based_on_end_year(
        energy_requirements=kwh_m2,
        requirement_at_period_end=25.0,
        period=YearRange(2011, 2014)
    )

    expected = pd.Series(data=[100.0, 100.0, 75.0, 50.0, 25.0, 25.0, 25.0, 25.0],
                         index=YearRange(2010, 2017),
                         name='kwh_m2')

    pd.testing.assert_series_equal(result, expected)


def test_calculate_proportional_energy_change_based_on_end_year_with_no_requirement_at_period_end():
    kwh_m2 = pd.Series(data=[100.0]*8, index=YearRange(2010, 2017), name='kwh_m2')

    result = calculate_proportional_energy_change_based_on_end_year(
        energy_requirements=kwh_m2,
        requirement_at_period_end=None,
        period=YearRange(2010, 2017)
    )

    expected = pd.Series(data=[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                         index=YearRange(2010, 2017),
                         name='kwh_m2')

    pd.testing.assert_series_equal(result, expected)


def test_calculate_proportional_energy_change_based_on_end_year_raise_value_error_when_period_is_missing_from_index():

    kwh_m2 = pd.Series(data=[20]*8, index=YearRange(2001, 2008), name='kwh_m2')

    with pytest.raises(ValueError, match='Did not find all years from 2011 - 2014 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kwh_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2011, 2014))

    with pytest.raises(ValueError, match='Did not find all years from 2000 - 2008 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kwh_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2000, 2008))

    with pytest.raises(ValueError, match='Did not find all years from 2001 - 2009 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kwh_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2001, 2009))


def test_calculate_energy_requirement_reduction():
    kwh_m2 = pd.Series(data=[100.0] * 8, index=YearRange(2010, 2017), name='kwh_m2')

    result = calculate_energy_requirement_reduction(
        energy_requirements=kwh_m2,
        yearly_reduction=0.1,
        reduction_period=YearRange(2011, 2016)
    )
    expected = pd.Series(data=[100.0, 90.0, 81.0, 72.9, 65.61, 59.049, 53.144100000000016, 100.00],
                         index=YearRange(2010, 2017),
                         name='kwh_m2')
    pd.testing.assert_series_equal(result, expected)


def test_calculate_energy_requirement_reduction_raise_value_error_when_period_is_missing_from_index():
    kwh_m2 = pd.Series(data=[20]*8, index=YearRange(2001, 2008), name='kwh_m2')

    with pytest.raises(ValueError, match='Did not find all years from 2011 - 2014 in energy_requirements'):
        calculate_energy_requirement_reduction(
            energy_requirements=kwh_m2,
            yearly_reduction=0.25,
            reduction_period=YearRange(2011, 2014))


def test_calculate_lighting_reduction():
    bema_years = YearRange(2010, 2050)
    normal_energy_requirement = 9.1075556
    sixty_percent_reduction_by_2030 = normal_energy_requirement * 0.4
    energy_requirement = pd.Series(data=[normal_energy_requirement] * len(bema_years),
                                   index=bema_years,
                                   name='kwh_m2')

    lighting = calculate_lighting_reduction(energy_requirement,
                                            yearly_reduction=0.005,
                                            end_year_energy_requirement=sixty_percent_reduction_by_2030,
                                            interpolated_reduction_period=YearRange(2018, 2030),
                                            year_range=bema_years)

    assert round(lighting.loc[2010], 5) == 9.10756
    assert round(lighting.loc[2018], 5) == 9.10756
    assert round(lighting.loc[2019], 5) == 8.65218
    assert round(lighting.loc[2030], 5) == 3.64302
    assert round(lighting.loc[2031], 5) == 3.62481
    assert round(lighting.loc[2036], 5) == 3.53509
    assert round(lighting.loc[2050], 5) == 3.29552


@pytest.fixture
def energy_requirement_original_condition():
    return pd.read_csv(io.StringIO("""
building_category,TEK,purpose,kwh_m2
apartment_block,PRE_TEK49_RES_1950,cooling,1.1
apartment_block,PRE_TEK49_RES_1950,electrical_equipment,2.2
apartment_block,PRE_TEK49_RES_1950,fans_and_pumps,3.3
apartment_block,PRE_TEK49_RES_1950,heating_dhw,4.4
apartment_block,PRE_TEK49_RES_1950,heating_rv,5.5
apartment_block,PRE_TEK49_RES_1950,lighting,5.5
apartment_block,TEK07,cooling,2.1
apartment_block,TEK07,electrical_equipment,2.2
apartment_block,TEK07,default,7.0""".strip()))


def test_energy_requirement_filter_return_empty_defaults(energy_requirement_original_condition):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         energy_requirement_original_condition,
                                         None,
                                         None,
                                         None)

    assert e_r_filter.get_yearly_improvements(tek='default', purpose='default') == 0.0
    assert e_r_filter.get_policy_improvement(tek='default', purpose='default') == (YearRange(2010, 2050), None)
    assert e_r_filter.get_reduction_per_condition(purpose='default', building_condition='default') == 0.0


def test_energy_requirement_filter_returns_correct_bema_defaults(energy_requirement_original_condition):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         energy_requirement_original_condition,
                                         None,
                                         None,
                                         None)

    assert e_r_filter.get_yearly_improvements(tek='default', purpose='electrical_equipment') == 0.01
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='lighting') == 0.005
    assert e_r_filter.get_policy_improvement(tek='default', purpose='lighting') == (YearRange(2018, 2030), 0.6)
    assert e_r_filter.get_reduction_per_condition(purpose='default', building_condition='default') == 0.0


def test_energy_requirement_returns_original_condition_from_dataframe():
    oc_dataframe = pd.read_csv(io.StringIO("""
building_category,TEK,purpose,kwh_m2
apartment_block,PRE_TEK49_RES_1950,cooling,1.1
apartment_block,PRE_TEK49_RES_1950,electrical_equipment,2.2
apartment_block,PRE_TEK49_RES_1950,fans_and_pumps,3.3
apartment_block,PRE_TEK49_RES_1950,heating_dhw,4.4
apartment_block,PRE_TEK49_RES_1950,heating_rv,5.5
apartment_block,PRE_TEK49_RES_1950,lighting,5.5
apartment_block,TEK07,cooling,2.1
apartment_block,TEK07,electrical_equipment,2.2
apartment_block,TEK07,default,7.0""".strip()))
    e_r_filter = EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                         energy_requirement_original_condition=oc_dataframe,
                                         energy_requirement_reduction_per_condition=None,
                                         energy_requirement_yearly_improvements=None,
                                         energy_requirement_policy_improvement=None)
    assert e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose='cooling') == 1.1
    assert e_r_filter.get_original_condition(tek='TEK07', purpose='electrical_equipment') == 2.2
