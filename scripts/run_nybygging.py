""" Program used to test nybygging calculation """
import argparse
import os
import pathlib
import sys

from loguru import logger
import pandas as pd
from IPython.display import display

from ebm.model import DatabaseManager, BuildingCategory
from ebm.model.new_buildings import NewBuildings


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True' and False:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    database_manager = DatabaseManager()

    new_buildings_population = database_manager.get_construction_population()[['population', 'household_size']]
    household_size = new_buildings_population['household_size']
    population = new_buildings_population['population']

    new_building_house = create_new_building_house_dataframe(database_manager, household_size, population)

    if new_building_house.loc['demolition_change'].sum() != 64370906.831874974:
        logger.warning(f'new_building_house.loc["demolition_change"].sum() {new_building_house.loc["demolition_change"].sum()} != 64370906.831874974')
    if new_building_house.loc['new_building_floor_area'].sum() != 123739128.72838475:
        logger.warning(f'new_building_house.new_building_floor_area  {new_building_house.loc["new_building_floor_area"].sum()} != 123739128.72838475')
    if new_building_house.loc['floor_area_change_accumulated'].sum() != 2630603443.124876:
        logger.warning(f'new_building_apartment_block.floor_area_change_accumulated  {new_building_house.loc["floor_area_change_accumulated"].sum()} != 2630603443.124876')

    new_building_apartment_block = create_new_building_apartment_block_dataframe(database_manager, household_size, population)

    if new_building_apartment_block.loc['demolition_change'].sum() != 12335966.989999998:
        logger.warning(f'new_building_apartment_block.loc["demolition_change"].sum() != {12335966.989999998}')
    if new_building_apartment_block.loc['new_building_floor_area'].sum() != 42501448.825284824:
        logger.warning(f'new_building_apartment_block.new_building_floor_area  {new_building_apartment_block.loc["new_building_floor_area"].sum()} != 42501448.825284824')
    if new_building_apartment_block.loc['floor_area_change_accumulated'].sum() != 957797360.1858981:
        logger.warning(f'new_building_apartment_block.floor_area_change_accumulated  {new_building_apartment_block.loc["floor_area_change_accumulated"].sum()} != 957797360.1858981')

    if pathlib.Path('output').is_dir():
        new_building_apartment_block.to_excel('output/new_building_apartment_block.xlsx', startcol=4)
    if pathlib.Path('output').is_dir():
        new_building_house.to_excel('output/new_building_house.xlsx', startcol=4)

    houses = new_building_house
    houses.insert(0, 'building_category', 'house')
    houses.to_excel('output/construction.xlsx', startcol=4)

    apartment_blocks = new_building_apartment_block
    apartment_blocks.insert(0, 'building_category', 'apartment_block')

    construction_df = pd.concat([houses, apartment_blocks])

    construction_df.to_excel('output/construction.xlsx', startcol=4)
    display(new_building_apartment_block)
    display(new_building_apartment_block.loc['floor_area_change_accumulated'].head())


def create_new_building_apartment_block_dataframe(database_manager, household_size, population):
    building_category_share = database_manager.get_new_buildings_category_share()

    build_area = database_manager.get_building_category_floor_area()
    build_area['building_category'] = 'unknown'
    build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[build_area.type_no >= '141', 'building_category'] = 'Apartment block'
    build_area_sum = build_area.groupby(by='building_category').sum()

    apartment_block_area = pd.Series(
        build_area_sum.loc['Apartment block', ['2010', '2011']], name='area').astype('float64')
    apartment_block_area.index = apartment_block_area.index.astype('int')  # [2010]

    new_buildings = NewBuildings()
    yearly_demolished_floor_area = new_buildings.calculate_floor_area_demolished(BuildingCategory.APARTMENT_BLOCK) #'st_bema2019_a_leil.xlsx',

    return new_buildings.create_new_building_dataframe(
        population,
        household_size,
        building_category_share,
        apartment_block_area,
        yearly_demolished_floor_area, average_floor_area=75)


def create_new_building_house_dataframe(database_manager, household_size, population):
    new_buildings = NewBuildings()
    building_category_share = database_manager.get_new_buildings_category_share()
    build_area = database_manager.get_building_category_floor_area()
    build_area['building_category'] = 'unknown'
    build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[
        build_area.type_no >= '141', 'building_category'] = 'Apartment block'
    build_area_sum = build_area.groupby(by='building_category').sum()

    house = pd.Series(
        build_area_sum.loc['Small house', ['2010', '2011']], name='area').astype('float64')
    house.index = house.index.astype('int')  # [2010]

    yearly_demolished_floor_area = new_buildings.calculate_floor_area_demolished(BuildingCategory.HOUSE) # filename = 'st_bema2019_a_hus.xlsx',

    new_building_house = new_buildings.create_new_building_dataframe(
        population,
        household_size,
        building_category_share,
        house,
        yearly_demolished_floor_area, average_floor_area=175)

    return new_building_house


if __name__ == '__main__':
    main()
