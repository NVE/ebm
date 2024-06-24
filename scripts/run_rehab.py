import argparse
import os
import sys

from loguru import logger

from ebm.main import get_demolition_shares_per_tek
from ebm.model import Buildings

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    df = get_demolition_shares_per_tek('House')
    #df = get_total_small_measures_shares_per_tek('House')
    #df = get_total_renovation_shares_per_tek('House')
    print(df)

if __name__ == '__main__':
    main()