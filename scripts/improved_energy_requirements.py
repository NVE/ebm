#%%
import numpy as np
import pandas as pd
from loguru import logger
#%%
from ebm.model.building_category import BuildingCategory
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.data_classes import YearRange
from ebm.model.building_condition import BuildingCondition

import time

from ebm.services.files import make_unique_path

#%% md
# ## New functions
#%%
st = time.time()
#%%
def explode_column_alias(df, column, values=None, alias='default', de_dup_by=None):
    values = values if values else [c for c in df[column].unique().tolist() if c!=alias]
    df['_explode_column_alias_default'] = df[column]==alias
    df.loc[df[df[column] == alias].index, column] = '+'.join(values)
    df = df.assign(**{column: df[column].str.split('+')}).explode(column)
    if de_dup_by:
        df = df.sort_values(by='_explode_column_alias_default', ascending=True)
        df = df.drop_duplicates(de_dup_by)
    return df.drop(columns=['_explode_column_alias_default'], errors='ignore')


def yearly_reduction(x):
    if x.year < x.period_start_year:
        return 1.0
    if x.year > x.period_end_year:
        return 1.0 - x.improvement_at_period_end
    #year = int()
    return np.linspace(1.0, 1.0 - x.improvement_at_period_end, int(x.period_end_year - x.period_start_year + 1.0))[x.year_no] #x.year_no.astype(int)
#%% md
# ## count combinations
#%%
all_teks = pd.read_csv('kalibrering/TEK_ID.csv').TEK.tolist()
print('all_teks', len(all_teks))
all_building_categories = list(BuildingCategory)
print('all_building_categories', len(all_building_categories))
all_purpose = list(EnergyPurpose)
print('all_purpose', len(all_purpose))
most_conditions = list(BuildingCondition.existing_conditions())
print('most_conditions', len(most_conditions))
model_years = YearRange(2020, 2050)
print('years', len(model_years))
print('total', len(all_building_categories) * len(all_teks) * len(all_purpose) * len(most_conditions) * len(model_years))
#%% md
# ## Full frame
#%%

df_bc = pd.DataFrame(all_building_categories, columns=['building_category'])
df_tek = pd.merge(df_bc, pd.DataFrame({'TEK': all_teks}), how='cross')
df_purpose = pd.merge(df_tek, pd.DataFrame(all_purpose, columns=['purpose']), how='cross')
df_condition = pd.merge(df_purpose, pd.DataFrame({'building_condition': most_conditions}), how='cross')
df_years = pd.merge(df_condition, pd.DataFrame({'year': model_years}), how='cross')

print(df_years)
#%% md
# ## Energy requirements original condition
#%%
erq_oc = pd.read_csv('kalibrering/energy_requirement_original_condition.csv')
erq_oc = erq_oc[erq_oc['TEK']!='TEK21']
erq_oc['_src_erq_oc'] = 'src'
erq_oc = explode_column_alias(erq_oc, 'TEK', all_teks, 'default')
print(erq_oc)
#%% md
# ## Merge oc to energy_requirements
#
# ### building_conditions
#%%
erq_all_conditions = pd.merge(left=df_condition, right=erq_oc, how='left')
erq_all_conditions['_src_erq_a_c'] = 'src'

print(erq_all_conditions.sample(7))
#%% md
# ### years
#%%

erq_all_years = pd.merge(left=df_years, right=erq_oc, how='left')
erq_all_years['_erq_al_yrs'] = 'src'

print(erq_all_years.sample(7))

#%% md
# ### energy_requirements from energy requirement reduction by condigion and all years
#
#%%

energy_requirements = erq_all_years.drop(columns=['index', 'level_0'], errors='ignore')

print(energy_requirements)
#%% md
# ## Reduction share to reduction_condition
#%%
r_s = pd.read_csv('kalibrering/energy_requirement_reduction_per_condition.csv')
r_s['reduction_condition'] = 1.0-r_s['reduction_share']
r_s = explode_column_alias(r_s, 'building_category', all_building_categories, 'default')
r_s = explode_column_alias(df=r_s, column='TEK', values=all_teks, alias='default', de_dup_by=['building_category', 'TEK', 'purpose', 'building_condition'])
r_s = r_s[r_s['TEK']!='TEK21']
r_s.loc[:, 'reduction_condition'] = r_s.loc[:, 'reduction_condition'].fillna(1.0)
r_s['_src_r_s'] = 'src'

#%%
r_s[r_s.duplicated(['building_category', 'TEK', 'purpose', 'building_condition'])]


