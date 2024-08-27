""" Program to calculate total floor area including construction"""
import typing

import pandas as pd
import rich.pretty

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

years = [y for y in range(2010, 2050 + 1)]
area_forecast = buildings.build_area_forecast(database_manager, START_YEAR, END_YEAR)

demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=years)

yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area, database_manager)

constructed_floor_area = yearly_constructed.accumulated_constructed_floor_area
forecast: typing.Dict = area_forecast.calc_area_with_construction([v for v in constructed_floor_area])

rich.pretty.pprint(forecast)


