import io
import typing

import pandas as pd
import pytest

from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
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


@pytest.fixture
def default_parameters(original_condition, reduction_per_condition, yearly_improvements, policy_improvement) \
        -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.APARTMENT_BLOCK,
            'original_condition': original_condition,
            'reduction_per_condition': reduction_per_condition,
            'yearly_improvements': yearly_improvements,
            'policy_improvement': policy_improvement}


# -------------------------------------- init method ------------------------------------------------

def test_instance_var_dtype(default_parameters):
    with pytest.raises(TypeError, match="_condition expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'original_condition': None})

    with pytest.raises(TypeError):
        EnergyRequirementFilter(**{**default_parameters, 'reduction_per_condition': None})

    with pytest.raises(TypeError):
        EnergyRequirementFilter(**{**default_parameters, 'yearly_improvements': None})

    with pytest.raises(TypeError):
        EnergyRequirementFilter(**{**default_parameters, 'policy_improvement': None})


# -------------------------------------- _filter_df ---------------------------------------------------
#TODO: evaluate if this edge case should be allowed or not 
def test_filter_df_filter_val_edge_case(default_parameters):
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': 'not_a_building_category'})
    
    df = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,value
            default,default,default,100
            """.strip()), skipinitialspace=True)
    
    # If allowed this should pass:
    assert e_r_filter._filter_df(df, 'building_category', 'not_a_building_category').value.iloc[0] == 100
    assert e_r_filter._filter_df(df, 'purpose', 'not_a_purpose').value.iloc[0] == 100
    assert e_r_filter._filter_df(df, 'TEK', 'not_a_tek').value.iloc[0] == 100
    
    ## if not allowed this should pass:
    #assert e_r_filter._filter_df(df, 'building_category', 'not_a_building_category') is False
    #assert e_r_filter._filter_df(df, 'purpose', 'not_a_purpose') is False
    #assert e_r_filter._filter_df(df, 'TEK', 'not_a_tek') is False

# -------------------------------------- get_original condition --------------------------------------

def test_energy_requirement_returns_original_condition_from_dataframe(default_parameters):
    e_r_filter = EnergyRequirementFilter(**default_parameters)
    pre_tek49_cooling = e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose=EnergyPurpose.COOLING)
    assert pre_tek49_cooling.iloc[0].kwh_m2 == 1.1

    tek07_and_electrical_equipment = e_r_filter.get_original_condition(tek='TEK07', purpose='electrical_equipment')
    assert tek07_and_electrical_equipment.iloc[0].kwh_m2 == 2.2


# -------------------------------------- get_reduction_per_condition ---------------------------------

# TODO

# -------------------------------------- get_policy_improvement --------------------------------------

def test_get_policy_improvement_filter_purpose(default_parameters):
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 'building_category': BuildingCategory.KINDERGARTEN})

    assert e_r_filter.get_policy_improvement(tek='default',
                                             purpose=EnergyPurpose.LIGHTING) == (YearRange(2011, 2012), 0.5)
    assert e_r_filter.get_policy_improvement(tek='default', purpose='meaningoflife') is None


def test_get_policy_improvement_filter_tek(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,lighting,2011,2012,0.5
                         default,TEK17,lighting,2012,2013,0.9""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    tek17_and_lighting = e_r_filter.get_policy_improvement(tek='TEK17', purpose=EnergyPurpose.LIGHTING)
    assert tek17_and_lighting == (YearRange(2012, 2013), 0.9)

    unknown_tek_and_lighting = e_r_filter.get_policy_improvement(tek='meaningoflife', purpose=EnergyPurpose.LIGHTING)
    assert unknown_tek_and_lighting == (YearRange(2011, 2012), 0.5)


def test_get_policy_improvement_use_default(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,default,default,2011,2012,0.5""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    assert e_r_filter.get_policy_improvement(tek='TEK17', purpose=EnergyPurpose.COOLING) == (YearRange(2011, 2012), 0.5)


def test_get_policy_improvement_filter_purpose_and_tek(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         default,default,heating_rv,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose='heating_rv') == (YearRange(2012, 2013), 0.2)


def test_get_policy_improvement_filter_building_category_return_default_building_category(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    tek01_and_lighting = e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
    assert tek01_and_lighting == (YearRange(2011, 2012), 0.1)


def test_get_policy_improvement_filter_building_category_return_default_building_category(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.1
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    tek01_and_lighting = e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
    assert tek01_and_lighting == (YearRange(2011, 2012), 0.1)


def test_get_policy_improvement_filter_building_category_none(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING) is None


# -------------------------------------- get_yearly_improvements -------------------------------------

def test_get_yearly_improvements_filter_purpose(default_parameters):
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 'building_category': BuildingCategory.HOUSE})

    assert e_r_filter.get_yearly_improvements(tek='default', purpose='electrical_equipment') == 0.1

def test_get_yearly_improvements_filter_purpuse_use_default(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,default,0.9
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='not_a_purpose') == 0.9

def test_get_yearly_improvements_purpose_not_in_df(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,electrical_equipment,0.1
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    assert e_r_filter.get_yearly_improvements(tek='default', purpose='not_a_purpose') == 0.0
