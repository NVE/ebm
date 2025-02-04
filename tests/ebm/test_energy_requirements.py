import numpy as np
import pandas as pd
import pytest
from unittest.mock import Mock

from ebm.model.building_condition import BuildingCondition
from ebm.model.building_category import BuildingCategory
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import (
    calculate_energy_requirement_reduction_by_condition,
    calculate_proportional_energy_change_based_on_end_year,
    calculate_energy_requirement_reduction,
    calculate_lighting_reduction,
    EnergyRequirement)


def test_calculate_energy_requirement_reduction_by_condition():
    condition_reduction = pd.DataFrame(data=[[BuildingCondition.ORIGINAL_CONDITION, 0],
                                             [BuildingCondition.SMALL_MEASURE, 0.2],
                                             [BuildingCondition.RENOVATION, 0.4],
                                             [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.8]],
                                       columns=['building_condition', 'reduction_share'])

    df = calculate_energy_requirement_reduction_by_condition(100.0, condition_reduction,
                                                             building_category='apartment_block',
                                                             purpose='HeatingRV',
                                                             tek='PRE_TEK49'
                                                             )

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


def test_calculate_energy_requirement_reduction_kindergarten_electrical():
    kwh_m2 = pd.Series(data=[5.22] * 41, index=YearRange(2010, 2050), name='kwh_m2')

    result = calculate_energy_requirement_reduction(
        energy_requirements=kwh_m2,
        yearly_reduction=0.01,
        reduction_period=YearRange(2020, 2050)
    )

    assert result.loc[2010] == 5.22
    assert result.loc[2018] == 5.22
    assert result.loc[2019] == 5.22
    assert result.loc[2020] == 5.1678
    assert result.loc[2021] == 5.116122
    assert round(result.loc[2030], 8) == 4.67366569
    assert round(result.loc[2031], 8) == 4.62692903
    assert result.loc[2049] == 3.86123594908682
    assert result.loc[2050] == 3.82262358959595


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


def test_calculate_lighting_reduction_like_policy_improvement():
    policy_improvement = (YearRange(start=np.int64(2020),
                                    end=np.int64(2030)),
                          np.float64(0.54))
    period = YearRange(2020, 2050)
    kwh_m2 = pd.Series([20.88] * 31, index=period.to_index())
    yearly_improvements = np.float64(0.05)
    energy_req_end = kwh_m2.iloc[0] * (1.0 - 0.6)
    result = calculate_lighting_reduction(
        energy_requirement=kwh_m2,
        yearly_reduction=yearly_improvements,
        end_year_energy_requirement=energy_req_end,
        interpolated_reduction_period=policy_improvement[0],
        year_range=period)

    expected = pd.Series([
        20.88, 19.6272, 18.3744, 17.1216, 15.8688, 14.616, 13.3632, 12.1104, 10.8576, 9.6048,
        8.352, 7.9344, 7.53768, 7.160796, 6.8027562, 6.46261839, 6.1394874705, 5.832513, 5.54088, 5.263843,
        5.00065, 4.75061, 4.513087, 4.28743, 4.07306, 3.8694, 3.67593, 3.492141, 3.31753, 3.151657,
        2.99407442395614],
                         index=period.to_index())
    pd.testing.assert_series_equal(result, expected)


def test_calculate_reduction_with_policy_improvement():
    period = YearRange(2020, 2050)
    dm = DatabaseManager()

    dm.get_energy_req_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'lighting', 0.0]],
        columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement']))

    dm.get_energy_req_policy_improvements = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'lighting', 2020, 2030, 0.5555555555555556]],
        columns=['building_category','TEK','purpose','period_start_year','period_end_year','improvement_at_period_end']))


    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list,
                               period=period,
                               calibration_year=2023,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'default', 'lighting', 20.88, 1.0]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behavior_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.LIGHTING]], columns=['purpose'])

    df = en_req.calculate_energy_request2(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_teks = tek_list,
        erq_oc=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    result = df.kwh_m2

    expected = pd.Series([20.88, 19.72, 18.56, 17.4, 16.24, 15.07999, 13.91999, 12.76, 11.6, 10.44, 9.28] + [9.28] * 20,
                         index=period.to_index())
    
    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)


