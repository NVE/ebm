import pandas as pd

from ebm.model.database_manager import DatabaseManager 
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition 
from ebm.model.filter_scurve_params import FilterScurveParams
from ebm.model.scurve_processor import ScurveProcessor
from ebm.model.filter_tek import FilterTek
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.data_classes import YearRange


database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

tek_list = FilterTek.get_filtered_list(building_category, database_manager.get_tek_list())
tek_params = database_manager.get_tek_params(tek_list)

# Get scurve params (run scurve process)
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
scurve_params_df = database_manager.get_scurve_params()
scurve_params = FilterScurveParams().filter(building_category=building_category, 
                                            scurve_condition_list=scurve_condition_list,
                                            scurve_params=scurve_params_df)

scurve_processor = ScurveProcessor(scurve_condition_list=scurve_condition_list,
                                   scurve_params=scurve_params)
scurves = scurve_processor.get_scurves()
never_shares = scurve_processor.get_never_shares()

# Run SharesPerCondition
s = SharesPerCondition(tek_list, tek_params, scurves, never_shares) 
s._control_shares()