#%%
reduction_condition = pd.merge(left=r_s, right=pd.DataFrame({'year': model_years}), how='cross')
reduction_condition = pd.merge(df_years, reduction_condition)

print(reduction_condition)
#%% md
# ## Policy improvement
#%%
p_i = pd.read_csv('kalibrering/energy_requirement_policy_improvements.csv')

p_i = explode_column_alias(p_i, 'building_category', all_building_categories, 'default')
p_i = explode_column_alias(p_i, 'TEK', all_teks, 'default')
p_i['_src_p_i'] = 'src'

policy_improvement = pd.merge(right=pd.DataFrame({'year': model_years}), left=p_i, how='cross')

print(policy_improvement)
#%%

e_y = policy_improvement.copy()
e_y.loc[:, 'year_no'] = e_y.loc[:, 'year'] - e_y.loc[:, 'period_start_year']
e_y.loc[:, 'year_no'] = e_y.loc[:, 'year_no'].fillna(0)
e_y['_src_e_y'] = 'src'

policy_improvement_slice = e_y[~e_y.year_no.isna()].index
e_y.loc[policy_improvement_slice, 'reduction_policy'] = e_y.loc[policy_improvement_slice].apply(yearly_reduction, axis=1)


policy_improvement = e_y

print(policy_improvement)
#%% md
# ## yearly improvements

y_i = pd.read_csv('kalibrering/energy_requirement_yearly_improvements.csv')

y_i = explode_column_alias(y_i, 'building_category', all_building_categories, 'default')
y_i = explode_column_alias(y_i, 'TEK', all_teks, 'default')
y_i.loc[:, 'efficiency_start_year'] = 2020
y_i = pd.merge(y_i, pd.DataFrame({'year': model_years}), how='cross')
y_i.loc[:, 'reduce_efficiency_improvement'] = 1.0 - y_i.loc[:, 'yearly_efficiency_improvement']
y_i.loc[:, 'year_efficiency'] = y_i.loc[:, 'year'] - y_i.loc[:, 'efficiency_start_year']
y_i['_src_y_i'] = 'src'

yearly_improvements = y_i

print(yearly_improvements)

#%%
yearly_improvements = pd.merge(y_i, policy_improvement, how='left')

print(yearly_improvements)
#%%
yearly_improvements[yearly_improvements.duplicated(['building_category', 'TEK', 'purpose', 'year'])]
#%%

yearly_improvements['efficiency_start_year'] = yearly_improvements[['period_end_year', 'efficiency_start_year']].max(axis=1).astype(int)
yearly_improvements.loc[:, 'year_efficiency'] = (yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:, 'efficiency_start_year']).clip(0)
yearly_improvements.loc[:, 'reduction_yearly'] = (1.0-yearly_improvements.loc[:, 'yearly_efficiency_improvement'])**yearly_improvements.loc[:, 'year_efficiency']
yearly_improvements.loc[:, 'year_efficiency'] = yearly_improvements.loc[:, 'year'] - yearly_improvements.loc[:, 'efficiency_start_year']

print(yearly_improvements.sample(7))

#%% md
# ## merge all
#%%
m_nrg_yi = pd.merge(left=energy_requirements.copy(), right=yearly_improvements.copy(), how='left')
merged = pd.merge(left=m_nrg_yi.copy(), right=reduction_condition.copy(), on=['building_category', 'TEK', 'purpose', 'building_condition', 'year'], how='left')

merged.loc[:, 'reduction_yearly'] = merged.loc[:, 'reduction_yearly'].fillna(1.0)
merged.loc[:, 'reduction_policy'] = merged.loc[:, 'reduction_policy'].fillna(1.0)
merged.loc[:, 'reduction_share'] = merged.loc[:, 'reduction_share'].fillna(1.0)
merged['reduction_condition'] = merged['reduction_condition'].fillna(1.0)

merged['reduced_kwh_m2'] = merged['kwh_m2'] * merged['reduction_condition'] * merged['reduction_yearly'] * merged['reduction_policy']
merged['behavior_kwh_m2'] = merged['reduced_kwh_m2'] * merged['behavior_factor']

print(merged)
#%% md
# ## Write to disk
#%%
print('time:', time.time() - st, ' s')
uniq_path = make_unique_path('output/new_energy_requirements.xlsx')
logger.info(f'Writing to {uniq_path}')
merged.to_excel(uniq_path)
logger.info(f'Wrote   to {uniq_path}')
#%%

#%% md
# ### Calculate reduced KWh/m2
#%%
df = merged
print(df[df.duplicated(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])])
#%%