from time import time, sleep
import os
import pathlib

from dotenv import load_dotenv

from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.heating_systems_projection import *

load_dotenv(pathlib.Path('.env'))


file_handler = FileHandler(directory=os.environ.get('EBM_INPUT_DIRECTORY', 'input'))

shares_start_year = file_handler.get_heating_systems_shares_start_year()
efficiencies = file_handler.get_heating_systems_efficiencies()
projection = file_handler.get_heating_systems_projection()
period = YearRange(2023, 2050)

dm = DatabaseManager()
tek_list = dm.get_tek_list()

def run_projection():
    start_time = time()
    hsp = HeatingSystemsProjection(shares_start_year,
                               efficiencies,
                               projection,
                               tek_list,
                               period)

    print((time() - start_time) * 13)
    df = hsp.calculate_projection()
    return df

df = run_projection()
df = df[['building_category','TEK','heating_systems','year','heating_system_share']]
print(df)
print(df.building_category.unique())