#%%
import pandas as pd
import numpy as np


#%% md
# ## Setup
#
#%%
from ebm.energy_consumption import EnergyConsumption
from ebm.energy_consumption import *
#%%
WRITE_TO_EXCEL=False
#%%
hsp = pd.read_csv('qq_hsp.csv')
hsp
#%%

#%%

er = pd.read_csv('qq_er.csv')
er
#%%
# Load = B, P, T, O, v

columns = ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'heating_systems', 'load', 'energy_product', 'load_share', 'load_efficiency']

df = hsp.copy().reset_index()
df['_num_loads'] = df.heating_systems.apply(lambda s: len(s.split('-')))
df[['heating_systems', '_num_loads']]

heating_systems_parameters = df.copy()
df
#%% md
# ### heating_rv
#
# #### Base load
#
#%%
heating_systems_parameters['heating_system'] = '-'

df_bl = heating_systems_parameters[['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD,GRUNNLAST_ENERGIVARE, '_num_loads', 'heating_system']].copy()
df_bl = df_bl.rename(columns={GRUNNLAST_ANDEL: 'load_share', GRUNNLAST_VIRKNINGSGRAD: 'load_efficiency', GRUNNLAST_ENERGIVARE: 'energy_product'})
df_bl.loc[:, 'load'] = 'base'
df_bl.loc[:, 'purpose'] = 'heating_rv'
df_bl['heating_system'] = df_bl.heating_systems.apply(lambda s: s.split('-')[0])

df_bl
#%% md
# #### Peak load
#%%

df_pl = heating_systems_parameters[['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD,SPISSLAST_ENERGIVARE, '_num_loads' , 'heating_system']].copy()
df_pl = df_pl.rename(columns={SPISSLAST_ANDEL: 'load_share', SPISSLAST_VIRKNINGSGRAD: 'load_efficiency', SPISSLAST_ENERGIVARE: 'energy_product'})
df_pl.loc[:, 'load'] = 'peak'
df_pl.loc[:, 'purpose'] = 'heating_rv'
df_pl['heating_system'] = df_pl.heating_systems.apply(lambda s: s.split('-')[1:2]).explode('heating_system')
df_pl
#%% md
# #### tertiary load
#%%

df_tl = heating_systems_parameters[['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, EKSTRALAST_ANDEL, EKSTRALAST_VIRKNINGSGRAD,EKSTRALAST_ENERGIVARE, '_num_loads', 'heating_system']].copy()
df_tl = df_tl.rename(columns={EKSTRALAST_ANDEL: 'load_share', EKSTRALAST_VIRKNINGSGRAD: 'load_efficiency', EKSTRALAST_ENERGIVARE: 'energy_product'})
df_tl.loc[:, 'load'] = 'tertiary'
df_tl.loc[:, 'purpose'] = 'heating_rv'
df_tl.loc[df_tl[df_tl['_num_loads']==3].index ,'heating_system'] = df_tl.loc[df_tl[df_tl['_num_loads']==3].index].heating_systems.apply(lambda s: s.split('-')[2])
#%% md
# ### Electrical equipment, lighting, cooling, fans_and_pumps
#
#%%

df_o = heating_systems_parameters[['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE, '_num_loads']].copy()
df_o.loc[:, GRUNNLAST_ANDEL] = 1.0
df_o.loc[:, GRUNNLAST_VIRKNINGSGRAD] = 1.0
df_o.loc[:, GRUNNLAST_ENERGIVARE] = 'Electricity'
df_o = df_o.rename(columns={GRUNNLAST_ANDEL: 'load_share', GRUNNLAST_VIRKNINGSGRAD: 'load_efficiency', GRUNNLAST_ENERGIVARE: 'energy_product'})
df_o.loc[:, 'load'] = 'other'
df_o.loc[:, '_purposes'] = 'cooling,electrical_equipment,fans_and_pumps,lighting'
df_o = df_o.assign(**{'purpose': df_o['_purposes'].str.split(',')}).explode('purpose')
df_o = df_o.drop(columns=['_purposes'], errors='ignore')
df_o
#%% md
# ### heating_dhw
#%%

df_v = df[['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, DHW_EFFICIENCY, TAPPEVANN_ENERGIVARE, '_num_loads']].copy()
df_v.loc[:, GRUNNLAST_ANDEL] = 1.0
df_v = df_v.rename(columns={GRUNNLAST_ANDEL: 'load_share', DHW_EFFICIENCY: 'load_efficiency', TAPPEVANN_ENERGIVARE: 'energy_product'})
df_v.loc[:, 'load'] = 'dhw'
df_v['purpose'] = 'heating_dhw'
df_v

#%% md
# ### heating_systems concat
#%%

hs = pd.concat([df_bl, df_pl, df_tl, df_o, df_v])


hs

#%%
if WRITE_TO_EXCEL:
    hs.to_excel('output/hs-long.xlsx')
#%% md
# ### Efficiency factor
#%%
df = hs.copy()

df.loc[:, 'efficiency_factor'] =  df.loc[:, 'TEK_shares'] * df.loc[:, 'load_share'] / df.loc[:, 'load_efficiency']

efficiency_factor = df.copy()
print(efficiency_factor.columns)
df




#%%
df[['building_category', 'TEK', 'year', 'purpose', 'heating_systems',  'load', 'heating_system', 'energy_product', 'TEK_shares', 'load_share', 'load_efficiency', 'efficiency_factor']]
#%%
if WRITE_TO_EXCEL:
    efficiency_factor.to_excel('output/efficiency_factor.xlsx')
#%%
hs.query('building_category=="house" and year==2020 and heating_systems=="HP - Bio - Electricity" and TEK=="TEK49"')
#%% md
# ### Merge energy requirement into hs_log
#%%
hs_long = efficiency_factor.copy()
nrj = er.copy()


df = nrj.reset_index().merge(hs_long,
            left_on=['building_category', 'TEK', 'purpose', 'year'],
            right_on=['building_category', 'TEK', 'purpose', 'year'])[['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'kwh_m2', 'm2', 'energy_requirement', HEATING_SYSTEMS, TEK_SHARES, 'load', 'load_share', 'load_efficiency', 'energy_product', '_num_loads']]
        # Unused columns
        # ,'Innfyrt_energi_kWh','Innfyrt_energi_GWh','Energibehov_samlet_GWh']]
# df = df.set_index(['building_category', 'building_condition', 'purpose', 'TEK', 'year', HEATING_SYSTEMS, 'load']).sort_index()
heating_systems = df.copy()
df
#%% md
# ### Filter out redundant load
#%%
## Hvor mange rader med overflødig spiss og esktra borte?
#df = heating_systems.copy().iloc[0:48]
#df = heating_systems.copy()


#df = df[~(df['load']=='tertiary') & (df['_num_loads']<3)]
#df = df[~(df['load']=='peak') & (df['_num_loads']<2)]
df['tre'] = ~((df['_num_loads']<3) & (df['load']=='tertiary'))
df = df[~((df['_num_loads']<3) & (df['load']=='tertiary'))]
df = df[~((df['_num_loads']<2) & (df['load']=='peak'))]

df

#%% md
# ### Check HP - Bio - Electricity
#%%
df.query('building_category=="house" and year==2020 and TEK=="TEK49" and heating_systems=="HP - Bio - Electricity"')
#%%
6.056834e+07 + 3.757341e+07 + 6.838361e+07

#%%
df['kwh'] = df['energy_requirement'] * df['TEK_shares'] * df['load_share'] / df['load_efficiency']

df[['building_category', 'year', 'load', 'kwh']].groupby(by=['building_category','year', 'load']).sum()[['kwh']]
#%%
df.loc[df['building_category'].isin(['house', 'apartment_block']), 'building_category'] = 'bolig'
#%%
df[df['building_category'].isin(['house', 'apartment_block'])]['building_category'] = 'bolig'

df[['building_category','year', 'kwh']].groupby(by=['building_category','year']).sum()[['kwh']]
#%%
if WRITE_TO_EXCEL:
    heating_systems.iloc[0:1048575].to_excel('output/heating_systems-long.xlsx')

print(df)
#%%

# ec = EnergyConsumption(hsp)
# ec.heating_systems_parameters = ec.grouped_heating_systems()

# df = ec.calculate(er)
# df
#%%
if WRITE_TO_EXCEL:
    df.to_excel('hs-not-as-long.xlsx')
#%%

#%%
