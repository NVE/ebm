import os
import pandas as pd

class FileHandler():
    """
    Handles file operations.
    """
    #TODO: Add input validtion (loguru)

    # Filenames
    BUILDING_CATEGORIES = 'building_categories.xlsx'
    BUILDING_CONDITIONS = 'building_conditions.xlsx'
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

    def get_building_categories(self):
        """
        Get building categories DataFrame.

        Returns:
        - building_categories (pd.DataFrame): DataFrame containing building categories.
        """
        building_categories = self.get_file(self.BUILDING_CATEGORIES)
        return building_categories

    def get_building_conditions(self):
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
    



