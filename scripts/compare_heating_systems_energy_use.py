import os

from loguru import logger

from ebm.cmd.helpers import load_environment_from_dotenv, configure_loglevel
from ebm.cmd.result_handler import EbmDefaultHandler
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler


def load_heating_systems():
    load_environment_from_dotenv()
    configure_loglevel(os.environ.get('LOG_FORMAT', None))

    fh = FileHandler(directory=os.environ.get('EBM_INPUT'))
    database_manager = DatabaseManager(file_handler=fh)
    df = EbmDefaultHandler().extract_model(YearRange(2020, 2050), building_categories=None, database_manager=database_manager)
    logger.info('Done')

    print(df)

    return df

hs = None
if __name__ == '__main__':
    hs = load_heating_systems()