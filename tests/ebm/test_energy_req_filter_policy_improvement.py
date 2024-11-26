import io
import typing
import re
import pytest

import pandas as pd

from ebm.model.database_manager import DatabaseManager
from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement_filter import EnergyRequirementFilter
from ebm.model.exceptions import AmbiguousDataError


@pytest.fixture
def policy_improvement() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
default,default,lighting,2011,2012,0.5
default,TEK01,lighting,2011,2012,0.123
apartment_block,TEK02,lighting,2012,2013,0.234
default,TEK02,cooling,2011,2030,0.345
default,TEK01,default,2011,2012,0.456
default,default,default,2011,2012,0.99                                                                                                         
""".strip()), skipinitialspace=True)


@pytest.fixture
def no_default_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
apartment_block,TEK02,lighting,2012,2013,0.234                                                                                                        
""".strip()), skipinitialspace=True)


@pytest.fixture
def default_parameters(policy_improvement) \
        -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.APARTMENT_BLOCK,
            'original_condition': pd.DataFrame(),
            'reduction_per_condition': pd.DataFrame(),
            'yearly_improvements': pd.DataFrame(),
            'policy_improvement': policy_improvement}


@pytest.mark.parametrize('tek,purpose,expected_value',
                         [('PRE_TEK49_RES_1950', EnergyPurpose.LIGHTING, (YearRange(2011, 2012), 0.5)),
                          ('TEK01', EnergyPurpose.LIGHTING, (YearRange(2011, 2012), 0.123)),
                          ('TEK02', EnergyPurpose.LIGHTING, (YearRange(2012, 2013), 0.234)),
                          ('TEK01', EnergyPurpose.COOLING, (YearRange(2011, 2012), 0.456)),
                          ])
def test_get_policy_improvement_return_value_for_best_match(default_parameters,
                                                            tek,
                                                            purpose,
                                                            expected_value):
    """
    Return value for best match on filter variables (building_category, tek and purpose). 
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters})
    result = e_r_filter.get_policy_improvement(tek=tek, purpose=purpose)
    assert result == expected_value


def test_get_policy_improvement_default_value_when_not_found(default_parameters):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    value of those 'default' options.  
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN})
    result = e_r_filter.get_policy_improvement(tek='TEK17', purpose=EnergyPurpose.COOLING)
    expected_value = (YearRange(2011, 2012), 0.99)
    assert result == expected_value


def test_get_policy_improvement_return_false_value_when_building_category_not_found(default_parameters,
                                                                                    no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': no_default_df})
    result = e_r_filter.get_policy_improvement(tek='TEK02', purpose=EnergyPurpose.LIGHTING)
    expected_value = None
    assert result == expected_value


def test_get_policy_improvement_return_false_value_when_purpose_not_found(default_parameters,
                                                                          no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'policy_improvement': no_default_df})
    result = e_r_filter.get_policy_improvement(tek='TEK02', purpose=EnergyPurpose.COOLING)
    expected_value = None
    assert result == expected_value


def test_get_policy_improvement_return_false_value_when_tek_not_found(default_parameters,
                                                                      no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'policy_improvement': no_default_df})
    result = e_r_filter.get_policy_improvement(tek='TEK17', purpose=EnergyPurpose.LIGHTING)
    expected_value = None
    assert result == expected_value


def test_get_policy_improvement_return_value_when_matches_has_equal_priority(default_parameters):
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2030,0.1
                         house,default,lighting,2011,2030,0.2
                         house,TEK01,default,2011,2030,0.3                                                 
                         default,default,default,2011,2030,0.4
                         """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.HOUSE,
                                            'policy_improvement': policy_improvement})
    result = e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
    expected =  (YearRange(2011, 2030), 0.3)
    assert result == expected


def test_get_policy_improvement_raise_error_for_duplicate_rows_with_different_values(default_parameters):
    """
    Raise an AmbiguousDataError when there are duplicate rows for 'building_category', 'tek' and 'purpose' 
    and one or more of the corresponding values ('period_start_year', 'period_end_year', 'improvement_at_period_end') 
    are different. In this case, the method have no way of deciding which value is correct and the program should crash.
    """
    policy_improvement = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
            house,TEK01,lighting,2011,2030,0.1 
            house,TEK01,lighting,2012,2031,0.2
            default,TEK01,lighting,2013,2033,0.3
            default,TEK01,lighting,2014,2034,0.4                                                                                                                                                                                                                            
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'policy_improvement': policy_improvement}) 
    expected_error_msg = re.escape(
        "Conflicting data found in 'policy_improvement' dataframe for "
        "building_category='house', tek='TEK01' and purpose='lighting'."
    )        
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)    
