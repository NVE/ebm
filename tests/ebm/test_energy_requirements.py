from unittest.mock import Mock

import pandas as pd
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement import EnergyRequirement


def test_calculate_reduction_policy():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()
    er = EnergyRequirement(building_code_list=['TEK01'],
                      period=period,
                      calibration_year=2014,
                      database_manager=dm)

    all_things =pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y] for y in period]
             +  [['kindergarten', 'TEK01', 'lighting', y] for y in period],
        columns=['building_category', 'building_code', 'purpose', 'year'])

    p_i_df = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.6, 2015],
            ['kindergarten', 'TEK01', 'lighting', 2012, 0.6, 2016]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    df = er.calculate_reduction_policy(policy_improvement=p_i_df, all_things=all_things)
    df = df.set_index(['building_category', 'building_code', 'purpose', 'year'])

    expected_reduction_policy = pd.Series(
        data=[1.0, 0.85, 0.7, 0.55, 0.4, 0.4, 0.4]+
             [1.0, 1.0, 0.85, 0.7, 0.55, 0.4, 0.4],
        name='reduction_policy',
        index=pd.Index(
            data=[('house', 'TEK01', 'lighting', y) for y in period] +
                 [('kindergarten', 'TEK01', 'lighting', y) for y in period],
            name=('building_category', 'building_code', 'purpose', 'year'))

    )
    pd.testing.assert_series_equal(df['reduction_policy'], expected_reduction_policy)


def test_calculate_reduction_policy_with_start_year_in_all_things():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()
    er = EnergyRequirement(building_code_list=['TEK01'],
                      period=period,
                      calibration_year=2014,
                      database_manager=dm)

    all_things =pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y, period.start, None] for y in period]
             +  [['kindergarten', 'TEK01', 'lighting', y, period.start, period.end] for y in period],
        columns=['building_category', 'building_code', 'purpose', 'year', 'start_year', 'end_year'])

    p_i_df = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.6, 2015],
            ['kindergarten', 'TEK01', 'lighting', 2012, 0.6, 2016]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    er.calculate_reduction_policy(policy_improvement=p_i_df, all_things=all_things)


def test_calculate_reduction_policy_handle_missing_policy_improvement():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()
    er = EnergyRequirement(building_code_list=['TEK01'],
                      period=period,
                      calibration_year=2014,
                      database_manager=dm)

    all_things =pd.DataFrame(
        data=[['office', 'TEK01', 'lighting', y] for y in period],
        columns=['building_category', 'building_code', 'purpose', 'year'])

    p_i_df = pd.DataFrame(
        data=[
            ['kindergarten', 'TEK01', 'lighting', 2012, 0.6, 2016]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    df = er.calculate_reduction_policy(policy_improvement=p_i_df, all_things=all_things)
    df = df.set_index(['building_category', 'building_code', 'purpose', 'year'])

    expected_reduction_policy = pd.Series(
        data=[1.0] * 7,
        name='reduction_policy',
        index=pd.Index(
            data=[('office', 'TEK01', 'lighting', y) for y in period],
            name=('building_category', 'building_code', 'purpose', 'year'))

    )
    pd.testing.assert_series_equal(df['reduction_policy'], expected_reduction_policy)


def test_calculate_reduction_policy_return_expected_columns():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()
    er = EnergyRequirement(building_code_list=['TEK01'],
                      period=period,
                      calibration_year=2014,
                      database_manager=dm)

    all_things =pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y] for y in period],
        columns=['building_category', 'building_code', 'purpose', 'year'])

    p_i_df = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.6, 2015]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    df = er.calculate_reduction_policy(policy_improvement=p_i_df, all_things=all_things)

    assert df.columns.tolist() == ['building_category', 'building_code', 'purpose', 'year', 'reduction_policy']


