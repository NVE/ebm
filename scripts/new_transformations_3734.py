#!/usr/bin/env python
# coding: utf-8

# # Nye transformasjoner

# ## Import

# In[1]:


import sys
from loguru import logger
from ebm.cmd.run_calculation import configure_loglevel
import os

import numpy as np
import pandas as pd

import pathlib

print(os.getcwd())

cwd = pathlib.Path(os.getcwd())
if cwd.name != 'workspace':
    os.chdir('../workspace')

configure_loglevel(os.environ.get('LOG_FORMAT', None))

# logger.remove()
# options = {'level': 'INFO'}
# logger.add(sys.stderr, **options)


# ## Setup

# In[2]:


from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.model.building_category import BuildingCategory

# In[3]:


os.environ['EBM_WRITE_TO_DISK'] = 'False'

#
# ## Prerequisite
#
# ### Create a DatabaseManager containing a FileHandler
#
# The FileHandler read files from a specified directory. When unspecified «input» is used.

# In[4]:


years = YearRange(2020, 2050)
input_path = pathlib.Path('t2734_input')
output_path = pathlib.Path('t2734_output')
output_path.mkdir(exist_ok=True)

file_handler = FileHandler(directory=input_path)
database_manager = DatabaseManager(file_handler=file_handler)

try:
    print(file_handler.validate_input_files())
except FileNotFoundError:
    print('Missing files: ', file_handler.check_for_missing_files())

# In[ ]:


# ## area

# ### load area

# In[5]:


from ebm.model.buildings import Buildings
from ebm.model.area_forecast import AreaForecast

from ebm.model.construction import ConstructionCalculator

# In[6]:


construction: pd.DataFrame | None = None
demolition: pd.DataFrame | None = None

for building_category in BuildingCategory:
    buildings = Buildings.build_buildings(building_category=building_category, database_manager=database_manager,
                                          period=years)
    area_forecast: AreaForecast = buildings.build_area_forecast(database_manager, years.start, years.end)
    s = area_forecast.calc_total_demolition_area_per_year()
    building_category_demolition = s.to_frame().reset_index()
    building_category_demolition['building_category'] = building_category

    demolition_floor_area = building_category_demolition[
        building_category_demolition['building_category'] == building_category].set_index('year').demolition

    df = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area, database_manager,
                                                       period=years)
    df['building_category'] = building_category
    df = df.reset_index().set_index(['building_category', 'year'])
    if construction is None:
        construction = df
        demolition = s
    else:
        construction = pd.concat([construction, df])
        demolition = pd.concat([demolition, s])
    print(building_category)

construction.to_excel(output_path / 'construction.xlsx', merge_cells=False)
construction

# In[7]:


demolition

# In[ ]:


# In[8]:


construction

# In[9]:


forecasts: pd.DataFrame | None = None

for building_category in BuildingCategory:
    buildings = Buildings.build_buildings(building_category=building_category, database_manager=database_manager,
                                          period=years)
    area_forecast: AreaForecast = buildings.build_area_forecast(database_manager, years.start, years.end)

    accumulated_constructed_floor_area = construction.loc[building_category, 'accumulated_constructed_floor_area']
    forecast: pd.DataFrame = area_forecast.calc_area(accumulated_constructed_floor_area)
    forecast['building_category'] = building_category
    if forecasts is None:
        forecasts = forecast
    else:
        forecasts = pd.concat([forecasts, forecast])

forecasts.to_excel(output_path / 'forecasts.xlsx', merge_cells=False)
forecasts

# ## area fane 1 (wide)

# ### Transformation

# In[10]:


from ebm.cmd.result_handler import transform_model_to_horizontal, append_result

# In[11]:


df = forecasts.copy()

df = df.query('building_condition!="demolition"')
df.loc[:, 'TEK'] = 'all'
df.loc[:, 'building_condition'] = 'all'

df = transform_model_to_horizontal(df).drop(columns=['TEK', 'building_condition'])

area_fane_1 = df.copy()

df.sample(3)

# ### Result

# In[12]:


area_fane_1

# In[13]:


append_result(output_path / 'area.xlsx', area_fane_1, sheet_name='wide')

# ## area fane 2 (long)

# ### Transformation

# In[14]:


df = forecasts['year,building_category,TEK,building_condition,m2'.split(',')].copy()
df = df.query('building_condition!="demolition"')

df = df.groupby(by='year,building_category,TEK'.split(','))[['m2']].sum().rename(columns={'m2': 'area'})
df.insert(0, 'U', 'm2')
area_fane_2 = df.reset_index()
df

# ### Result

# In[15]:


area_fane_2

# In[16]:


append_result(output_path / 'area.xlsx', area_fane_2, sheet_name='long')

# ## energy_purpose
#

# ### Load energy_need

# In[17]:


from ebm.model.energy_requirement import EnergyRequirement
from ebm.model.building_category import BEMA_ORDER as building_category_order
from ebm.model.tek import BEMA_ORDER as tek_order

# In[18]:


