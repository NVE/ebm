#!/usr/bin/env python
# coding: utf-8
import itertools
import os
import pathlib

from loguru import logger

from ebm.cmd.helpers import load_environment_from_dotenv, configure_loglevel
from ebm.extractors import extract_area_forecast
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager, FileHandler
import pandas as pd


def dataframe_to_csv(area_unstacked, target_file):
    def increment_filename(filename: pathlib.Path):
        yield filename
        for i in range(1, 100):
            yield filename.parent / f'{filename.stem}-{i}{filename.suffix}'

    for output_file in increment_filename(target_file):
        logger.debug(f'Writing to {output_file}')
        try:
            area_unstacked.to_csv(output_file,
                                  index=False,
                                  sep=os.environ.get('EBM_CSV_DELIMITER', ';'),
                                  decimal=os.environ.get('EBM_CSV_DECIMAL_POINT', '.'))
        except IOError as io_error:
            logger.debug(io_error)
            logger.debug(f'IOError writing to {output_file}')
        else:
            logger.info(f'Wrote {output_file.absolute()}')
            break


def main():
    pd.set_option('display.float_format', '{:.6f}'.format)
    load_environment_from_dotenv()
    configure_loglevel(log_format=os.environ.get('LOG_FORMAT'))

    years = YearRange(2020, 2050)
    dm = DatabaseManager(FileHandler(directory='t2734_input'))

    scurve_parameters = dm.get_scurve_params()

    area_parameters = dm.get_area_parameters()
    area_parameters['year'] = years.start

    building_code_parameters = dm.file_handler.get_building_code()

    logger.info('Call extract_area_forecast')
    area_by_condition = extract_area_forecast(years, scurve_parameters, building_code_parameters, area_parameters, dm)

    logger.info('Write output')
    dataframe_to_csv(area_by_condition, pathlib.Path('output/area_dataframes.csv'))



if __name__ == '__main__':
    main()