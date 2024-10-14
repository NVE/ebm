import pandas as pd

from ebm.__main__ import calculate_building_category_area_forecast
from ebm.model import BuildingCategory, DatabaseManager
from ebm.model.bema import filter_existing_area, calculate_area_distribution
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import (calculate_energy_requirement_reduction_by_condition,
                                          calculate_energy_requirement_reduction,
                                          calculate_lighting_reduction)
from ebm.services.console import rich_display_dataframe


def load_area_forecast(building_category: BuildingCategory = BuildingCategory.KINDERGARTEN) -> pd.DataFrame:
    dm = DatabaseManager()
    area = calculate_building_category_area_forecast(building_category=building_category,
                                                     database_manager=dm,
                                                     start_year=2010,
                                                     end_year=2050)

    data = {'building_category': [], 'TEK': [], 'building_condition': [], 'year': [], 'area': []}
    for tek, item in area.items():
        for condition, years in item.items():
            if condition == BuildingCondition.DEMOLITION:
                continue
            for year, area in enumerate(years, start=2010):
                data.get('building_category').append(building_category)
                data.get('TEK').append(tek)
                data.get('building_condition').append(condition)
                data.get('year').append(year)
                data.get('area').append(area)

    area_forecast = pd.DataFrame(data=data)
    return area_forecast


def load_heating_reduction(purpose='heating_rv'):
    def make_zero_reduction():
        r = [{'building_condition': condition, 'reduction': 0} for condition in BuildingCondition if condition != BuildingCondition.DEMOLITION]
        return r
    heating_reduction = pd.read_csv('input/energy_requirement_reduction_per_condition.csv')
    if purpose != 'heating_rv':
        return pd.DataFrame(data=make_zero_reduction())
    heating_reduction['reduction'] = heating_reduction['reduction_share']
    heating_reduction = heating_reduction[heating_reduction.TEK == 'default'][['building_condition', 'reduction']]
    return heating_reduction


def load_energy_by_floor_area(building_category, purpose='heating_rv'):
    energy_by_floor_area = pd.read_csv('input/energy_requirement_original_condition.csv')
    df = energy_by_floor_area[(energy_by_floor_area.building_category == building_category) &
                              (energy_by_floor_area.purpose == purpose)]
    return df


def distribute_energy_requirement_over_area(area_forecast, requirement_by_condition):
    area_requirements = pd.merge(left=area_forecast,
                                 right=requirement_by_condition,
                                 on=['building_category', 'TEK', 'building_condition', 'year']).copy()
    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])
    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)
    return existing_heating_rv_by_year


def calculate_heating_reduction(building_category=BuildingCategory.KINDERGARTEN, purpose='heating_rv'):
    heating_reduction = load_heating_reduction(purpose)

    heating_rv_requirements = load_energy_by_floor_area(building_category, purpose=purpose)

    requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
        energy_requirements=heating_rv_requirements,
        condition_reduction=heating_reduction)
   # return requirement_by_condition
    heating_reduction = pd.merge(left=requirement_by_condition,
                                 right=pd.DataFrame({'year': YearRange(2010, 2050).year_range}),
                                 how='cross')
    return heating_reduction


def calculate_electrical_equipment(building_category, heating_reduction, purpose):
    # By default there is no heating_reduction defined for fans n pumps

    # heating_reduction.reduction = 0
    lighting = load_energy_by_floor_area(building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name = 'year'
    energy_requirement = pd.Series([requirement_by_condition['kwh_m2'].iloc[0]] * 41, index=idx,
                                   name='kwh_m2')
    light_requirements = calculate_energy_requirement_reduction(energy_requirements=energy_requirement,
                                                                yearly_reduction=0.01,
                                                                reduction_period=YearRange(2020, 2050))
    merged = pd.merge(
        requirement_by_condition[['building_category', 'TEK', 'building_condition']],
        pd.DataFrame({'kwh_m2': light_requirements, 'year': light_requirements.index.values}),
        how='cross')

    return merged


def calculate_lighting(building_category, purpose):
    heating_reduction = load_heating_reduction(purpose)

    # heating_reduction.reduction = 0
    lighting = load_energy_by_floor_area(building_category=building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name = 'year'
    energy_requirement = pd.Series([requirement_by_condition['kwh_m2'].iloc[0]] * 41, index=idx,
                                   name='kwh_m2')
    end_year_requirement = requirement_by_condition['kwh_m2'].iloc[0] * (1-0.6)
    light_requirements = calculate_lighting_reduction(
            energy_requirement=energy_requirement,
            yearly_reduction=0.005,
            end_year_energy_requirement=end_year_requirement,
            interpolated_reduction_period=YearRange(2018, 2030),
            year_range=YearRange(2010, 2050))
    merged = pd.merge(
        requirement_by_condition[['building_category', 'TEK', 'building_condition']],
        pd.DataFrame({'kwh_m2': light_requirements, 'year': light_requirements.index.values}),
        how='cross')
    return merged


def main(building_category = BuildingCategory.KINDERGARTEN):
    area_forecast = load_area_forecast(building_category=building_category)

    return pd.DataFrame({
        'heating_rv': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category)),
        'fans_and_pumps': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category, purpose='fans_and_pumps')),
        'heating_dhw': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category,
                purpose='heating_dhw')),
        'lighting': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_lighting(building_category, 'lighting')),
        'electrical_equipment': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_electrical_equipment(
                building_category=building_category,
                heating_reduction=load_heating_reduction('electrical_equipment'),
                purpose='electrical_equipment')),
        'cooling': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category,
                purpose='cooling'))
        })


df = None
if __name__ == '__main__':
    building_category = BuildingCategory.KINDERGARTEN
    df = main(building_category)

    print('=== ', building_category, ' === ')
    rich_display_dataframe(df)
