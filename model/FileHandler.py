import os
import pandas as pd

class FileHandler():

    #TODO: Add input validtion (loguru)

    # Filenames
    BUILDING_TYPES = 'building_types.xlsx'
    RENOVATION_TYPES = 'renovation_types.xlsx'
    S_CURVES = 's_curves.xlsx'

    def __init__(self):
        
        self.input_folder = 'input'

    def get_file(self, file_name):
        """
        Finds and returns a file, by searching in the folder defined by the instance variable self.input_folder.
        
        Parameters:
            - filename: str
        
        Returns:
            - file_df: Pandas dataframe
        """
        file_path = os.path.join(self.input_folder, file_name)
        if file_path.endswith('.xlsx'):
            file_df = pd.read_excel(file_path)

        return file_df

    def get_building_types(self):
        building_types = self.get_file(self.BUILDING_TYPES)
        return building_types

    def get_renovation_types(self):
        renovation_types = self.get_file(self.RENOVATION_TYPES)
        return renovation_types
    
    def get_s_curve_params(self):
        s_curve_params = self.get_file(self.S_CURVES)
        return s_curve_params
    