def test_calculate_reduction_with_yearly_reduction():
    period = YearRange(2020, 2050)
    dm = DatabaseManager()

    dm.get_energy_req_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'electrical_equipment', 0.1]],
        columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement']))

    dm.get_energy_req_policy_improvements = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'lighting', 2020, 2030, 0.6]],
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list,
                               period=period,
                               calibration_year=2023,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'default', 'electrical_equipment', 100, 1.0]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behavior_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.ELECTRICAL_EQUIPMENT]], columns=['purpose'])

    df = en_req.calculate_energy_request2(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_teks=tek_list,
        erq_oc=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    result = df.kwh_m2

    expected = pd.Series(
        [100.0, 90.0, 81.0, 72.9,
         65.61, 59.04900000000001, 53.14410000000001, 47.82969000000001, 43.04672100000001,
         38.74204890000001, 34.86784401000001, 31.381059609000005, 28.242953648100013, 25.418658283290007,
         22.87679245496101, 20.58911320946491, 18.530201888518416, 16.677181699666576, 15.009463529699918,
         13.508517176729928, 12.157665459056934, 10.941898913151242, 9.847709021836119, 8.862938119652506,
         7.9766443076872555, 7.17897987691853, 6.461081889226677, 5.81497370030401, 5.233476330273609,
         4.710128697246248, 4.239115827521624], index=period.to_index())

    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)


def test_calculate_reduction_by_condition():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_req_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['default', 'default', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement']))

    dm.get_energy_req_policy_improvements = Mock(
        return_value=pd.DataFrame(data=[['default', 'default', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(data=[['house', 'default', EnergyPurpose.HEATING_RV, 100.0, 1.0]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behavior_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
            ['default', 'default', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
            ['default', 'default', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
            ['default', 'default', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3]],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_request2(all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
        erq_oc=erq_oc, model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.SMALL_MEASURE,
                         BuildingCondition.RENOVATION, BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
        database_manager=dm)

    result = df[['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected_rows = (
            [['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 100.0] for y in range(2020, 2026)] + [
        ['house', 'TEK01', 'small_measure', 'heating_rv', y, 100.0, 90.0] for y in range(2020, 2026)] + [
                ['house', 'TEK01', 'renovation', 'heating_rv', y, 100.0, 80.0] for y in range(2020, 2026)] + [
                ['house', 'TEK01', 'renovation_and_small_measure', 'heating_rv', y, 100.0, 70.0] for y in
                range(2020, 2026)])

    expected = pd.DataFrame(data=expected_rows,
                            columns=['building_category', 'TEK', 'building_condition', 'purpose', 'year',
                                     'original_kwh_m2', 'kwh_m2'])

    assert len(result) == len(expected)
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_reduction_by_behavior():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_req_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['default', 'default', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'yearly_efficiency_improvement']))

    dm.get_energy_req_policy_improvements = Mock(
        return_value=pd.DataFrame(data=[['default', 'default', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(data=[['house', 'default', EnergyPurpose.HEATING_RV, 100.0, 0.8]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behavior_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['default', 'default', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
            ['default', 'default', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3]],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_request2(all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
        erq_oc=erq_oc, model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
        database_manager=dm)

    result = df[['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected_rows = (
            [['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 80.0] for y in range(2020, 2026)] + [
        ['house', 'TEK01', 'renovation_and_small_measure', 'heating_rv', y, 100.0, 56.0] for y in range(2020, 2026)])

    expected = pd.DataFrame(data=expected_rows,
                            columns=['building_category', 'TEK', 'building_condition', 'purpose', 'year',
                                     'original_kwh_m2', 'kwh_m2'])

    assert len(result) == len(expected)
    pd.testing.assert_frame_equal(result, expected)


if __name__ == '__main__':
    pytest.main()
