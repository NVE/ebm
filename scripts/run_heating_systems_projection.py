import os
import pathlib

from dotenv import load_dotenv

from ebm.model.file_handler import FileHandler
from ebm.heating_systems_projection import *


load_dotenv(pathlib.Path('.env'))


file_handler = FileHandler(directory=os.environ.get('EBM_INPUT_DIRECTORY', 'input'))


shares_start_year = file_handler.get_heating_systems_shares_start_year()
efficiencies = file_handler.get_heating_systems_efficiencies()
projection = file_handler.get_heating_systems_projection()
period = YearRange(2020, 2050)


df = HeatingSystems.calculate_heating_systems_projection(heating_systems_shares=shares_start_year,
                                          heating_systems_efficiencies=efficiencies,
                                          heating_systems_forecast=projection,
                                          period=period)

print(df)

