import os
import pathlib

from loguru import logger
import pandas as pd


class FileHandler:
    """
    Handles file operations.
    """

    # Filenames
    BUILDING_CATEGORIES = 'building_categories.csv'
    BUILDING_CONDITIONS = 'building_conditions.csv'
    TEK_ID = 'TEK_ID.csv'
    TEK_PARAMS = 'TEK_parameters.csv'
    SCURVE_PARAMETERS = 'scurve_parameters.csv'
    CONSTRUCTION_POPULATION = 'nybygging_befolkning.csv'
    CONSTRUCTION_BUILDING_CATEGORY_SHARE = 'nybygging_husandeler.csv'
    CONSTRUCTION_BUILDING_CATEGORY_AREA = 'nybygging_ssb_05940_areal.csv'
    AREA_PARAMETERS = 'area_parameters.csv'

    def __init__(self):

        self.input_folder = 'input'

    def get_file(self, file_name: str) -> pd.DataFrame:
        """
        Finds and returns a file by searching in the folder defined by self.input_folder.

        Parameters:
        - file_name (str): Name of the file to retrieve.

        Returns:
        - file_df (pd.DataFrame): DataFrame containing file data.
        """
        logger.debug(f'get_file {file_name}')
        file_path: pathlib.Path = pathlib.Path(self.input_folder) / file_name

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

    def get_building_categories(self) -> pd.DataFrame:
        """
        Get building categories DataFrame.

        Returns:
        - building_categories (pd.DataFrame): DataFrame containing building categories.
        """
        building_categories = self.get_file(self.BUILDING_CATEGORIES)
        return building_categories

    def get_building_conditions(self) -> pd.DataFrame:
        """
        Get building conditions DataFrame.

        Returns:
        - building_conditions (pd.DataFrame): DataFrame containing building conditions.
        """
        building_conditions = self.get_file(self.BUILDING_CONDITIONS)
        return building_conditions
    
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
        return self.get_file(self.CONSTRUCTION_BUILDING_CATEGORY_AREA)

    def get_area_parameters(self) -> pd.DataFrame:
        """
        Get dataframe with area parameters.

        Returns:
        - area_parameters (pd.DataFrame): Dataframe containing total area (m^2) per
                                          building category and TEK.
        """
        return self.get_file(self.AREA_PARAMETERS)





