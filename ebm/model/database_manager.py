import typing

import pandas as pd

from ebm.model.file_handler import FileHandler
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.data_classes import TEKParameters


# TODO:
# - add method to change all strings to lower case and underscore instead of space
# - change column strings used in methods to constants 

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
    COL_BUILDING_CONDITION = 'building_condition'
    COL_AREA = 'area'
    COL_ENERGY_REQUIREMENT_PURPOSE = 'purpose'
    COL_ENERGY_REQUIREMENT_VALUE = 'kw_h_m'
    COL_HEATING_REDUCTION = 'heating_reduction'

    def __init__(self, file_handler: FileHandler = None):
        # Create default FileHandler if file_hander is None
        self.file_handler = file_handler if file_handler is not None else FileHandler()
    
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
        df['year'] = df['year'].astype(int)
        df = df.set_index('year')
        return df

    def get_building_category_floor_area(self, building_category: BuildingCategory) -> pd.Series:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """
        df = self.file_handler.get_building_category_area()

        building_category_floor_area = df[building_category].dropna()

        return building_category_floor_area

    #TODO: remove after refactoring
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
    
    def get_area_start_year(self) -> typing.Dict[BuildingCategory, pd.Series]:
        """
        Retrieve total floor area in the model start year for each TEK within a building category.

        Returns
        -------
        dict
            A dictionary where:
            - keys are `BuildingCategory` objects derived from the building category string.
            - values are `pandas.Series` with the 'tek' column as the index and the corresponding
              'area' column as the values.
        """
        area_data = self.file_handler.get_area_parameters()
        
        area_dict = {}
        for building_category in area_data[self.COL_BUILDING_CATEGORY].unique():
            area_building_category = area_data[area_data[self.COL_BUILDING_CATEGORY] == building_category]
            area_series = area_building_category.set_index(self.COL_TEK)[self.COL_AREA]
            area_series.index.name = "tek"
            area_series.rename(f"{BuildingCategory.from_string(building_category)}_area", inplace=True)
            
            area_dict[BuildingCategory.from_string(building_category)] = area_series

        return area_dict
    
    #TODO: evaluate method based on further use in calculations + add docstrings
    def get_energy_by_floor_area(self) -> typing.Dict[BuildingCategory, typing.Dict[EnergyPurpose, typing.Dict[str, float]]]: 
        """
        """
        df = self.file_handler.get_energy_by_floor_area()

        energy_req = {}
        for building_category in df[self.COL_BUILDING_CATEGORY].unique():
            df_building_category = df[df[self.COL_BUILDING_CATEGORY] == building_category]
            purpose_dict = {}
            for purpose in df_building_category[self.COL_ENERGY_REQUIREMENT_PURPOSE]:
                df_purpose = df_building_category[df_building_category[self.COL_ENERGY_REQUIREMENT_PURPOSE] == purpose]
                tek_dict = {}
                for tek in df_purpose[self.COL_TEK].unique():
                    df_tek = df_purpose[df_purpose[self.COL_TEK] == tek]
                    energy_req_val = float(df_tek.iloc[0][self.COL_ENERGY_REQUIREMENT_VALUE])
                    tek_dict[tek] = energy_req_val
                purpose_dict[EnergyPurpose(purpose)] = tek_dict
            energy_req[BuildingCategory.from_string(building_category)] = purpose_dict 
        
        return energy_req

    #TODO: evaluate method based on further use in calculations + add docstrings
    def get_heating_reduction(self) -> typing.Dict[str, typing.Dict[BuildingCondition, float]]:
        """
        """
        df = self.file_handler.get_heating_reduction()
        
        heating_red = {}
        for tek in df[self.COL_TEK].unique():
            df_tek = df[df[self.COL_TEK] == tek]
            heating_red_condition = {}
            for condition in df_tek[self.COL_BUILDING_CONDITION].unique():
                df_condition = df_tek[df_tek[self.COL_BUILDING_CONDITION] == condition]
                heating_red_val = float(df_condition.iloc[0][self.COL_HEATING_REDUCTION])
                heating_red_condition[BuildingCondition(condition)] = heating_red_val
            heating_red[tek] = heating_red_condition
        
        return heating_red

    def validate_database(self):
        missing_files = self.file_handler.check_for_missing_files()
        return True
    
if __name__ == '__main__':
    db = DatabaseManager()
    a = db.get_energy_by_floor_area()
    #a = db.get_heating_reduction()
    print(a)