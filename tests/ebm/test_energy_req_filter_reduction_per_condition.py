import io
import re
import typing

import pandas as pd
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.energy_need_filter import filter_improvement_building_upgrade
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.exceptions import AmbiguousDataError


@pytest.fixture
def reduction_per_condition() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,building_code,purpose,building_condition,reduction_share
house,TEK17,heating_rv,original_condition,0.0
house,TEK17,heating_rv,small_measure,0.07
house,TEK17,heating_rv,renovation,0.2
house,TEK17,heating_rv,renovation_and_small_measure,0.25
default,TEK21,heating_rv,original_condition,0.234
default,TEK21,heating_rv,small_measure,0.234
default,TEK21,heating_rv,renovation,0.234
default,TEK21,heating_rv,renovation_and_small_measure,0.234
default,TEK21,default,original_condition,0.345
default,TEK21,default,small_measure,0.345
default,TEK21,default,renovation,0.345
default,TEK21,default,renovation_and_small_measure,0.345
default,default,default,original_condition,0.456
default,default,default,small_measure,0.456
default,default,default,renovation,0.456
default,default,default,renovation_and_small_measure,0.456
""".strip()), skipinitialspace=True)


@pytest.fixture
def default_parameters(reduction_per_condition) \
        -> typing.Dict[str, pd.DataFrame]:
    return {'building_category': BuildingCategory.HOUSE,
            'original_condition': pd.DataFrame(),
            'reduction_per_condition': reduction_per_condition,
            'yearly_improvements': pd.DataFrame(),
            'policy_improvement': pd.DataFrame()}


@pytest.fixture
def no_default_df() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
building_category,building_code,purpose,building_condition,reduction_share
house,TEK17,heating_rv,original_condition,0.0
house,TEK17,heating_rv,small_measure,0.07
house,TEK17,heating_rv,renovation,0.2
house,TEK17,heating_rv,renovation_and_small_measure,0.25
""".strip()), skipinitialspace=True)


@pytest.fixture
def false_return_value() -> pd.DataFrame:
    return pd.DataFrame([
        [BuildingCondition.ORIGINAL_CONDITION, 0.0],
        [BuildingCondition.SMALL_MEASURE, 0.0],
        [BuildingCondition.RENOVATION, 0.0],
        [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.0]
        ], columns=['building_condition', 'reduction_share'])


def expected_df(original_condition_val: float, 
                small_measure_val: float,
                renovation_val: float,
                renovation_small_measure_val: float) \
                -> pd.DataFrame:
    return pd.DataFrame([
        [BuildingCondition.ORIGINAL_CONDITION, original_condition_val],
        [BuildingCondition.SMALL_MEASURE, small_measure_val],
        [BuildingCondition.RENOVATION, renovation_val],
        [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, renovation_small_measure_val]
        ], columns=['building_condition', 'reduction_share'])


def sort_result_df_by_building_condition(df: pd.DataFrame)-> pd.DataFrame:
    condition_order = {condition: index for index, condition in enumerate(BuildingCondition.existing_conditions())}
    df['condition_rank'] = df['building_condition'].map(condition_order)
    df = df.sort_values(by='condition_rank').drop(columns=['condition_rank'])
    df.reset_index(drop=True, inplace=True)
    return df


@pytest.mark.parametrize('tek,purpose,expected_df',
                         [('TEK17', EnergyPurpose.HEATING_RV, expected_df(0.0, 0.07, 0.2, 0.25)),
                          ('TEK21', EnergyPurpose.HEATING_RV, expected_df(0.234, 0.234, 0.234, 0.234)),
                          ('TEK21', EnergyPurpose.LIGHTING, expected_df(0.345, 0.345, 0.345, 0.345)),
                          ])
