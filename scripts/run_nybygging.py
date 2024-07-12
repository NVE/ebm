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
                                  build_area_sum: pd.DataFrame,
                                  yearly_demolished_floor_area: pd.Series,
                                  average_floor_area=175) -> pd.DataFrame:
    # Befolkningsøkning (Ikke brukt videre)
    population_growth = calculate_population_growth(population)
    households = calculate_households_by_year(household_size, population)

    # Årlig endring i antall boliger (brukt Årlig endring i antall småhus)
    households_change = calculate_household_change(households)
    house_change = calculate_house_change(building_category_share, households_change, average_floor_area)

    ## Årlig endring areal småhus (brukt Årlig nybygget areal småhus)
    yearly_floor_area_change = calculate_yearly_floor_area_change(building_category_share['new_house_share'] if average_floor_area == 175 else building_category_share['new_apartment_block_share'],
                                                                  house_change, average_floor_area)

    # Årlig revet areal småhus

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

    yearly_new_building_floor_area_house.loc[build_area_sum.index.values] = build_area_sum.loc[build_area_sum.index.values]

    return pd.Series(yearly_new_building_floor_area_house, name='new_building_floor_area')


def calculate_floor_area_demolished(filename: str = 'st_bema2019_a_hus.xlsx', row=655):
    # Loading demolition data from spreadsheet. Should be changed to a parameter with calculated data
    demolition = calculate_house_floor_area_demolished_by_year(pathlib.Path(filename), row=row)['demolition']
    yearly_demolished_floor_area_house = demolition.diff(1)  ## Årlig revet areal småhus
    return pd.Series(yearly_demolished_floor_area_house, name='demolition_change')


def calculate_yearly_floor_area_change(building_category_share: pd.Series, house_change: pd.Series, average_floor_area=175) -> pd.Series:
    yearly_floor_area_change = average_floor_area * house_change
    yearly_floor_area_change.loc[[2010, 2011]] = 0
    return pd.Series(yearly_floor_area_change, name='house_floor_area_change')


def calculate_population_growth(population):
    population_growth = (population / population.shift(1)) - 1
    return pd.Series(population_growth, name='population_growth')


def calculate_house_change(building_category_share: pd.DataFrame, households_change: pd.Series, average_floor_area=175) -> pd.Series:
    house_share = building_category_share['new_house_share'] if average_floor_area == 175 else building_category_share['new_apartment_block_share']
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

    new_building_house = create_new_building_house_dataframe(database_manager, household_size, population)

    if pathlib.Path('output').is_dir():
        new_building_house.to_excel('output/new_building_house.xlsx', startcol=4)

    new_building_apartment_block = create_new_building_apartment_block_dataframe(database_manager, household_size, population)

    if pathlib.Path('output').is_dir():
        new_building_apartment_block.to_excel('output/new_building_apartment_block.xlsx', startcol=4)
    display(new_building_apartment_block.loc['floor_area_change_accumulated'].head())


def create_new_building_apartment_block_dataframe(database_manager, household_size, population):
    building_category_share = database_manager.get_new_buildings_category_share()

    build_area = database_manager.get_building_category_floor_area()
    build_area['building_category'] = 'unknown'
    build_area.loc[(build_area.type_no >= '111') & (build_area.type_no <= '136'), 'building_category'] = 'Small house'
    build_area.loc[
        build_area.type_no >= '141', 'building_category'] = 'Apartment block'
    build_area_sum = build_area.groupby(by='building_category').sum()

    apartment_block_area = pd.Series(
        build_area_sum.loc['Apartment block', ['2010', '2011']], name='area').astype('float64')
    apartment_block_area.index = apartment_block_area.index.astype('int')  # [2010]

    yearly_demolished_floor_area = calculate_floor_area_demolished('st_bema2019_a_leil.xlsx', 655)

    return create_new_building_dataframe(population,
                                         household_size,
                                         building_category_share,
                                         apartment_block_area,
                                         yearly_demolished_floor_area,  average_floor_area=75)


def create_new_building_house_dataframe(database_manager, household_size, population):
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

    yearly_demolished_floor_area = calculate_floor_area_demolished('st_bema2019_a_hus.xlsx', 656)

    new_building_house = create_new_building_dataframe(population, household_size, building_category_share, house,
                                                       yearly_demolished_floor_area, average_floor_area=175)

    return new_building_house


if __name__ == '__main__':
    main()
