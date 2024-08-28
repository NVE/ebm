from pprint import pprint as pp

from ebm.model import BuildingCategory, Buildings, DatabaseManager
from ebm.model.construction import ConstructionCalculator

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

buildings = Buildings.build_buildings(building_category=building_category)

area_forecast = buildings.build_area_forecast(database_manager)

demolished_floor_area = area_forecast.calc_total_demolition_area_per_year()
yearly_constructed = ConstructionCalculator.calculate_construction_as_list(building_category, demolished_floor_area)

forecast = area_forecast.calc_area_with_construction(yearly_constructed)

pp(forecast)