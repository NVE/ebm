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
            apartment_block,TEK07,default,7.0
            """.strip()), skipinitialspace=True)

@pytest.fixture
def reduction_per_condition():
    return pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,building_condition,reduction_share
            default,default,heating_rv,original_condition,0.0
            default,default,heating_rv,small_measure,0.07
            default,default,heating_rv,renovation,0.2
            default,default,heating_rv,renovation_and_small_measure,0.25
            default,TEK17,heating_rv,original_condition,0.0
            default,TEK17,heating_rv,small_measure,0.02
            default,TEK17,heating_rv,renovation,0.05
            default,TEK17,heating_rv,renovation_and_small_measure,0.07
            default,TEK21,heating_rv,original_condition,0.0
            default,TEK21,heating_rv,small_measure,0.02
            default,TEK21,heating_rv,renovation,0.05
            default,TEK21,heating_rv,renovation_and_small_measure,0.07
            """.strip()), skipinitialspace=True)

@pytest.fixture
def policy_improvement():
    return pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
            default,default,lighting,2011,2012,0.5
            """.strip()), skipinitialspace=True)

@pytest.fixture
def yearly_improvements():
    return pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,cooling,0.0
            default,default,electrical_equipment,0.1
            default,default,fans_and_pumps,0.0
            default,default,heating_dhw,0.0
            default,default,lighting,0.05
            """.strip()), skipinitialspace=True)

# -------------------------------------- init method ------------------------------------------------

def test_instance_var_dtype(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    
    with pytest.raises(TypeError):
        EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                None,
                                reduction_per_condition,
                                yearly_improvements,
                                policy_improvement)
   
    with pytest.raises(TypeError):
        EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                original_condition,
                                None,
                                yearly_improvements,
                                policy_improvement)
                   
    with pytest.raises(TypeError):
        EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                original_condition,
                                reduction_per_condition,
                                None,
                                policy_improvement)

    with pytest.raises(TypeError):
        EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                original_condition,
                                reduction_per_condition,
                                yearly_improvements,
                                None)

# -------------------------------------- get_original condition --------------------------------------

def test_energy_requirement_returns_original_condition_from_dataframe(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.APARTMENT_BLOCK,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    pre_tek49_cooling = e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose='cooling')
    assert pre_tek49_cooling.iloc[0].kwh_m2 == 1.1

    tek07_and_electical_equipment = e_r_filter.get_original_condition(tek='TEK07', purpose='electrical_equipment')
    assert tek07_and_electical_equipment.iloc[0].kwh_m2 == 2.2

# -------------------------------------- get_reduction_per_condition ---------------------------------

#TODO

# -------------------------------------- get_policy_improvement --------------------------------------

def test_get_policy_improvement_filter_purpose(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='default', purpose='lighting') == (YearRange(2011, 2012), 0.5)
    assert e_r_filter.get_policy_improvement(tek='default', purpose='meaningoflife') is None


def test_get_policy_improvement_filter_tek(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,lighting,2011,2012,0.5
                         default,TEK17,lighting,2012,2013,0.9""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK17', purpose='lighting') == (YearRange(2012, 2013), 0.9)
    assert e_r_filter.get_policy_improvement(tek='meaningoflife', purpose='lighting') == (YearRange(2011, 2012), 0.5)


def test_get_policy_improvement_use_default(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,default,2011,2012,0.5""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK17', purpose='cooling') == (YearRange(2011, 2012), 0.5)


def test_get_policy_improvement_filter_purpose_and_tek(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         default,default,heating_rv,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose='heating_rv') == (YearRange(2012, 2013), 0.2)


def test_get_policy_improvement_filter_building_category(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.HOUSE,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose='lighting') == (YearRange(2012, 2013), 0.2)

def test_get_policy_improvement_filter_building_category_default(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose='lighting') == (YearRange(2011, 2012), 0.1)

def test_get_policy_improvement_filter_building_category_none(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(BuildingCategory.KINDERGARTEN,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose='lighting') is None

# -------------------------------------- get_yearly_improvements -------------------------------------

def test_get_yearly_improvements_filter_purpose(original_condition, reduction_per_condition, yearly_improvements, policy_improvement):
    
    e_r_filter = EnergyRequirementFilter(BuildingCategory.HOUSE,
                                         original_condition,
                                         reduction_per_condition,
                                         yearly_improvements,
                                         policy_improvement)
    
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='electrical_equipment') == 0.01
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='lighting') == 0.005
