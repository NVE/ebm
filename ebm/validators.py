"""
Pandera validators for ebm input files.
"""
import pandas as pd
import pandera as pa

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.energy_purpose import EnergyPurpose


def check_building_category(value: pd.Series) -> pd.Series:
    """
    Makes sure that the series value contains values that are corresponding to a BuildingCategory

    Parameters
    ----------
    value: pd.Series
        A series of str that will be checked against BuildingCategory

    Returns
    -------
    pd.Series of bool values

    """
    return value.isin(iter(BuildingCategory))

def check_default_building_category(value: pd.Series) -> pd.Series:
    """
    Makes sure that the series value contains values that are corresponding to a BuildingCategory or default

    Parameters
    ----------
    value: pd.Series
        A series of str that will be checked against BuildingCategory and 'default' 

    Returns
    -------
    pd.Series of bool values

    """
    return value.isin(list(BuildingCategory) + ['default'])


def check_building_condition(value: pd.Series) -> pd.Series:
    """
    Makes sure that the series value contains values that are corresponding to a BuildingCondition

    Parameters
    ----------
    value: pd.Series
        A series of str that will be checked against BuildingCondition

    Returns
    -------
    pd.Series of bool values

    """
    return value.isin(iter(BuildingCondition))

def check_existing_building_conditions(value: pd.Series) -> pd.Series:
    """
    Makes sure that the series contains values that are corresponding to 'existing' building conditions.

    Existing building conditions are all members (conditions) of BuildingCondition, except of DEMOLITION.

    Parameters
    ----------
    value: pd.Series
        A series of str that will be checked against 'existing' BuildingCondition members

    Returns
    -------
    pd.Series of bool values

    """
    return value.isin(iter(BuildingCondition.existing_conditions()))


def check_energy_purpose(value: pd.Series) -> pd.Series:
    """
    Makes sure that the value contain one of the values corresponding to purpose
     - 'Cooling'
     - 'Electrical equipment'
     - 'Fans and pumps'
     - 'HeatingDHW'
     - 'HeatingRV'
     - 'Lighting'

     Returns
     -------
     pd.Series of bool values

    """
    return value.isin(iter(EnergyPurpose))

def check_default_energy_purpose(value: pd.Series) -> pd.Series:
    """
    Makes sure that the value contain one of the values corresponding to 'default' or purpose 
     - 'Cooling'
     - 'Electrical equipment'
     - 'Fans and pumps'
     - 'HeatingDHW'
     - 'HeatingRV'
     - 'Lighting'

     Returns
     -------
     pd.Series of bool values

    """
    return value.isin(list(EnergyPurpose) + ['default'])


def check_tek(value: str) -> bool:
    """
    A crude check to determine if value is a 'TEK'

    Parameters
    ----------
    value: str
    Returns
    -------
    bool
        True when the function thinks that value might be a TEK

    """
    return 'TEK' in value


def check_default_tek(value: str) -> bool:
    """
    A crude check to determine if value is a 'TEK' or default

    Parameters
    ----------
    value: str
    Returns
    -------
    bool
        True when the function thinks that value might be a TEK

    """
    return check_tek(value) or value == 'default'


def check_building_category_share(values: pd.DataFrame) -> pd.Series:
    """
   Make sure that the sum of values in values.new_house_share + values.new_apartment_block_share is 1.0

    Parameters
    ----------
    values: pd.DataFrame
        A dataframe with new_house_share and new_apartment_block_share
    -------
    pd.Series
        A series of bool with the truth value of new_house_share + new_apartment_block_share equals 1.0

    """
    return values.new_house_share + values.new_apartment_block_share == 1.0


def create_residential_area_checks():
    """
    Creates a list of checks used for house and apartment_block categories.
        - Checks that the first two rows are not empty
        - Checks that the next (3) rows are empty
        - Checks that non-empty rows are not negative

    Returns
    -------
    List[pa.Check]
    """
    return [
        pa.Check(lambda s: s.iloc[:2].notnull().all(),
                 element_wise=False,
                 error='Expects number in first two rows for house'),
        pa.Check(lambda s: s.iloc[2:].isnull().all(),
                 element_wise=False,
                 error='Expects empty in the last four years for house'),
        pa.Check.greater_than_or_equal_to(0.0)]


area_parameters = pa.DataFrameSchema(
    columns={
        "building_category": pa.Column(str, checks=[pa.Check(check_building_category)]),
        "TEK": pa.Column(str, checks=[pa.Check(check_tek, element_wise=True)]),
        "area": pa.Column(float, checks=[pa.Check.greater_than(0)], coerce=True)},
    name='area_parameters'
)

tek_parameters = pa.DataFrameSchema(columns={
    "TEK": pa.Column(str, unique=True, checks=[pa.Check(check_tek, element_wise=True)]),
    'building_year': pa.Column(int, checks=[
        pa.Check.greater_than_or_equal_to(1940),
        pa.Check.less_than_or_equal_to(2070)]),
    'period_start_year': pa.Column(int, checks=[
        pa.Check.greater_than_or_equal_to(0),
        pa.Check.less_than_or_equal_to(2070),
    ]),
    'period_end_year': pa.Column(int, checks=[
        pa.Check.greater_than_or_equal_to(1940),
        pa.Check.less_than_or_equal_to(2070, error='period_end_year should be 2070 or lower'),
        pa.Check.between(1940, 2070, error='period_end_year should be between 1940 and 2070')])},
    checks=[pa.Check(lambda df: df["period_end_year"] > df["period_start_year"],
                     error="period_end_year should be greater than period_start_year")],
    name='tek_parameters'
)


