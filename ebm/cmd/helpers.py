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
    """
    Configures JSON logging using the `loguru` logger.

    This function sets up structured JSON logging to a file, with the log file path
    determined by the `LOG_DIRECTORY` environment variable or the provided `log_directory` argument.
    If `LOG_DIRECTORY` is set to 'TRUE', the default directory 'log' is used.
    If it is set to 'FALSE', logging is skipped.

    Parameters
    ----------
    log_directory : str or bool, optional
        The directory where the log file should be saved. If set to `False`, logging is disabled
        unless overridden by the `LOG_DIRECTORY` environment variable.

    Environment Variables
    ---------------------
    LOG_DIRECTORY : str
        Overrides the `log_directory` argument when set. Special values:
        - 'TRUE': uses default directory 'log'
        - 'FALSE': disables logging

    Notes
    -----
    - The log file is named using the current timestamp in ISO format (without colons).
    - The log file is serialized in JSON format.
    - The directory is created if it does not exist.

    Examples
    --------
    >>> configure_json_log("logs")
    >>> os.environ["LOG_DIRECTORY"] = "TRUE"

    >>> configure_json_log(False)
    """
    script_name = pathlib.Path(pathlib.Path(sys.argv[0]))
    file_stem = script_name.stem if script_name.stem!='__main__' else script_name.parent.name + script_name.stem

    env_log_directory = os.environ.get('LOG_DIRECTORY', log_directory)
    env_log_directory = env_log_directory if env_log_directory.upper().strip() != 'TRUE' else 'log'

    log_to_json = env_log_directory.upper().strip()!='FALSE'
    if log_to_json:
        log_directory = pathlib.Path(env_log_directory if env_log_directory else log_directory)
        if log_directory.is_file():
            logger.warning(f'LOG_DIRECTORY={log_directory} is a file. Skipping json logging')
            return
        log_directory.mkdir(exist_ok=True)

        log_start = datetime.now()
        log_filename = log_directory / f'{file_stem}-{log_start.isoformat(timespec='seconds').replace(':', '')}.json'
        if log_filename.is_file():
            log_start_milliseconds = log_start.isoformat(timespec='milliseconds').replace(':', '')
            log_filename = log_filename.with_stem(f'{file_stem}-{log_start_milliseconds}')

        logger.debug(f'Logging json to {log_filename}')
        logger.add(log_filename, level=os.environ.get('LOG_LEVEL_JSON', 'TRACE'), serialize=True)
        if len(sys.argv) > 1:
            logger.info(f'argv={sys.argv[1:]}')
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
