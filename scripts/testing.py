import argparse
import os
import sys

from loguru import logger

from ebm.main import *
from ebm.model import Buildings
from ebm.model import DatabaseManager

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--debug', action='store_true')
    arguments = arg_parser.parse_args()

    if not arguments.debug and os.environ.get('DEBUG', '') != 'True':
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    building_category = 'House'
    
    def s_curve_params_dict():
        db = DatabaseManager()
        input = db.get_scurve_params_per_building_category('House', 'Small measure')
        print(input)

    #s_curve_params_dict()

    df = s_curves_to_dataframe(building_category)
    print(df)
    #df.to_excel(f's_curve_{building_category}.xlsx')
    

if __name__ == '__main__':
    main()
