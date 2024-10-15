import io
import typing

import pandas as pd
import pytest

from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement_filter import EnergyRequirementFilter


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
