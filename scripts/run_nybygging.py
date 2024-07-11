""" Program used to test nybygging calculation """
import argparse
import os
from pprint import pprint as pp
import sys

from loguru import logger
import pandas as pd

from ebm.model import FileHandler, DatabaseManager
from scripts.run_nybygging_draft import calculate_house_floor_area_demolished_by_year, calculate_yearly_built_floor_area_house


def calculate_yearly_floor_area():
    database_manager = DatabaseManager()

    new_buildings_population = database_manager.get_construction_population()[['population', 'household_size']]
    building_category_share = database_manager.get_new_buildings_category_share()
    build_area = database_manager.get_building_category_floor_area()

    population = new_buildings_population['population']  ## Befolkning
    household_size = new_buildings_population['household_size']

    population_growth = (population/population.shift(1)) - 1  ## Befolkningsøkning (Ikke brukt videre)
    households = population / household_size ## Husholdninger
    households_change = households - households.shift(1)  ## Årlig endring i antall boliger (brukt Årlig endring i antall småhus)

    house_share = building_category_share['new_house_share']
    apartment_block_share = building_category_share['new_apartment_block_share']
    house_average_floor_area = building_category_share['floor_area_new_house']

    house_change = households_change*house_share  ## Årlig endring i antall småhus (brukt  Årlig endring areal småhus)

    yearly_floor_area_change = house_average_floor_area * house_change
    yearly_floor_area_change.loc[[2010, 2011]] = 0 ## Årlig endring areal småhus (brukt Årlig nybygget areal småhus)

    demolition = calculate_house_floor_area_demolished_by_year()['demolition']
    yearly_demolished_floor_area_house = demolition.diff(1)  ## Årlig revet areal småhus

    build_area['building_category'] = 'unknown'
    build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[
        (build_area.type_no >= '141') & (build_area.type_no <= '146'), 'building_category'] = 'Apartment block'
    build_area_sum = build_area.groupby(by='building_category').sum()

    yearly_new_building_floor_area_house = yearly_floor_area_change + yearly_demolished_floor_area_house ## Årlig nybygget areal småhus (brukt  Nybygget småhus akkumulert)
    yearly_new_building_floor_area_house.loc[[2010]] = build_area_sum.loc['Small house', '2010']
    yearly_new_building_floor_area_house.loc[[2011]] = build_area_sum.loc['Small house', '2011']
    return yearly_new_building_floor_area_house

    new_building_house_accumulated = yearly_new_building_floor_area_house.cumsum()  ## Nybygget småhus akkumulert

    return new_building_house_accumulated


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    pp(calculate_yearly_floor_area())
    #file_handler = FileHandler()
    #population = file_handler.get_file('new_buildings_population.csv')
    #print(population)
    #area_built = file_handler.get_file('nybygging_ssb_05939.csv')
    #print(area_built)


if __name__ == '__main__':
    main()
