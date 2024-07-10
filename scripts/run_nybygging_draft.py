#!/usr/bin/env python
# coding: utf-8

import itertools
import pathlib
import string

from IPython.display import display
from loguru import logger
from openpyxl import load_workbook
import numpy as np
import pandas as pd

from ebm.model import DatabaseManager

print('# Nybygging formler')

database_manager = DatabaseManager()

print('### Andeler småhus/leiligheter')

new_buildings_category_share = database_manager.get_new_buildings_category_share()
#pd.set_option('display.float_format', '{:.15f}'.format)
# andeler['Andel nye småhus'] = 1-andeler['Andel nye leiligheter']

display(new_buildings_category_share.head())

print('### Husholdninger (scenario)')

population = database_manager.get_construction_population()

population['households'] = (population['population'] / population['household_size'])
population['population_change'] = population.population.diff(1) / population.population.shift(1)
population['households_change'] = population.households.diff(1)
population['building_change'] = population.households

display(population[population.year == 2024])
display(population.head())

print('### Årlig endring antall småhus')

yearly_change_small_house = population.merge(new_buildings_category_share, left_on='year', right_on='year')
yearly_change_small_house['yearly_change_house_count'] = ((yearly_change_small_house['households_change'] *
                                                             yearly_change_small_house['new_house_share'])).fillna(0)
yearly_change_small_house = yearly_change_small_house[
    ['year', 'yearly_change_house_count', 'floor_area_new_house', 'new_house_share']]
yearly_change_small_house = yearly_change_small_house.set_index('year')
display(yearly_change_small_house.head())

print('### Årlig endring areal småhus')

display((yearly_change_small_house['yearly_change_house_count'] * yearly_change_small_house['floor_area_new_house']))
yearly_change_small_house['yearly_change_floor_area_house'] = (
    (yearly_change_small_house['yearly_change_house_count'] *
     yearly_change_small_house['floor_area_new_house'])).fillna(0)

yearly_change_small_house = yearly_change_small_house[
    ['yearly_change_house_count', 'yearly_change_floor_area_house', 'floor_area_new_house']]

if 'year' in yearly_change_small_house.columns:
    yearly_change_small_house = yearly_change_small_house.set_index('year')
display(yearly_change_small_house.head())

print('### Årlig revet areal småhus')

p = pathlib.Path(
    "C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/st_bema2019_a_hus.xlsx")

wb = load_workbook(filename=p)
sheet_ranges = wb.sheetnames
sheet = wb[sheet_ranges[0]]
cells = list(string.ascii_uppercase)[4:] + [a + b for a, b in itertools.product(string.ascii_uppercase, repeat=2)][:19]
area_demolition_house = sheet['F656'].value - sheet['E656'].value
display(area_demolition_house)

a_hus_revet = pd.DataFrame({'demolition': [sheet[f'{c}656'].value for c in cells]}, index=list(range(2010, 2051)))
a_hus_revet['demolition'] = a_hus_revet['demolition']
a_hus_revet['demolition_change'] = a_hus_revet.demolition.diff(1).fillna(0)
a_hus_revet.index = a_hus_revet.index.rename('year')

display(a_hus_revet.head())
display(a_hus_revet.tail())

print('-----------------')
print('### Årlig nybygget areal småhus')
print('-----------------')

build_area = database_manager.get_building_category_floor_area()

build_area['building_category'] = 'unknown'
build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
build_area.loc[(build_area.type_no >= '141') & (build_area.type_no <= '146'), 'building_category'] = 'Apartment block'

display(build_area.head())

build_area_sum = build_area.groupby(by='building_category').sum()

display(build_area_sum.head())

years = pd.Series({y: np.float64(0) for y in range(2012, 2051)})
padded_build_area_sum = pd.DataFrame(pd.concat([build_area_sum.loc['Small house'].loc[['2010', '2011']], years]),
                                     columns=['area'])

display(padded_build_area_sum.head())
display(yearly_change_small_house.columns)
display(yearly_change_small_house['yearly_change_floor_area_house'])

a_hus_revet['demolition_change'] = a_hus_revet['demolition_change'].fillna(0)

yearly_change_small_house['yearly_new_house_floor_area'] = yearly_change_small_house['yearly_change_floor_area_house'] + \
                                                           a_hus_revet['demolition_change']
yearly_change_small_house.loc[2010, 'yearly_new_house_floor_area'] = build_area_sum.loc['Small house']['2010']
yearly_change_small_house.loc[2011, 'yearly_new_house_floor_area'] = build_area_sum.loc['Small house']['2011']

print('## Nybygget småhus akkumulert')

display(yearly_change_small_house.head())

yearly_change_small_house['new_house_accumulated'] = yearly_change_small_house[
    'yearly_new_house_floor_area'].cumsum()

display(yearly_change_small_house.head())

display(build_area_sum.head())
