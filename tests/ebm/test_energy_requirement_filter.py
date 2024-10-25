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
from ebm.model.custom_exceptions import AmbiguousDataError


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
apartment_block,TEK07,electrical_equipment,2.2                      
apartment_block,TEK07,default,7.0
apartment_block,default,cooling,7.1
default,TEK07,cooling,7.3
apartment_block,default,default,7.4
default,default,cooling,7.5
default,default,default,7.6
house,PRE_TEK49_RES_1950,cooling,3.1
house,PRE_TEK49_RES_1950,electrical_equipment,3.2
house,TEK07,cooling,4.1
house,TEK07,electrical_equipment,4.2                                                                                                                                                                                                                                            
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

@pytest.fixture
def reduction_value_name() -> str:
    return 'reduction_share'

# -------------------------------------- init method ------------------------------------------------
#TODO: add match string to the rest
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
#TODO: evaluate if default should be used when values that doesn't make sense are passed
# - could ensure that the passed filter values also must be a BuildingCategory or EnergyPurpose in order
# for default to be used, but currently we do not have any criteria defined for TEK.  
def test_filter_df_filter_values_goes_to_default_when_not_in_filter_col(default_parameters):
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

def test_get_orginal_condition_return_df_for_specified_building_category_tek_purpose(default_parameters):
    """
    Return df for best match on filter variables (building_category, tek and purpose) when all the 
    specified filter variables are present in the original dataframe. 
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                               'building_category': BuildingCategory.APARTMENT_BLOCK})
    result1 = e_r_filter.get_original_condition(tek='PRE_TEK49_RES_1950', purpose=EnergyPurpose.COOLING)
    expected1 = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,PRE_TEK49_RES_1950,cooling,1.1                                                                                                                                                                                                                                         
    """.strip()), skipinitialspace=True)
    pd.testing.assert_frame_equal(result1, expected1)

    result2 = e_r_filter.get_original_condition(tek='TEK07', purpose=EnergyPurpose.ELECTRICAL_EQUIPMENT)
    expected2 = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    apartment_block,TEK07,electrical_equipment,2.2
    """.strip()), skipinitialspace=True)
    pd.testing.assert_frame_equal(result2, expected2)


# TODO:
# - 'default' should not be returned in columns, but be replaced with the given category, tek and purpose (if this should return df)  
# - is it necessary to have individual checks on this for building_cat, tek and purpose? (applies to all method tests in script) 
def test_get_orginal_condition_return_default_df_when_not_found(default_parameters):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    df of those 'default' options.  
    """
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.CULTURE})
    result = e_r_filter.get_original_condition(tek='TEK07', purpose=EnergyPurpose.ELECTRICAL_EQUIPMENT)
    expected = pd.read_csv(io.StringIO("""
    building_category,TEK,purpose,kwh_m2
    default,default,default,7.6""".strip()), skipinitialspace=True)
    pd.testing.assert_frame_equal(result, expected)


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
    expected = pd.DataFrame(data={'building_category': {0: BuildingCategory.HOUSE},
                                  'TEK': {0: 'PRE_TEK49_RES_1950'},
                                  'purpose': {0: EnergyPurpose.COOLING},
                                  'kwh_m2': {0: 0.0}})
    pd.testing.assert_frame_equal(result, expected)


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
    expected = pd.DataFrame(data={'building_category': {0: BuildingCategory.APARTMENT_BLOCK},
                                  'TEK': {0: 'PRE_TEK49_RES_1950'},
                                  'purpose': {0: EnergyPurpose.LIGHTING},
                                  'kwh_m2': {0: 0.0}})
    pd.testing.assert_frame_equal(result, expected)


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
    expected = pd.DataFrame(data={'building_category': {0: BuildingCategory.APARTMENT_BLOCK},
                                  'TEK': {0: 'TEK21'},
                                  'purpose': {0: EnergyPurpose.COOLING},
                                  'kwh_m2': {0: 0.0}})
    pd.testing.assert_frame_equal(result, expected)

