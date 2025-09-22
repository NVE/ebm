import os
import pathlib
import shutil
import typing

import polars as pl
from loguru import logger
from pandera.errors import SchemaErrors, SchemaError



class FileHandler:
    """
    Handles file operations.
    """

    # Filenames
    ELHUB_DATA = 'yearly_aggregated_elhub_data.parquet'
    DH_DATA = 'fjernvarme_kommune_fordelingsnøkler.xlsx'
    BIO_DATA = 'ved_kommune_fordelingsnøkler.xlsx'

    input_directory: pathlib.Path

    def __init__(self, directory: typing.Union[str, pathlib.Path, None] = None):
        """
        Constructor for FileHandler Object. Sets FileHandler.input_directory.

        Parameters
        ----------
        directory : pathlib.Path | None | (str)
            When directory is None the constructor will attempt to read directory location from
                environment variable EBM_INPUT_DIRECTORY
        """
        if directory is None:
            # Use 'input' as fall back when EBM_INPUT_DIRECTORY is not set in environment.
            directory = os.environ.get('EBM_INPUT_DIRECTORY', 'input')

        self.input_directory = directory if isinstance(directory, pathlib.Path) else pathlib.Path(directory)
        self.files_to_check = [self.ELHUB_DATA, self.DH_DATA, self.BIO_DATA]

    def __repr__(self):
        return f'FileHandler(input_directory="{self.input_directory}")'

    def __str__(self):
        return repr(self)

    @staticmethod
    def default_data_directory() -> pathlib.Path:
        """
        Returns the path for GD default data. The function is used when content is needed for a new input directory.
        Not to be confused with FileHandler.input_directory.

        Returns
        -------
        pathlib.Path

        See Also
        --------
        create_missing_input_files
        """
        return pathlib.Path(__file__).parent / 'data'

    def get_file(self, file_name: str) -> pl.DataFrame:
        """
        Finds and returns a file by searching in the folder defined by self.input_folder.

        Parameters:
        - file_name (str): Name of the file to retrieve.

        Returns:
        - file_df (pd.DataFrame): DataFrame containing file data.
        """
        logger.debug(f'get_file {file_name}')
        file_path: pathlib.Path = pathlib.Path(self.input_directory) / file_name
        logger.debug(f'{file_path=}')

        try:
            if file_path.suffix == '.parquet':
                file_df = pl.read_parquet(file_path)
            elif file_path.suffix in ['.xlsx', '.xls']:
                file_df = pl.read_excel(file_path)
            else:
                msg = f'{file_name} is not of type xlsx or parquet.'
                logger.error(msg)
                raise ValueError(msg)
            return file_df
        except FileNotFoundError as ex:
            logger.exception(ex)
            logger.debug(f'Current directory is {os.getcwd()}')
            logger.error(f'Unable to open {file_path}. File not found.')
            raise
        except PermissionError as ex:
            logger.exception(ex)
            logger.error(f'Unable to open {file_path}. Permission denied.')
            raise
        except IOError as ex:
            logger.exception(ex)
            logger.error(f'Unable to open {file_path}. Unable to read file.')
            raise
    
    def _check_is_file(self, filename: str) -> bool:
        """
        Check if the filename is a file in self.input_folder

        Parameters
        ----------
        filename : str

        Returns
        -------
        file_exists : bool
        """
        return (pathlib.Path(self.input_directory) / filename).is_file()

    def check_for_missing_files(self) -> typing.List[str]:
        """
        Returns a list of required files that are not present in self.input_folder

        Returns
        -------
        missing_files : List[str]
        """
        missing_files = [file for file in self.files_to_check if not self._check_is_file(file)]
        if missing_files:
            plural = 's' if len(missing_files) != 1 else ''
            msg = f'{len(missing_files)} required file{plural} missing from {self.input_directory}'
            logger.error(msg)
            for f in missing_files:
                logger.error(f'Could not find {f}')
        return missing_files


    def create_missing_input_files(self, source_directory: (pathlib.Path | None)=None) -> None:
        """
        Creates any input files missing in self.input_directory. When source is omitted FileHandler

        Parameters
        ----------
        source_directory : pathlib.Path, optional
                           Optional directory for sourcing files to copy.

        Returns
        -------
        None

        See Also
        --------
        default_data_directory : default source for data files
        """
        source = FileHandler.default_data_directory() if not source_directory else source_directory
    
        if not source.is_dir():
            raise NotADirectoryError(f'{self.input_directory} is not a directory')
        if not self.input_directory.is_dir():
            logger.info(f'Creating directory {self.input_directory}')
            self.input_directory.mkdir()
        for file in self.files_to_check:
            logger.debug(f'Create input file {file}')
            self.create_input_file(file, source_directory=source)

    def create_input_file(self, file, source_directory=None):
        source_directory = FileHandler.default_data_directory() if not source_directory else source_directory

        source_file = source_directory / file
        target_file = self.input_directory / file
        if target_file.is_file():
            logger.debug(f'Skipping existing file {target_file}')
        elif not source_file.is_file():
            logger.error(f'Source file {source_file} does not exist!')
        else:
            shutil.copy(source_file, target_file)
            logger.info( f'Creating missing file  {target_file}')

    