import pathlib
from dotenv import load_dotenv, find_dotenv
from loguru import logger


def load_environment_from_dotenv():
    env_file = pathlib.Path(find_dotenv(usecwd=True))
    if env_file.is_file():
        logger.debug(f'Loading environment from {env_file}')
        load_dotenv(env_file)