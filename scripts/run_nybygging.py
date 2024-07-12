""" Program used to test nybygging calculation """
import argparse
import os
import pathlib
from pprint import pprint as pp
import sys

from loguru import logger
import pandas as pd
from IPython.display import display

from ebm.model import FileHandler, DatabaseManager
from ebm.services.spreadsheet import calculate_house_floor_area_demolished_by_year


def create_new_building_dataframe(population: pd.Series,
                                 household_size: pd.Series,
                                 building_category_share: pd.DataFrame,
                                 build_area_sum: pd.DataFrame) -> pd.DataFrame:
    database_manager = DatabaseManager()

    # Befolkningsøkning (Ikke brukt videre)
    population_growth = calculate_population_growth(population)
    households = calculate_households_by_year(household_size, population)

    # Årlig endring i antall boliger (brukt Årlig endring i antall småhus)
    households_change = calculate_household_change(households)
    house_change = calculate_house_change(building_category_share, households_change)

    ## Årlig endring areal småhus (brukt Årlig nybygget areal småhus)
    yearly_floor_area_change = calculate_yearly_floor_area_change(building_category_share, house_change)

    # Årlig revet areal småhus
    yearly_demolished_floor_area = calculate_floor_area_demolished()
    yearly_new_building_floor_area = calculate_yearly_new_building_floor_area(build_area_sum,
                                                                              yearly_floor_area_change,
                                                                              yearly_demolished_floor_area)

    # Nybygget småhus akkumulert
    floor_area_change_accumulated = calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area)

    df = pd.DataFrame(data=[
        population,
        population_growth,
        household_size,
        households,
        households_change,
        house_change,
        yearly_floor_area_change,
        yearly_demolished_floor_area,
        yearly_new_building_floor_area,
        floor_area_change_accumulated])

    return df


def calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house: pd.Series):
    return pd.Series(yearly_new_building_floor_area_house.cumsum(), name='floor_area_change_accumulated')


def calculate_yearly_new_building_floor_area(build_area_sum,
                                             yearly_floor_area_change,
                                             yearly_demolished_floor_area) -> pd.Series:

    yearly_new_building_floor_area_house = yearly_floor_area_change + yearly_demolished_floor_area  # Årlig nybygget areal småhus (brukt  Nybygget småhus akkumulert)
    display(yearly_new_building_floor_area_house)
    yearly_new_building_floor_area_house.loc[build_area_sum.index.values] = build_area_sum.loc[build_area_sum.index.values]
    #yearly_new_building_floor_area_house.loc[[2010]] = build_area_sum.loc['Small house', '2010']
    #yearly_new_building_floor_area_house.loc[[2011]] = build_area_sum.loc['Small house', '2011']
    display(yearly_new_building_floor_area_house)
    return pd.Series(yearly_new_building_floor_area_house, name='new_building_floor_area')


def calculate_floor_area_demolished():
    # Loading demolition data from spreadsheet. Should be changed to a parameter with calculated data
    demolition = calculate_house_floor_area_demolished_by_year(
        pathlib.Path("st_bema2019_a_leil.xlsx"))['demolition']
    yearly_demolished_floor_area_house = demolition.diff(1)  ## Årlig revet areal småhus
    return pd.Series(yearly_demolished_floor_area_house, name='demolition_change')


def calculate_yearly_floor_area_change(building_category_share: pd.Series, house_change: pd.Series) -> pd.Series:
    building_category_share['floor_area_new_house'] = 75
    house_average_floor_area = building_category_share['floor_area_new_house']
    yearly_floor_area_change = house_average_floor_area * house_change
    yearly_floor_area_change.loc[[2010, 2011]] = 0
    return pd.Series(yearly_floor_area_change, name='house_floor_area_change')


def calculate_population_growth(population):
    population_growth = (population / population.shift(1)) - 1
    return pd.Series(population_growth, name='population_growth')


def calculate_house_change(building_category_share: pd.DataFrame, households_change: pd.Series) -> pd.Series:
    house_share = building_category_share['new_house_share']
    house_share = building_category_share['new_apartment_block_share']
    #apartment_block_share = building_category_share['new_apartment_block_share']
    house_change = households_change * house_share  ## Årlig endring i antall småhus (brukt  Årlig endring areal småhus)
    return pd.Series(house_change, name='house_change')


def calculate_household_change(households: pd.Series) -> pd.Series:
    return pd.Series(households - households.shift(1), name='household_change')


def calculate_households_by_year(household_size: pd.Series, population: pd.Series) -> pd.Series:
    households = population / household_size  ## Husholdninger
    return pd.Series(households, name='households')


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    database_manager = DatabaseManager()

    new_buildings_population = database_manager.get_construction_population()[['population', 'household_size']]
    household_size = new_buildings_population['household_size']
    population = new_buildings_population['population']

    #new_building_house = create_new_building_house_dataframe(database_manager, household_size, population)
    #display(new_building_house.transpose())

    new_building_apartment_block = create_new_building_apartment_block_dataframe(database_manager, household_size, population)

    new_building_apartment_block.to_excel('utputt.xlsx')
    display(new_building_apartment_block.transpose()[['demolition_change', 'house_floor_area_change']])


def create_new_building_apartment_block_dataframe(database_manager, household_size, population):
    building_category_share = database_manager.get_new_buildings_category_share()
    #display( building_category_share['new_house_share'])
    building_category_share['new_house_share'] = building_category_share['new_apartment_block_share']
    building_category_share['new_house_share']

    build_area = database_manager.get_building_category_floor_area()
    build_area['building_category'] = 'unknown'
    #build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[
        (build_area.type_no >= '141') & (build_area.type_no <= '146'), 'building_category'] = 'Small house'
    build_area_sum = build_area.groupby(by='building_category').sum()

    apartment_block_area = pd.Series(
        build_area_sum.loc['Small house', ['2010', '2011']], name='area').astype('float64')
    apartment_block_area.index = apartment_block_area.index.astype('int')  # [2010]

    return create_new_building_dataframe(population, household_size, building_category_share, apartment_block_area)


def create_new_building_house_dataframe(database_manager, household_size, population):
    building_category_share = database_manager.get_new_buildings_category_share()
    build_area = database_manager.get_building_category_floor_area()
    build_area['building_category'] = 'unknown'
    build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[
        (build_area.type_no >= '141') & (build_area.type_no <= '146'), 'building_category'] = 'Apartment block'
    build_area_sum = build_area.groupby(by='building_category').sum()

    house = pd.Series(
        build_area_sum.loc['Small house', ['2010', '2011']], name='area').astype('float64')
    house.index = house.index.astype('int')  # [2010]

    new_building_house = create_new_building_dataframe(population, household_size, building_category_share, house)

    return new_building_house


if __name__ == '__main__':
    main()