# -------------------------------------- get_reduction_per_condition ---------------------------------

def test_get_reduction_per_condition_return_df_for_specified_building_category_tek_purpose(default_parameters, reduction_value_name):
    """
    Return df for best match on filter variables (building_category, tek and purpose) when all the 
    specified filter variables are present in the original dataframe. 
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                                building_category,TEK,purpose,building_condition,reduction_share
                                house,TEK17,heating_rv,original_condition,0.0
                                house,TEK17,heating_rv,small_measure,0.07
                                house,TEK17,heating_rv,renovation,0.2
                                house,TEK17,heating_rv,renovation_and_small_measure,0.25
                                default,TEK17,heating_rv,original_condition,0.123                      
                                house,default,heating_rv,original_condition,0.123
                                house,TEK17,default,original_condition,0.123 
                                default,default,default,original_condition,0.123                                           
                                """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK17', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                             1: 'small_measure',
                                                             2: 'renovation',
                                                             3: 'renovation_and_small_measure'},
                                   reduction_value_name: {0: 0.0, 1: 0.07, 2: 0.2, 3: 0.25}})
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_default_df_when_not_found(default_parameters, reduction_value_name):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    df of those 'default' options.  
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                                building_category,TEK,purpose,building_condition,reduction_share
                                default,default,default,original_condition,0.0
                                default,default,default,small_measure,0.07
                                default,default,default,renovation,0.2
                                default,default,default,renovation_and_small_measure,0.25                                          
                                """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK17', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                             1: 'small_measure',
                                                             2: 'renovation',
                                                             3: 'renovation_and_small_measure'},
                                   reduction_value_name: {0: 0.0, 1: 0.07, 2: 0.2, 3: 0.25}})
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_false_value_when_building_category_not_found(default_parameters, reduction_value_name):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                                building_category,TEK,purpose,building_condition,reduction_share
                                house,TEK17,heating_rv,original_condition,0.0
                                house,TEK17,heating_rv,small_measure,0.07
                                house,TEK17,heating_rv,renovation,0.2
                                house,TEK17,heating_rv,renovation_and_small_measure,0.25
                                """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.KINDERGARTEN,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK17', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0: 0.0, 1: 0, 2: 0, 3: 0}})
    pd.testing.assert_frame_equal(result, expected)