def test_calculate_reduction_policy_works_with_multiple_periods():
    period = YearRange(2011, 2020)
    dm = DatabaseManager()
    er = EnergyRequirement(building_code_list=['TEK01'],
                      period=period,
                      calibration_year=2014,
                      database_manager=dm)

    all_things =pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', y] for y in period],
        columns=['building_category', 'building_code', 'purpose', 'year'])

    p_i_df = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.6, 2015],
            ['house', 'TEK01', 'lighting', 2017, 0.8, 2020]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    df = er.calculate_reduction_policy(policy_improvement=p_i_df, all_things=all_things)
    df = df.set_index(['building_category', 'building_code', 'purpose', 'year'])

    expected_reduction_policy = pd.Series(
        data=[1.  , 0.85, 0.7 , 0.55, 0.4 ]+
             [0.4] +
             [0.4, 0.33333333, 0.26666667, 0.2],
        name='reduction_policy',
        index=pd.Index(
            data=[('house', 'TEK01', 'lighting', y) for y in period],
            name=('building_category', 'building_code', 'purpose', 'year'))

    )
    pd.testing.assert_series_equal(df['reduction_policy'], expected_reduction_policy)


def test_calculate_reduction_with_policy_improvement():
    period = YearRange(2011, 2017)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 0.1, period.start, period.end]],
        columns=['building_category', 'building_code', 'purpose', 'yearly_efficiency_improvement', 'start_year', 'end_year']))

    policy_improvement = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.9, 2014],
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year'])

    dm.get_energy_need_policy_improvement = Mock(return_value=policy_improvement)

    # pd.DataFrame( data=[['house', 'TEK01', 'lighting', y, factor] for y, factor in zip(range(2011, 2015), [1., .7, .4, .1])], columns=['building_category', 'building_code', 'purpose', 'year', 'policy_improvement_factor'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','building_code','purpose','building_condition','reduction_share']
    ))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list,
                               period=period,
                               calibration_year=2014,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', 50.0, 1.0]],
        columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.LIGHTING]], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_building_codes = building_code_list,
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

@pytest.fixture
def energy_need():
    period = YearRange(2010, 2022)
    return EnergyRequirement(building_code_list=['TEK01', 'TEK02'], period=period, calibration_year=2013,
                                    database_manager=DatabaseManager())


def test_calculate_yearly_reduction_raise_value_error_on_missing_columns(energy_need):
    """
    calculate_reduction_yearly should check validity of its parameters.
    """
    yearly_efficiency_improvement = pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', energy_need.period.start, 0.1, energy_need.period.end],
            ['house', 'TEK01', 'electrical_equipment', energy_need.period.start + 1, 0.05,
             energy_need.period.end - 1], ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'yearly_efficiency_improvement', 'end_year'])

    for column in ['yearly_efficiency_improvement', 'start_year', 'end_year']:
        with pytest.raises(ValueError):
            energy_need.calculate_reduction_yearly(df_years=energy_need.period.to_dataframe(),
                yearly_improvement=yearly_efficiency_improvement.drop(columns=[column]))

    with pytest.raises(ValueError):
        energy_need.calculate_reduction_yearly(df_years=pd.DataFrame(data={'month': [1, 2, 3]}),
                                               yearly_improvement=yearly_efficiency_improvement)


def test_calculate_yearly_reduction_adds_column_reduction_yearly(energy_need):
    """
    calculate_reduction_yearly add column reduction_yearly and no others
    """
    yearly_efficiency_improvement = pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', energy_need.period.start, 0.1, energy_need.period.end],
            ['house', 'TEK01', 'electrical_equipment', energy_need.period.start + 1, 0.05,
             energy_need.period.end - 1], ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'yearly_efficiency_improvement', 'end_year'])

    df = energy_need.calculate_reduction_yearly(df_years=energy_need.period.to_dataframe(),
                                                yearly_improvement=yearly_efficiency_improvement)

    expected_columns = ['building_category', 'building_code', 'purpose', 'year', 'reduction_yearly']

    assert df.columns.tolist() == expected_columns


