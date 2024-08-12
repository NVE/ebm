import pandas as pd

from ebm.model.area_forecast import AreaForecast
from ebm.model.building_condition import BuildingCondition
from ebm.model.buildings import Buildings
from ebm.model.database_manager import DatabaseManager
from ebm.model.scurve import SCurve

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
tek_w_construction = 'TEK17' # update when changing building category

def dict_to_df(dict, add_year_index=False):
    df = pd.DataFrame(dict)
    if add_year_index == True:
        df['year'] = range(2010, 2051)
        df = df.set_index('year')
    return df

# Load necessary input arguments
db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
tek_list = db.get_tek_list()
tek_params = db.get_tek_params(tek_list)
scurve_params = db.get_scurve_params()
area_params = db.get_area_parameters()

scurve_condition_list = BuildingCondition.get_scruve_condition_list()
full_condition_list = BuildingCondition.get_full_condition_list()

building = Buildings(building_category, tek_list, tek_params, scurve_condition_list, scurve_params, area_params)
tek_list = building.tek_list   # get filtered tek list for given building category
shares_per_condition = building.get_shares()

# Create class object
area_forecast = AreaForecast(start_year, end_year, building_category, area_params, tek_list, tek_params, full_condition_list, shares_per_condition)

def calc_area_pre_construction_tek(tek):
    area_forecast_tek = area_forecast._calc_area_pre_construction_tek(tek)
    df = dict_to_df(area_forecast_tek, True)
    df = df.round(0).astype(int)
    print(df)

#print(f'Area pre construction for: {tek_wo_construction}')
#calc_area_pre_construction_tek(tek_wo_construction)

def calc_area_pre_construction():
    area = area_forecast.calc_area_pre_construction()
    a = dict_to_df(area)
    print(a)

#print(f'Area pre construction for all TEKs')
#calc_area_pre_construction()

demolition_area = area_forecast.calc_total_demolition_area_per_year()
#print(f'List with total demolition area')
#print(demolition_area)

def calc_area_construction_tek(tek):
    area_with_construction_tek = area_forecast._calc_area_with_construction_tek(tek)
    df = dict_to_df(area_with_construction_tek, True)
    df = df.round(0).astype(int)
    df['total'] = df['small_measure'] + df['renovation'] + df['renovation_and_small_measure'] + df['demolition'] + df['original_condition']
    #df = df.transpose()
    print(df)

#print(f'Area with construction for: {tek_w_construction}')
#calc_area_construction_tek(tek_w_construction)


def calc_area_construction(area_forecast):
    area_with_construction = area_forecast.calc_area_with_construction()
    area_with_construction_df = dict_to_df(area_with_construction)
    print(area_with_construction_df)


#print(f'Area with construction for all TEKs')
calc_area_construction(area_forecast)

area = area_forecast.calc_area()
print(dict_to_df(area))

###### other stuff #####

# Control shares
def print_shares(condition):
    df = dict_to_df(shares_per_condition)
    print(df)

    share_condition = building.get_shares_per_condition(condition)
    share_condition_df = dict_to_df(share_condition, True)
    print(share_condition_df)

#print_shares('original_condition')

def control_yearly_rates_scurve(condition):
    scurve_params_building_category = building.scurve_params
    scurve_params_condition = scurve_params_building_category[condition]
    s = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                       scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share)
    print('pre_rush_rate:', s._pre_rush_rate)
    print('rush_rate:', s._rush_rate)
    print('post_rush_rate:', s._post_rush_rate)

#control_yearly_rates_scurve('renovation')