""" Program to calculate total floor area including construction"""

import pandas as pd

from ebm.model import Buildings, BuildingCategory
from ebm.model.construction import ConstructionCalculator
from ebm.model.database_manager import DatabaseManager

START_YEAR = 2010
END_YEAR = 2050
YEARS = [y for y in range(START_YEAR, END_YEAR + 1)]

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

buildings = Buildings.build_buildings(building_category=building_category,
                                      database_manager=database_manager)

area_forecast = buildings.build_area_forecast(database_manager=database_manager,
                                              start_year=START_YEAR,
                                              end_year=END_YEAR)
demolition_floor_area = area_forecast.calc_total_demolition_area_per_year()

yearly_constructed = ConstructionCalculator.calculate_construction(
    building_category=building_category,
    demolition_floor_area=pd.Series(data=demolition_floor_area, index=YEARS),
    database_manager=database_manager)

result = area_forecast.calc_area_with_construction(yearly_constructed.accumulated_constructed_floor_area.tolist())

for tek, building_condition in result.items():
    df = pd.DataFrame(data=building_condition, index=YEARS)
    print(tek)
    print(df)
