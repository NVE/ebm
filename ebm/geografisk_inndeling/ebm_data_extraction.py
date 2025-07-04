import os

from loguru import logger

from ebm.cmd.helpers import load_environment_from_dotenv
from ebm.cmd.result_handler import EbmDefaultHandler
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler


def load_energy_use():
    load_environment_from_dotenv()
    configure_loglevel(os.environ.get('LOG_FORMAT', None))

    fh = FileHandler(directory=os.environ.get('EBM_OUTPUT'))
    database_manager = DatabaseManager(file_handler=fh)
    df = EbmDefaultHandler().extract_model(YearRange(2020, 2050), building_categories=None, database_manager=database_manager)
    logger.info('Done')

    print(df)

    return df

energy_use = None
if __name__ == '__main__':
    energy_use = load_energy_use()


print("Energy use data loaded successfully.")
