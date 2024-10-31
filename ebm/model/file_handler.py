import os
import pathlib
import shutil
import typing

import pandas as pd
from loguru import logger
from pandera.errors import SchemaErrors, SchemaError

import ebm.validators as validators


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
    ENERGY_REQ_ORIGINAL_CONDITION = 'energy_requirement_original_condition.csv'
    ENERGY_REQ_REDUCTION_CONDITION = 'energy_requirement_reduction_per_condition.csv'
    ENERGY_REQ_YEARLY_IMPROVEMENTS = 'energy_requirement_yearly_improvements.csv'
    ENERGY_REQ_POLICY_IMPROVEMENTS = 'energy_requirement_policy_improvements.csv'
    TEKANDELER = 'tekandeler.csv'

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
                               self.AREA_PARAMETERS, self.ENERGY_REQ_ORIGINAL_CONDITION, self.ENERGY_REQ_REDUCTION_CONDITION, 
                               self.ENERGY_REQ_YEARLY_IMPROVEMENTS, self.ENERGY_REQ_POLICY_IMPROVEMENTS, self.TEKANDELER]

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
        logger.debug(f'{file_path=}')

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

    def get_population(self) -> pd.DataFrame:
        """
        Loads population data from new_buildings_population.csv as float64

        Should probably be merged with get_construction_population

        Returns population : pd.DataFrame
            dataframe with population
        -------

        """
        file_path = self.input_directory / self.CONSTRUCTION_POPULATION
        logger.debug(f'{file_path=}')
        return pd.read_csv(file_path, dtype={"household_size": "float64"})

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
        file_path = self.input_directory / self.CONSTRUCTION_BUILDING_CATEGORY_AREA
        logger.debug(f'{file_path=}')
        return pd.read_csv(file_path,
                           index_col=0, header=0)

    def get_area_parameters(self) -> pd.DataFrame:
        """
        Get dataframe with area parameters.

        Returns:
        - area_parameters (pd.DataFrame): Dataframe containing total area (m^2) per
                                          building category and TEK.
        """
        return self.get_file(self.AREA_PARAMETERS)
    
    def get_energy_req_original_condition(self) -> pd.DataFrame:
        """
        Get dataframe with energy requirement (kWh/m^2) for floor area in original condition.

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement (kWh/m^2) for floor area in original condition,
            per building category and purpose.
        """
        return self.get_file(self.ENERGY_REQ_ORIGINAL_CONDITION)
    
    def get_energy_req_reduction_per_condition(self) -> pd.DataFrame:
        """
        Get dataframe with shares for reducing the energy requirement of the different building conditions.

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement reduction shares for the different building conditions, 
            per building category, TEK and purpose.
        """
        return self.get_file(self.ENERGY_REQ_REDUCTION_CONDITION)
    
    def get_energy_req_yearly_improvements(self) -> pd.DataFrame:
        """
        Get dataframe with yearly efficiency rates for energy requirement improvements.

        Returns
        -------
        pd.DataFrame
            Dataframe containing yearly efficiency rates (%) for energy requirement improvements,
            per building category, tek and purpose.
        """
        return self.get_file(self.ENERGY_REQ_YEARLY_IMPROVEMENTS)
    
    def get_energy_req_policy_improvements(self) -> pd.DataFrame:
        """
        Get dataframe with total energy requirement improvement in a period related to a policy.

        Returns
        -------
        pd.DataFrame
            Dataframe containing total energy requirement improvement (%) in a policy period,
            per building category, tek and purpose.
        """
        return self.get_file(self.ENERGY_REQ_POLICY_IMPROVEMENTS)

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
            logger.debug(f'Creating directory: {self.input_directory}')
            self.input_directory.mkdir()
        for file in self.files_to_check:
            logger.debug(f'Create input file {file}')
            self.create_input_file(file)

    def create_input_file(self, file):
        target_file = self.input_directory / file
        source_file = pathlib.Path(__file__).parent.parent / 'data' / file
        if target_file.is_file():
            logger.warning(f'Skipping existing file {target_file}')
        elif not source_file.is_file():
            logger.error(f'Source file {source_file} does not exist!')
        else:
            shutil.copy(source_file, target_file)
            logger.info(f'Created {target_file}')

    def validate_input_files(self):
        """
        Validates the input files for correct formatting.

        Raises
        ------
        pa.errors.SchemaErrors
            If any invalid data for formatting is found when validating files. The validation is lazy, meaning
            multiple errors may be listed in the exception.
        """
        for file_to_validate in self.files_to_check:
            if file_to_validate == 'TEK_ID.csv':
                # No validator for tek_id exists. Fix this later.
                continue
            df = self.get_file(file_to_validate)
            validator = getattr(validators, file_to_validate[:-4].lower())
            try:
                validator.validate(df, lazy=True)
            except (SchemaErrors, SchemaError):
                logger.error(f'Got error while validating {file_to_validate}')
                raise

    def make_output_directory(self, output_directory: pathlib.Path) -> None:
        """
        Creates the output directory if it does not exist.

        Parameters
        ----------
        output_directory : pathlib.Path
            The path to the output directory.
        Raises
        -------
        IOError
            The output_directory exists, but it is a file.
        Returns
        -------
        None
        """
        if output_directory.is_file():
            raise IOError(f'{output_directory} is a file')
        if not output_directory.is_dir():
            logger.debug(f'Creating output directory {output_directory}')
            output_directory.mkdir()
