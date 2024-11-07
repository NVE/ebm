import typing

import pandas as pd
from loguru import logger

from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import TEKParameters


class FilterTek:
    """
    Utility class for filtering TEK lists and parameters. 
    """

    CATEGORY_APARTMENT = 'apartment_block'
    CATEGORY_HOUSE = 'house'
    COMMERCIAL_BUILDING = 'COM'
    RESIDENTIAL_BUILDING = 'RES'
    PRE_TEK49_APARTMENT = 'PRE_TEK49_RES_1950'
    PRE_TEK49_HOUSE = 'PRE_TEK49_RES_1940'

    @staticmethod
    def get_filtered_list(building_category: BuildingCategory, tek_list: typing.List[str]) -> typing.List[str]:
        """
        Filters the provided TEK list based on the building category.

        Parameters:
        - building_category (BuildingCategory): The category of the building.
        - tek_list (List[str]): List of TEK strings to be filtered.

        Returns:
        - filtered_tek_list (List[str]): Filtered list of TEK strings.
        """
        residential_building_list = [FilterTek.CATEGORY_APARTMENT, FilterTek.CATEGORY_HOUSE]
        
        if building_category in residential_building_list:
            # Filter out all TEKs associated with commercial buildings
            filtered_tek_list = [tek for tek in tek_list if FilterTek.COMMERCIAL_BUILDING not in tek]

            # Further filtering based on the specific residential building category
            if building_category == FilterTek.CATEGORY_APARTMENT:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != FilterTek.PRE_TEK49_HOUSE]
            elif building_category == FilterTek.CATEGORY_HOUSE:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != FilterTek.PRE_TEK49_APARTMENT]

        else:
            # Filter out all TEKs associated with residential buildings
            filtered_tek_list = [tek for tek in tek_list if FilterTek.RESIDENTIAL_BUILDING not in tek]

        return filtered_tek_list
    
    # This method is only needed if tek_params are initialized in the Buildings class
    @staticmethod
    def get_filtered_params(tek_list: typing.List[str],
                            tek_params: typing.Dict[str, TEKParameters]) -> typing.Dict[str, TEKParameters]:
        """
        Filters the TEK parameters to include only those relevant to the provided TEK list.

        This method takes a dictionary of TEK parameters and filters it to include only 
        the parameters for TEKs that are present in the `tek_list`. This ensures that 
        only the relevant TEK parameters are retained for use in subsequent calculations.

        Parameters:
        - tek_list (List[str]): A list of TEK identifiers to filter by.
        - tek_params (Dict[str, TEKParameters]): A dictionary where the keys are TEK identifiers 
                                                    and the values are TEKParameters objects containing
                                                    the parameters for each TEK.

        Returns:
        - filtered_tek_params (Dict[str, TEKParameters]): A dictionary containing only the TEK parameters
                                                        for the TEKs present in the `tek_list`.
        """
        filtered_tek_params = {}
        for tek in tek_list:
            filtered_tek_params[tek] = tek_params[tek]    

        return filtered_tek_params

    @staticmethod
    def merge_tek(df: pd.DataFrame,
                  new_tek_name: str,
                  old_tek_names: typing.List[str],
                  aggregates: typing.Dict[str, str] = None) -> pd.DataFrame:
        """
        Merge rows in a DataFrame based on specified 'tek' names and aggregate their values.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame with a MultiIndex.
        new_tek_name : str
            The new 'tek' name to assign to the merged rows.
        old_tek_names : typing.List[str]
            A list of 'tek' names to be merged.
        aggregates : typing.Dict[str, str], optional
            A dictionary specifying the aggregation functions for each column.
            If not provided, default aggregations will be used:
            {'tek': 'max', 'm2': 'first', 'kwh_m2': 'mean', 'energy_requirement': 'sum'}.

        Returns
        -------
        pd.DataFrame
            The DataFrame with the specified 'tek' rows merged and aggregated.
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("`df` should be a pandas DataFrame.")
        if not isinstance(old_tek_names, list):
            raise ValueError("`old_tek_names` should be a list of strings.")

        # Apply default aggregates if the parameter is empty
        aggregates = aggregates or {'TEK': 'max', 'm2': 'first', 'kwh_m2': 'mean', 'energy_requirement': 'sum'}
        tek_values = [tek for tek in old_tek_names if tek in df.index.get_level_values('TEK')]

        if not tek_values:
            return df

        level_values = df.index.get_level_values('building_category')
        building_categories = [bc for bc in BuildingCategory if bc.is_residential() and bc in level_values]
        if not building_categories:
            return df

        residential = df.loc[
                (building_categories, slice(None), slice(None), slice(None), slice(None))].reset_index()

        tek_to_merge = residential[residential.TEK.isin(tek_values)]
        agg_tek = tek_to_merge.groupby(by=['building_category',
                                           'building_condition',
                                           'purpose',
                                           'year']).agg(aggregates)
        agg_tek = agg_tek.reset_index()

        agg_tek['TEK'] = new_tek_name
        rows_to_remove = df.loc[(slice(None), tek_values, slice(None), slice(None), slice(None))].index
        df = df.drop(rows_to_remove)
        df = pd.concat([df, agg_tek.set_index(['building_category', 'TEK', 'building_condition',  'year', 'purpose'])])
        df = df.sort_index()

        return df

    @staticmethod
    def remove_tek_suffix(df: pd.DataFrame, suffix) -> pd.DataFrame:
        # Convert MultiIndex to DataFrame
        index_df = df.index.to_frame(index=False)

        key_name = 'tek' if 'tek' in index_df.keys() else 'TEK'
        # Remove '_RES' from 'tek' values
        index_df[key_name] = index_df[key_name].str.replace(suffix, '')

        # Set the modified DataFrame back to MultiIndex
        df.index = pd.MultiIndex.from_frame(index_df)

        return df
