import pandas as pd

from ebm.model.database_manager import DatabaseManager 
from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import *

er_2019 = EnergyRequirement.new_instance(YearRange(2010, 2050), calibration_year=2019)
df = pd.concat([s for s in er_2019.calculate_energy_requirements()])
df = df.to_frame()
df = df.reset_index()
df = df[df['purpose'] == 'lighting']

# the value should be the same across TEK's, but the input data is not correctly updated. Thus, the PRE_TEK49 value is used
# values are the same building_codnition, so filtered condition doesn't matter
df_years = df[(df['TEK'] == 'PRE_TEK49') &
            (df['building_condition'] == 'original_condition') &
            (df['year'] >= 2020) & (df['year'] <= 2030)].copy()

# get input values for 2020 data
inp = df_years[df_years['year'].isin([2020,2030])].copy()

inp = inp.pivot(
    index=['building_category', 'TEK', 'purpose', 'building_condition'], 
    columns='year', 
    values='kwh_m2'
).reset_index()

# Get reduction values for 2020 dataset
inp['BEMA2020_reduction'] = 1 - (inp[2030]/inp[2020]) 
print(inp)

# Get start values for 2020 data per building category 
for building_category in inp['building_category'].unique():
    inp_building_category = inp[inp['building_category'] == building_category] 
    logger.info(f'{building_category}')
    print(inp_building_category.iloc[0][2020])