def test_calculate_yearly_reduction():
    """
    reduction_yearly starts on start_year and ends in end_year
    reduction_yearly replace nan values with 1.0 before start_year and by ffill after end_year

    """
    period = YearRange(2010, 2022)
    dm = DatabaseManager()

    yearly_efficiency_improvement = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 2011, 0.1, period.end],
            ['house', 'TEK01', 'electrical_equipment', 2012, 0.05, 2020],
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'yearly_efficiency_improvement', 'end_year'])

    en_req = EnergyRequirement(building_code_list=['TEK01'], period=period, calibration_year=2013, database_manager=dm)

    df = en_req.calculate_reduction_yearly(df_years=period.to_dataframe(), yearly_improvement=yearly_efficiency_improvement)

    house_lighting = df.query('purpose=="lighting"').set_index(['year'])

    expected = pd.Series(
        data={2010:1.0, 2011:0.9, 2012:0.81, 2013:0.7290000000000001, 2014: 0.6561, 2015:0.5904900000000001,
              2016:0.531441, 2017:0.4782969000000001, 2018:0.4304672100000001, 2019:0.3874204890000001,
              2020:0.3486784401000001, 2021:0.31381059609000006, 2022:0.2824295364810001},
        name='reduction_yearly',
        index=period.to_index())

    pd.testing.assert_series_equal(house_lighting.reduction_yearly, expected)

    house_el_eq = df.query('purpose=="electrical_equipment"').set_index(['year'])

    house_el_expected = pd.Series(
        data=[1.0, 1.0, 0.95, 0.9025, 0.8573749999999999, 0.8145062499999999, 0.7737809374999998, 0.7350918906249998,
              0.6983372960937497, 0.6634204312890623, 0.6302494097246091,  0.6302494097246091,  0.6302494097246091
        ],
        name='reduction_yearly',
        index=period.to_index())

    pd.testing.assert_series_equal(house_el_eq.reduction_yearly, house_el_expected)


def test_calculate_reduction_with_yearly_reduction():
    """
    Test calculate_energy_requirement with yearly reduction and policy improvement
    """

    period = YearRange(2010, 2022)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', period.start, 0.1, period.end],
            ['house', 'TEK01', 'electrical_equipment', period.start, 0.05, period.end]
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'yearly_efficiency_improvement', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', 2011, 0.6, 2014]],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'improvement_at_end_year', 'end_year']))

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','building_code','purpose','building_condition','reduction_share']
    ))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list,
                               period=period,
                               calibration_year=2013,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 100, 1.0],
            ['house', 'TEK01', 'electrical_equipment', 100, 1.0]
        ],
        columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[EnergyPurpose.LIGHTING, EnergyPurpose.ELECTRICAL_EQUIPMENT], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_building_codes=building_code_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    house_lighting = df.query('purpose=="lighting"')


    assert house_lighting.reduction_policy.round(8).tolist() == [1.0, 1.0, 0.8, 0.6, 0.4] + [0.4]*8
    assert house_lighting.reduction_yearly.round(5).tolist() == [0.9, 0.81, 0.729,
                                            0.6561, 0.59049, 0.53144, 0.4783,
                                            0.43047, 0.38742, 0.34868,
                                            0.31381, 0.28243, 0.25419]

    result = house_lighting.kwh_m2
    expected = pd.Series(data=[90., 81., 58.32, 39.366,
                               23.6196, 21.25764, 19.131876,
                               17.218688, 15.496820, 13.947138,
                               12.55242, 11.29718, 10.1674],
                         index=period.to_index())

    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)

    house_electrical = df.query('purpose=="electrical_equipment"')

    assert house_electrical.reduction_policy.tolist() == [1.0] * 13


