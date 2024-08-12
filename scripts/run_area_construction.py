""" Program to calculate total floor area including construction"""
import pandas as pd

from ebm.model import Buildings, BuildingCategory
from ebm.model.construction import ConstructionCalculator
from ebm.model.database_manager import DatabaseManager

database_manager = DatabaseManager()

building_category = BuildingCategory.HOUSE

buildings = Buildings.build_buildings(building_category, database_manager)
area_forecast = buildings.build_area_forecast(database_manager, start_year=2010, end_year=2050)

years = [y for y in range(2010, 2050 + 1)]
demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=years)

yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area, database_manager)

constructed_floor_area = yearly_constructed.accumulated_constructed_floor_area

result = area_forecast.calc_area_with_construction([v for v in constructed_floor_area])

for tek, building_condition in result.items():
    df = pd.DataFrame(data=building_condition, index=[y for y in range(2010, 2051)])
    print(tek)
    print(df)
