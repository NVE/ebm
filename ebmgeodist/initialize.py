"""Module for setting up input, output and managing default data"""
import os
import argparse
from pathlib import Path
from loguru import logger
from typing import Union, Optional
from ebmgeodist.file_handler import FileHandler
from ebm.__version__ import version
DEFAULT_INPUT = Path(f'X:\\NAS\\Data\\ebm\\default-input-{".".join(version.split(".")[:2])}\\')

class NameHandler:
    """
    Handles column names
    """
    COLUMN_NAME_RESIDENTIAL = "bolig"
    COLUMN_NAME_HOLIDAY_HOME = "Fritidsboliger"
    COLUMN_NAME_NON_RESIDENTIAL = "yrkesbygg"
    ENERGY_PRODUCT_ELECTRICITY = "electricity"
    ENERGY_PRODUCT_DISTRICT_HEATING = "dh"
    ENERGY_PRODUCT_FUELWOOD = "fuelwood"
    ENERGY_PRODUCT_FOSSILFUEL = "fossilfuel"

    
    @classmethod
    def normalize_category(cls, value: str) -> Union[str, list[str]]:
        """
        Normalizes the category input to a standard format.
        """
        value = value.strip().lower()
        mapping = {
            "residential": cls.COLUMN_NAME_RESIDENTIAL,
            "residential-building": cls.COLUMN_NAME_RESIDENTIAL,
            "bolig": cls.COLUMN_NAME_RESIDENTIAL,
            "holiday": cls.COLUMN_NAME_HOLIDAY_HOME,
            "holiday-home": cls.COLUMN_NAME_HOLIDAY_HOME,
            "holiday-homes": cls.COLUMN_NAME_HOLIDAY_HOME,
            "fritidsboliger": cls.COLUMN_NAME_HOLIDAY_HOME,
            "non-residential": cls.COLUMN_NAME_NON_RESIDENTIAL,
            "non-residential-building": cls.COLUMN_NAME_NON_RESIDENTIAL,
            "yrkesbygg": cls.COLUMN_NAME_NON_RESIDENTIAL,
            "all": [cls.COLUMN_NAME_RESIDENTIAL, cls.COLUMN_NAME_HOLIDAY_HOME, cls.COLUMN_NAME_NON_RESIDENTIAL]
        }
        
        if value in mapping:
            return mapping[value]
        else:
            raise argparse.ArgumentTypeError(
                f"Invalid building category: '{value}'. Valid values are: residential, holiday home, non-residential, all."
            )
    
    @classmethod
    def normalize_to_list(cls, value: Union[str, list[str]]) -> list[str]:
        """
        Always returns a list of normalized categories,
        even if input is a single string or a list of strings.
        """
        if isinstance(value, list):
            result = []
            for v in value:
                normalized = cls.normalize_category(v)
                result.append(normalized)
            return list(result)
        else:
            normalized = cls.normalize_category(value)
            return normalized if isinstance(normalized, list) else [normalized]