def test_get_reduction_per_condition_return_false_value_when_purpose_not_found(default_parameters, reduction_value_name):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                                building_category,TEK,purpose,building_condition,reduction_share
                                house,TEK17,heating_rv,original_condition,0.0
                                house,TEK17,heating_rv,small_measure,0.07
                                house,TEK17,heating_rv,renovation,0.2
                                house,TEK17,heating_rv,renovation_and_small_measure,0.25
                                """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK17', purpose=EnergyPurpose.LIGHTING)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0: 0.0, 1: 0, 2: 0, 3: 0}})
    pd.testing.assert_frame_equal(result, expected)

def test_get_reduction_per_condition_return_false_value_when_tek_not_found(default_parameters, reduction_value_name):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                                building_category,TEK,purpose,building_condition,reduction_share
                                house,TEK17,heating_rv,original_condition,0.0
                                house,TEK17,heating_rv,small_measure,0.07
                                house,TEK17,heating_rv,renovation,0.2
                                house,TEK17,heating_rv,renovation_and_small_measure,0.25
                                """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0: 0.0, 1: 0, 2: 0, 3: 0}})
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_value_for_best_match_on_filter_variables_example1(default_parameters, reduction_value_name):
    """
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                            building_category,TEK,purpose,building_condition,reduction_share
                            house,TEK17,heating_rv,original_condition,0.0
                            house,TEK17,heating_rv,small_measure,0.07
                            house,TEK17,heating_rv,renovation,0.2
                            house,TEK17,heating_rv,renovation_and_small_measure,0.25
                            default,TEK21,heating_rv,original_condition,0.123
                            default,TEK21,heating_rv,small_measure,0.234
                            default,TEK21,heating_rv,renovation,0.345
                            default,TEK21,heating_rv,renovation_and_small_measure,0.456
                            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0 : 0.123, 1: 0.234, 2: 0.345, 3: 0.456}})
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_value_for_best_match_on_filter_variables_example2(default_parameters, reduction_value_name):
    """
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                            building_category,TEK,purpose,building_condition,reduction_share
                            house,TEK17,heating_rv,original_condition,0.0
                            house,TEK17,heating_rv,small_measure,0.07
                            house,TEK17,heating_rv,renovation,0.2
                            house,TEK17,heating_rv,renovation_and_small_measure,0.25
                            default,TEK21,default,original_condition,0.123
                            default,TEK21,default,small_measure,0.234
                            default,TEK21,default,renovation,0.345
                            default,TEK21,default,renovation_and_small_measure,0.456
                            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    result = e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.LIGHTING)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0 : 0.123, 1: 0.234, 2: 0.345, 3: 0.456}})
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_correct_df_when_matches_has_equal_priority(default_parameters, reduction_value_name):
    """
    If all matches fits the given params, then prioritize in this order: building_category, tek and purpose 
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                        building_category,TEK,purpose,building_condition,reduction_share
                        default,TEK21,heating_rv,original_condition,0.11
                        default,TEK21,heating_rv,small_measure,0.12
                        default,TEK21,heating_rv,renovation,0.13
                        default,TEK21,heating_rv,renovation_and_small_measure,0.14
                        house,default,heating_rv,original_condition,0.21
                        house,default,heating_rv,small_measure,0.22
                        house,default,heating_rv,renovation,0.23
                        house,default,heating_rv,renovation_and_small_measure,0.24
                        house,TEK21,default,original_condition,0.31
                        house,TEK21,default,small_measure,0.32
                        house,TEK21,default,renovation,0.33
                        house,TEK21,default,renovation_and_small_measure,0.34
                        default,default,default,original_condition,0.9
                        default,default,default,small_measure,0.9
                        default,default,default,renovation,0.9
                        default,default,default,renovation_and_small_measure,0.9                                                                                                                                                              
                        """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                        1: 'small_measure',
                                                        2: 'renovation',
                                                        3: 'renovation_and_small_measure'},
                                reduction_value_name: {0 : 0.31, 1: 0.32, 2: 0.33, 3: 0.34}})
    result = e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.HEATING_RV)
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_raise_error_for_duplicate_rows_with_different_values(default_parameters, reduction_value_name):
    """
    Test to ensure an AmbiguousDataError is raised when duplicate rows
    with different 'reduction_share' values are found.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                        building_category,TEK,purpose,building_condition,reduction_share
                        house,TEK21,heating_rv,original_condition,0.11
                        house,TEK21,heating_rv,small_measure,0.12
                        house,TEK21,heating_rv,renovation,0.13
                        house,TEK21,heating_rv,renovation_and_small_measure,0.14
                        house,TEK21,heating_rv,original_condition,0.21
                        house,TEK21,heating_rv,small_measure,0.22
                        house,TEK21,heating_rv,renovation,0.23
                        house,TEK21,heating_rv,renovation_and_small_measure,0.24
                        default,default,default,original_condition,0.31
                        default,default,default,small_measure,0.32
                        default,default,default,renovation,0.33
                        default,default,default,renovation_and_small_measure,0.34
                        default,default,default,original_condition,0.9
                        default,default,default,small_measure,0.9
                        default,default,default,renovation,0.9
                        default,default,default,renovation_and_small_measure,0.9                                                                                                                                                              
                        """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})
    expected_error_msg = re.escape(
        "Conflicting data found for building_category='house', tek='TEK21' "
        "and purpose='heating_rv', in file 'energy_requirement_reduction_per_condition'."
    )
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.HEATING_RV)

