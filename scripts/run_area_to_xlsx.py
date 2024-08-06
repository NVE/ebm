import pandas as pd
import pathlib

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.area_forecast import AreaForecast
from ebm.model.building_condition import BuildingCondition



# help list
building_list = ['apartment_block', 'house',
                 'kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                 'hospital', 'nursinghome', 'culture', 'sports', 'storage_repairs']

# input arguments and function variables
start_year = 2010
end_year = 2050
building_category = 'house'

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

# Get area for all TEKs, with and without construction
area = area_forecast.calc_area()

# Define folder path for export
folder_path = 'output'
filename = f'area_{building_category}'
path = pathlib.Path(f'{folder_path}/{filename}.xlsx')

# Dictionary to dataframe
def dict_to_df(dict, add_year_index=False):
    df = pd.DataFrame(dict)
    if add_year_index == True:
        df['year'] = range(2010, 2051)
        df = df.set_index('year')
    return df

# Export area data to excel
def area_to_xlsx(area, path):
    df_list = []
    for tek in area:
        area_tek = area[tek]
        df = dict_to_df(area_tek, True)
        df = df.round(0).astype(int)
        df = df.transpose()
        df = df.reset_index()
        df = df.rename(columns={'index': 'building_condition'})
        df['tek'] = tek
        df = df.set_index('tek')
        
        df_list.append(df)
        
    combined_df = pd.concat(df_list)
    print(combined_df)

    combined_df.to_excel(path, index=True)

area_to_xlsx(area, path)
