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

SPREADSHEET_START_COLUMN = 2


def calculate_more_construction():
    for building_category in [BuildingCategory.KINDERGARTEN,
                              BuildingCategory.SCHOOL,
                              BuildingCategory.UNIVERSITY,
                              BuildingCategory.OFFICE,
                              BuildingCategory.RETAIL,
                              BuildingCategory.HOTEL,
                              BuildingCategory.HOSPITAL,
                              BuildingCategory.NURSING_HOME,
                              BuildingCategory.CULTURE,
                              BuildingCategory.SPORTS,
                              BuildingCategory.STORAGE_REPAIRS]:
        demolition_floor_area = NewBuildings.calculate_floor_area_demolished(building_category)

        df = NewBuildings.calculate_commercial_construction(
            building_category=building_category,
            yearly_construction_floor_area=None,
            total_floor_area=None,
            demolition_floor_area=demolition_floor_area)

        transposed = df.transpose()
        transposed.insert(0, 'building_category', str(building_category))
        yield transposed


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

    if new_building_house.loc['demolished_floor_area'].sum() != 64370906.831874974:
        logger.warning(f'{new_building_house.loc["demolished_floor_area"].sum()=} != 64370906.831874974')
    if new_building_house.loc['constructed_floor_area'].sum() != 123739128.72838475:
        logger.warning(f'{new_building_house.loc["constructed_floor_area"].sum()=} != 123739128.72838475')
    if new_building_house.loc['accumulated_constructed_floor_area'].sum() != 2630603443.124876:
        logger.warning(f'{new_building_house.loc["accumulated_constructed_floor_area"].sum()=} != 2630603443.124876')

    new_building_apartment_block = create_new_building_apartment_block_dataframe(database_manager, household_size, population)

    if new_building_apartment_block.loc['demolished_floor_area'].sum() != 12335966.989999998:
        logger.warning(f'new_building_apartment_block.loc["demolished_floor_area"].sum() != {12335966.989999998}')
    if new_building_apartment_block.loc['constructed_floor_area'].sum() != 42501448.825284824:
        logger.warning(f'new_building_apartment_block.new_building_floor_area  {new_building_apartment_block.loc["new_building_floor_area"].sum()} != 42501448.825284824')
    if new_building_apartment_block.loc['accumulated_constructed_floor_area'].sum() != 957797360.1858981:
        logger.warning(f'new_building_apartment_block.accumulated_constructed_floor_area  {new_building_apartment_block.loc["accumulated_constructed_floor_area"].sum()} != 957797360.1858981')

    if pathlib.Path('output').is_dir():
        new_building_apartment_block.to_excel('output/new_building_apartment_block.xlsx',
                                              startcol=SPREADSHEET_START_COLUMN)
    if pathlib.Path('output').is_dir():
        new_building_house.to_excel('output/new_building_house.xlsx',
                                    startcol=SPREADSHEET_START_COLUMN)

    houses = new_building_house
    houses.insert(0, 'building_category', 'house')
    houses.to_excel('output/construction.xlsx',
                    startcol=SPREADSHEET_START_COLUMN)

    apartment_blocks = new_building_apartment_block
    apartment_blocks.insert(0, 'building_category', 'apartment_block')

    more_construction = list(calculate_more_construction())

    construction_df = pd.concat([houses, apartment_blocks] + more_construction)

    construction_df.to_excel('output/construction.xlsx',
                             startcol=SPREADSHEET_START_COLUMN)
    display(new_building_apartment_block)
    display(new_building_apartment_block.loc['accumulated_constructed_floor_area'].head())


def create_new_building_apartment_block_dataframe(database_manager, household_size, population):
    building_category_share = database_manager.get_new_buildings_category_share()

    build_area = database_manager.get_building_category_floor_area()
    apartment_block_area = build_area['apartment_block'].dropna()

    new_buildings = NewBuildings()
    yearly_demolished_floor_area = new_buildings.calculate_floor_area_demolished(BuildingCategory.APARTMENT_BLOCK) #'st_bema2019_a_leil.xlsx',

    return new_buildings.calculate_residential_construction(
        population,
        household_size,
        building_category_share,
        apartment_block_area,
        yearly_demolished_floor_area, average_floor_area=75)


def create_new_building_house_dataframe(database_manager, household_size, population):
    new_buildings = NewBuildings()
    building_category_share = database_manager.get_new_buildings_category_share()
    build_area = database_manager.get_building_category_floor_area()
    house_floor_area = build_area[BuildingCategory.HOUSE].dropna()

    yearly_demolished_floor_area = new_buildings.calculate_floor_area_demolished(BuildingCategory.HOUSE) # filename = 'st_bema2019_a_hus.xlsx',

    new_building_house = new_buildings.calculate_residential_construction(
        population,
        household_size,
        building_category_share,
        house_floor_area,
        yearly_demolished_floor_area, average_floor_area=175)

    return new_building_house


if __name__ == '__main__':
    main()
