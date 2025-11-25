#%%

import pathlib

import pandas as pd
import rich

from ebm.model.building_category import BuildingCategory
from ebm.model.column_operations import explode_unique_columns, replace_column_alias
from ebm.model.energy_purpose import EnergyPurpose

#%%

#%% md
# # Investigate behaviour factor priority
#%% md
# ## Load energy_need_behaviour_factor.csv
#%%
building_code_list = pd.read_csv('input/building_codes.csv').building_code.tolist()
building_code_list
#%%
filenames = {
    'default':pathlib.Path('kalibrert/energy_need_behaviour_factor.csv'),
    'ebm_data': pathlib.Path('C:\\Users\\kenord\\pyc\\Energibruksmodell\\ebm\\data\\energy_need_behaviour_factor.csv')
}

file_to_load=filenames.get('ebm_data')
#%% md
# ### As CSV
#%%
print(file_to_load.read_text())
#%% md
# ### As Dataframe
#%%

df_bh: pd.DataFrame = pd.read_csv(file_to_load)
df_bh['row'] = df_bh.index + 1
df_bh.reset_index(drop=True, inplace=True)
df_bh
#%% md
# ## Expand column groups
# 
# ### expand building_category
#%%
df_bh = replace_column_alias(df_bh, 'building_category', values=[b for b in BuildingCategory if b.is_residential()], alias='residential')
df_bh = replace_column_alias(df_bh, 'building_category', values=[b for b in BuildingCategory if not b.is_residential()], alias='non_residential')
df_bh = replace_column_alias(df_bh, 'building_category', values=[b for b in BuildingCategory], alias='default')
df_bh
#%% md
# ### expand TEK
#%%
df_bh = replace_column_alias(df_bh, 'building_code', values=building_code_list, alias='default')
df_bh
#%% md
# ### expand purpose
#%%
df_bh = replace_column_alias(df_bh, 'purpose', values=[p for p in EnergyPurpose], alias='default')
df_bh


#%% md
# ## Add priority column and sort
#%%
df_bh['bc_priority'] = df_bh.building_category.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
df_bh['t_priority'] = df_bh.building_code.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
df_bh['p_priority'] = df_bh.purpose.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
if not 'priority' in df_bh.columns:
    df_bh.insert(8, 'priority', 0)
df_bh['priority'] = df_bh.bc_priority + df_bh.t_priority + df_bh.p_priority
df_bh
#%% md
# ## Explode building_category, TEK, purpose
#%%
df_bh=df_bh.assign(**{'building_category': df_bh['building_category'].str.split('+'),}).explode('building_category')

df_bh=df_bh.assign(**{'building_code': df_bh['building_code'].str.split('+')}).explode('building_code')
df_bh=df_bh.assign(**{'purpose': df_bh['purpose'].str.split('+'),}).explode('purpose')
df_bh=df_bh.sort_values(by=['building_category', 'building_code', 'purpose', 'priority'])
df_bh['dupe'] = df_bh.duplicated(['building_category', 'building_code', 'purpose'], keep=False)
df_bh

#%% md
# ### List of duplicates
#%%
df_bh[df_bh.dupe]
#%%
### count building_category, TEK, purpose
#%%
unique_building_categories = len(df_bh.building_category.unique())
unique_building_code = len(df_bh.building_code.unique())
unique_purpose = len(df_bh.purpose.unique())
# unique_condition = len(df_bh.building_condition.unique())
# unique_year = len(df_bh.year.unique())

unique_all = unique_building_categories * unique_building_code * unique_purpose # * unique_year #* unique_condition
print('expected:', unique_all)
print('actual:', len(df_bh))
#%% md
# ## Show different building_category, TEK, purpose
#%%

# df_bh[df_bh.duplicated(['building_category', 'building_code', 'purpose'], keep=False)]
#df_bh.drop_duplicates(['building_category', 'building_code', 'purpose'], keep='first')
rich.print(df_bh.query('building_category=="house" and building_code=="PRE_TEK49" and purpose=="lighting"'))
rich.print(df_bh.query('building_category=="house" and building_code=="PRE_TEK49" and purpose=="electrical_equipment"'))
rich.print(df_bh.query('building_category=="house" and building_code=="TEK17" and purpose=="lighting"'))
rich.print(df_bh.query('building_category=="house" and building_code=="TEK17" and purpose=="electrical_equipment"'))
rich.print(df_bh.query('building_category=="retail" and purpose=="electrical_equipment"'))
#%%
# df_bh['bc_priority'] = (2* df_bh.building_category.isin(['residential', 'non_residential'])).astype(int) + (4*(df_bh.building_category == 'default').astype(int))
# df_bh['t_priority'] = (4*(df_bh.building_category == 'default').astype(int))
# df_bh['p_priority'] = (4*(df_bh.purpose == 'default').astype(int))
# if 'priority' not in df_bh.columns:
#     df_bh.insert(8, 'priority', 0)
# df_bh['priority'] = df_bh.bc_priority + df_bh.t_priority + df_bh.p_priority
# df_bh
#%% md
# ## Load behavior_factor from energy_requirement_original_condition.csv
#%%

# df = energy_need_behaviour_factor.validate(df_bh)
df = df_bh


# df['dupe'] = df.duplicated(['building_category', 'building_code', 'purpose', 'year', 'building_condition'], keep=False)
df = df.drop_duplicates(['building_category', 'building_code', 'purpose'], keep='first')

ddf = df.set_index(['building_category', 'building_code', 'purpose',])[['behaviour_factor']]
ddf
#%%
eroc = pd.read_csv('kalibrert/energy_requirement_original_condition.csv')
eroc = explode_unique_columns(eroc, ['building_category', 'building_code', 'purpose'])

eroc = eroc.set_index(['building_category', 'building_code', 'purpose'])[['behavior_factor']]
eroc
#%% md
# ## Compare energy_needs_behaviour_factor to energy_requirement_original_condition
#%%
r = eroc.join(ddf)
r
#%% md
# ### same
#%%

rich.print(r[r.behavior_factor==r.behaviour_factor])

#%% md
# ### Different
#%%
rich.print(r[r.behavior_factor!=r.behaviour_factor])
if len(r[r.behavior_factor!=r.behaviour_factor]) == 0:
    print('Nothing to show')
#%% md
# ## Display various rows
#%%
rich.print(r.query('building_category=="house" and purpose=="lighting"'))
#%%
assert r.query('building_category=="house" and purpose=="lighting"')['behaviour_factor'].tolist() == [0.85] * 8
#%%

#%%

#%%

#%%

#%%
