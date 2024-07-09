
import typing

import pandas as pd

from .file_handler import FileHandler
from .data_classes import ScurveParameters, TEKParameters


class DatabaseManager():
    """
    Manages database operations.
    """

    # TODO:
    # - change all strings to lower case and underscore instead of space

    # Column names
    COL_TEK = 'TEK'
    COL_TEK_BUILDING_YEAR = 'building_year'
    COL_TEK_START_YEAR = 'period_start_year'
    COL_TEK_END_YEAR = 'period_end_year'
    COL_BUILDING_CATEGORY = 'building_category'
    COL_BUILDING_CONDITION = 'condition'
    COL_EARLIEST_AGE = 'earliest_age_for_measure'
    COL_AVERAGE_AGE = 'average_age_for_measure'
    COL_LAST_AGE = 'last_age_for_measure'
    COL_RUSH_YEARS = 'rush_period_years'
    COL_RUSH_SHARE = 'rush_share'
    COL_NEVER_SHARE = 'never_share'
    
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

    def get_scurve_params_per_building_category(self, building_category: str,
                                                              condition_list: typing.List[str]) -> ScurveParameters:
        """
        Get S-curve parameters for a given building category and list of conditions.

        This method retrieves S-curve parameters from a data source, filters them by the specified
        building category and conditions, and converts them into a dictionary of `ScurveParameters` 
        dataclass instances.

        Parameters:
        - building_category (str): building category
        - condition_list (List[str]): list of building conditions 

        Returns:
        - scurve_params (dict): A dictionary where the keys are the conditions (str) and the values are 
                                `ScurveParameters` dataclass instances containing the S-curve parameters.
        """
        scurve_params = {}
        scurve_params_df = self.file_handler.get_scurve_params()

        for condition in condition_list:

            # Filter dataframe on building category and condition
            scurve_params_filtered = scurve_params_df[(scurve_params_df[self.COL_BUILDING_CATEGORY] == building_category) & (scurve_params_df[self.COL_BUILDING_CONDITION] == condition)]

            # Assuming there is only one row in the filtered DataFrame
            scurve_params_row = scurve_params_filtered.iloc[0]

            # Convert the single row to a dictionary
            scurve_params_dict = scurve_params_row.to_dict()
            
            # Map the dictionary values to the dataclass attributes
            scurve_parameters = ScurveParameters(
                building_category=scurve_params_dict[self.COL_BUILDING_CATEGORY],
                condition=scurve_params_dict[self.COL_BUILDING_CONDITION],
                earliest_age=scurve_params_dict[self.COL_EARLIEST_AGE],
                average_age=scurve_params_dict[self.COL_AVERAGE_AGE], 
                rush_years=scurve_params_dict[self.COL_RUSH_YEARS], 
                last_age=scurve_params_dict[self.COL_LAST_AGE],
                rush_share=scurve_params_dict[self.COL_RUSH_SHARE],
                never_share=scurve_params_dict[self.COL_NEVER_SHARE],
            )

            scurve_params[condition] = scurve_parameters

        return scurve_params 

    def get_construction_population(self) -> pd.DataFrame:
        """
        Get construction population DataFrame.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          year population household_size
        """
        return self.file_handler.get_construction_population()

    def get_construction_building_category_share(self) -> pd.DataFrame:
        """
        Get building category share by year DataFrame from a file.

        The number can be used in conjunction with number of households to calculate total number
        of buildings of category house and apartment block

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "year", "Andel nye småhus", "Andel nye leiligheter", "Areal nye småhus", "Areal nye leiligheter"
        """
        return self.file_handler.get_construction_building_category_share()

    def get_building_category_area(self) -> pd.DataFrame:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """
        return self.file_handler.get_building_category_area()

    def get_building_category_area_by_tek(self, building_category=None) -> pd.DataFrame:
        """
        Get total area of building_category by TEK.

        Parameters:
        - building_category (str): optional parameter that filter the returned dataframe by building_category

        Returns:
        - building_category_area_by_tek (pd.DataFrame): Dataframe containing area numbers
          "building_category","TEK","area"
        """

        df = self.file_handler.get_building_category_area_by_tek()
        df.loc[df.TEK == '-> TEK49', 'TEK'] = 'PRE_TEK49'
        if building_category:
            return df[df.building_category == building_category]
        return df

