import os
import pathlib
from time import time

from dotenv import load_dotenv

from ebm.heating_system_forecast import *
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler

load_dotenv(pathlib.Path('.env'))


file_handler = FileHandler(directory=os.environ.get('EBM_INPUT_DIRECTORY', 'input'))

shares_start_year = file_handler.get_heating_systems_shares_start_year()
efficiencies = file_handler.get_heating_system_efficiencies()
projection = file_handler.get_heating_system_forecast()
period = YearRange(2023, 2050)

dm = DatabaseManager()
building_code_list = dm.get_building_code_list()

def run_projection():
    start_time = time()
    hsp = HeatingSystemsForecast(shares_start_year,
                                 efficiencies,
                                 projection,
                                 building_code_list,
                                 period)

    print((time() - start_time) * 13)
    df = hsp.calculate_forecast()
    return df

df = run_projection()
df = df[['building_category','building_code','heating_systems','year','heating_system_share']]
print(df)
print(df.building_category.unique())