er_calculator = EnergyRequirement.new_instance(period=years, calibration_year=2023, database_manager=database_manager)
energy_needs = er_calculator.calculate_for_building_category(database_manager=database_manager)

energy_needs = energy_needs.set_index(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])

energy_needs

# ## energy_purpose Fane 1

# ### Transformation

# In[19]:


df_a = forecasts.copy()
df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
    ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

df_e = energy_needs.copy().reset_index().set_index(
    ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000
df.loc[:, ('TEK', 'building_condition')] = ('all', 'all')

non_residential = [b for b in BuildingCategory if b.is_non_residential()]

df.loc[df[df['building_category'].isin(non_residential)].index, 'building_category'] = 'non_residential'

df = df.groupby(by=['building_category', 'purpose', 'year'], as_index=False).sum()
df = df[['building_category', 'purpose', 'year', 'GWh']]

df = df.pivot(columns=['year'], index=['building_category', 'purpose'], values=['GWh']).reset_index()
df = df.sort_values(by=['building_category', 'purpose'],
                    key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                        tek_order) if x.name == 'building_category' else x.map(
                        {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                         'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

df.insert(2, 'U', 'GWh')
df.columns = ['building_category', 'purpose', 'U'] + [y for y in range(2020, 2051)]

energy_purpose_fane1 = df
df.sample(5)

# ### Result

# In[20]:


energy_purpose_fane1

# In[ ]:


# In[21]:


append_result(output_path / 'energy_purpose.xlsx', energy_purpose_fane1, sheet_name='wide')

# ## energy_purpose Fane 2
#

# ### Transformation

# In[22]:


df_a = forecasts.copy()
df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
    ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

df_e = energy_needs.copy().reset_index().set_index(
    ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000

df = df.groupby(by=['year', 'building_category', 'TEK', 'purpose'], as_index=False).sum()
df = df[['year', 'building_category', 'TEK', 'purpose', 'GWh']]
df = df.sort_values(by=['year', 'building_category', 'TEK', 'purpose'],
                    key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                        tek_order) if x.name == 'building_category' else x.map(tek_order) if x.name == 'TEK' else x.map(
                        {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                         'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

df = df.rename(columns={'GWh': 'energy_use [GWh]'})

df.reset_index(inplace=True, drop=True)
energy_purpose_fane2 = df

df

# ### Result

# In[23]:


energy_purpose_fane2

# In[24]:


append_result(output_path / 'energy_purpose.xlsx', energy_purpose_fane2, sheet_name='long')

# In[ ]:


# In[25]:


pd.concat([df.head(7), df.sample(14), df.tail(7)]).sort_index()

# ## fans_and_pumps

# In[26]:


energy_purpose_fane2.query('building_category=="house" and TEK=="PRE_TEK49" and purpose=="fans_and_pumps"')

# In[ ]:


# In[ ]:


# ## demolition_construction
#

# ### debug

# In[27]:


construction.loc[('house', 2022)]

# In[28]:


construction.loc[('kindergarten', 2023)]

# Det er forskjell på residential og non_residential
#
# non_residential har ikke demolition. Det må legges inn. (Det er vel tilgjenglig?)

# In[29]:


df = construction.copy().reset_index()

df = df[['year', 'building_category', 'constructed_floor_area', 'demolished_floor_area']]

df.melt(id_vars=['year', 'building_category'], value_vars=['constructed_floor_area', 'demolished_floor_area'],
        var_name='action', value_name='m2')

# In[ ]:


# #### tek_params

# In[30]:


tek_params = database_manager.get_tek_params(database_manager.get_tek_list())

tek = pd.DataFrame(data=[[t.tek, t.start_year, t.building_year, t.end_year] for key, t in tek_params.items()],
                   columns=['TEK', 'start_year', 'building_year', 'end_year'])

tek

# ### Transformation

# In[31]:


from ebm.model.building_condition import BuildingCondition

# In[32]:


demolition_construction = construction.copy().reset_index()
demolition_construction['TEK'] = 'TEK17'
demolition_construction['demolition_construction'] = 'construction'
demolition_construction = demolition_construction[
    ['year', 'building_category', 'TEK', 'demolition_construction', 'constructed_floor_area']]
demolition_construction = demolition_construction.rename(columns={'constructed_floor_area': 'm2'})

demolition_construction = demolition_construction[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']]

demolition = pd.DataFrame([], columns=['building_category', 'TEK', 'year', 'demolition_construction', 'm2'])
tek_list = database_manager.get_tek_list()

for building_category in BuildingCategory:
    buildings = Buildings.build_buildings(building_category=building_category, database_manager=database_manager,
                                          period=years)
    area_forecast: AreaForecast = buildings.build_area_forecast(database_manager, years.start, years.end)

    nested_list = [
        area_forecast.calc_area_pre_construction(t, BuildingCondition.DEMOLITION).to_frame().assign(**{'TEK': t}) for t
        in tek_params if t not in ['TEK17', 'TEK21']]
    bc_demolition = pd.concat(nested_list)

    bc_demolition['building_category'] = building_category
    bc_demolition['demolition_construction'] = 'demolition'
    bc_demolition.rename(columns={'area': 'm2'}, inplace=True)
    bc_demolition = bc_demolition.reset_index()
    demolition = pd.concat([demolition, bc_demolition])

df = pd.concat([demolition_construction, demolition])[
    ['year', 'demolition_construction', 'building_category', 'TEK', 'm2']]
sort_order = ['demolition_construction', 'year', 'building_category', 'TEK']

df = df.sort_values(by=sort_order,
                    key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                        tek_order) if x.name == 'TEK' else x != 'demolition' if x.name == 'demolition_construction' else x)

demo_index = df.demolition_construction == 'demolition'
df.loc[:, 'area'] = df.loc[:, 'm2']
df.loc[demo_index, 'area'] = df.loc[demo_index, 'm2'] * -1

df = df.set_index(['building_category', 'TEK', 'year'])

e_n = energy_needs.copy()
e_n = e_n.query('building_condition == "renovation_and_small_measure"')
# e_n = e_n.query('building_condition == "original_condition"')
e_n = e_n.groupby(by=['building_category', 'TEK', 'year']).sum()[['kwh_m2']]

df = df.join(e_n).reset_index()

df['energy_use'] = (df['area'] * df['kwh_m2']) / 1_000_000

# df = df.query('year != 2020')
df = df[['year', 'demolition_construction', 'building_category', 'TEK', 'area', 'energy_use']]
df = df.rename(columns={'area': 'Area [m2]', 'energy_use': 'Energy_use [GWh]'})
demolition_construction_fane1 = df

df

# ### Result

# In[33]:


demolition_construction_fane1

# In[34]:


# demolition_construction_fane1
append_result(output_path / 'demolition_construction.xlsx', demolition_construction_fane1, sheet_name='long')

# In[35]:


e_n = energy_needs.copy()
e_n = e_n.query('building_condition == "original_condition"')
e_n.groupby(by=['building_category', 'TEK', 'year']).sum()[['kwh_m2']]

# ## Heating systems

# In[36]:


from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.energy_consumption import EnergyConsumption
from ebm.model.calibrate_heating_systems import group_heating_systems_by_energy_carrier

# In[37]:


projection_period = YearRange(2023, 2050)
hsp = HeatingSystemsProjection.new_instance(projection_period, database_manager)
df = hsp.calculate_projection()
df = hsp.pad_projection(df, YearRange(2020, 2022))

heating_system_projection = df.copy()
df

# In[38]:


total_area = forecasts.copy().set_index(['building_category', 'TEK', 'building_condition', 'year'])
df = total_area.merge(energy_needs.copy(), left_index=True, right_index=True)
df['energy_requirement'] = df['m2'] * df['kwh_m2']
energy_use = df.copy()
df

# In[39]:


calculator = EnergyConsumption(heating_system_projection.copy())

calculator.heating_systems_parameters = calculator.grouped_heating_systems()

calculator.heating_systems_parameters.to_excel(output_path / 'heating_systems_parameters.xlsx', merge_cells=False)

df = calculator.calculate(energy_use)

heating_systems = df.copy()
df

# In[40]:


df = group_heating_systems_by_energy_carrier(heating_systems)
df

# ## heating-system-share

# In[ ]:


# In[41]:


heating_system_projection

# ### heating-system-share fane 2

# In[42]:


df = heating_system_projection.copy()

value_column = 'TEK_shares'

fane2_columns = ['building_category', 'heating_systems', 'year', 'TEK_shares']

df.loc[~df['building_category'].isin(['house', 'apartment_block']), 'building_category'] = 'non_residential'

mean_tek_shares_yearly = df[fane2_columns].groupby(by=['year', 'building_category', 'heating_systems']).mean()
# df = df[fane2_columns].groupby(by=['building_category', 'heating_systems', 'year'], as_index=False).mean()[fane2_columns]

tek_shares_yearly = mean_tek_shares_yearly.copy()
mean_tek_shares_yearly

# ### heating-system-share fane 1
#

# In[43]:


# df = heating_system_projection.copy()

# value_column = 'TEK_shares'

# fane2_columns = ['building_category', 'heating_systems', 'year', 'TEK_shares']

# df.loc[~df['building_category'].isin(['house', 'apartment_block']), 'building_category'] = 'non_residential'

# mean_tek_shares_yearly= df[fane2_columns].groupby(by=['building_category', 'heating_systems', 'year', 'TEK_shares']).mean()
### df = df[fane2_columns].groupby(by=['building_category', 'heating_systems', 'year'], as_index=False).mean()[fane2_columns]

# tek_shares_yearly = mean_tek_shares_yearly.copy()
# mean_tek_shares_yearly


# In[44]:


df = tek_shares_yearly.copy().reset_index()
df = df.pivot(columns=['year'], index=['building_category', 'heating_systems'], values=[value_column]).reset_index()

df = df.sort_values(by=['building_category', 'heating_systems'],
                    key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x)
df.insert(2, 'U', value_column)
df['U'] = '%'

df.columns = ['building_category', 'heating_systems', 'U'] + [y for y in range(2020, 2051)]

heating_system_fane2 = df.copy()
df
