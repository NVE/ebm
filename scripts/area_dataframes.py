#!/usr/bin/env python
# coding: utf-8
import pathlib

# In[426]:

from loguru import logger
import pandas as pd

import time


pd.set_option('display.float_format', '{:.9f}'.format)


# In[427]:


from ebm.model.data_classes import YearRange
from ebm.model.area import building_condition_scurves, building_condition_accumulated_scurves

from ebm.model.database_manager import DatabaseManager, FileHandler
from ebm.model.construction import ConstructionCalculator
start_time = time.time()

years = YearRange(2020, 2050)


# # S-kurve

# In[428]:


input_directory = pathlib.Path('t2734_input')
scurve_parameters_path = input_directory / 'scurve_parameters.csv'


scurve_parameters = pd.read_csv(scurve_parameters_path)

# area_parameters = area_parameters.query('building_category=="house"')

scurve_parameters


# In[ ]:





# ### area_parameters

# In[429]:


area_parameters_path = input_directory / 'area_parameters.csv'
area_parameters = pd.read_csv(area_parameters_path)
area_parameters['year'] = years.start

area_parameters = area_parameters[['building_category', 'TEK', 'year', 'area']]
area_parameters


# ### tek_parameters

# In[430]:


tek_parameters_path = input_directory / 'tek_parameters.csv'
tek_parameters = pd.read_csv(tek_parameters_path)
tek_parameters = tek_parameters[['TEK', 'period_start_year', 'building_year', 'period_end_year']]
tek_parameters


# #### Filter parameters

# In[ ]:





# In[431]:


if False:
    area_parameters=area_parameters.query('building_category=="house"')
    tek_parameters=tek_parameters.query('TEK=="PRE_TEK49"')
    scurve_parameters=scurve_parameters.query('building_category=="house"')


# ## Make building_condition scurves

# In[ ]:





# In[432]:


scurve_normal = building_condition_scurves(scurve_parameters)
scurve_max = building_condition_accumulated_scurves(scurve_parameters)

s_df = pd.concat([scurve_normal, scurve_max])


s_df


# #### renovation scurve

# In[433]:


s_df.query('building_category=="house" and building_condition=="renovation_acc"')


# In[434]:


df_never_share = pd.DataFrame([(r.building_category, i, r.condition + '_nvr', r.never_share) for i in range(-130, 131) for r in scurve_parameters.itertuples()],
             columns=['building_category', 'age', 'building_condition', 'scurve']).sort_values(['building_category', 'building_condition', 'age']).set_index(['building_category', 'age', 'building_condition'])
df_never_share


# In[435]:


s_df = pd.concat([s_df, df_never_share])
s_df


# In[ ]:





# In[ ]:





# In[436]:


s_df.query(f'building_category=="house" and building_condition=="renovation" and age >= {2020-1945}')


# ## Join scurve and tek parameters into scurve_by_tek
# 
# 

# In[437]:


df = s_df.reset_index().join(tek_parameters, how='cross')
#df = s_df.reset_index().join(left=s_df.reset_index(), right=tek_parameters, how=['cross'])

df['year'] = df['building_year'] + df['age']

scurve_by_tek = df.copy()
df




# In[438]:


df.query('TEK=="TEK17"')


# In[439]:


s_df.reset_index().sample(7)




# In[ ]:





# In[440]:


r=scurve_by_tek.reset_index()
r


# In[441]:


r.query('TEK=="TEK17"')

q=r.pivot(index=['building_category', 'TEK', 'year'], columns=['building_condition'], values='scurve')
q


# In[442]:


df_p = r.pivot(index=['building_category', 'TEK', 'year'], columns=['building_condition'], values='scurve')


df_p


# In[443]:


df_p.xs(level='TEK', key='TEK17', drop_level=False)


# In[444]:


#.rename_axis(None, axis=1)
df_p = df_p.reset_index().set_index(['building_category', 'TEK', 'year'], drop=True).rename_axis(None, axis=1)
df_p.query('building_category=="house"')


# In[445]:


df = df_p.copy() #.loc['house']

df


# ## Calculate new cumulative demolition with zero demolition in start year

# In[446]:


pd.set_option('display.float_format', '{:.6f}'.format)

df.loc[df.query(f'year<={years.start}').index, 'demolition'] = 0.0
df['demolition_acc'] = df.groupby(by=['building_category', 'TEK'])[['demolition']].cumsum()[['demolition']]


#df=df.query(f'year>={years.start}')
df.query('building_category=="house" and TEK=="PRE_TEK49" and year > 2018')

df_p = df.copy()
df_p


# ## Load construction

# In[447]:


