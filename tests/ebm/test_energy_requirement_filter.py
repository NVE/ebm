import io
import typing

import pandas as pd
import pytest

from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement_filter import EnergyRequirementFilter


@pytest.fixture
def original_condition():
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

@pytest.fixture
def policy_improvement():
    return pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,lighting,2011,2012,0.5""".strip()), skipinitialspace=True)


def test_energy_requirement_filter_returns_correct_bema_defaults(original_condition, policy_improvement):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         None,
                                         None,
                                         policy_improvement)
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='electrical_equipment') == 0.01
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='lighting') == 0.005


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


def test_get_policy_improvement_filter_purpose(original_condition, policy_improvement):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         None,
                                         None,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='default', purpose='lighting') == (YearRange(2011, 2012), 0.5)
    assert e_r_filter.get_policy_improvement(tek='default', purpose='meaningoflife') is None


def test_get_policy_improvement_filter_tek(original_condition, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,lighting,2011,2012,0.5
                         default,TEK17,lighting,2012,2013,0.9""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         None,
                                         None,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK17', purpose='lighting') == (YearRange(2012, 2013), 0.9)
    assert e_r_filter.get_policy_improvement(tek='meaningoflife', purpose='lighting') == (YearRange(2011, 2012), 0.5)


def test_get_policy_improvement_use_default(original_condition, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,default,2011,2012,0.5""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         None,
                                         None,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK17', purpose='cooling') == (YearRange(2011, 2012), 0.5)
    