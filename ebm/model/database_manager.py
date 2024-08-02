import typing

from loguru import logger
import pandas as pd

from .building_category import BuildingCategory
from .demolition import demolition_by_year_all
from .file_handler import FileHandler
from .data_classes import TEKParameters

# TODO:
# - add method to change all strings to lower case and underscore instead of space

class DatabaseManager():
    """
    Manages database operations.
    """

    # Column names
    COL_TEK = 'TEK'
    COL_TEK_BUILDING_YEAR = 'building_year'
    COL_TEK_START_YEAR = 'period_start_year'
    COL_TEK_END_YEAR = 'period_end_year'
    COL_BUILDING_CATEGORY = 'building_category'
    COL_BUILDING_CONDITION = 'condition'
    
    def __init__(self):
        self.file_handler = FileHandler()

    def get_building_category_list(self):
        """
        Get a list of building categories.

        Returns:
        - building_category_list (list): List of building categories.
        """
        building_categories = self.file_handler.get_building_categories()
        building_category_list = building_categories[self.COL_BUILDING_CATEGORY].unique()
        return building_category_list

    def get_condition_list(self):
        """
        Get a list of building conditions.

        Returns:
        - condition_list (list): List of building conditions.
        """
        building_conditions = self.file_handler.get_building_conditions()
        condition_list = building_conditions[self.COL_BUILDING_CONDITION].unique()
        return condition_list
    
    def get_tek_list(self):
        """
        Get a list of TEK IDs.

        Returns:
        - tek_list (list): List of TEK IDs.
        """
        tek_id = self.file_handler.get_tek_id()
        tek_list = tek_id[self.COL_TEK].unique()
        return tek_list
    
    def get_tek_params(self, tek_list: typing.List[str]):
        """
        Retrieve TEK parameters for a list of TEK IDs.

        This method fetches TEK parameters for each TEK ID in the provided list,
        converts the relevant data to a dictionary, and maps these values to the 
        corresponding attributes of the TEKParameters dataclass. The resulting 
        dataclass instances are stored in a dictionary with TEK IDs as keys.

        Parameters:
        - tek_list (list of str): List of TEK IDs.

        Returns:
        - tek_params (dict): Dictionary where each key is a TEK ID and each value 
                            is a TEKParameters dataclass instance containing the 
                            parameters for that TEK ID.
        """
        tek_params = {}
        tek_params_df = self.file_handler.get_tek_params()

        for tek in tek_list:
            # Filter on TEK ID
            tek_params_filtered = tek_params_df[tek_params_df[self.COL_TEK] == tek]

            # Assuming there is only one row in the filtered DataFrame
            tek_params_row = tek_params_filtered.iloc[0]

            # Convert the single row to a dictionary
            tek_params_dict = tek_params_row.to_dict()

            # Map the dictionary values to the dataclass attributes
            tek_params_per_id = TEKParameters(
                tek = tek_params_dict[self.COL_TEK],
                building_year = tek_params_dict[self.COL_TEK_BUILDING_YEAR],
                start_year = tek_params_dict[self.COL_TEK_START_YEAR],
                end_year = tek_params_dict[self.COL_TEK_END_YEAR],
                )

            tek_params[tek] = tek_params_per_id    

        return tek_params

    def get_scurve_params(self):
        """
        Get input dataframe with S-curve parameters/assumptions.

        Returns:
        - scurve_params (pd.DataFrame): DataFrame with S-curve parameters.
        """
        scurve_params = self.file_handler.get_scurve_params()
        return scurve_params

    def get_construction_population(self) -> pd.DataFrame:
        """
        Get construction population DataFrame.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          year population household_size
        """
        new_buildings_population = self.file_handler.get_construction_population()
        new_buildings_population["household_size"] = new_buildings_population['household_size'].astype('float64')
        new_buildings_population = new_buildings_population.set_index('year')
        return new_buildings_population

    def get_new_buildings_category_share(self) -> pd.DataFrame:
        """
        Get building category share by year as a DataFrame.

        The number can be used in conjunction with number of households to calculate total number
        of buildings of category house and apartment block

        Returns:
        - new_buildings_category_share (pd.DataFrame): Dataframe containing population numbers
          "year", "Andel nye småhus", "Andel nye leiligheter", "Areal nye småhus", "Areal nye leiligheter"
        """
        df = self.file_handler.get_construction_building_category_share()
        df['new_house_share'] = df['new_house_share'].astype('float64')
        df['new_apartment_block_share'] = df['new_apartment_block_share'].astype('float64')

        return df.set_index('year')

    def get_building_category_floor_area(self) -> pd.DataFrame:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """

        df = self.file_handler.get_building_category_area()
        types = df['type_of_building'].apply(lambda r: pd.Series(r.split(' ', 1)))
        df[['type_no', 'typename']] = types

        df = df.drop(columns=['type_of_building', 'area'])
        return df

    def get_area_parameters(self) -> pd.DataFrame:
        """
        Get total area (m^2) per building category and TEK.

        Parameters:
        - building_category (str): Optional parameter that filter the returned dataframe by building_category

        Returns:
        - area_parameters (pd.DataFrame): Dataframe containing total area (m^2) per
                                          building category and TEK.
        """
        area_params = self.file_handler.get_area_parameters()
        return area_params

    def load_demolition_floor_area_from_spreadsheet(self, building_category: BuildingCategory) -> pd.Series:
        logger.debug(f'Loading static demolished floor area for "{building_category}"')
        if building_category.name.lower() not in demolition_by_year_all.keys():
            ValueError(f'No such building_category "{building_category}" in demolition.demolition_by_year_all')
        demolition = pd.Series(demolition_by_year_all.get(building_category.name.lower()), index=range(2010, 2051))

        return demolition