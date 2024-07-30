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

start_year = 2010
building_category = 'house'
full_condition_list = ['small_measure', 'renovation', 'renovation_and_small_measure', 'demolition', 'original_condition']

def dict_to_df(dict, add_year_index=False):
    df = pd.DataFrame(dict)
    if add_year_index == True:
        df['year'] = range(2010, 2051)
        df = df.set_index('year')
    return df

db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
tek_list = db.get_tek_list()
tek_params = db.get_tek_params(tek_list)
condition_list = db.get_condition_list()
scurve_params = db.get_scurve_params()
area_params = db.get_area_parameters()

building = Buildings(building_category, tek_list, tek_params, condition_list, scurve_params, area_params)
tek_list = building.tek_list   # get filtered tek list for given building category
shares_per_condition = building.get_shares()

area_forecast = AreaForecast(start_year, building_category, area_params, tek_list, tek_params, full_condition_list, shares_per_condition)

#['PRE_TEK49_RES_1940', 'TEK49_RES', 'TEK69_RES_1976', 'TEK69_RES_1986', 'TEK87_RES', 'TEK97_RES', 'TEK07', 'TEK10', 'TEK17', 'TEK21']
def calc_area_per_tek(tek):
    area_forecast_tek = area_forecast._calc_area_pre_construction_per_tek(tek)
    df = dict_to_df(area_forecast_tek, True)
    df = df.round(0).astype(int)
    #df['year'] = range(2010, 2051)
    #df = df.set_index('year')
    print(df)

#calc_area_per_tek('PRE_TEK49_RES_1940')

area = area_forecast.calc_area_pre_construction()
a = dict_to_df(area)
#print(a)

demolition_area = area_forecast.calc_total_demolition_area_per_year()
print(demolition_area)


# Control shares
def print_shares(condition):
    df = dict_to_df(shares_per_condition)
    print(df)

    share_condition = building.get_shares_per_condition(condition)
    share_condition_df = dict_to_df(share_condition, True)
    print(share_condition_df)

#print_shares('small_measure')

def control_yearly_rates_scurve(condition):
    scurve_params_building_category = building.scurve_params
    scurve_params_condition = scurve_params_building_category[condition]
    s = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                       scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share)
    print('pre_rush_rate:', s._pre_rush_rate)
    print('rush_rate:', s._rush_rate)
    print('post_rush_rate:', s._post_rush_rate)

#control_yearly_rates_scurve('renovation')

print(building.acc_construction_area)