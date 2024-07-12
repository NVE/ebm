import typing
import pandas as pd

class Area():

    COL_BUILDING_CATEGORY = 'building_category'
    COL_TEK = 'TEK'
    COL_AREA = 'area'

    def __init__(self, area_params: pd.DataFrame) -> None:
        
        self.area_params = area_params

    def get_area_per_building_category_tek(self, building_category: str, tek: str) -> int:
        """
        Retrieves the total area (m^2) of specific building category and TEK.

        This method filters the DataFrame `area_params` using the provided `building_category` and `tek`.
        It assumes that the filtered DataFrame will contain only one row. The area value from this row,
        in the column specified by `COL_AREA`, is then retrieved and returned.
        
        Parameters:
        - building_category (str): The building category to filter on.
        - tek (str): The TEK value to filter on.

        Returns:
        - area_value (int): The area value for the specified building category and TEK.
        """
        # Check if the building category is in the DataFrame
        if building_category not in self.area_params[self.COL_BUILDING_CATEGORY].values:
            raise ValueError(f"Building category '{building_category}' not found in the DataFrame.")
        
        # Filter dataframe on building category
        filtered_area_params = self.area_params[self.area_params[self.COL_BUILDING_CATEGORY] == building_category]

        # Check if the tek is in the DataFrame
        if tek not in filtered_area_params[self.COL_TEK].values:
            raise ValueError(f"'{tek}' not found in the DataFrame.")
        
        # Filter dataframe on building category and tek
        filtered_area_params = filtered_area_params[filtered_area_params[self.COL_TEK] == tek]
        
        # Retrieve the are value, assuming there is only one row in the filtered DataFrame
        area_value = filtered_area_params.iloc[0][self.COL_AREA]
        return area_value