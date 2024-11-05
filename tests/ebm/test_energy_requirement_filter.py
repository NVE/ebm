import io
import typing
import re
import pytest

import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model import BuildingCategory
from ebm.model.energy_requirement_filter import EnergyRequirementFilter


@pytest.fixture
def original_condition() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,TEK,purpose,kwh_m2
apartment_block,PRE_TEK49_RES_1950,cooling,1.1
apartment_block,PRE_TEK49_RES_1950,electrical_equipment,2.2
apartment_block,PRE_TEK49_RES_1950,fans_and_pumps,3.3
apartment_block,PRE_TEK49_RES_1950,heating_dhw,4.4
apartment_block,PRE_TEK49_RES_1950,heating_rv,5.5
apartment_block,PRE_TEK49_RES_1950,lighting,5.5
apartment_block,TEK07,cooling,2.1                                                                      
default,TEK21,cooling,3.1
default,TEK17,default,3.2                                   
default,default,default,3.3                                   
""".strip()), skipinitialspace=True)


@pytest.fixture
def reduction_per_condition() -> pd.DataFrame:
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
def policy_improvement() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
default,default,lighting,2011,2012,0.5
""".strip()), skipinitialspace=True)


@pytest.fixture
def yearly_improvements() -> pd.DataFrame:
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


def test_instance_var_dtype(default_parameters):
    with pytest.raises(TypeError, match="'original_condition' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'original_condition': None})

    with pytest.raises(TypeError, match="'reduction_per_condition' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'reduction_per_condition': None})

    with pytest.raises(TypeError, match="'yearly_improvements' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'yearly_improvements': None})

    with pytest.raises(TypeError, match="'policy_improvement' expected to be of type pd.DataFrame. Got: <class 'NoneType'>"):
        EnergyRequirementFilter(**{**default_parameters, 'policy_improvement': None})


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
