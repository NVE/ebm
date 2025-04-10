import pandas as pd
import pytest
from unittest.mock import Mock

from ebm.model.building_condition import BuildingCondition
from ebm.model.building_category import BuildingCategory
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


def test_calculate_reduction_with_policy_improvement():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', y, (0.9**(y-2015)) if y > 2015 else 1.0, 2015, 2017] for y in period],
        columns=['building_category', 'TEK', 'purpose', 'year', 'yearly_reduction_factor', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y, factor] for y, factor in zip(range(2011, 2015), [1., .7, .4, .1])],
        columns=['building_category', 'TEK', 'purpose', 'year', 'policy_improvement_factor']))

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','TEK','purpose','building_condition','reduction_share']
    ))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list,
                               period=period,
                               calibration_year=2014,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', 50.0, 1.0]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.LIGHTING]], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_teks = tek_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    result = df.kwh_m2

    expected = pd.Series([50.0, 35.0, 20.0, 5.0, 5., 5., 5.],
                         index=period.to_index())
    
    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)


def test_calculate_reduction_with_yearly_reduction():
    """


    """
    period = YearRange(2010, 2022)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y, (0.9**(y-period.start))] for y in period]+
             [['house', 'TEK01', 'electrical_equipment', y, (0.95**(y-period.start))] for y in period],
        columns=['building_category', 'TEK', 'purpose', 'year', 'yearly_reduction_factor']))

    factors_by_year = zip(range(2011, 2016), [1.0, 0.8, 0.6, 0.4])
    dm.get_energy_need_policy_improvement = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y, 0.4, factor] for y, factor in factors_by_year],
        columns=['building_category', 'TEK', 'purpose', 'year', 'improvement_at_end_year', 'policy_improvement_factor']))

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','TEK','purpose','building_condition','reduction_share']
    ))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list,
                               period=period,
                               calibration_year=2013,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 100, 1.0],
            ['house', 'TEK01', 'electrical_equipment', 100, 1.0]
        ],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[EnergyPurpose.LIGHTING, EnergyPurpose.ELECTRICAL_EQUIPMENT], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_teks=tek_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    house_lighting = df.query('purpose=="lighting"')


    assert house_lighting.reduction_policy.tolist() == [1.0, 1.0, 0.8, 0.6, 0.4] + [0.4]*8
    assert house_lighting.reduction_yearly.tolist() == [1.0, 0.9, 0.81, 0.7290000000000001,
                                            0.6561, 0.5904900000000001, 0.531441, 0.4782969000000001,
                                            0.4304672100000001, 0.3874204890000001, 0.3486784401000001,
                                            0.31381059609000006, 0.2824295364810001]

    result = house_lighting.kwh_m2
    expected = pd.Series([100., 90., 64.8, 43.74,
         26.244, 23.6196, 21.25764, 19.131876,
         17.2186884, 15.49681956, 13.9471376, 12.55242384,
         11.29718146], index=period.to_index())

    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)

    house_electrical = df.query('purpose=="electrical_equipment"')

    assert house_electrical.reduction_policy.tolist() == [1.0] * 13


def test_calculate_reduction_with_yearly_reduction_with_year():
    period = YearRange(2010, 2022)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=
        [['house', 'TEK01', 'electrical_equipment', y, (0.9**(y-period.start))] for y in period] +
        [['house', 'TEK01', 'lighting', y, (0.9**(y-2020))] for y in period.subset(10)],
        columns=['building_category', 'TEK', 'purpose', 'year', 'yearly_reduction_factor']))

    dm.get_energy_need_policy_improvement = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', 2010, 2020, 0.6]],
        columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                 'improvement_at_period_end']))

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','TEK','purpose','building_condition','reduction_share']
    ))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list,
                               period=period,
                               calibration_year=2013,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'TEK01', 'electrical_equipment', 100, 1.0],
              ['house', 'TEK01', 'lighting', 100, 1.0]],
        columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[EnergyPurpose.ELECTRICAL_EQUIPMENT, EnergyPurpose.LIGHTING], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_teks=tek_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    result = df.query('purpose=="electrical_equipment"').kwh_m2

    expected = pd.Series(
        [100.0, 90.0, 81.0, 72.9, 65.61,
         59.04900000000001, 53.14410000000001, 47.82969000000001, 43.04672100000001, 38.74204890000001,
         34.86784401000001, 31.381059609000005, 28.242953648100013], index=period.to_index())

    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)

    result = df.query('purpose=="lighting"').kwh_m2

    expected = pd.Series(
        [100.,  94.,  88.,  82.,  76.,  70.,  64.,  58.,  52.,  46.,  40., 36., 32.4], index=period.to_index())
    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)