def test_calculate_reduction_with_yearly_reduction_with_year():
    period = YearRange(2010, 2022)
    dm = DatabaseManager()
    dm.get_energy_need_yearly_improvements = Mock(return_value=pd.DataFrame(
        data=[
            ['house', 'TEK01', 'lighting', 0.1, period.subset(11).start, period.end],
            ['house', 'TEK01', 'electrical_equipment', 0.1, period.start+1, period.end],
        ],
        columns=['building_category', 'building_code', 'purpose', 'yearly_efficiency_improvement', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'lighting', 2010, 2020, 0.6]],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
                 'improvement_at_end_year']))

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', 'original_condition', 0.0]],
        columns=['building_category','building_code','purpose','building_condition','reduction_share']
    ))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list,
                               period=period,
                               calibration_year=2013,
                               database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(
        data=[['house', 'TEK01', 'electrical_equipment', 100, 1.0],
              ['house', 'TEK01', 'lighting', 100, 1.0]],
        columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[EnergyPurpose.ELECTRICAL_EQUIPMENT, EnergyPurpose.LIGHTING], columns=['purpose'])

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings,
        all_purpose=purpose,
        all_building_codes=building_code_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION],
        database_manager=dm
    )
    result = df.query('purpose=="electrical_equipment"').set_index(['year']).kwh_m2

    expected = pd.Series(
        [100.0, 90.0, 81.0, 72.9, 65.61,
         59.04900000000001, 53.14410000000001, 47.82969000000001, 43.04672100000001, 38.74204890000001,
         34.86784401000001, 31.381059609000005, 28.242953648100013], name='kwh_m2', index=period.to_index())

    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_index=False, check_names=False)

    result = df.query('purpose=="lighting"').set_index(['year']).kwh_m2

    expected = pd.Series(
        data=[100.,  94.,  88.,  82.,  76.,  70.,  64.,  58.,  52.,  46.,  40., 36., 32.4],
        name='kwh_m2',
        index=period.to_index())
    assert len(result) == len(expected)
    pd.testing.assert_series_equal(result, expected, check_like=True)


