import io

import pandas as pd
import pytest

from ebm.energy_requirements import (
    calculate_energy_requirement_reduction_by_condition,
    calculate_proportional_energy_change_based_on_end_year,
    calculate_energy_requirement_reduction)
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange


def test_calculate_energy_requirement_reduction_by_condition():
    test_data = io.StringIO("""building_category,TEK,purpose,kw_h_m
apartment_block,PRE_TEK49,HeatingRV, 100
apartment_block,TEK07,HeatingRV,200
house,TEK07,HeatingRV,400""")
    energy_requirements = pd.read_csv(test_data)
    condition_reduction = pd.DataFrame(data=[[BuildingCondition.ORIGINAL_CONDITION, 0],
                                             [BuildingCondition.SMALL_MEASURE, 0.2],
                                             [BuildingCondition.RENOVATION, 0.4],
                                             [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.8]],
                                       columns=['building_condition', 'reduction'])

    df = calculate_energy_requirement_reduction_by_condition(energy_requirements, condition_reduction)

    pre_tek49 = df[(df.building_category == 'apartment_block') &
                   (df.TEK == 'PRE_TEK49') &
                   (df.purpose == 'HeatingRV')]

    expected_pre_tek49 = pd.Series([100.0], name='kw_h_m')
    pd.testing.assert_series_equal(pre_tek49[pre_tek49.building_condition == 'original_condition'].kw_h_m,
                                   expected_pre_tek49)

    pd.testing.assert_series_equal(
        pre_tek49.kw_h_m,
        pd.Series([100.0, 80.0, 60.0, 20.0], name='kw_h_m'),
        check_index=False)


def test_calculate_proportional_energy_change_based_on_end_year():
    kw_h_m2 = pd.Series(data=[100.0]*8, index=YearRange(2010, 2017), name='kw_h_m2')

    result = calculate_proportional_energy_change_based_on_end_year(
        energy_requirements=kw_h_m2,
        requirement_at_period_end=25.0,
        period=YearRange(2011, 2014)
    )

    expected = pd.Series(data=[100.0, 100.0, 75.0, 50.0, 25.0, 25.0, 25.0, 25.0],
                         index=YearRange(2010, 2017),
                         name='kw_h_m2')

    pd.testing.assert_series_equal(result, expected)


def test_calculate_proportional_energy_change_based_on_end_year_raise_value_error_when_period_is_missing_from_index():

    kw_h_m2 = pd.Series(data=[20]*8, index=YearRange(2001, 2008), name='kw_h_m2')

    with pytest.raises(ValueError, match='Did not find all years from 2011 - 2014 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kw_h_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2011, 2014))

    with pytest.raises(ValueError, match='Did not find all years from 2000 - 2008 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kw_h_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2000, 2008))

    with pytest.raises(ValueError, match='Did not find all years from 2001 - 2009 in energy_requirements'):
        calculate_proportional_energy_change_based_on_end_year(
            energy_requirements=kw_h_m2,
            requirement_at_period_end=25.0,
            period=YearRange(2001, 2009))


def test_calculate_energy_requirement_reduction():
    kw_h_m2 = pd.Series(data=[100.0] * 8, index=YearRange(2010, 2017), name='kw_h_m2')

    result = calculate_energy_requirement_reduction(
        energy_requirements=kw_h_m2,
        yearly_reduction=0.1,
        reduction_period=YearRange(2011, 2016)
    )
    expected = pd.Series(data=[100.0, 90.0, 81.0, 72.9, 65.61, 59.049, 53.144100000000016, 100.00],
                         index=YearRange(2010, 2017),
                         name='kw_h_m2')
    pd.testing.assert_series_equal(result, expected)


def test_calculate_energy_requirement_reduction_raise_value_error_when_period_is_missing_from_index():
    kw_h_m2 = pd.Series(data=[20]*8, index=YearRange(2001, 2008), name='kw_h_m2')

    with pytest.raises(ValueError, match='Did not find all years from 2011 - 2014 in energy_requirements'):
        calculate_energy_requirement_reduction(
            energy_requirements=kw_h_m2,
            yearly_reduction=0.25,
            reduction_period=YearRange(2011, 2014))


def test_calculate_lighting_reduction_and_proportional_energy_change_based_on_end_year():
    bema_years = YearRange(2010, 2050)
    kw_h_m2 = pd.Series(data=[9.1075556] * 41, index=bema_years, name='kw_h_m2')

    based_on_end_year = calculate_proportional_energy_change_based_on_end_year(kw_h_m2,
                                                                               3.6430222,
                                                                               YearRange(2018, 2030))
    lighting = calculate_energy_requirement_reduction(based_on_end_year,
                                                      yearly_reduction=0.005,
                                                      reduction_period=YearRange(2031, 2050))
    assert round(lighting.loc[2010], 5) == 9.10756
    assert round(lighting.loc[2018], 5) == 9.10756
    assert round(lighting.loc[2019], 5) == 8.65218
    assert round(lighting.loc[2030], 5) == 3.64302
    assert round(lighting.loc[2031], 5) == 3.62481
    assert round(lighting.loc[2036], 5) == 3.53509
    assert round(lighting.loc[2050], 5) == 3.29552





