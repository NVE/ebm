#!/usr/bin/env python
# coding: utf-8

import itertools
import pathlib
import string

from IPython.display import display
from openpyxl import load_workbook
import numpy as np
import pandas as pd

from ebm.model import FileHandler

print('# Nybygging formler')

file_handler = FileHandler()

nybygging_ssb_areal = 'C:/Users/kenord/dev2/Energibruksmodell/input/nybygging_ssb_05940_areal.csv'
nybygging_andeler = 'C:/Users/kenord/dev2/Energibruksmodell/input/nybygging_husandeler.csv'
nybygging_befolkning = 'C:/Users/kenord/dev2/Energibruksmodell/input/nybygging_befolkning.csv'

print('### Andeler småhus/leiligheter')

andeler = pd.read_csv(nybygging_andeler, dtype={"Andel nye småhus": "float64", 'Andel nye leiligheter': 'float64'})
pd.set_option('display.float_format', '{:.15f}'.format)
# andeler['Andel nye småhus'] = 1-andeler['Andel nye leiligheter']

andeler = andeler.rename(columns={'årstall': 'year'})

display(andeler)

print('### Husholdninger (scenario)')

befolkning = pd.read_csv(nybygging_befolkning, dtype={"household_size": "float64"})
display(befolkning.sample(7))
befolkning['households'] = (befolkning['population'] / befolkning['household_size'])
befolkning['population_change'] = befolkning.population.diff(1) / befolkning.population.shift(1)
befolkning['households_change'] = befolkning.households.diff(1)
befolkning['building_change'] = befolkning.households

display(befolkning[befolkning.year == 2024])
display(5472086 / 2.115)
display(befolkning)

print('### Årlig endring antall småhus')

yearly_change_small_house = befolkning.merge(andeler, left_on='year', right_on='year')
yearly_change_small_house['Årlig endring antall småhus'] = ((yearly_change_small_house['households_change'] *
                                                             yearly_change_small_house['Andel nye småhus'])).fillna(0)
yearly_change_small_house = yearly_change_small_house[
    ['year', 'Årlig endring antall småhus', 'Areal nye småhus', 'Andel nye småhus']]
yearly_change_small_house = yearly_change_small_house.set_index('year')
display(yearly_change_small_house)

print('### Årlig endring areal småhus')

display((yearly_change_small_house['Årlig endring antall småhus'] * yearly_change_small_house['Areal nye småhus']))
yearly_change_small_house['Årlig endring areal småhus'] = (
    (yearly_change_small_house['Årlig endring antall småhus'] *
     yearly_change_small_house['Areal nye småhus'])).fillna(0)

yearly_change_small_house = yearly_change_small_house[
    ['Årlig endring antall småhus', 'Årlig endring areal småhus', 'Areal nye småhus']]

if 'year' in yearly_change_small_house.columns:
    yearly_change_small_house = yearly_change_small_house.set_index('year')
display(yearly_change_small_house)

print('### Årlig revet areal småhus')

p = pathlib.Path(
    "C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/st_bema2019_a_hus.xlsx")

wb = load_workbook(filename=p)
sheet_ranges = wb.sheetnames
sheet = wb[sheet_ranges[0]]
cells = list(string.ascii_uppercase)[4:] + [a + b for a, b in itertools.product(string.ascii_uppercase, repeat=2)][:19]
area_demolition_house = sheet['F656'].value - sheet['E656'].value
display(area_demolition_house)

a_hus_revet = pd.DataFrame({'revet': [sheet[f'{c}656'].value for c in cells]}, index=list(range(2010, 2051)))
a_hus_revet['revet'] = a_hus_revet['revet']
a_hus_revet['revet_change'] = a_hus_revet.revet.diff(1).fillna(0)
a_hus_revet.index = a_hus_revet.index.rename('year')

display(a_hus_revet.head())
display(a_hus_revet.tail())

print('-----------------')
print('### Årlig nybygget areal småhus')
print('-----------------')

build_area = pd.read_csv(nybygging_ssb_areal)
types = build_area['type of building'].apply(lambda r: pd.Series(r.split(' ', 1)))

build_area[['type_no', 'typename']] = types

build_area = build_area.drop(columns=['type of building', 'area'])

build_area['building_category'] = 'unknown'
build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
build_area.loc[(build_area.type_no >= '141') & (build_area.type_no <= '146'), 'building_category'] = 'Apartment block'

display(build_area)
build_area_sum = build_area.groupby(by='building_category').sum()
display(build_area_sum)

years = pd.Series({y: np.float64(0) for y in range(2012, 2051)})

padded_build_area_sum = pd.DataFrame(pd.concat([build_area_sum.loc['Small house'].loc[['2010', '2011']], years]),
                                     columns=['area'])

display(padded_build_area_sum.head())
display(yearly_change_small_house.columns)
display(yearly_change_small_house['Årlig endring areal småhus'])

a_hus_revet['revet_change'] = a_hus_revet['revet_change'].fillna(0)

yearly_change_small_house['Årlig nybygget areal småhus'] = yearly_change_small_house['Årlig endring areal småhus'] + \
                                                           a_hus_revet['revet_change']

yearly_change_small_house.loc[2010, 'Årlig nybygget areal småhus'] = build_area_sum.loc['Small house']['2010']
yearly_change_small_house.loc[2011, 'Årlig nybygget areal småhus'] = build_area_sum.loc['Small house']['2011']

print('## Nybygget småhus akkumulert')

display(yearly_change_small_house.head())

yearly_change_small_house['Nybygget småhus akkumulert'] = yearly_change_small_house[
    'Årlig nybygget areal småhus'].cumsum()

display(yearly_change_small_house)

display(build_area_sum)