def test_get_reduction_per_condition_return_df_for_best_match(default_parameters, 
                                                              tek: str,
                                                              purpose: EnergyPurpose,
                                                              expected_df: pd.DataFrame):
    """
    Return value for best match on filter variables (building_category, tek and purpose).
    """

    result = filter_improvement_building_upgrade(default_parameters.get('reduction_per_condition'),
                                         building_category=default_parameters.get('building_category'),
                                         tek=tek,
                                         purpose=purpose)
    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]

    expected = expected_df
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_default_df_when_not_found(default_parameters):
    """
    When the specified filter variables (building_category, tek and/or purpose) aren't present in the
    original dataframe, and there is a 'default' option available for those variables, then return the
    df of those 'default' options.  
    """
    result = filter_improvement_building_upgrade(default_parameters.get('reduction_per_condition'),
                                                 building_category=BuildingCategory.CULTURE,
                                                 tek='TEK01',
                                                 purpose=EnergyPurpose.LIGHTING)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]
    result = sort_result_df_by_building_condition(result)

    expected = expected_df(
        original_condition_val=0.456,
        small_measure_val=0.456,
        renovation_val=0.456,
        renovation_small_measure_val=0.456)
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_false_value_when_building_category_not_found(default_parameters,
                                                                                         no_default_df, 
                                                                                         false_return_value):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    result = filter_improvement_building_upgrade(no_default_df,
                                                 building_category=BuildingCategory.KINDERGARTEN,
                                                 tek='TEK17',
                                                 purpose=EnergyPurpose.HEATING_RV)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]

    expected = expected_df(
        original_condition_val=0.0,
        small_measure_val=0.0,
        renovation_val=0.0,
        renovation_small_measure_val=0.0)

    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_return_false_value_when_purpose_not_found(default_parameters,
                                                                               no_default_df,
                                                                               false_return_value):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """

    result = filter_improvement_building_upgrade(no_default_df,
                                                 building_category=default_parameters.get('building_category'),
                                                 tek='TEK17',
                                                 purpose=EnergyPurpose.LIGHTING)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]
    pd.testing.assert_frame_equal(result, false_return_value)


def test_get_reduction_per_condition_return_false_value_when_building_code_not_found(default_parameters,
                                                                           no_default_df,
                                                                           false_return_value):
    """
    When the specified filter variable (building_category, tek or purpose) isn't present in the
    original dataframe, and there isn't a 'default' option available for that variable, then return 
    the false_return_value of the function.
    """
    result = filter_improvement_building_upgrade(no_default_df,
                                                 building_category=default_parameters.get('building_category'),
                                                 tek='TEK21',
                                                 purpose=EnergyPurpose.HEATING_RV)

    pd.testing.assert_frame_equal(result[['building_condition', 'reduction_share']], false_return_value)


def test_get_reduction_per_condition_return_correct_df_when_matches_has_equal_priority(default_parameters):
    """
    If there are more than one match for the given params (building_category, tek and purpose) and
    they have the same priority, then they should be sorted by a pre-defined preferance order. The
    order in which they should be prioritized is as follows: building_category, tek and purpose.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,building_condition,reduction_share
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

    result = filter_improvement_building_upgrade(reduction_per_condition,
                                                 building_category=default_parameters.get('building_category'),
                                                 tek='TEK21',
                                                 purpose=EnergyPurpose.HEATING_RV)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]

    expected = expected_df(original_condition_val=0.31,
                        small_measure_val=0.32,
                        renovation_val=0.33,
                        renovation_small_measure_val=0.34)
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.skip(reason='Not implemented')
def test_get_reduction_per_condition_raise_error_for_duplicate_rows_with_different_values(default_parameters):
    """
    Raise an AmbiguousDataError when there are duplicate rows for 'building_category', 'tek' and 'purpose' 
    and the corresponding value ('reduction_share') is different. In this case, the method have no way of 
    deciding which value is correct and the program should crash. 
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,building_condition,reduction_share
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


    expected_error_msg = re.escape(
        "Conflicting data found in 'reduction_per_condition' dataframe for "
        "building_category='house', tek='TEK21' and purpose='heating_rv'."
    )    
    with pytest.raises(AmbiguousDataError, match=expected_error_msg):
        filter_improvement_building_upgrade(reduction_per_condition,
                                            building_category=default_parameters.get('building_category'),
                                            tek='TEK21',
                                            purpose=EnergyPurpose.HEATING_RV)


def test_get_reduction_per_condition_return_df_with_default_values_when_building_condition_missing(default_parameters):
    """
    When any of the expected building conditions (BuildingConditions.exisiting_conditions()) are missing,
    then add a row with the missing condition and set the value to ~~the default value (0.0)~~ 0.9.
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,building_condition,reduction_share
    house,TEK21,heating_rv,original_condition,0.11
    house,TEK21,heating_rv,small_measure,0.12
    default,default,default,original_condition,0.9
    default,default,default,small_measure,0.9
    default,default,default,renovation,0.9
    default,default,default,renovation_and_small_measure,0.9                                                                                                                                                              
    """.strip()), skipinitialspace=True)

    result = filter_improvement_building_upgrade(reduction_per_condition,
                                                 building_category=BuildingCategory.HOUSE,
                                                 tek='TEK21',
                                                 purpose=EnergyPurpose.HEATING_RV)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]

    expected = expected_df(original_condition_val=0.11,
                    small_measure_val=0.12,
                    renovation_val=0.9,
                    renovation_small_measure_val=0.9)
    pd.testing.assert_frame_equal(result, expected)


def test_get_reduction_per_condition_require_expected_building_conditions(default_parameters):
    """
    Case where there is duplicates for building_conditions after all the rows have been sorted by 
    priority according to the helper methods. Ensure that there are no duplicates on building conditions,
    the highest priority is used and that missing conditions are added. 
    """
    reduction_per_condition = pd.read_csv(io.StringIO("""
    building_category,building_code,purpose,building_condition,reduction_share
    house,default,heating_rv,original_condition,0.1
    house,default,heating_rv,renovation,0.2
    default,TEK21,heating_rv,original_condition,0.234
    default,TEK21,heating_rv,small_measure,0.234
    default,TEK21,heating_rv,renovation,0.234                                     
    """.strip()), skipinitialspace=True)

    result = filter_improvement_building_upgrade(reduction_per_condition,
                                                 building_category=BuildingCategory.HOUSE,
                                                 tek='TEK21',
                                                 purpose=EnergyPurpose.HEATING_RV)

    result = sort_result_df_by_building_condition(result)[['building_condition', 'reduction_share']]

    expected = expected_df(original_condition_val=0.1,
                           small_measure_val=0.234,
                           renovation_val=0.2,
                           renovation_small_measure_val=0.0)
    pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    import sys
    pytest.main([sys.argv[0]])
