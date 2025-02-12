import os

import pathlib

import pandas as pd

from dotenv import load_dotenv
from ebm.model.database_manager import DatabaseManager




load_dotenv(pathlib.Path('.env'))
dm = DatabaseManager()



data_directory = os.path.join(os.path.dirname(dm.file_handler.HOLIDAY_HOME_ENERGY_CONSUMPTION), "ebm", "data")
print(data_directory)


df = dm.file_handler.get_file(dm.file_handler.HOLIDAY_HOME_ENERGY_CONSUMPTION)
print(os.path.abspath(dm.file_handler.HOLIDAY_HOME_ENERGY_CONSUMPTION))

# Legge til en ny kolonne for fossilfuel oppvarming
df["fossilfuel"] = df["year"].apply(lambda x: 100 if x == 2006 else None)
print(df.head())



# Lagre endringene tilbake til CSV-filen
absolute_path = os.path.join(data_directory, "holiday_home_energy_consumption.csv")
df.to_csv(absolute_path, index=False)
