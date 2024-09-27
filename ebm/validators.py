import pandera as pa

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition


def check_building_category(value) -> bool:
    return value.isin(iter(BuildingCategory))


def check_building_condition(value) -> bool:
    return value.isin(iter(BuildingCondition))


def check_energy_purpose(value):
    return value.isin(('Cooling', 'Electrical equipment', 'Fans and pumps', 'HeatingDHW', 'HeatingRV', 'Lighting'))


def check_tek(value) -> bool:
    return 'TEK' in value


def check_building_category_share(values):
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

energy_by_floor_area = pa.DataFrameSchema(
    columns={
        'building_category': pa.Column(str, checks=[pa.Check(check_building_category)]),
        'TEK': pa.Column(str, checks=[pa.Check(check_tek, element_wise=True)]),
        'purpose': pa.Column(str, checks=[pa.Check(check_energy_purpose)]),
        'kw_h_m': pa.Column(float, checks=[pa.Check.greater_than_or_equal_to(0)])
    }
)

__all__ = [area_parameters,
           tek_parameters,
           construction_building_category_yearly,
           new_buildings_house_share,
           new_buildings_population,
           scurve_parameters,
           new_buildings_house_share]
