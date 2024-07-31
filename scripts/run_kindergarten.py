import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd
from pandas import Series
from rich.pretty import pprint
from loguru import logger

from ebm.model import BuildingCategory, DatabaseManager, NewBuildings

logger.info = pprint


def calculate_construction(building_category: BuildingCategory = None):
    bc = building_category if building_category else BuildingCategory.KINDERGARTEN
    if bc != BuildingCategory.KINDERGARTEN:
        raise NotImplementedError(f'calculate_construction does not support category {bc}')

    # Faste tall
    kg_totalt_areal_2010 = pd.Series(data=[1_275_238], index=[2010])

    logger.debug('kg_totalt_areal (2010)')
    logger.info(kg_totalt_areal_2010)

    logger.debug('kg_barnehage_nybygget (2010-2014)')
    kg_barnehage_nybygget = pd.Series(data=[97_574, 90_644, 65_847, 62_022, 79_992],
                                      index=[2010, 2011, 2012, 2013, 2014])
    logger.info(kg_barnehage_nybygget)

    # Eksterne tall

    logger.debug('kg_årlig_revet_areal')
    kg_arlig_revet_areal = NewBuildings.calculate_floor_area_demolished(BuildingCategory.KINDERGARTEN)
    # logger.info(kg_arlig_revet_areal)

    befolkning: pd.DataFrame = pd.read_csv('C:/Users/kenord/dev2/Energibruksmodell/input/nybygging_befolkning.csv',
                             dtype={"household_size": "float64"})

    population = befolkning.set_index('year')['population']
    population_growth = (population / population.shift(1)) - 1

    # Barnehage totalareal 2011

    logger.debug(kg_barnehage_nybygget.loc[2010])

    #    logger.debug('=+E41-F46+F47')
    tall = kg_totalt_areal_2010.loc[2010] - kg_arlig_revet_areal.loc[2011] + kg_barnehage_nybygget.loc[2011]
    kg_totalt_areal_2010.loc[2011] = tall
    logger.debug(
        f'{kg_totalt_areal_2010.loc[2010]=} - {kg_arlig_revet_areal.loc[2011]=} + {kg_barnehage_nybygget.loc[2011]=}')
    logger.debug('sum 1 364 963')
    logger.info(f'{tall=}')
    logger.info(kg_totalt_areal_2010.loc[2011])

    # Barnehage totalareal 2012 - 2015

    logger.debug('kg_totalt_areal_2011 ')
    logger.info(kg_totalt_areal_2010.loc[2011])

    logger.debug('=+F41-G46+G47')
    logger.debug(
        f'{kg_totalt_areal_2010.loc[2011]=} - {kg_arlig_revet_areal.loc[2012]=} + {kg_barnehage_nybygget.loc[2012]=}')
    logger.debug('sum 1 429 891')
    logger.info(kg_totalt_areal_2010)

    for year in range(2011, 2015):
        logger.debug(
            f'{year} {kg_totalt_areal_2010.loc[year - 1]} {kg_arlig_revet_areal.loc[year]} {kg_barnehage_nybygget.loc[year]}')
        kg_totalt_areal_2010.loc[year] = kg_totalt_areal_2010.loc[year - 1] - kg_arlig_revet_areal.loc[year] + \
                                         kg_barnehage_nybygget.loc[year]
    # logger.info(kg_totalt_areal_2010)

    # barnehagevekst og areal-/befolkningsøkning
    population_growth = (population / population.shift(1)) - 1

    kg_barnehagevekst: Series = pd.Series(data=itertools.repeat(0.0, 41), index=[y for y in range(2010, 2051)])
    barnehagevekst_2011 = (kg_totalt_areal_2010.loc[2011] / kg_totalt_areal_2010.loc[2010]) - 1
    kg_barnehagevekst.loc[2011] = barnehagevekst_2011
    kg_barnehagevekst.loc[2010] = np.nan
    logger.debug('kg_barnehagevekst')

    kg_floor_area_population: Series = pd.Series(data=[np.nan] + list(itertools.repeat(1, 40)), index=range(2010, 2051))
    kg_floor_area_population.loc[2011] = barnehagevekst_2011 / population_growth.loc[2011]

    # logger.info(kg_floor_area_population)

    # Barnehage Total areal 2015

    # barnehagevekst og areal-/befolkningsøkning 22

    for year in range(2011, 2015):
        kg_barnehagevekst.loc[year] = (kg_totalt_areal_2010.loc[year] / kg_totalt_areal_2010.loc[year - 1]) - 1
        kg_floor_area_population[year] = kg_barnehagevekst.loc[year] / population_growth.loc[year]

    # logger.info(kg_barnehagevekst)

    mean_floor_area_population = kg_floor_area_population.loc[2011:2014].mean()
    for year in range(2015, 2021):
        kg_floor_area_population.loc[year] = mean_floor_area_population
    for year in range(2021, 2050):
        kg_floor_area_population.loc[year] = 1

    for year in range(2021, 2031):
        kg_floor_area_population.loc[year] = (kg_floor_area_population.loc[2020] - (year - 2020) * (
                    (kg_floor_area_population.loc[2020] - kg_floor_area_population.loc[2030]) / 10))

    # logger.info(kg_floor_area_population)

    for year in range(2015, 2051):
        j53 = kg_floor_area_population.loc[year]
        j5 = population_growth.loc[year]
        i41 = kg_totalt_areal_2010.loc[year - 1]
        kg_totalt_areal_2010.loc[year] = ((j53 * j5) + 1) * i41

    # Årlig nybygget areal barnehage (2015 - 2050)

    for year in range(2015, 2051):
        j41 = kg_totalt_areal_2010.loc[year]
        i41 = kg_totalt_areal_2010.loc[year - 1]
        j46 = kg_arlig_revet_areal.loc[year]
        kg_barnehage_nybygget[year] = j41 - i41 + j46

    # kg_arlig_nybygget_akkumulert = kg_barnehage_nybygget.cumsum()
    # kg_nybygg_rate = kg_barnehage_nybygget / kg_totalt_areal_2010
    kg_arlig_nybygget_akkumulert = kg_barnehage_nybygget.cumsum()

    return kg_arlig_nybygget_akkumulert


if __name__ == '__main__':
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True' and False:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    logger.info(calculate_construction())
