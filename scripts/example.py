from ebm.model import BuildingCategory, Buildings, DatabaseManager
from ebm.model.construction import ConstructionCalculator

database_manager = DatabaseManager()

buildings = Buildings.build_buildings(building_category=BuildingCategory.HOUSE)

area_forecast = buildings.build_area_forecast(database_manager)

demolished_floor_area = area_forecast.calc_total_demolition_area_per_year()

yearly_constructed = ConstructionCalculator.calculate_construction_as_list(
    building_category=BuildingCategory.HOUSE,
    demolition_floor_area=demolished_floor_area)

forecast = area_forecast.calc_area_with_construction(yearly_constructed)

print(forecast)