def test_calculate_reduction_by_condition():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1, 2020, 2025]],
            columns=['building_category', 'TEK', 'purpose', 'yearly_reduction_factor', 'year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]

    erq_oc = pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.HEATING_RV, y, 100.0, 100.0, 100.0, 1.0] for y in period],
                          columns=['building_category', 'TEK', 'purpose', 'year',
                 'uncalibrated_kwh_m2', 'calibrated_kwh_m2', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3]],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.SMALL_MEASURE,
                         BuildingCondition.RENOVATION, BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
        database_manager=dm)

    result = df[['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected_rows = (
            [['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 100.0] for y in period] +
            [['house', 'TEK01', 'small_measure', 'heating_rv', y, 100.0, 90.0] for y in period] +
            [['house', 'TEK01', 'renovation', 'heating_rv', y, 100.0, 80.0] for y in period] +
            [['house', 'TEK01', 'renovation_and_small_measure', 'heating_rv', y, 100.0, 70.0] for y in period])

    expected = pd.DataFrame(
        data=expected_rows,
        columns=['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2'])

    assert len(result) == len(expected)
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_reduction_by_behavior():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1, 2020, 2025]],
            columns=['building_category', 'TEK', 'purpose', 'yearly_reduction_factor', 'year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.HEATING_RV, 120.0, 100.0, 100.0, 0.8]],
        columns=['building_category', 'TEK', 'purpose',
                 'uncalibrated_kwh_m2', 'calibrated_kwh_m2', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.3]],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
                                             energy_requirement_original_condition=erq_oc, model_years=period,
                                             most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.RENOVATION],
                                             database_manager=dm)

    result = df[['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected = pd.DataFrame(
        data=[['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 80.0] for y in period] +
             [['house', 'TEK01', 'renovation', 'heating_rv', y, 100.0, 56.0] for y in period],
        columns=['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2'])

    assert len(result) == len(expected)
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_energy_requirements():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    energy_requirements_original_condition = pd.DataFrame(
        data=[
         ['house', 'TEK01', EnergyPurpose.HEATING_RV, 200.0, 1.0],
         ['house', 'TEK01', EnergyPurpose.HEATING_DHW, 100.0, 0.8],
         ['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 50.0, 0.6],
         ['house', 'TEK01', EnergyPurpose.LIGHTING, 100.0, 0.5]
    ], columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor'])


    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=
            [['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, y, (0.8**(y-2020)), 2020, 2025] for y in period] +
            [['house', 'TEK01', EnergyPurpose.LIGHTING, y, (0.9**(y-2023)), 2023, 2025] for y in period.subset(3)],
            columns=['building_category', 'TEK', 'purpose', 'year', 'yearly_reduction_factor', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2021, 2023, 0.5]],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]

    purpose = pd.DataFrame(data=[EnergyPurpose.HEATING_RV,
                                 EnergyPurpose.HEATING_DHW,
                                 EnergyPurpose.ELECTRICAL_EQUIPMENT,
                                 EnergyPurpose.LIGHTING], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3],
              ],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
                                             energy_requirement_original_condition=energy_requirements_original_condition,
                                             model_years=period,
                                             most_conditions=[BuildingCondition.ORIGINAL_CONDITION,
                         BuildingCondition.SMALL_MEASURE,
                         BuildingCondition.RENOVATION,
                         BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
                                             database_manager=dm)

    assert len(df) == 96

    assert df[df.purpose == 'heating_rv'].behaviour_factor.to_list() == [1.0] * 24
    assert df[df.purpose == 'heating_dhw'].behaviour_factor.to_list() == [0.8] * 24
    assert df[df.purpose == 'electrical_equipment'].behaviour_factor.to_list() == [0.6] * 24
    assert df[df.purpose == 'lighting'].behaviour_factor.to_list() == [0.5] * 24

    heating_rv_original_condition = df[(df.purpose == 'heating_rv') & (df.building_condition == 'original_condition')]
    assert heating_rv_original_condition.kwh_m2.to_list() == [200.0] * 6
    assert heating_rv_original_condition.reduction_condition.to_list() == [1.0] * 6
    assert heating_rv_original_condition.behaviour_factor.to_list() == [1.0] * 6

    heating_rv_small_measure = df[(df.purpose == 'heating_rv') & (df.building_condition == 'small_measure')]
    assert heating_rv_small_measure.kwh_m2.to_list() == [180.0] * 6
    assert heating_rv_small_measure.reduction_condition.to_list() == [0.9] * 6

    heating_rv_renovation = df[(df.purpose == 'heating_rv') & (df.building_condition == 'renovation')]
    assert heating_rv_renovation.kwh_m2.to_list() == [160.0] * 6
    assert heating_rv_renovation.reduction_condition.to_list() == [0.8] * 6

    heating_rv_renovation_and_small_measure = df[(df.purpose == 'heating_rv') &
                                                 (df.building_condition == 'renovation_and_small_measure')]
    assert heating_rv_renovation_and_small_measure.kwh_m2.to_list() == [140.0] * 6
    assert heating_rv_renovation_and_small_measure.reduction_condition.to_list() == [0.7] * 6

    assert df[df.purpose != 'heating_rv'].reduction_condition.to_list() == [1.0] * 72

    heating_dhw_original_condition = df[df.purpose == 'heating_dhw']
    assert heating_dhw_original_condition.original_kwh_m2.to_list() == [100.0] * 24
    assert heating_dhw_original_condition.kwh_m2.to_list() == [80.0] * 24

    electrical_equipment = df[df.purpose=='electrical_equipment'].set_index(['building_condition', 'year'])
    assert electrical_equipment.kwh_m2.round(4).to_list() == [30.0, 24.0, 19.2, 15.36,
                                                     12.288, 9.8304] * len(purpose)

    lighting = df[df.purpose == 'lighting'].set_index(['building_condition', 'year'])
    assert lighting.reduction_policy.to_list() == [1.0, 1.0, 0.75, 0.5, 0.5, 0.5] * 4
    assert lighting.reduction_yearly.to_list() == [1.0, 1.0, 1.0, 1.0, 0.9, 0.81] * 4
    assert lighting.reduced_kwh_m2.to_list() == [100.0, 100.0, 75.0, 50.0, 45.0, 40.5] * 4
    assert lighting.kwh_m2.to_list() == [50.0, 50.0, 37.5, 25.0, 22.5, 20.25] * 4


def test_calculate_energy_requirements_with_multiple_teks():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    erq_oc = pd.DataFrame(
        data=[
         ['house', 'TEK01', EnergyPurpose.HEATING_RV, 100.0, 1.0],
         ['house', 'TEK02', EnergyPurpose.HEATING_RV, 200.0, 1.1],
         ['house', 'TEK01', EnergyPurpose.HEATING_DHW, 210.0, 0.8],
         ['house', 'TEK02', EnergyPurpose.HEATING_DHW, 100.0, 0.9],
         ['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 10.0, 0.2],
         ['house', 'TEK02', EnergyPurpose.ELECTRICAL_EQUIPMENT, 20.0, 0.4],
         ['house', 'TEK01', EnergyPurpose.LIGHTING, 100.0, 0.5],
         ['house', 'TEK02', EnergyPurpose.LIGHTING, 100.0, 0.6]
    ], columns=['building_category', 'TEK', 'purpose', 'kwh_m2', 'behaviour_factor'])


    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(
            data=[['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, (0.99**(y-period.start)), y,period.start, period.end] for y in period]+
                 [['house', 'TEK02', EnergyPurpose.ELECTRICAL_EQUIPMENT, (0.98**(y-period.start)), y,period.start, period.end] for y in period]+
                 [['house', 'TEK01', EnergyPurpose.LIGHTING, (0.9**(y-2023)), y, 2023, period.end] for y in period.subset(2)]+
                 [['house', 'TEK02', EnergyPurpose.LIGHTING, (0.8**(y-2023)), y, 2023, period.end] for y in period.subset(2)],
            columns=['building_category', 'TEK', 'purpose', 'yearly_reduction_factor', 'year', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[
            ['house', 'TEK01', 'lighting', 2021, 2023, 0.5],
            ['house', 'TEK02', 'lighting', 2021, 2023, 0.5]
        ],
            columns=['building_category', 'TEK', 'purpose', 'period_start_year', 'period_end_year',
                     'improvement_at_period_end']))

    tek_list = ['TEK01', 'TEK02']
    en_req = EnergyRequirement(tek_list=tek_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]

    purpose = pd.DataFrame(data=[EnergyPurpose.HEATING_RV,
                                 EnergyPurpose.HEATING_DHW,
                                 EnergyPurpose.ELECTRICAL_EQUIPMENT,
                                 EnergyPurpose.LIGHTING], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3],
              ['house', 'TEK02', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
              ['house', 'TEK02', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
              ['house', 'TEK02', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
              ['house', 'TEK02', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3],
              ],
        columns=['building_category', 'TEK', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_teks=tek_list,
                                             energy_requirement_original_condition=erq_oc, model_years=period,
                                             most_conditions=[BuildingCondition.ORIGINAL_CONDITION,
                                                              BuildingCondition.SMALL_MEASURE,
                                                              BuildingCondition.RENOVATION,
                                                              BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
                                             database_manager=dm)
    tek01 = df[(df.TEK=='TEK01')].set_index(['purpose', 'building_condition', 'year'])
    tek02 = df[(df.TEK=='TEK02')].set_index(['purpose', 'building_condition', 'year'])

    assert (tek01.loc['heating_rv', 'behaviour_factor'] == 1.0).all()
    assert (tek02.loc['heating_rv'].behaviour_factor == 1.1).all()

    assert (tek01.loc['heating_rv'].behaviour_factor == 1.0).all()
    assert (tek01.loc[('heating_rv', 'original_condition')].reduction_condition == 1.0).all()
    assert (tek01.loc[('heating_rv', 'small_measure')].reduction_condition == 0.9).all()
    assert (tek01.loc[('heating_rv', 'renovation')].reduction_condition == 0.8).all()
    assert tek01.loc[('lighting', 'original_condition', 2023)].reduction_policy == 0.5
    assert tek01.loc[('lighting', 'original_condition', 2024)].reduction_yearly == 0.9
    assert tek01.loc[('electrical_equipment', 'original_condition', 2021)].reduction_yearly == 0.99

    assert (tek02.loc['heating_rv'].behaviour_factor == 1.1).all()
    assert (tek02.loc[('heating_rv', 'original_condition')].reduction_condition == 1.0).all()
    assert (tek02.loc[('heating_rv', 'small_measure')].reduction_condition == 0.9).all()
    assert (tek02.loc[('heating_rv', 'renovation')].reduction_condition == 0.8).all()
    assert tek02.loc[('lighting', 'original_condition', 2024)].reduction_yearly == 0.8
    assert tek02.loc[('lighting', 'original_condition', 2023)].reduction_policy == 0.5
    assert tek02.loc[('electrical_equipment', 'original_condition', 2021)].reduction_yearly == 0.98


if __name__ == '__main__':
    pytest.main()
