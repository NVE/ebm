import os
import pathlib
import shutil
import typing

import pandas as pd
from loguru import logger


class FileHandler:
    """
    Handles file operations.
    """
    # Filenames
    BUILDING_CONDITIONS = 'building_conditions.csv'
    TEK_ID = 'TEK_ID.csv'
    TEK_PARAMS = 'TEK_parameters.csv'
    SCURVE_PARAMETERS = 'scurve_parameters.csv'
    CONSTRUCTION_POPULATION = 'new_buildings_population.csv'
    CONSTRUCTION_BUILDING_CATEGORY_SHARE = 'new_buildings_house_share.csv'
    CONSTRUCTION_BUILDING_CATEGORY_AREA = 'construction_building_category_yearly.csv'
    AREA_PARAMETERS = 'area_parameters.csv'

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
        self.files_to_check = [self.TEK_ID, self.TEK_PARAMS, self.SCURVE_PARAMETERS, self.CONSTRUCTION_POPULATION,
                               self.CONSTRUCTION_BUILDING_CATEGORY_SHARE, self.CONSTRUCTION_BUILDING_CATEGORY_AREA,
                               self.AREA_PARAMETERS]

    def get_file(self, file_name: str) -> pd.DataFrame:
        """
        Finds and returns a file by searching in the folder defined by self.input_folder.

        Parameters:
        - file_name (str): Name of the file to retrieve.

        Returns:
        - file_df (pd.DataFrame): DataFrame containing file data.
        """
        logger.debug(f'get_file {file_name}')
        file_path: pathlib.Path = pathlib.Path(self.input_directory) / file_name

        try:
            if file_path.suffix == '.xlsx':
                file_df = pd.read_excel(file_path)
            elif file_path.suffix == '.csv':
                file_df = pd.read_csv(file_path)
            else:
                msg = f'{file_name} is not of type xlsx or csv'
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

    def get_tek_id(self):
        """
        Get TEK ID DataFrame.

        Returns:
        - tek_id (pd.DataFrame): DataFrame containing TEK IDs.
        """        
        tek_id = self.get_file(self.TEK_ID)
        return tek_id

    def get_tek_params(self) -> pd.DataFrame:
        """
        Get TEK parameters DataFrame.

        Returns:
        - tek_params (pd.DataFrame): DataFrame containing TEK parameters.
        """
        tek_params = self.get_file(self.TEK_PARAMS)
        return tek_params
    
    def get_scurve_params(self) -> pd.DataFrame:
        """
        Get S-curve parameters DataFrame.

        Returns:
        - scurve_params (pd.DataFrame): DataFrame containing S-curve parameters.
        """
        scurve_params = self.get_file(self.SCURVE_PARAMETERS)
        return scurve_params

    def get_construction_population(self) -> pd.DataFrame:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          year population household_size
        """
        return self.get_file(self.CONSTRUCTION_POPULATION)

    def get_construction_building_category_share(self) -> pd.DataFrame:
        """
        Get building category share by year DataFrame from a file.

        The number can be used in conjunction with number of households to calculate total number
        of buildings of category house and apartment block

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "year", "Andel nye småhus", "Andel nye leiligheter", "Areal nye småhus", "Areal nye leiligheter"
        """
        return self.get_file(self.CONSTRUCTION_BUILDING_CATEGORY_SHARE)

    def get_building_category_area(self) -> pd.DataFrame:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """
        return pd.read_csv(self.input_directory / self.CONSTRUCTION_BUILDING_CATEGORY_AREA,
                           index_col=0, header=0)

    def get_area_parameters(self) -> pd.DataFrame:
        """
        Get dataframe with area parameters.

        Returns:
        - area_parameters (pd.DataFrame): Dataframe containing total area (m^2) per
                                          building category and TEK.
        """
        return self.get_file(self.AREA_PARAMETERS)

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

    def create_missing_input_files(self) -> None:
        """
        Creates any input files missing in self.input_directory

        Returns
        -------
        None
        """

        if self.input_directory.is_file():
            raise NotADirectoryError(f'{self.input_directory} is a file')
        if not self.input_directory.is_dir():
            logger.debug(f'{self.input_directory} is not a directory')
            self.input_directory.mkdir()
        for file in self.files_to_check:
            logger.debug(f'Create input file {file}')
            target_file = self.input_directory / file
            source_file = pathlib.Path(__file__).parent.parent / 'data' / file
            if target_file.is_file():
                logger.warning(f'Skipping existing file {target_file}')
                continue
            if not source_file.is_file():
                logger.error(f'Source file {source_file} does not exist!')
                continue
            shutil.copy(source_file, target_file)
            logger.info(f'Created {target_file}')