df_ap = area_parameters.set_index(['building_category', 'TEK']).copy()
demolition_by_year = (df_ap.loc[:, 'area'] * df.loc[:, 'demolition'])

print('demolition_floor_area.describe()=\n', demolition_by_year.describe())
print('demolition_floor_area.sum()=\n', demolition_by_year.sum())
#df[['demolition_acc']] * .area
demolition_by_year.name = 'demolition'
demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(2020, 2050))]
demolition_by_year.loc[(slice(None), slice(None), [2020, 2021, 2030, 2049, 2050])]



# In[448]:


demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()
demolition_by_building_category_year
#demolition_floor_area.loc[(['apartment_block'], slice(None), [2050])]


# In[449]:


#demolition_by_building_category_year.loc[(['culture'])]


# ## Make area

# In[450]:


df = area_parameters.copy()
# Define the range of years

# Create a MultiIndex with all combinations of cat_a, cat_b, and year



index = pd.MultiIndex.from_product([scurve_parameters['building_category'].unique(), tek_parameters.TEK.unique(), years], names=['building_category', 'TEK', 'year'])

# Reindex the DataFrame to include all combinations, filling missing values with NaN
area = index.to_frame().set_index(['building_category', 'TEK', 'year']).reindex(index).reset_index()

# Optional: Fill missing values with a default, e.g., 0
# df_full['value'] = df_full['value'].fillna(0)
ap_df = area_parameters.set_index(['building_category', 'TEK'])
ap_df

existing_area = pd.merge(left=ap_df, right=area, on=['building_category', 'TEK'], suffixes=['_r', ''])
existing_area = existing_area.set_index(['building_category', 'TEK', 'year'])
existing_area


# In[451]:


existing_area.loc[(['culture',], slice(None), slice(None))]


# In[452]:


area_parameters


# In[453]:


demolition_by_building_category_year


# In[454]:


dm = DatabaseManager(FileHandler(directory=input_directory))
construction = ConstructionCalculator.calculate_all_construction(demolition_by_building_category_year, database_manager=dm, period=years)

construction
#df.query('building_category=="house" and TEK=="PRE_TEK49" and year > 2018')


# In[455]:


logger.warning('Cheating by assuming TEK17')
constructed_tek17 = construction.copy()
constructed_tek17['TEK'] = 'TEK17'
construction_by_building_category_yearly = constructed_tek17.set_index(['building_category', 'TEK', 'year']).accumulated_constructed_floor_area
construction_by_building_category_yearly.name = 'area'
construction_by_building_category_yearly


# In[456]:


construction_by_building_category_yearly.loc['university']


# In[457]:


existing_area


# In[458]:


total_area_by_year = pd.concat([existing_area.drop(columns=['year_r'], errors='ignore'), construction_by_building_category_yearly])
print(total_area_by_year)


# In[459]:


df = total_area_by_year.copy()

df.query(f'building_category=="house" and TEK=="TEK17" and year >= {years.start} and year <={years.end}')


# ## Join area into df_p

# In[460]:


with_area = df.join(df_p, how='left').fillna(0.0)
with_area


# In[461]:


with_area.loc[(['university'], ['TEK17'], slice(None))]


# In[462]:


with_area = df.join(df_p, how='left').fillna(0.0)
#with_area.loc[(slice(None), slice(['culture']))]
with_area.index.get_level_values(level='TEK').unique()
with_area.index.get_level_values(level='building_category').unique()
with_area.index.get_level_values(level='year').unique()
with_area = with_area.sort_index()
with_area


# In[463]:


with_area.loc[(slice(None), ['TEK17'], slice(None))]
df_p.loc[(slice(None), ['TEK17'], slice(None))]


# 
# ## set max values

# In[464]:


#df = df_p.copy()
df = with_area.copy()

df.loc[:, 'renovation_max'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'renovation_nvr']
df.loc[:, 'small_measure_max'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'small_measure_nvr']
df.query('building_category=="house" and year > 2018')


# In[465]:


# hus=df.query('building_category=="house" and year > 2018')
# hus.loc[:, 'sm2'] = hus['small_measure_acc'] - hus['demolition_acc']
# hus[['sm2', 'small_measure_max']]


# ## small_measure and renovation to shares_small_measure_total, RN

# ## SharesPerCondition calc_renovation
# 
#  - ❌ Ser ut som det er edge case for byggeår.
#  - ❌ Årene før byggeår må settes til 0 for shares_renovation?

# In[466]:


