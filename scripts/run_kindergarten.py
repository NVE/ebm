import argparse
import os
import sys

from rich.pretty import pprint
from loguru import logger

from ebm.model.new_buildings import NewBuildings

logger.info = pprint

if __name__ == '__main__':
    """ Program used to test nybygging kindergarten calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True' and False:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    expected_values = [97574,
                       188218,
                       254065,
                       316087,
                       396079,
                       470970,
                       536935,
                       599494,
                       653696,
                       707496,
                       761822,
                       797373,
                       831966,
                       866076,
                       896322,
                       923447,
                       947622,
                       968409,
                       987638,
                       1003524,
                       1018640,
                       1033603,
                       1048354,
                       1062933,
                       1077371,
                       1091662,
                       1105822,
                       1119722,
                       1133249,
                       1146405,
                       1159207,
                       1171662,
                       1184612,
                       1197210,
                       1211952,
                       1226342,
                       1240370,
                       1254043,
                       1267362,
                       1280335,
                       1292971]

    construction_floor_area = NewBuildings.calculate_construction()

    error_count = 0
    for (year, cfa), expected_value in zip(construction_floor_area.items(), expected_values):
        if round(cfa) != expected_value:
            error_count = error_count + 1
            logger.error(f'Expected {expected_value} was {round(cfa)} {year=} {cfa=}')
        else:
            logger.debug(f'Found expected value {expected_value} {year=} {cfa=}')