def make_arguments(program_name: str, default_path: Path) -> argparse.Namespace:

    arg_parser = argparse.ArgumentParser(prog=program_name,
                                         description="Energibruksmodell - Geographical distribution of energy use",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
    
    arg_parser.add_argument('--input', '--input-directory', '-i',
                            nargs='?',
                            type=Path,
                            default=Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input')),
                            help='path to the directory with input files')
    
    arg_parser.add_argument('--building-category', '-c', 
        type=NameHandler.normalize_to_list,
        nargs='?',
        default=NameHandler.normalize_to_list("all"),
        help="Choose building category: residential, holiday home, non-residential or all (default: all)"
    )

    arg_parser.add_argument(
        "--years", "-y",
        type=int,
        nargs="+",
        metavar="ÅR",
        default=[2022,2023,2024],
        help="Years to be included in the calculation of distribution keys, e.g.: --years 2022 2023 2024 (default: 2022 2023 2024)"
    )

    arg_parser.add_argument('--source','-s', choices=['azure', 'local'], default='local',
                            help='''
Choose data source: 'azure' to load data directly from Elhub data lake, or 'local' to use the included parquet 
file, (default: local)
                            ''')
    
    arg_parser.add_argument('--create-input', action='store_true',
                            help='''
                            Create input directory and copy necessary data files from data/ directory.
                            ''')
    
    arg_parser.add_argument('--start-end-years', action='store_true', help='''The output file only includes the start and end years. Default is to include all years.''')

    arg_parser.add_argument('--energy-product', '-e',
                            choices=['electricity', 'dh', 'fuelwood', 'fossilfuel'],
                             default=['electricity','dh', 'fuelwood', 'fossilfuel'],
                             help='''
                             Choose energy product: electricity, dh, fuelwood or fossilfuel. (default: electricity) 
                            ''')

    arguments = arg_parser.parse_args()
    return arguments
    

def get_project_root(root_name: str = "Energibruksmodell") -> Path:
    """
    Finds the nearest parent folder matching `root_name` from this script's location.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name.lower() == root_name.lower():
            return parent
    raise FileNotFoundError(f"Could not find project root named '{root_name}' starting from {current}")



def get_output_file(relative_path: str, root_folder: str = "Energibruksmodell") -> Path:
    """
    Builds an output path relative to the detected project root.
    """
    if not relative_path:
        raise ValueError("Relative path must be provided.")
    return get_project_root(root_folder) / relative_path

def create_input(file_handler: FileHandler,
                 source_directory: Optional[Path]=None) -> bool:
    """
    Create any input file missing in file_handler.input_directory using the default data source.

    Parameters
    ----------
    source_directory :
    file_handler : FileHandler

    Returns
    -------
    bool
    """

    source = file_handler.default_data_directory()
    
    if source_directory:
        if not source_directory.is_dir():
            raise NotADirectoryError(f'{source_directory} is not a directory')

        source_fh = FileHandler(directory=source_directory)
        missing_files = source_fh.check_for_missing_files()
        if len(missing_files) > 0:
            msg = f'File not found {missing_files[0]}'
            raise FileNotFoundError(msg)
        source = source_directory
    
    file_handler.create_missing_input_files(source_directory=source)

    return True


def create_output_directory(output_directory: Optional[Path]=None,
                            filename: Optional[Path]=None) -> Path:
    """
    Creates the output directory if it does not exist. If a filename is supplied its parent will be created.

    Parameters
    ----------
    output_directory : pathlib.Path, optional
        The path to the output directory.
    filename : pathlib.Path, optional
        The name of a file in a directory expected to exist.
    Raises
    -------
    IOError
        The output_directory exists, but it is a file.
    ValueError
        output_directory and filename is empty
    Returns
    -------
    pathlib.Path
        The directory
    """
    if not output_directory and not filename:
        raise ValueError('Both output_directory and filename cannot be None')
    if output_directory and output_directory.is_file():
        raise IOError(f'{output_directory} is a file')

    if output_directory:
        if output_directory.is_dir():
            return output_directory
        logger.debug(f'Creating output directory {output_directory}')
        output_directory.mkdir(exist_ok=True)
        return output_directory
    elif filename and not filename.is_file():
        logger.debug(f'Creating output directory {filename.parent}')
        filename.parent.mkdir(exist_ok=True)
        return filename.parent


def init(file_handler: FileHandler, source_directory: Path|None = None) -> Path:
    """
    Initialize file_handler with input data from ebm.data or DEFAULT_INPUT_OVERRIDE.
    Create output directory in current working directory if missing

    Parameters
    ----------
    file_handler : FileHandler
    source_directory : pathlib.Path, optional
        Where location of input data

    Returns
    -------
    pathlib.Path
    """
    if source_directory is None:
        default_input_override = Path(os.environ.get('EBM_DEFAULT_INPUT', DEFAULT_INPUT))
        if default_input_override.is_dir():
            logger.debug(f'{default_input_override=} exists')
            source_directory = default_input_override
        else:
            logger.info(f'{default_input_override=} does not exist.')
            source_directory = file_handler.default_data_directory()
    elif not source_directory.is_dir():
        raise NotADirectoryError(f'{source_directory} is not a directory')

    logger.info(f'Copy input from {source_directory}')
    create_input(file_handler, source_directory=source_directory)
    create_output_directory(Path('output'))
    return file_handler.input_directory
