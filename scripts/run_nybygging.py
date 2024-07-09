""" Program used to test nybygging calculation """
import argparse
import os
import sys

from loguru import logger

from ebm.model import FileHandler


def main():
    """ Program used to test nybygging calculation main function """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments: argparse.Namespace = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    file_handler = FileHandler()
    population = file_handler.get_file('nybygging_befolkning.csv')
    print(population)
    area_built = file_handler.get_file('nybygging_ssb_05939.csv')
    print(area_built)

if __name__ == '__main__':
    main()
