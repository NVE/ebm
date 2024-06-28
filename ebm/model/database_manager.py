from .file_handler import FileHandler
import pandas as pd

class DatabaseManager():
    """
    Manages database operations.
    """

    # Column names
    COL_BUILDING_CATEGORY = 'building_category'
    COL_BUILDING_CONDITION = 'condition'
    COL_TEK_ID = 'TEK_ID'
    
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

    def get_s_curve_params_per_building_category_and_condition(self, building_category, condition):
        """
        Get input dataframe with S-curve parameters/assumptions and filter it by building category and condition.

        Parameters:
        - building_category (str): Building category.
        - condition (str): Building condition.

        Returns:
        - s_curve_params_dict (dict): Dictionary containing S-curve parameters with column names as keys and 
                                      corresponding column values as values.
        """
        # Retrieve input data and filter on building category and condition
        s_curve_params = self.file_handler.get_s_curve_params()
        s_curve_params_filtered = s_curve_params[(s_curve_params[self.COL_BUILDING_CATEGORY] == building_category) & (s_curve_params[self.COL_BUILDING_CONDITION] == condition)]

        # Assuming there is only one row in the filtered DataFrame
        s_curve_params_row = s_curve_params_filtered.iloc[0]

        # Convert the single row to a dictionary
        s_curve_params_dict = s_curve_params_row.to_dict()

        return s_curve_params_dict

