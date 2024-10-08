import pandas as pd

from ebm.__main__ import calculate_building_category_area_forecast
from ebm.energy_requirements import (calculate_energy_requirement_reduction_by_condition,
                                     calculate_energy_requirement_reduction,
                                     calculate_lighting_reduction)
from ebm.model import BuildingCategory, DatabaseManager
from ebm.model.bema import filter_existing_area
from ebm.model.building_condition import BuildingCondition
from model.data_classes import YearRange


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


def load_heating_reduction(building_category, purpose='heating_rv'):
    def make_zero_reduction(purpose):
        r = [{'building_condition': condition, 'reduction': 0} for condition in BuildingCondition if condition != BuildingCondition.DEMOLITION]
        return r
    heating_reduction = pd.read_csv('input/heating_reduction.csv')
    if purpose != 'heating_rv':
        return pd.DataFrame(data=make_zero_reduction(purpose))
    heating_reduction['reduction'] = heating_reduction['heating_reduction']
    heating_reduction = heating_reduction[heating_reduction.TEK == 'default'][['building_condition', 'reduction']]
    return heating_reduction




def load_energy_by_floor_area(building_category, purpose='heating_rv'):
    energy_by_floor_area = pd.read_csv('input/energy_by_floor_area2.csv')
    df = energy_by_floor_area[(energy_by_floor_area.building_category == building_category) &
                              (energy_by_floor_area.purpose == purpose)]
    return df


def calculate_heating_rv(building_category=BuildingCategory.KINDERGARTEN):
    heating_reduction = load_heating_reduction(building_category)

    area_forecast = load_area_forecast(building_category=building_category)
    heating_rv_requirements = load_energy_by_floor_area(building_category, purpose='heating_rv')

    requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
        energy_requirements=heating_rv_requirements,
        condition_reduction=heating_reduction)

    area_requirements = pd.merge(left=area_forecast,
                                 right=requirement_by_condition,
                                 on=['building_category', 'TEK', 'building_condition']).copy()

    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])

    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)

    return existing_heating_rv_by_year


def calculate_purpose(building_category, purpose):
    # By default there is no heating_reduction defined for fans n pumps
    heating_reduction = load_heating_reduction(building_category, purpose)

    # heating_reduction.reduction = 0
    area_forecast = load_area_forecast(building_category=building_category)
    fans_n_pumps_requirements = load_energy_by_floor_area(building_category, purpose=purpose)

    requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
        energy_requirements=fans_n_pumps_requirements,
        condition_reduction=heating_reduction)

    area_requirements = pd.merge(left=area_forecast,
                                 right=requirement_by_condition,
                                 on=['building_category', 'TEK', 'building_condition']).copy()

    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])

    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)

    return existing_heating_rv_by_year


def calculate_electrical_equipment(building_category, purpose):
    # By default there is no heating_reduction defined for fans n pumps
    heating_reduction = load_heating_reduction(building_category, purpose)

    # heating_reduction.reduction = 0
    area_forecast = load_area_forecast(building_category=building_category)
    lighting = load_energy_by_floor_area(building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name='year'
    energy_requirement = pd.Series([requirement_by_condition['kw_h_m'].iloc[0]] * 41, index=idx,
                                   name='kw_h_m')
    light_requirements = calculate_energy_requirement_reduction(energy_requirements=energy_requirement,
                                                                yearly_reduction=0.01,
                                                                reduction_period=YearRange(2020, 2050))

    area_requirements = pd.merge(left=area_forecast, right=light_requirements, left_on='year', right_on='year')
    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])

    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)

    return existing_heating_rv_by_year


def calculate_area_distribution(area_requirements, existing_area):
    total_area = existing_area.groupby(level=['building_category', 'year']).sum()[['area']]
    existing_area['pct'] = existing_area.area / total_area.area
    area_requirements['adjusted'] = existing_area.pct * area_requirements.kw_h_m
    existing_heating_rv_by_year = area_requirements.groupby(level=['building_category', 'year'])['adjusted'].sum()
    return existing_heating_rv_by_year


def calculate_lighting(building_category, purpose):
    # By default there is no heating_reduction defined for fans n pumps
    heating_reduction = load_heating_reduction(building_category, purpose)

    # heating_reduction.reduction = 0
    area_forecast = load_area_forecast(building_category=building_category)
    lighting = load_energy_by_floor_area(building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name='year'
    energy_requirement = pd.Series([requirement_by_condition['kw_h_m'].iloc[0]] * 41, index=idx,
                                   name='kw_h_m')
    end_year_requirement = requirement_by_condition['kw_h_m'].iloc[0] * (1-0.6)
    light_requirements = calculate_lighting_reduction(
            energy_requirement=energy_requirement,
            yearly_reduction=0.005,
            end_year_energy_requirement=end_year_requirement,
            interpolated_reduction_period=YearRange(2018, 2030),
            year_range=YearRange(2010, 2050))

    area_requirements = pd.merge(left=area_forecast, right=light_requirements, left_on='year', right_on='year')
    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])

    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)
    return existing_heating_rv_by_year


def main():
    building_category = BuildingCategory.STORAGE_REPAIRS

    return pd.DataFrame({'heating_rv': calculate_heating_rv(building_category=building_category),
                         'fans_and_pumps': calculate_purpose(building_category, 'fans_and_pumps'),
                         'heating_dhw': calculate_purpose(building_category, 'heating_dhw'),
                         'lighting': calculate_lighting(building_category, 'lighting'),
                         'electrical_equipment': calculate_electrical_equipment(building_category, 'electrical_equipment'),
                         'cooling': calculate_purpose(building_category, 'cooling')})


df = None
if __name__ == '__main__':
    df = main()
    print(df)