def test_calculate_reduction_by_condition():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1, 2020, 2025]],
            columns=['building_category', 'building_code', 'purpose', 'yearly_efficiency_improvement', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
                     'improvement_at_end_year']))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]

    erq_oc = pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.HEATING_RV, y, 100.0, 100.0, 100.0, 1.0] for y in period],
                          columns=['building_category', 'building_code', 'purpose', 'year',
                 'uncalibrated_kwh_m2', 'calibrated_kwh_m2', 'kwh_m2', 'behaviour_factor'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.SMALL_MEASURE, 0.1],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.2],
            ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.3]],
        columns=['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(
        all_building_categories=buildings, all_purpose=purpose, all_building_codes=building_code_list,
        energy_requirement_original_condition=erq_oc,
        model_years=period,
        most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.SMALL_MEASURE,
                         BuildingCondition.RENOVATION, BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
        database_manager=dm)

    result = df[['building_category', 'building_code', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected_rows = (
            [['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 100.0] for y in period] +
            [['house', 'TEK01', 'small_measure', 'heating_rv', y, 100.0, 90.0] for y in period] +
            [['house', 'TEK01', 'renovation', 'heating_rv', y, 100.0, 80.0] for y in period] +
            [['house', 'TEK01', 'renovation_and_small_measure', 'heating_rv', y, 100.0, 70.0] for y in period])

    expected = pd.DataFrame(
        data=expected_rows,
        columns=['building_category', 'building_code', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2'])

    assert len(result) == len(expected)
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_reduction_by_behavior():
    period = YearRange(2020, 2025)
    dm = DatabaseManager()

    dm.get_energy_need_yearly_improvements = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1, 2021, 2025]],
            columns=['building_category', 'building_code', 'purpose', 'yearly_efficiency_improvement', 'start_year', 'end_year']))

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2020, 2024, 0.1]],
            columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
                     'improvement_at_end_year']))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list, period=period, calibration_year=2023, database_manager=dm)

    buildings = [BuildingCategory.HOUSE]
    erq_oc = pd.DataFrame(data=[['house', 'TEK01', EnergyPurpose.HEATING_RV,
                                 120.0, 100.0, 100.0, 0.8, period.start, period.end]],
        columns=['building_category', 'building_code', 'purpose',
                 'uncalibrated_kwh_m2', 'calibrated_kwh_m2', 'kwh_m2', 'behaviour_factor',
                 'start_year', 'end_year'])

    purpose = pd.DataFrame(data=[[EnergyPurpose.HEATING_RV]], columns=['purpose'])

    dm.get_energy_req_reduction_per_condition = Mock(return_value=pd.DataFrame(
        data=[['house', 'TEK01', 'heating_rv', BuildingCondition.ORIGINAL_CONDITION, 0.0],
              ['house', 'TEK01', 'heating_rv', BuildingCondition.RENOVATION, 0.3]],
        columns=['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_building_codes=building_code_list,
                                             energy_requirement_original_condition=erq_oc, model_years=period,
                                             most_conditions=[BuildingCondition.ORIGINAL_CONDITION, BuildingCondition.RENOVATION],
                                             database_manager=dm)

    result = df[['building_category', 'building_code', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2']]

    expected = pd.DataFrame(
        data=[['house', 'TEK01', 'original_condition', 'heating_rv', y, 100.0, 80.0] for y in period] +
             [['house', 'TEK01', 'renovation', 'heating_rv', y, 100.0, 56.0] for y in period],
        columns=['building_category', 'building_code', 'building_condition', 'purpose', 'year', 'original_kwh_m2', 'kwh_m2'])

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
    ], columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor'])

    yearly_improvement = pd.DataFrame(
        data=[
            ['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 2021, 2025, 0.2],
            ['house', 'TEK01', EnergyPurpose.LIGHTING, 2024, 2025, 0.1]],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year', 'yearly_efficiency_improvement'])

    dm.get_energy_need_yearly_improvements = Mock(return_value=yearly_improvement)

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[['house', 'TEK01', 'lighting', 2021, 2023, 0.5]],
            columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
                     'improvement_at_end_year']))

    building_code_list = ['TEK01']
    en_req = EnergyRequirement(building_code_list=building_code_list, period=period, calibration_year=2023, database_manager=dm)

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
        columns=['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_building_codes=building_code_list,
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


def test_calculate_energy_requirements_with_multiple_building_codes():
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
    ], columns=['building_category', 'building_code', 'purpose', 'kwh_m2', 'behaviour_factor'])

    yearly_improvements = pd.DataFrame(
        data=[
            ['house', 'TEK01', EnergyPurpose.ELECTRICAL_EQUIPMENT, 2021, 2025, 0.01],
            ['house', 'TEK02', EnergyPurpose.ELECTRICAL_EQUIPMENT, 2021, 2025, 0.02],
            ['house', 'TEK01', EnergyPurpose.LIGHTING, 2024, 2025, 0.1],
            ['house', 'TEK02', EnergyPurpose.LIGHTING, 2024, 2025, 0.2]],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year', 'yearly_efficiency_improvement'])

    dm.get_energy_need_yearly_improvements = Mock(return_value=yearly_improvements)

    dm.get_energy_need_policy_improvement = Mock(
        return_value=pd.DataFrame(data=[
            ['house', 'TEK01', 'lighting', 2021, 2023, 0.5],
            ['house', 'TEK02', 'lighting', 2021, 2023, 0.5]
        ],
            columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
                     'improvement_at_end_year']))

    building_code_list = ['TEK01', 'TEK02']
    en_req = EnergyRequirement(building_code_list=building_code_list, period=period, calibration_year=2023, database_manager=dm)

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
        columns=['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share']))

    df = en_req.calculate_energy_requirement(all_building_categories=buildings, all_purpose=purpose, all_building_codes=building_code_list,
                                             energy_requirement_original_condition=erq_oc, model_years=period,
                                             most_conditions=[BuildingCondition.ORIGINAL_CONDITION,
                                                              BuildingCondition.SMALL_MEASURE,
                                                              BuildingCondition.RENOVATION,
                                                              BuildingCondition.RENOVATION_AND_SMALL_MEASURE],
                                             database_manager=dm)
    tek01 = df[(df.building_code=='TEK01')].set_index(['purpose', 'building_condition', 'year'])
    tek02 = df[(df.building_code=='TEK02')].set_index(['purpose', 'building_condition', 'year'])

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
