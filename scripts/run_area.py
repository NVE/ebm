import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.scurve import SCurve
from ebm.model.area import Area
from ebm.model.area_forecast import AreaForecast

building_list = ['apartment_block', 'house',
                 'kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                 'hospital', 'nursinghome', 'culture', 'sports', 'storage_repairs']

full_condition_list = ['small_measure', 'renovation', 'renovation_and_small_measure', 'demolition', 'original_condition']

def dict_to_df(dict):
    df = pd.DataFrame(dict)
    return df

# Shares workflow:

db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
tek_list = db.get_tek_list()
tek_params = db.get_tek_params(tek_list)
condition_list = db.get_condition_list()
scurve_params = db.get_scurve_params()
area_params = db.get_area_parameters()

house = Buildings('house', tek_list, tek_params, condition_list, scurve_params, area_params)
shares_per_condition = house.get_shares()
#shares_condition = shares_per_condition['renovation']
#shares_tek = shares_condition['TEK49_RES']

area = Area(area_params)
a =  area.get_area_per_building_category_tek('house', 'TEK49_RES')

area_forecast = AreaForecast('house', area_params, tek_list, tek_params, full_condition_list, shares_per_condition)

# THIS WORKS:
area_forecast_tek = area_forecast.get_area_per_condition('TEK49_RES')
df = dict_to_df(area_forecast_tek)
df = df.round(0).astype(int)
df['year'] = range(2010, 2051)
df = df.set_index('year')
print(df)

# THIS DOES NOT WORK
area_per_tek_condition = house.get_area_per_tek_condition()
print(area_per_tek_condition)