# add tests on this where same building condition is duplicated
def test_get_reduction_per_condition_return_df_with_default_values_when_building_condition_missing(default_parameters, reduction_value_name):
    """
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
                        building_category,TEK,purpose,building_condition,reduction_share
                        house,TEK21,heating_rv,original_condition,0.11
                        house,TEK21,heating_rv,small_measure,0.12
                        default,default,default,original_condition,0.9
                        default,default,default,small_measure,0.9
                        default,default,default,renovation,0.9
                        default,default,default,renovation_and_small_measure,0.9                                                                                                                                                              
                        """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category':BuildingCategory.HOUSE,
                                            'reduction_per_condition': reduction_per_condition})

    result = e_r_filter.get_reduction_per_condition(tek='TEK21', purpose=EnergyPurpose.HEATING_RV)
    expected = pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                                         1: 'small_measure',
                                                         2: 'renovation',
                                                         3: 'renovation_and_small_measure'},
                                  reduction_value_name: {0 : 0.11, 1: 0.12, 2: 0.0, 3: 0.0}})
    pd.testing.assert_frame_equal(result, expected)


# -------------------------------------- get_policy_improvement --------------------------------------

#TODO: refactor and add/change tests as done for get_orginal_condition and get_reduction_per_condition

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
                         building_category,TEK,purpose,period_start_year,period_end_year,"improvement_at_period_end"
                         default,TEK01,lighting,2011,2012,0.1
                         default,default,heating_rv,2012,2013,0.2                       
                         """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})
    tek01_heating_rv = e_r_filter.get_policy_improvement(tek='TEK01', purpose='heating_rv')  
    assert tek01_heating_rv == (YearRange(2012, 2013), 0.2)


def test_get_policy_improvement_filter_building_category_none(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         house,TEK01,lighting,2012,2013,0.2""".strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.KINDERGARTEN,
                                            'policy_improvement': policy_improvement})

    assert e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING) is None

#TODO: parameterize tests
def test_get_policy_improvement_return_value_for_best_match_case1(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK01,lighting,2011,2012,0.123
                         house,TEK02,lighting,2012,2013,0.2
                         """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.HOUSE,
                                            'policy_improvement': policy_improvement})

    result = e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
    expected =  (YearRange(2011, 2012), 0.123)
    assert result == expected

def test_get_policy_improvement_return_value_for_best_match_case2(default_parameters):
    policy_improvement = pd.read_csv(io.StringIO("""
                         building_category,TEK,purpose,period_start_year,period_end_year,improvement_at_period_end
                         default,TEK02,lighting,2011,2030,0.5
                         default,TEK01,default,2011,2012,0.123
                         """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters,
                                            'building_category': BuildingCategory.HOUSE,
                                            'policy_improvement': policy_improvement})

    result = e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)
    expected =  (YearRange(2011, 2012), 0.123)
    assert result == expected

def test_get_policy_improvement_return_value_when_matches_has_equal_priority(default_parameters):
    """
    If all matches fits the given params, then prioritize in this order: building_category, tek and purpose 
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
    Test to ensure an AmbiguousDataError is raised when duplicate rows
    with different values are found in the value columns: period_start_year,
    period_end_year, improvement_at_period_end.
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
        "Conflicting data found for building_category='house', tek='TEK01' "
        "and purpose='lighting', in file 'energy_requirement_policy_improvements'."
    )
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_policy_improvement(tek='TEK01', purpose=EnergyPurpose.LIGHTING)    

# -------------------------------------- get_yearly_improvements -------------------------------------

#TODO: refactor and add/change tests as done for get_orginal_condition and get_reduction_per_condition

