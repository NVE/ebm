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

    print(NewBuildings.calculate_construction())
