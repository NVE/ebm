
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.database_manager import DatabaseManager
from ebm.model.filter_scurve_params import FilterScurveParams
from ebm.model.scurve_processor import ScurveProcessor

# Refactoring improvements in scurve classes
# - use BuildingCondition members instead of strings (classes, ScurveParameters and get_scurve_condition_list())

database_manager = DatabaseManager()

building_category = BuildingCategory.HOUSE

scurve_condition_list = BuildingCondition.get_scruve_condition_list()

scurve_params_df = database_manager.get_scurve_params()

scurve_params = FilterScurveParams().filter(building_category=building_category, 
                                            scurve_condition_list=scurve_condition_list,
                                            scurve_params=scurve_params_df)

scurve_processor = ScurveProcessor(scurve_condition_list=scurve_condition_list,
                                   scurve_params=scurve_params)

scurves = scurve_processor.get_scurves()
never_shares = scurve_processor.get_never_shares()

print(scurves)
print(never_shares)