construction_building_category_yearly = pa.DataFrameSchema(
    columns={
        'year': pa.Column(int),
        'house': pa.Column(pa.Float64, nullable=True, checks=create_residential_area_checks()),
        'apartment_block': pa.Column(pa.Float64, nullable=True, checks=create_residential_area_checks()),
        'kindergarten': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'school': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'university': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'office': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'retail': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'hotel': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'hospital': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'nursing_home': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'culture': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'sports': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)]),
        'storage_repairs': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0.0)])
    },
    name='construction_building_category_yearly'
)


new_buildings_house_share = pa.DataFrameSchema(
    columns={
        'year': pa.Column(int, checks=[pa.Check.between(2010, 2070)]),
        'new_house_share': pa.Column(float, checks=[pa.Check.between(0.0, 1.0)]),
        'new_apartment_block_share': pa.Column(float, checks=[pa.Check.between(0.0, 1.0)]),
        'floor_area_new_house': pa.Column(int, checks=[pa.Check.between(1, 1000)]),
        'flood_area_new_apartment_block': pa.Column(int, checks=[pa.Check.between(1, 1000)])
    },
    checks=[pa.Check(check_building_category_share,
                     error='The sum of new_house_share and new_apartment_block_share should be 1.0 (100%)')],
    name='new_buildings_house_share'
)


new_buildings_population = pa.DataFrameSchema(
    columns={
        'year': pa.Column(int, coerce=True, checks=[pa.Check.between(2010, 2070)]),
        'population': pa.Column(int, coerce=True, checks=[pa.Check.greater_than_or_equal_to(0)]),
        'household_size': pa.Column(float, coerce=True, checks=[pa.Check.greater_than_or_equal_to(0)])},
    name='new_buildings_population')

#TODO: evaluete if restrictions on rush and never share make sense (if the program crashes unless they are there)
scurve_parameters = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=[pa.Check(check_building_category)]),
        'condition': pa.Column(str, checks=[pa.Check(check_building_condition)]),
        'earliest_age_for_measure': pa.Column(int, checks=[pa.Check.greater_than(0)]),
        'average_age_for_measure': pa.Column(int, checks=[pa.Check.greater_than(0)]),
        'rush_period_years': pa.Column(int, checks=[pa.Check.greater_than(0)]),
        'last_age_for_measure': pa.Column(int, checks=[pa.Check.greater_than(0)]),
        'rush_share': pa.Column(float, checks=[pa.Check.between(min_value=0.0, max_value=1.0, include_min=False)]),
        'never_share': pa.Column(float, checks=[pa.Check.between(min_value=0.0, max_value=1.0, include_min=False)])
    },
    name='scurve_parameters')


### TODO: remove strong restrictions on float values and add warnings (should be able to be neg values)
energy_requirement_original_condition = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=[pa.Check(check_default_building_category)]),
        'TEK': pa.Column(str, checks=[pa.Check(check_default_tek, element_wise=True)]),
        'purpose': pa.Column(str, checks=[pa.Check(check_default_energy_purpose)]),
        'kwh_m2': pa.Column(float, coerce=True, checks=[pa.Check.greater_than_or_equal_to(0)])
    }
)


energy_requirement_reduction_per_condition = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=pa.Check(check_default_building_category)),
        'TEK': pa.Column(str, checks=pa.Check(check_default_tek, element_wise=True)),
        'purpose': pa.Column(str, checks=pa.Check(check_default_energy_purpose)),
        'building_condition': pa.Column(str, checks=[pa.Check(check_existing_building_conditions)]),
        'reduction_share': pa.Column(float, coerce=True, checks=[pa.Check.between(min_value=0.0, include_min=True,
                                                                                  max_value=1.0, include_max=True)])
    }
)


energy_requirement_yearly_improvements = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=pa.Check(check_default_building_category)),
        'TEK': pa.Column(str, checks=pa.Check(check_default_tek, element_wise=True)),
        'purpose':pa.Column(str, checks=pa.Check(check_default_energy_purpose)),
        'yearly_efficiency_improvement': pa.Column(float, coerce=True, 
                                                   checks=[pa.Check.between(min_value=0.0, include_min=True,
                                                                            max_value=1.0, include_max=True)])
    }
)


# TODO: add checks for period start and end year that can handle blank value on period_start_year (nullable=True)? 
energy_requirement_policy_improvements = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=pa.Check(check_default_building_category)),
        'TEK': pa.Column(str, checks=pa.Check(check_default_tek, element_wise=True)),
        'purpose': pa.Column(str, checks=pa.Check(check_default_energy_purpose)),
        'period_start_year': pa.Column(int, coerce=True, checks=[pa.Check.greater_than_or_equal_to(0)]),
        'period_end_year': pa.Column(int, coerce=True),
        'improvement_at_period_end': pa.Column(float, coerce=True, 
                                               checks=[pa.Check.between(min_value=0.0, include_min=True,
                                                                        max_value=1.0, include_max=True)])
    },checks=[pa.Check(lambda df: df["period_end_year"] > df["period_start_year"],
                       error="period_end_year should be greater than period_start_year")]
)

__all__ = [area_parameters,
           tek_parameters,
           construction_building_category_yearly,
           new_buildings_house_share,
           new_buildings_population,
           scurve_parameters,
           new_buildings_house_share,
           energy_requirement_reduction_per_condition]
