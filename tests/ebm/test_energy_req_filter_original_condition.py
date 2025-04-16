import io
import typing
import re
import pytest

import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.energy_need_filter import filter_original_condition
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement_filter import EnergyRequirementFilter
from ebm.model.exceptions import AmbiguousDataError


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
def default_parameters(original_condition) \
        -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.APARTMENT_BLOCK,
            'original_condition': original_condition,
            'reduction_per_condition': pd.DataFrame(),
            'yearly_improvements': pd.DataFrame(),
            'policy_improvement': pd.DataFrame()}


@pytest.mark.parametrize('tek,purpose,expected_value',
                         [('PRE_TEK49_RES_1950', EnergyPurpose.COOLING, 1.1),
                          ('TEK07', EnergyPurpose.COOLING, 2.1),
                          ('TEK21', EnergyPurpose.COOLING, 3.1),
                          ('TEK17', EnergyPurpose.COOLING, 3.2),
                          ])
def test_get_orginal_condition_return_value_for_best_match(default_parameters,
                                                           tek: str,
                                                           purpose: EnergyPurpose,
                                                           expected_value: float):
    """
    Return value for best match on filter variables (building_category, tek and purpose). 
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters})
    result = e_r_filter.get_original_condition(tek=tek, purpose=purpose)

    assert result == expected_value

    rs = filter_original_condition(default_parameters.get('original_condition'),
                              building_category='apartment_block',
                              tek=tek,
                              purpose=purpose)
    assert len(rs) == 1
    assert rs.iloc[0].kwh_m2 == expected_value


def test_get_orginal_condition_return_default_value_when_not_found(default_parameters):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    value of those 'default' options.  
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.CULTURE})
    result = e_r_filter.get_original_condition(tek='TEK07', purpose=EnergyPurpose.ELECTRICAL_EQUIPMENT)
    assert result == 3.3

    rs = filter_original_condition(default_parameters.get('original_condition'),
                              building_category='apartment_block',
                              tek='TEK07',
                              purpose=EnergyPurpose.ELECTRICAL_EQUIPMENT)
    assert len(rs) == 1
    assert rs.iloc[0].kwh_m2 == 3.3


def test_get_orginal_condition_return_false_value_when_building_category_not_found(default_parameters):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,PRE_TEK49_RES_1950,cooling,1.1                                                                                                                                                                                                                                           
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.HOUSE,
                                            'original_condition':original_condition})
    result = e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose=EnergyPurpose.COOLING)
    assert result == 0.0

    rs = filter_original_condition(original_condition,
                              building_category='house',
                              tek='PRE_TEK49_RES_1950',
                              purpose=EnergyPurpose.COOLING)
    assert len(rs) == 0



def test_get_orginal_condition_return_false_value_when_purpose_not_found(default_parameters):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,PRE_TEK49_RES_1950,cooling,1.1                                                                                                                                                                                                                                           
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.APARTMENT_BLOCK,
                                            'original_condition':original_condition})
    result = e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose=EnergyPurpose.LIGHTING)
    assert result == 0.0


def test_get_orginal_condition_return_false_value_when_tek_not_found(default_parameters):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,PRE_TEK49_RES_1950,cooling,1.1                                                                                                                                                                                                                                           
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                               'building_category': BuildingCategory.APARTMENT_BLOCK,
                                               'original_condition':original_condition})
    result = e_r_filter.get_original_condition(tek='TEK21', purpose=EnergyPurpose.COOLING)
    assert result == 0.0

    rs = filter_original_condition(original_condition,
                              building_category=BuildingCategory.APARTMENT_BLOCK,
                              tek='TEK21',
                              purpose=EnergyPurpose.COOLING)
    assert len(rs) == 0



def test_get_original_condition_return_value_when_match_has_same_priority(default_parameters):
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    default,TEK07,cooling,0.1
    apartment_block,default,cooling,0.2                                                                                   
    apartment_block,TEK07,default,0.3
    default,default,default,0.99                                                                                                                                                                                                                                                                                          
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                               'building_category': BuildingCategory.APARTMENT_BLOCK,
                                               'original_condition':original_condition})
    result = e_r_filter.get_original_condition(tek='TEK07', purpose=EnergyPurpose.COOLING)
    assert result == 0.3

    rs = filter_original_condition(original_condition,
                              building_category=BuildingCategory.APARTMENT_BLOCK,
                              tek='TEK07',
                              purpose=EnergyPurpose.COOLING)
    assert len(rs) == 1
    assert rs.iloc[0].kwh_m2 == 0.1 # Diverging implementation


def test_get_original_condition_raise_error_for_duplicate_rows_with_different_values(default_parameters):
    """
    Raise an AmbiguousDataError when there are duplicate rows for 'building_category', 'tek' and 'purpose' 
    and the corresponding value ('kwh_m2') is different. In this case, the method have no way of deciding
    which value is correct and the program should crash. 
    """
    original_condition = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,TEK07,cooling,0.1 
    apartment_block,TEK07,cooling,0.2                                                                                                                                                                                                                                                                                     
    """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                               'building_category': BuildingCategory.APARTMENT_BLOCK,
                                               'original_condition':original_condition})
    expected_error_msg = re.escape(
        "Conflicting data found in 'original_condition' dataframe for "
        "building_category='apartment_block', tek='TEK07' and purpose='cooling'."
    )
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_original_condition(tek='TEK07', purpose=EnergyPurpose.COOLING)
