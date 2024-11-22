import pathlib
import pytest
import pandas as pd

from ebm.model.file_handler import FileHandler
from ebm.model.database_manager import DatabaseManager 
from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import *

dir_2020 = pathlib.Path('C:/Users/lfep/work_space/Energibruksmodell/input_2020')
file_handler_2020 = FileHandler(directory=dir_2020)
db_2020 = DatabaseManager(file_handler=file_handler_2020)

# Calculate energy requirement with updated input data for startyear=2020
er_2020 = EnergyRequirement.new_instance(YearRange(2020, 2050), 
                                    calibration_year=2023, 
                                    database_manager=db_2020)

# Calculate energy requirement with input data as in BEMA2019
er_2019 = EnergyRequirement.new_instance(YearRange(2010, 2050), calibration_year=2019)

for building_category in iter(BuildingCategory):
    series_2020 = pd.concat([s for s in er_2020.calculate_for_building_category(building_category, db_2020)])
    series_2019 = pd.concat([s for s in er_2019.calculate_for_building_category(building_category)])

    logger.info(f'testing for building category = {building_category}')

    def get_lighting_reduction_from_series(series, tek):
        df = series.to_frame()
        df = df.reset_index()
        df = df[df['purpose'] == 'lighting']

        # values are the same across building_condition, so specified condition doesn't matter
        df = df[(df['TEK'] == tek) &
                    (df['building_condition'] == 'original_condition') &
                    (df['year'] >= 2020) & (df['year'] <= 2030)].copy()
        df = df.reset_index(drop=True)
        return df

    tek = 'PRE_TEK49'
    logger.info(f'comparing values for: {tek}')
    df_2020 = get_lighting_reduction_from_series(series_2020, tek)
    df_2019 = get_lighting_reduction_from_series(series_2019, tek)
    
    pd.testing.assert_frame_equal(df_2019, df_2020)