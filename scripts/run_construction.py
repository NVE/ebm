import argparse
import collections.abc
import os
import sys

from rich.pretty import pprint
from loguru import logger

from ebm.model import BuildingCategory
from ebm.model.new_buildings import NewBuildings

logger.info = pprint


def load_expected_yearly_constructed(building_category: BuildingCategory) -> collections.abc.Collection:
    if building_category == BuildingCategory.KINDERGARTEN:
        return (97574, 188218, 254065, 316087, 396079, 470970, 536935, 599494, 653696, 707496, 761822, 797373,
                831966, 866076, 896322, 923447, 947622, 968409, 987638, 1003524, 1018640, 1033603, 1048354,
                1062933, 1077371, 1091662, 1105822, 1119722, 1133249, 1146405, 1159207, 1171662,
                1184612, 1197210, 1211952, 1226342, 1240370, 1254043, 1267362, 1280335, 1292971,)
    if building_category == BuildingCategory.UNIVERSITY:
        return (112747, 161952, 206052, 240818, 325158, 375511, 418991, 459447, 494127, 528000, 561635, 584973, 608459,
                632529, 655126, 676778, 697665, 717495, 739952, 761405, 785527, 809435, 833046, 856416, 879589, 902557,
                925341, 947760, 969657, 991035, 1011918, 1032313, 1053229, 1073650, 1106477, 1138810, 1170638, 1201968,
                1232802, 1263152, 1293028,)

    return (443334, 798437, 1447903, 1979251, 2299729, 2721889, 3087734, 3428423, 3722538, 4009570, 4294057, 4500971,
            4712697, 4933270, 5145688, 5354382, 5561004, 5762916, 5993702, 6220151, 6536014, 6849630, 7160135, 7468127,
            7774059, 8077834, 8379696, 8677741, 8970321, 9257475, 9539452, 9816326, 10099873, 10378254, 10802821,
            11222223, 11636340, 12045246, 12448964, 12847624, 13241332,)


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('building_category', type=str, nargs='?', default='university')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True' and False:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    building_category = BuildingCategory.from_string(arguments.building_category)
    expected_values = load_expected_yearly_constructed(building_category)

    construction_floor_area = NewBuildings.calculate_yearly_construction(
        building_category=building_category
    )

    error_count = 0
    for (year, cfa), expected_value in zip(construction_floor_area.items(), expected_values):
        if round(cfa) != expected_value:
            error_count = error_count + 1
            logger.error(f'Expected {expected_value} was {round(cfa)} {building_category.name} {year=} {cfa=}')
            logger.debug(f'The difference is {expected_value - round(cfa)}')
        else:
            logger.debug(f'Found expected value {expected_value} {year=} {cfa=}')

    sys.exit(error_count)


if __name__ == '__main__':
    main()
