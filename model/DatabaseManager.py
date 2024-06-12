from FileHandler import *
import pandas as pd

class DatabaseManager():
    """
    Manages database operations.
    """

    # Column names
    COL_BUILDING_TYPE = 'building_type'
    COL_RENOVATION_TYPE = 'renovation_type'
    COL_TEK_ID = 'TEK_ID'
    
    def __init__(self):
        
        self.file_handler = FileHandler()                    

    def get_building_type_list(self):
        """
        Get a list of building types.

        Returns:
        - building_type_list (list): List of building types.
        """
        building_types = self.file_handler.get_building_types()
        building_type_list = building_types[self.COL_BUILDING_TYPE].unique()
        return building_type_list
    
    def get_renovation_type_list(self):
        """
        Get a list of renovation types.

        Returns:
        - renovation_type_list (list): List of renovation types.
        """
        renovation_types = self.file_handler.get_renovation_types()
        renovation_type_list = renovation_types[self.COL_RENOVATION_TYPE].unique()
        return renovation_type_list
    
    def get_tek_id_list(self):
        """
        Get a list of TEK IDs.

        Returns:
        - tek_id_list (list): List of TEK IDs.
        """
        tek_id = self.file_handler.get_tek_id()
        tek_id_list = tek_id[self.COL_TEK_ID].unique()
        return tek_id_list
    
    def get_tek_params(self):
        """
        Get dataframe with all TEK parameters.

        Returns:
        - tek_params (pd.DataFrame): DataFrame with TEK parameters.
        """
        tek_params = self.file_handler.get_tek_params()
        return tek_params
    
    def get_tek_params_per_id(self, tek_id):
        """
        Get dataframe with TEK parameters for a specific TEK ID.

        Parameters:
        - tek_id (str): TEK ID.

        Returns:
        - tek_params_per_id (pd.DataFrame): DataFrame with TEK parameters for the specified TEK ID.
        """
        tek_params = self.file_handler.get_tek_params()
        tek_params_per_id = tek_params[tek_params[self.COL_TEK_ID] == tek_id]

        return tek_params_per_id

    def get_s_curve_params(self):
        """
        Get input dataframe with S-curve parameters/assumptions.

        Returns:
        - s_curve_params (pd.DataFrame): DataFrame with S-curve parameters.
        """
        s_curve_params = self.file_handler.get_s_curve_params()
        return s_curve_params

    def get_s_curve_params_per_building_and_renovation_type(self, building_type, renovation_type):
        """
        Get input dataframe with S-curve parameters/assumptions and filter it by building and renovation type.

        Parameters:
        - building_type (str): Building type.
        - renovation_type (str): Renovation type.

        Returns:
        - s_curve_params_filtered (pd.DataFrame): Filtered DataFrame containing S-curve parameters.
        """
        s_curve_params = self.file_handler.get_s_curve_params()
        s_curve_params_filtered = s_curve_params[(s_curve_params[self.COL_BUILDING_TYPE] == building_type) & (s_curve_params[self.COL_RENOVATION_TYPE] == renovation_type)]
        return s_curve_params_filtered
    