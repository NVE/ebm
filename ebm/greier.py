import pandas as pd

from ebm.model import BuildingCategory
from ebm.model.building_condition import BuildingCondition


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