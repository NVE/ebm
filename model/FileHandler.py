import os
import pandas as pd

class FileHandler():
    """
    Handles file operations.
    """
    #TODO: Add input validtion (loguru)

    # Filenames
    BUILDING_TYPES = 'building_types.xlsx'
    RENOVATION_TYPES = 'renovation_types.xlsx'
    TEK_ID = 'TEK_ID.xlsx'
    TEK_PARAMS = 'TEK_parameters.xlsx'
    S_CURVES = 's_curves.xlsx'

    def __init__(self):
        
        self.input_folder = 'input'

    def get_file(self, file_name):
        """
        Finds and returns a file by searching in the folder defined by self.input_folder.

        Parameters:
        - file_name (str): Name of the file to retrieve.

        Returns:
        - file_df (pd.DataFrame): DataFrame containing file data.
        """
        file_path = os.path.join(self.input_folder, file_name)
        if file_path.endswith('.xlsx'):
            file_df = pd.read_excel(file_path)

        return file_df

    def get_building_types(self):
        """
        Get building types DataFrame.

        Returns:
        - building_types (pd.DataFrame): DataFrame containing building types.
        """
        building_types = self.get_file(self.BUILDING_TYPES)
        return building_types

    def get_renovation_types(self):
        """
        Get renovation types DataFrame.

        Returns:
        - renovation_types (pd.DataFrame): DataFrame containing renovation types.
        """
        renovation_types = self.get_file(self.RENOVATION_TYPES)
        return renovation_types
    
    def get_tek_id(self):
        """
        Get TEK ID DataFrame.

        Returns:
        - tek_id (pd.DataFrame): DataFrame containing TEK IDs.
        """        
        tek_id = self.get_file(self.TEK_ID)
        return tek_id

    def get_tek_params(self):
        """
        Get TEK parameters DataFrame.

        Returns:
        - tek_params (pd.DataFrame): DataFrame containing TEK parameters.
        """
        tek_params = self.get_file(self.TEK_PARAMS)
        return tek_params
    
    def get_s_curve_params(self):
        """
        Get S-curve parameters DataFrame.

        Returns:
        - s_curve_params (pd.DataFrame): DataFrame containing S-curve parameters.
        """
        s_curve_params = self.get_file(self.S_CURVES)
        return s_curve_params
    