def test_get_yearly_improvements_use_default(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,default,0.9
            """.strip()), skipinitialspace=True)
    
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    house_tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.COOLING)
    assert house_tek01_cooling == 0.9

def test_get_yearly_improvements_filter_building_category(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,default,0.8
            kindergarten,default,default,0.9
            house,default,default,0.123
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    house_tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.COOLING) 
    assert house_tek01_cooling == 0.123

def test_get_yearly_improvements_return_false_value_when_building_category_not_found(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            kindergarten,default,default,0.9
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    house_tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.COOLING) 
    assert house_tek01_cooling == 0.0

def test_get_yearly_improvements_filter_purpose(default_parameters):
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 'building_category': BuildingCategory.HOUSE})
    
    default_and_lighting = e_r_filter.get_yearly_improvements(tek='default', purpose=EnergyPurpose.LIGHTING)
    assert default_and_lighting == 0.05

def test_get_yearly_improvements_purpose_not_in_df(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,default,electrical_equipment,0.1
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    default_and_not_a_purpose = e_r_filter.get_yearly_improvements(tek='default', purpose=EnergyPurpose.LIGHTING)
    assert default_and_not_a_purpose == 0.0

def test_get_yearly_improvements_filter_tek(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,TEK01,cooling,0.1
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    tek01_and_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.COOLING) 
    assert tek01_and_cooling == 0.1

def test_get_yearly_improvements_tek_not_in_df(default_parameters):
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,TEK01,cooling,0.1
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    
    tek02_and_cooling = e_r_filter.get_yearly_improvements(tek='TEK02', purpose=EnergyPurpose.COOLING) 
    assert tek02_and_cooling == 0.0


def test_get_yearly_improvements_return_value_for_best_match_on_filter_variables_example1(default_parameters):
    """
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,TEK01,cooling,0.1
            house,TEK02,cooling,0.123                                                   
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.COOLING) 
    assert tek01_cooling == 0.1


def test_get_yearly_improvements_return_value_for_best_match_on_filter_variables_example2(default_parameters):
    """
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,TEK02,lighting,0.5 
            default,TEK01,default,0.123                                                                                                   
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.LIGHTING) 
    assert tek01_cooling == 0.123

def test_get_yearly_improvements_return_value_for_best_match_on_filter_variables_example3(default_parameters):
    """
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            house,TEK02,lighting,0.5
            default,TEK01,default,0.6
            house,default,default,0.7
            kindergarten,TEK01,lighting,0.8
            default,TEK01,lighting,0.123                                                                                                                                                     
            """), skipinitialspace=True)
    yearly_improvements.columns = yearly_improvements.columns.str.strip()
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.LIGHTING) 
    assert tek01_cooling == 0.123


def test_get_yearly_improvements_return_value_when_match_has_same_priority(default_parameters):
    """
    If all matches fits the given params, then prioritize in this order: building_category, tek and purpose 
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            default,TEK01,lighting,0.3
            house,default,lighting,0.2
            house,TEK01,default,0.1
            default,default,default,0.99                                                                                                                                                     
            """), skipinitialspace=True)
    yearly_improvements.columns = yearly_improvements.columns.str.strip()
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements})
    tek01_cooling = e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.LIGHTING) 
    assert tek01_cooling == 0.1


def test_get_yearly_improvements_raise_error_for_duplicate_rows_with_different_values(default_parameters):
    """
    Test to ensure an AmbiguousDataError is raised when duplicate rows
    with different 'yearly_efficiency_improvement' values are found.
    """
    yearly_improvements = pd.read_csv(io.StringIO("""
            building_category,TEK,purpose,yearly_efficiency_improvement
            house,TEK01,lighting,0.1 
            house,TEK01,lighting,0.2
            default,TEK01,lighting,0.3
            default,TEK01,lighting,0.4                                                                                                                                                                                                                                
            """.strip()), skipinitialspace=True)
    e_r_filter = EnergyRequirementFilter(**{**default_parameters, 
                                            'building_category': BuildingCategory.HOUSE,
                                            'yearly_improvements': yearly_improvements}) 
    expected_error_msg = re.escape(
        "Conflicting data found for building_category='house', tek='TEK01', "
        "and purpose='lighting', in file 'energy_requirement_yearly_improvements'."
    )
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        e_r_filter.get_yearly_improvements(tek='TEK01', purpose=EnergyPurpose.LIGHTING)    

# -------------------------------------- new_instance ------------------------------------------------


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
