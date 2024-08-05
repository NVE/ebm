import collections.abc
import itertools

import numpy as np
import pandas as pd
from loguru import logger
from pandas import Series

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory


class NewBuildings:
    def create_new_building_dataframe(self, population: pd.Series,
                                      household_size: pd.Series,
                                      building_category_share: pd.DataFrame,
                                      build_area_sum: pd.DataFrame,
                                      yearly_demolished_floor_area: pd.Series,
                                      average_floor_area=175) -> pd.DataFrame:
        # Befolkningsøkning (Ikke brukt videre)
        population_growth = self.calculate_population_growth(population)
        households = self.calculate_households_by_year(household_size, population)

        # Årlig endring i antall boliger (brukt Årlig endring i antall småhus)
        households_change = self.calculate_household_change(households)
        house_change = self.calculate_house_change(building_category_share, households_change, average_floor_area)

        # Årlig endring areal småhus (brukt Årlig nybygget areal småhus)
        yearly_floor_area_change = self.calculate_yearly_floor_area_change(
            building_category_share['new_house_share'] if average_floor_area == 175 else building_category_share[
                'new_apartment_block_share'],
            house_change, average_floor_area)

        # Årlig revet areal småhus
        yearly_demolition_floor_area = self.calculate_yearly_new_building_floor_area(
            build_area_sum, yearly_floor_area_change, yearly_demolished_floor_area)

        # Nybygget småhus akkumulert
        floor_area_change_accumulated = self.calculate_yearly_new_building_floor_area_sum(yearly_demolition_floor_area)

        df = pd.DataFrame(data=[
            population,
            population_growth,
            household_size,
            households,
            households_change,
            house_change,
            yearly_floor_area_change,
            yearly_demolished_floor_area,
            yearly_demolition_floor_area,
            floor_area_change_accumulated])

        return df

    @staticmethod
    def calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house: pd.Series):
        return pd.Series(yearly_new_building_floor_area_house.cumsum(), name='floor_area_change_accumulated')

    @staticmethod
    def calculate_yearly_new_building_floor_area(build_area_sum,
                                                 yearly_floor_area_change,
                                                 yearly_demolished_floor_area) -> pd.Series:
        # Årlig nybygget areal småhus (brukt  Nybygget småhus akkumulert)
        yearly_new_building_floor_area_house = yearly_floor_area_change + yearly_demolished_floor_area
        yearly_new_building_floor_area_house.loc[build_area_sum.index.values] = build_area_sum.loc[
            build_area_sum.index.values]

        return pd.Series(yearly_new_building_floor_area_house, name='new_building_floor_area')

    @staticmethod
    def calculate_floor_area_demolished(building_category: BuildingCategory):
        # Loading demolition data from spreadsheet. Should be changed to a parameter with calculated data
        demolition = DatabaseManager().load_demolition_floor_area_from_spreadsheet(building_category)

        # Årlig revet areal småhus
        yearly_demolished_floor_area_house = demolition.diff(1)
        return pd.Series(yearly_demolished_floor_area_house, name='demolition_change')

    @staticmethod
    def calculate_yearly_floor_area_change(building_category_share: pd.Series, house_change: pd.Series,
                                           average_floor_area=175) -> pd.Series:
        yearly_floor_area_change = average_floor_area * house_change
        yearly_floor_area_change.loc[[2010, 2011]] = 0
        return pd.Series(yearly_floor_area_change, name='house_floor_area_change')

    @staticmethod
    def calculate_population_growth(population):
        population_growth = (population / population.shift(1)) - 1
        return pd.Series(population_growth, name='population_growth')

    @staticmethod
    def calculate_house_change(building_category_share: pd.DataFrame, households_change: pd.Series,
                               average_floor_area=175) -> pd.Series:
        house_share = building_category_share['new_house_share'] if average_floor_area == 175 else \
            building_category_share['new_apartment_block_share']
        # Årlig endring i antall småhus (brukt  Årlig endring areal småhus)
        house_change = households_change * house_share
        return pd.Series(house_change, name='house_change')

    @staticmethod
    def calculate_household_change(households: pd.Series) -> pd.Series:
        return pd.Series(households - households.shift(1), name='household_change')

    @staticmethod
    def calculate_households_by_year(household_size: pd.Series, population: pd.Series) -> pd.Series:
        # Husholdninger
        households = population / household_size
        return pd.Series(households, name='households')

    @staticmethod
    def calculate_yearly_construction(building_category: BuildingCategory = None,
                                      total_floor_area: int = 0,
                                      yearly_construction_floor_area: collections.abc.Collection[int] = None) -> pd.Series:
        construction = NewBuildings.calculate_construction(
            building_category=building_category,
            total_floor_area=total_floor_area,
            yearly_construction_floor_area=yearly_construction_floor_area)

        return construction.accumulated_constructed_floor_area

    @staticmethod
    def calculate_construction(building_category: BuildingCategory = None,
                               total_floor_area: int = 1_275_238,
                               yearly_construction_floor_area: collections.abc.Collection[int] = None,
                               yearly_demolition_floor_area: pd.Series = None):
        if not building_category:
            building_category = BuildingCategory.KINDERGARTEN
        if not yearly_construction_floor_area:
            yearly_construction_floor_area = building_category.yearly_construction_floor_area()
        if not total_floor_area:
            total_floor_area = building_category.total_floor_area_2010()

        demolished_floor_area = yearly_demolition_floor_area
        if not demolished_floor_area:
            demolished_floor_area = NewBuildings.calculate_floor_area_demolished(building_category)
        # Faste tall
        total_floor_area = pd.Series(data=[total_floor_area], index=[2010])
        logger.debug('kg_totalt_areal (2010)')
        logger.info(total_floor_area)
        logger.debug('constructed_floor_area (2010-2014)')
        constructed_floor_area = pd.Series(
            data=yearly_construction_floor_area,
            index=[year for year in range(2010, 2010 + len(yearly_construction_floor_area))])
        logger.info(constructed_floor_area)
        # Eksterne tall
        logger.debug('kg_årlig_revet_areal')

        # logger.info(demolished_floor_area)
        befolkning: pd.DataFrame = pd.read_csv('input/new_buildings_population.csv', dtype={"household_size": "float64"})
        population = befolkning.set_index('year')['population']
        population_growth = (population / population.shift(1)) - 1
        # Barnehage totalareal 2011
        logger.debug(constructed_floor_area.loc[2010])
        #    logger.debug('=+E41-F46+F47')
        tall = total_floor_area.loc[2010] - demolished_floor_area.loc[2011] + constructed_floor_area.loc[2011]
        total_floor_area.loc[2011] = tall
        logger.debug(
            f'{total_floor_area.loc[2010]=} - {demolished_floor_area.loc[2011]=} + {constructed_floor_area.loc[2011]=}')
        logger.debug('sum 1 364 963')
        logger.info(f'{tall=}')
        logger.info(total_floor_area.loc[2011])
        # Barnehage totalareal 2012 - 2015
        logger.debug('kg_totalt_areal_2011 ')
        logger.info(total_floor_area.loc[2011])
        logger.debug('=+F41-G46+G47')
        logger.debug(
            f'{total_floor_area.loc[2011]=} - {demolished_floor_area.loc[2012]=} + {constructed_floor_area.loc[2012]=}')
        logger.debug('sum 1 429 891')
        logger.info(total_floor_area)
        for year in range(2011, 2015):
            logger.debug(
                f'{year} {total_floor_area.loc[year - 1]} {demolished_floor_area.loc[year]} {constructed_floor_area.loc[year]}')
            total_floor_area.loc[year] = total_floor_area.loc[year - 1] - demolished_floor_area.loc[year] + \
                                             constructed_floor_area.loc[year]
        # logger.info(total_floor_area)
        # barnehagevekst og areal-/befolkningsøkning
        population_growth = (population / population.shift(1)) - 1
        building_growth: Series = pd.Series(data=itertools.repeat(0.0, 41), index=[y for y in range(2010, 2051)])
        barnehagevekst_2011 = (total_floor_area.loc[2011] / total_floor_area.loc[2010]) - 1
        building_growth.loc[2011] = barnehagevekst_2011
        building_growth.loc[2010] = np.nan
        logger.debug('building_growth')
        floor_area_over_population_growth: Series = pd.Series(data=[np.nan] + list(itertools.repeat(1, 40)),
                                                     index=range(2010, 2051))
        floor_area_over_population_growth.loc[2011] = barnehagevekst_2011 / population_growth.loc[2011]
        # logger.info(floor_area_over_population_growth)
        # Barnehage Total areal 2015
        # barnehagevekst og areal-/befolkningsøkning 22
        for year in range(2011, 2015):
            building_growth.loc[year] = (total_floor_area.loc[year] / total_floor_area.loc[year - 1]) - 1
            floor_area_over_population_growth[year] = building_growth.loc[year] / population_growth.loc[year]
        # logger.info(building_growth)
        mean_floor_area_population = floor_area_over_population_growth.loc[2011:2014].mean()
        for year in range(2015, 2021):
            floor_area_over_population_growth.loc[year] = mean_floor_area_population
        for year in range(2021, 2050):
            floor_area_over_population_growth.loc[year] = 1
        for year in range(2021, 2031):
            floor_area_over_population_growth.loc[year] = (floor_area_over_population_growth.loc[2020] - (year - 2020) * (
                    (floor_area_over_population_growth.loc[2020] - floor_area_over_population_growth.loc[2030]) / 10))
        # logger.info(floor_area_over_population_growth)
        for year in range(2015, 2051):
            j53 = floor_area_over_population_growth.loc[year]
            j5 = population_growth.loc[year]
            i41 = total_floor_area.loc[year - 1]
            total_floor_area.loc[year] = ((j53 * j5) + 1) * i41
        # Årlig nybygget areal barnehage (2015 - 2050)
        for year in range(2015, 2051):
            j41 = total_floor_area.loc[year]
            i41 = total_floor_area.loc[year - 1]
            j46 = demolished_floor_area.loc[year]
            constructed_floor_area[year] = j41 - i41 + j46
        # accumulated_constructed_floor_area = constructed_floor_area.cumsum()
        # kg_nybygg_rate = constructed_floor_area / total_floor_area
        accumulated_constructed_floor_area = constructed_floor_area.cumsum()

        construction = pd.DataFrame(data={
            'total_floor_area': total_floor_area,
            'building_growth': building_growth,
            'demolished_floor_area': demolished_floor_area,
            'constructed_floor_area': constructed_floor_area,
            'accumulated_constructed_floor_area': accumulated_constructed_floor_area,
            'floor_area_over_population_growth': floor_area_over_population_growth
        }, index=[year for year in range(2010, 2051)])

        return construction
