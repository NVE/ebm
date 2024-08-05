import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.scurve import SCurve
from ebm.model.area import Area
from ebm.model.area_forecast import AreaForecast
from ebm.model.building_condition import BuildingCondition

#pd.set_option("display.max_columns", None)
#pd.set_option("display.max_rows", None)

building_list = ['apartment_block', 'house',
                 'kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                 'hospital', 'nursinghome', 'culture', 'sports', 'storage_repairs']

house_tek_list = ['PRE_TEK49_RES_1940', 'TEK49_RES', 'TEK69_RES_1976', 'TEK69_RES_1986', 'TEK87_RES', 'TEK97_RES', 'TEK07', 'TEK10', 'TEK17', 'TEK21']

# input arguments and function variables
start_year = 2010
end_year = 2050
building_category = 'house'
tek_wo_construction = 'TEK87_RES' # update when changing building category   
tek_w_construction = 'TEK17'    

# Load necessary input arguments
db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
tek_list = db.get_tek_list()
tek_params = db.get_tek_params(tek_list)
scurve_params = db.get_scurve_params()
area_params = db.get_area_parameters()
#scurve_condition_list = db.get_condition_list()

# Get condition lists via BuildingCondition class
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
full_condition_list = BuildingCondition.get_full_condition_list()

building = Buildings(building_category, tek_list, tek_params, scurve_condition_list, scurve_params, area_params)
tek_list = building.tek_list   # get filtered tek list for given building category
shares_per_condition = building.get_shares()

###### Area forecast testing ######

def dict_to_df(dict, add_year_index=False):
    df = pd.DataFrame(dict)
    if add_year_index == True:
        df['year'] = range(2010, 2051)
        df = df.set_index('year')
    return df

# Create class object
area_forecast = AreaForecast(start_year, end_year, building_category, area_params, tek_list, tek_params, full_condition_list, shares_per_condition)

area = area_forecast.calc_area()
print(dict_to_df(area))
