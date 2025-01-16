import io
import typing
import re
import pytest

import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.energy_requirement_filter import EnergyRequirementFilter
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.exceptions import AmbiguousDataError

#TODO: add more tests for the helper methods

@pytest.fixture
def default_parameters() \
        -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.APARTMENT_BLOCK,
            'original_condition': pd.DataFrame(),
            'reduction_per_condition': pd.DataFrame(),
            'yearly_improvements': pd.DataFrame(),
            'policy_improvement': pd.DataFrame()}


def test_instance_var_dtype(default_parameters):
    with pytest.raises(TypeError, match="'original_condition' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'original_condition': None})

    with pytest.raises(TypeError, match="'reduction_per_condition' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'reduction_per_condition': None})

    with pytest.raises(TypeError, match="'yearly_improvements' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'yearly_improvements': None})

    with pytest.raises(TypeError, match="'policy_improvement' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'policy_improvement': None})


def test_apply_filter(default_parameters):
    df = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value
    apartment_block,TEK01,lighting,100
    default,default,default,110
    house,default,default,110                                                                                                                                                                                      
    """), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters})
    result = e_r_filter._apply_filter(df, 
                                      building_category=BuildingCategory.APARTMENT_BLOCK,
                                      tek= 'TEK01',
                                      purpose=EnergyPurpose.LIGHTING)
    expected = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value
    apartment_block,TEK01,lighting,100
    default,default,default,110
    """), skipinitialspace=True)
    pd.testing.assert_frame_equal(result, expected)


def test_add_priority(default_parameters):
    df = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value
    default,default,default,110
    apartment_block,TEK01,lighting,100                                                                                                                                                                                                                 
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters})
    result = e_r_filter._add_priority(df)
    result.reset_index(drop=True, inplace=True)     
    expected = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value,priority
    apartment_block,TEK01,lighting,100,3
    default,default,default,110,0                                                                                                                                                                                                                                                    
    """.strip()), skipinitialspace=True)
    pd.testing.assert_frame_equal(result,expected)


def test_check_and_resolve_tied_priority(default_parameters):
    df = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value,priority
    default,TEK01,lighting,0.3,2
    house,default,lighting,0.2,2
    house,TEK01,default,0.1,2                                                                                                                                                                                                                                                   
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters})
    result = e_r_filter._check_and_resolve_tied_priority(df)
    result.reset_index(drop=True, inplace=True)  
    expected = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,value,priority,building_category_rank,TEK_rank,purpose_rank
    house,TEK01,default,0.1,2,1,1,0
    house,default,lighting,0.2,2,1,0,1                                       
    default,TEK01,lighting,0.3,2,0,1,1
    """.strip()), skipinitialspace=True)
    pd.testing.assert_frame_equal(result,expected)


def test_check_conflicting_data(default_parameters):
    df = pd.read_csv(io.StringIO("""
        building_category,TEK,purpose,value
        house,TEK01,lighting,0.1 
        house,TEK01,lighting,0.2
        default,TEK01,lighting,0.3
        default,TEK01,lighting,0.4                                                                                                                                                                                                                                
        """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters}) 
    expected_error_msg = re.escape(
        "yey"
    ) 
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter._check_conflicting_data(df=df,
                                           subset_cols=['building_category', 'TEK', 'purpose'],
                                           conflict_col='value',
                                           error_msg="yey")
    

@pytest.mark.skip
def test_new_instance():
    building_category = BuildingCategory.APARTMENT_BLOCK
    energy_requirement_filter = EnergyRequirementFilter.new_instance(building_category)
    dm = DatabaseManager()
    expected_original_condition = dm.get_energy_req_original_condition()
    expected_reduction_per_condition = dm.get_energy_req_reduction_per_condition()
    expected_yearly_improvements = dm.get_energy_req_yearly_improvements()
    expected_policy_improvement = dm.get_energy_req_policy_improvements()

    assert isinstance(energy_requirement_filter, EnergyRequirementFilter)
    assert energy_requirement_filter.building_category == building_category
    pd.testing.assert_frame_equal(energy_requirement_filter.original_condition, expected_original_condition)
    pd.testing.assert_frame_equal(energy_requirement_filter.reduction_per_condition, expected_reduction_per_condition)
    pd.testing.assert_frame_equal(energy_requirement_filter.yearly_improvements, expected_yearly_improvements)
    pd.testing.assert_frame_equal(energy_requirement_filter.policy_improvement, expected_policy_improvement)
