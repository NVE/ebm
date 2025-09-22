import io
import typing
import re
import pytest

import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.energy_need_filter import filter_original_condition
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.energy_requirement import EnergyRequirement
from ebm.model.exceptions import AmbiguousDataError


@pytest.fixture
def yearly_improvements() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,building_code,purpose,yearly_efficiency_improvement
default,default,cooling,0.0
default,default,electrical_equipment,0.1
default,default,fans_and_pumps,0.0
default,default,heating_dhw,0.0
default,default,lighting,0.05
default,TEK01,cooling,0.123
apartment_block,TEK02,cooling,0.234
default,TEK02,lighting,0.345
default,TEK01,default,0.456
apartment_block,TEK90,cooling,0.99
default,default,default,0.9                                                                                                                                                 
""".strip()), skipinitialspace=True)


@pytest.fixture
def no_default_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,building_code,purpose,yearly_efficiency_improvement
apartment_block,TEK90,cooling,0.99
""".strip()), skipinitialspace=True)


@pytest.fixture
def default_parameters(yearly_improvements) -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.APARTMENT_BLOCK,
            'original_condition': pd.DataFrame(),
            'reduction_per_condition': pd.DataFrame(),
            'yearly_improvements': yearly_improvements,
            'policy_improvement': pd.DataFrame()}


@pytest.mark.parametrize('tek,purpose,expected_value',
                         [('TEK90', EnergyPurpose.COOLING, 0.99),
                          ('TEK01', EnergyPurpose.COOLING, 0.123),
                          ('TEK01', EnergyPurpose.LIGHTING, 0.456)
                          ])
def test_yearly_improvements_return_value_for_best_match(default_parameters,
                                                         tek,
                                                         purpose,
                                                         expected_value):
    """
    Return value for best match on filter variables (building_category, tek and purpose). 
    """

    rs = filter_original_condition(default_parameters.get('yearly_improvements'),
                              building_category=default_parameters.get('building_category'),
                              tek=tek,
                              purpose=purpose)
    assert len(rs) == 1
    assert rs.iloc[0].yearly_efficiency_improvement == expected_value


def test_get_yearly_improvements_default_value_when_not_found(default_parameters):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    value of those 'default' options.  
    """
    rs = filter_original_condition(default_parameters.get('yearly_improvements'),
                              building_category=default_parameters.get('building_category'),
                              tek='TEK21',
                              purpose=EnergyPurpose.HEATING_RV)
    assert len(rs) == 1
    assert rs.iloc[0].yearly_efficiency_improvement == 0.9


def test_get_yearly_improvements_return_false_value_when_building_category_not_found(default_parameters,
                                                                                     no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """

    rs = filter_original_condition(default_parameters.get('yearly_improvements'),
                              building_category=default_parameters.get('building_category'),
                              tek='TEK90',
                              purpose=EnergyPurpose.HEATING_RV)
    assert len(rs) == 0



def test_get_yearly_improvements_return_false_value_when_purpose_not_found(default_parameters,
                                                                           no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """

    rs = filter_original_condition(default_parameters.get('yearly_improvements'),
                                   building_category=default_parameters.get('building_category'),
                                   tek='TEK90',
                                   purpose=EnergyPurpose.LIGHTING)
    assert len(rs) == 0


def test_get_yearly_improvements_return_false_value_when_building_code_not_found(default_parameters,
                                                                           no_default_df):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """

    rs = filter_original_condition(no_default_df,
                                   building_category=default_parameters.get('building_category'),
                                   tek='building_code',
                                   purpose=EnergyPurpose.cooling)
    assert len(rs) == 0


def test_get_yearly_improvements_return_value_when_match_has_same_priority(default_parameters):
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,building_code,purpose,yearly_efficiency_improvement
            default,TEK01,lighting,0.3
            house,default,lighting,0.2
            house,TEK01,default,0.1
            default,default,default,0.99                                                                                                                                                     
            """), skipinitialspace=True)
    yearly_improvements.columns = yearly_improvements.columns.str.strip()

    rs = filter_original_condition(yearly_improvements,
                              building_category=default_parameters.get('building_category'),
                              tek='TEK01',
                              purpose=EnergyPurpose.LIGHTING)
    assert len(rs) == 1
    assert rs.iloc[0].yearly_efficiency_improvement == 0.3 # diverging implementation


@pytest.mark.skip(reason="EnergyRequirementFilter deprecated")
def test_get_yearly_improvements_raise_error_for_duplicate_rows_with_different_values(default_parameters):
    """
    Raise an AmbiguousDataError when there are duplicate rows for 'building_category', 'tek' and 'purpose' 
    and one or more of the corresponding values ('period_start_year', 'period_end_year', 'improvement_at_period_end') 
    are different. In this case, the method have no way of deciding which value is correct and the program should crash.
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,building_code,purpose,yearly_efficiency_improvement
            house,TEK01,lighting,0.1 
            house,TEK01,lighting,0.2
            default,TEK01,lighting,0.3
            default,TEK01,lighting,0.4                                                                                                                                                                                                                                
            """.strip()), skipinitialspace=True)
    class EnergyRequirementFilter:
        pass
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    expected_error_msg = re.escape(
        "Conflicting data found in 'yearly_improvements' dataframe for "
        "building_category='house', tek='TEK01' and purpose='lighting'."
    )
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