df.loc[:, 'shares_small_measure_total'] = df.loc[:, ['small_measure_acc', 'small_measure_max']].min(axis=1).clip(lower=0.0)
df.loc[:, 'shares_renovation_total'] = df.loc[:, ['renovation_acc', 'renovation_max']].min(axis=1).clip(lower=0.0)
df.loc[:, 'shares_renovation'] = (df.loc[:, 'renovation_max'] - df.loc[:, 'shares_small_measure_total']).clip(lower=0.0)
df.loc[:, 'shares_total'] = (df.loc[:, 'shares_small_measure_total'] + df.loc[:, 'shares_renovation_total']).clip(lower=0.0)

# SharesPerCondition -> calc_renovation 273:285
df.loc[df[df.shares_total < df.renovation_max].index,  'shares_renovation'] = df.loc[df[df.shares_total < df.renovation_max].index, 'shares_renovation_total']

#df.loc[:, 'sr2'] = df.loc[:, ['shares_total', 'renovation_max']].min(axis=1).clip(lower=0.0)

df.query('building_category=="house" and year >= 2019 and year <= 2050 and TEK=="TEK49"')[['shares_small_measure_total', 'renovation_max', 'shares_renovation_total', 'shares_renovation', 'shares_total']]


# ### SharesPerCondition calc_renovation_and_Small_measure
# 
#  - ❌ Sette til 0 før byggeår
# 
# 

# In[467]:


df.loc[:, 'renovation_and_small_measure'] = df.loc[:, 'shares_renovation_total'] - df.loc[:, 'shares_renovation']

df.loc[:, ['renovation_and_small_measure', 'shares_small_measure_total', 'shares_renovation_total', 'shares_renovation']].query('building_category=="house" and TEK=="TEK49" and year >= 2020 and year <=2050')
#df.loc[:, ['shares_small_measure_total', 'shares_renovation_total']].query('building_category=="house" and TEK=="PRE_TEK49" and year >= 2020 and year <=2050').sum()


# ### SharesPerCondition calc_small_measure
# 
#  - ❌   sette til 0 før byggeår
# ```python
#     construction_year = self.tek_params[tek].building_year
#     shares.loc[self.period_index <= construction_year] = 0
# ```

# In[468]:


df.loc[:, 'shares_small_measure'] = df.loc[:, 'shares_small_measure_total'] -  df.loc[:, 'renovation_and_small_measure']

# and TEK=="PRE_TEK49" and year >= 2020 and year <=2050
df.loc[:, ['shares_small_measure_total', 'renovation_and_small_measure', 'shares_small_measure']].query('building_category=="house"') #.query("building_category=='house' and year>=2020 and year <=2050 and TEK=='TEK49'"




# ### SharesPerCondition calc_original_condition

# In[469]:


df.loc[:, 'original_condition'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'shares_renovation'] - df.loc[:, 'renovation_and_small_measure'] - df.loc[:, 'shares_small_measure']
df.query('building_category=="house" and TEK=="PRE_TEK49" and year >= 2020 and year <=2050')


# In[470]:


df.query('building_category=="house" and TEK=="TEK17" and year >= 2020 and year <=2050')



# ## join calculated scurves on area

# In[472]:


scurved = df.copy()
scurved


# In[473]:


scurved.loc[(slice(None), ['TEK17'], slice(None))]


# In[ ]:





# In[ ]:





# In[474]:


#sca.loc[:, ['demolition', 'shares_small_measure_total', 'RN', 'both']] * sca['area', 'area', 'area', 'area']]
a_mul = scurved[[
    'original_condition',
    'demolition_acc',
    'shares_small_measure',
    'shares_renovation',
    'renovation_and_small_measure', 'area']]

area_by_condition = a_mul[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation', 'renovation_and_small_measure']].multiply(a_mul['area'], axis=0)
#area_by_condition.query('TEK=="TEK10"').sort_index(level=['year', 'building_category', 'TEK'])
print('calculation time', time.time()- start_time)
area_by_condition




# # SUMS

# In[475]:


print(area_by_condition.sort_index(level=['building_category','year',  'TEK']).loc[(['university'], ['TEK49'], [2020, 2021, 2022, 2023, 2024, 2025, 2029, 2030, 2031, 2048, 2049, 2050])])


# In[476]:


print(area_by_condition.sort_index(level=['building_category','year',  'TEK']).loc[(['hotel'], ['PRE_TEK49'], [2020, 2021, 2022, 2023, 2024, 2025, 2029, 2030, 2031, 2048, 2049, 2050])])


# In[477]:


print(area_by_condition.sort_index(level=['building_category','year',  'TEK']).loc[(['hotel'], ['TEK17'], [2020, 2021, 2022, 2023, 2024, 2025, 2029, 2030, 2031, 2048, 2049, 2050])])


# In[478]:


print('diff', area_by_condition.sum(axis=1).sum() -17717147447.0043000000)
