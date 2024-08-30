import itertools
import typing
from typing import Union

import numpy as np
import pandas as pd
from loguru import logger
from pandas import Series

from ebm.model.building_category import BuildingCategory
from ebm.model.database_manager import DatabaseManager


class ConstructionCalculator:
    
    def calculate_residential_construction(self, population: pd.Series,
                                           household_size: pd.Series,
                                           building_category_share: pd.Series,
                                           build_area_sum: pd.Series,
                                           yearly_demolished_floor_area: pd.Series,
                                           average_floor_area=175) -> pd.DataFrame:
        # Befolkningsøkning (Ikke brukt videre)
        population_growth = self.calculate_population_growth(population)
        households = self.calculate_households_by_year(household_size, population)

        # Årlig endring i antall boliger (brukt Årlig endring i antall småhus)
        households_change = self.calculate_household_change(households)
        house_change = self.calculate_house_change(building_category_share, households_change)

        # Årlig endring areal småhus (brukt Årlig nybygget areal småhus)
        yearly_floor_area_constructed = self.calculate_yearly_floor_area_change(
            building_category_share,
            house_change,
            average_floor_area)

        # Årlig revet areal småhus
        floor_area_change = self.calculate_yearly_constructed_floor_area(
            build_area_sum, yearly_floor_area_constructed, yearly_demolished_floor_area)

        # Nybygget småhus akkumulert
        floor_area_change_accumulated = self.calculate_yearly_new_building_floor_area_sum(floor_area_change)

        df = pd.DataFrame(data={
            'population': population,
            'population_growth': population_growth,
            'household_size': household_size,
            'households': households,
            'households_change': households_change,
            'building_growth': house_change,
            'yearly_floor_area_constructed': yearly_floor_area_constructed,
            'demolished_floor_area': yearly_demolished_floor_area,
            'constructed_floor_area': floor_area_change,
            'accumulated_constructed_floor_area': floor_area_change_accumulated},
            index=floor_area_change_accumulated.index)

        return df

    @staticmethod
    def calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house: pd.Series):
        return pd.Series(yearly_new_building_floor_area_house.cumsum(), name='accumulated_constructed_floor_area')

    @staticmethod
    def calculate_yearly_constructed_floor_area(build_area_sum,
                                                yearly_floor_area_change,
                                                yearly_demolished_floor_area) -> pd.Series:
        # Årlig nybygget areal småhus (brukt  Nybygget småhus akkumulert)
        yearly_new_building_floor_area_house = yearly_floor_area_change + yearly_demolished_floor_area
        yearly_new_building_floor_area_house.loc[build_area_sum.index.values] = build_area_sum.loc[
            build_area_sum.index.values]

        return pd.Series(yearly_new_building_floor_area_house, name='constructed_floor_area')

    @staticmethod
    def calculate_floor_area_demolished(building_category: BuildingCategory):
        # Loading demolition data from spreadsheet. Should be changed to a parameter with calculated data
        demolition = DatabaseManager().load_demolition_floor_area_from_spreadsheet(building_category)

        # Årlig revet areal småhus
        yearly_demolished_floor_area_house = demolition.diff(1)
        return pd.Series(yearly_demolished_floor_area_house, name='demolished_floor_area')

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
    def calculate_house_change(building_category_share: pd.Series, households_change: pd.Series) -> pd.Series:
        house_share = building_category_share
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
    def calculate_commercial_construction(building_category: BuildingCategory = None,
                                          total_floor_area: int = 1_275_238,
                                          constructed_floor_area: pd.Series = None,
                                          demolition_floor_area: pd.Series = None) -> pd.DataFrame:
        if not building_category:
            building_category = BuildingCategory.KINDERGARTEN

        # Faste tall

        logger.debug('constructed_floor_area (2010-2014)')

        # Eksterne tall
        population: pd.DataFrame = pd.read_csv('input/new_buildings_population.csv',
                                               dtype={"household_size": "float64"})
        population = population.set_index('year')['population']

        total_floor_area = pd.Series(data=[total_floor_area], index=[2010])
        total_floor_area.loc[2011] = \
            total_floor_area.loc[2010] - demolition_floor_area.loc[2011] + constructed_floor_area.loc[2011]
        for year in range(2011, 2015):
            total_floor_area.loc[year] = total_floor_area.loc[year - 1] - \
                                         demolition_floor_area.loc[year] + \
                                         constructed_floor_area.loc[year]

        # barnehagevekst og areal-/befolkningsøkning
        population_growth = (population / population.shift(1)) - 1
        building_growth: Series = pd.Series(data=itertools.repeat(0.0, 41), index=[y for y in range(2010, 2051)])

        building_growth.loc[2011] = (total_floor_area.loc[2011] / total_floor_area.loc[2010]) - 1
        building_growth.loc[2010] = np.nan
        logger.debug('building_growth')
        floor_area_over_population_growth: Series = pd.Series(data=[np.nan] + list(itertools.repeat(1, 40)),
                                                              index=range(2010, 2051))
        floor_area_over_population_growth.loc[2011] = building_growth.loc[2011] / population_growth.loc[2011]

        # Barnehage Total areal til 2015
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
            floor_area_over_population_growth.loc[year] = \
                (floor_area_over_population_growth.loc[2020] - (year - 2020) * ((floor_area_over_population_growth.loc[
                                                                                     2020] -
                                                                                 floor_area_over_population_growth.loc[
                                                                                     2030]) / 10))

        for year in range(2015, 2051):
            floor_area_ch_over_pop_ch = floor_area_over_population_growth.loc[year]
            year_pop_growth = population_growth.loc[year]
            previous_year_floor_area = total_floor_area.loc[year - 1]
            total_floor_area.loc[year] = ((floor_area_ch_over_pop_ch * year_pop_growth) + 1) * previous_year_floor_area

        if building_category == BuildingCategory.STORAGE_REPAIRS:
            total_floor_area.loc[2010:2051] = total_floor_area.loc[2010]

        for year in range(2015, 2051):
            floor_area = total_floor_area.loc[year]
            previous_year_floor_area = total_floor_area.loc[year - 1]
            demolished = demolition_floor_area.loc[year]
            constructed = floor_area - previous_year_floor_area + demolished
            constructed_floor_area[year] = constructed

        # accumulated_constructed_floor_area = constructed_floor_area.cumsum()
        # kg_nybygg_rate = constructed_floor_area / total_floor_area
        accumulated_constructed_floor_area = constructed_floor_area.cumsum()

        construction = pd.DataFrame(data={
            'total_floor_area': total_floor_area,
            'building_growth': building_growth,
            'demolished_floor_area': demolition_floor_area,
            'constructed_floor_area': constructed_floor_area,
            'accumulated_constructed_floor_area': accumulated_constructed_floor_area,
            'floor_area_over_population_growth': floor_area_over_population_growth
        }, index=[year for year in range(2010, 2051)])

        return construction

    @staticmethod
    def calculate_construction_as_list(building_category: BuildingCategory,
                                       demolition_floor_area: Union[pd.Series, list],
                                       database_manager: DatabaseManager = None) -> typing.List:
        """
               Calculates constructed floor area for buildings based using provided demolition_floor_area
                 and input data from database_manager

               Parameters
               ----------
               building_category: BuildingCategory
               demolition_floor_area: pd.Series expects index=2010..2050
               database_manager: DatabaseManager (optional)

               Returns
               -------
               accumulated_constructed_floor_area: List

               """

        yearly_constructed = ConstructionCalculator.calculate_construction(
            building_category, demolition_floor_area, database_manager if database_manager else DatabaseManager())

        accumulated_constructed_floor_area = [v for v in yearly_constructed.accumulated_constructed_floor_area]
        return accumulated_constructed_floor_area

    @staticmethod
    def calculate_construction(building_category: BuildingCategory,
                               demolition_floor_area: Union[pd.Series, list],
                               database_manager: DatabaseManager) -> pd.DataFrame:
        """
        Calculates constructed floor area for buildings based using provided demolition_floor_area
          and input data from database_manager
        Parameters
        ----------
        building_category: BuildingCategory
        demolition_floor_area: pd.Series expects index=2010..2050
        database_manager: DatabaseManager

        Returns calculated_construction: pd.DataFrame
                                           dataframe columns include;
                                           (building_growth)
                                           (demolished_floor_area)
                                           (constructed_floor_area)
                                           (accumulated_constructed_floor_area)
                                           (total_floor_area)
                                           (floor_area_over_population_growth)
                                           (households)
                                           (household_size)
                                           (population)
                                           (population_growth)

        -------

        """
        if isinstance(demolition_floor_area, list):
            demolition_floor_area = pd.Series(demolition_floor_area, index=[y for y in range(2010, 2050 + 1)])

        yearly_construction_floor_area = database_manager.get_building_category_floor_area(building_category)
        area_parameters = database_manager.get_area_parameters()
        total_floor_area = area_parameters[area_parameters.building_category == building_category].area.sum()

        if building_category.is_residential():
            new_buildings_population = database_manager.get_construction_population()[['population', 'household_size']]
            household_size = new_buildings_population['household_size']
            population = new_buildings_population['population']

            share_name = 'new_house_share'
            if building_category == BuildingCategory.APARTMENT_BLOCK:
                share_name = 'new_apartment_block_share'
            building_category_share = database_manager.get_new_buildings_category_share()[share_name]

            average_floor_area = 175 if building_category == BuildingCategory.HOUSE else 75
            build_area_sum = pd.Series(
                data=yearly_construction_floor_area, index=range(2010, 2010+len(yearly_construction_floor_area)))

            return ConstructionCalculator().calculate_residential_construction(
                yearly_demolished_floor_area=demolition_floor_area,
                population=population,
                household_size=household_size,
                building_category_share=building_category_share,
                build_area_sum=build_area_sum,
                average_floor_area=average_floor_area)

        return ConstructionCalculator.calculate_commercial_construction(
            building_category=building_category,
            total_floor_area=total_floor_area,
            constructed_floor_area=yearly_construction_floor_area,
            demolition_floor_area=demolition_floor_area)
