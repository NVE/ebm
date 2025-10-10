import pathlib
import os
import sys
from dotenv import load_dotenv, find_dotenv
from loguru import logger


def load_environment_from_dotenv():
    env_file = pathlib.Path(find_dotenv(usecwd=True))
    if env_file.is_file():
        logger.debug(f'Loading environment from {env_file}')
        load_dotenv(env_file)



def configure_loglevel(log_format: str | None = None, level: str = 'INFO') -> None:
    """
    Configure the loguru logger with a specified log level and format.

    By default, sets the log level to INFO unless either:
    - The '--debug' flag is present in the command-line arguments (`sys.argv`), or
    - The environment variable DEBUG is set to 'TRUE' (case-insensitive).

    If debug mode is enabled, the log level is set to DEBUG and a filter is applied
    to suppress DEBUG logs from the 'ebm.model.file_handler' logger.

    Parameters
    ----------
    log_format : str, optional
        Custom format string for log messages. If not provided, the default format is used.
    level : str, optional
        Default log level to use when debug mode is not active. Defaults to 'INFO'.

    Returns
    -------
    None

    """
    logger.remove()
    options = {'level': level}
    if log_format:
        options['format'] = log_format

    # Accessing sys.argv directly since we want to figure out the log level before loading arguments with arg_parser.
    # Debug level may also be conveyed through environment variables, so read that from environ as well.
    if '--debug' in sys.argv or os.environ.get('DEBUG', '').upper() == 'TRUE':
        options['level'] = 'DEBUG'

    logger.add(sys.stderr,
               filter=lambda f: not (f['name'] == 'ebm.model.file_handler' and f['level'].name == 'DEBUG'),
               **options)