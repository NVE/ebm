import os
import pathlib
import sys
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from loguru import logger


def load_environment_from_dotenv():
    env_file = pathlib.Path(find_dotenv(usecwd=True))
    if env_file.is_file():
        logger.debug(f'Loading environment from {env_file}')
        load_dotenv(pathlib.Path('.env').absolute())
    else:
        logger.trace(f'.env not found in {env_file.absolute()}')


def configure_json_log(log_directory: str|bool=False):
    env_log_directory = os.environ.get('LOG_DIRECTORY', log_directory)
    if env_log_directory.upper().strip()!='FALSE':
        log_directory = env_log_directory if env_log_directory.upper().strip() != 'TRUE' else 'log'
        log_start_time = datetime.now().isoformat(timespec='seconds').replace(':', '')
        log_file_name = f'{log_directory}/ebm-{log_start_time}.json'
        logger.debug(f'Logging json to {log_file_name}')
        logger.add(log_file_name, level='TRACE', serialize=True)
    else:
        logger.debug('Skipping json log. LOG_DIRECTORY is undefined.')


def configure_loglevel(log_format: str = None):
    """
    Sets loguru loglevel to INFO unless ebm is called with parameter --debug and the environment variable DEBUG is not
    equal to True

    """
    logger.remove()
    options = {'level': 'INFO'}
    if log_format:
        options['format'] = log_format

    if '--debug' in sys.argv or os.environ.get('DEBUG', '').upper() == 'TRUE':
        options['level'] = 'DEBUG'

    # Add a new handler with a custom format
    if '--debug' not in sys.argv and os.environ.get('DEBUG', '').upper() != 'TRUE':
        logger.add(sys.stderr, **options)
    else:
        logger.add(sys.stderr,
                   filter=lambda f: not (f['name'] == 'ebm.model.file_handler' and f['level'].name == 'DEBUG'),
                   **options)
