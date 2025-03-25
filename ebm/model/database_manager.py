import itertools
import logging
import typing

import pandas as pd

from ebm.energy_consumption import calibrate_heating_systems
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.file_handler import FileHandler
from ebm.model.building_category import BuildingCategory, expand_building_categories
from ebm.model.data_classes import TEKParameters, YearRange


# TODO:
# - add method to change all strings to lower case and underscore instead of space
# - change column strings used in methods to constants 
def explode_column_alias(df, column, values=None, alias='default', de_dup_by=None):
    values = values if values is not None else [c for c in df[column].unique().tolist() if c != alias]
    df.loc[:, '_explode_column_alias_default'] = df.loc[:, column] == alias
    df.loc[df[df[column] == alias].index, column] = '+'.join(values)
    df = df.assign(**{column: df[column].str.split('+')}).explode(column)
    if de_dup_by:
        df = df.sort_values(by='_explode_column_alias_default', ascending=True)
        df = df.drop_duplicates(de_dup_by)
    return df.drop(columns=['_explode_column_alias_default'], errors='ignore')


class DatabaseManager:
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
    COL_ENERGY_REQUIREMENT_VALUE = 'kwh_m2'
    COL_HEATING_REDUCTION = 'reduction_share'

    DEFAULT_VALUE = 'default'

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

    def make_building_purpose(self, years: YearRange | None = None) -> pd.DataFrame:
        """
        Returns a dataframe of all combinations building_categories, teks, original_condition, purposes
        and optionally years.

        Parameters
        ----------
        years : YearRange, optional

        Returns
        -------
        pd.DataFrame
        """
        data = []
        columns = [list(BuildingCategory), self.get_tek_list().tolist(), EnergyPurpose]
        column_headers = ['building_category', 'TEK', 'building_condition', 'purpose']
        if years:
            columns.append(years)
            column_headers.append('year')

        for bc, tek, purpose, *year in itertools.product(*columns):
            row = [bc, tek, 'original_condition', purpose]
            if years:
                row.append(year[0])
            data.append(row)

        return pd.DataFrame(data=data, columns=column_headers)

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

    def get_energy_req_original_condition(self) -> pd.DataFrame:
        """
        Get dataframe with energy requirement (kWh/m^2) for floor area in original condition. The result will be
            calibrated using the dataframe from DatabaseManger.get_calibrate_heating_rv

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement (kWh/m^2) for floor area in original condition,
            per building category and purpose.
        """
        ff = self.file_handler.get_energy_req_original_condition()
        df = self.explode_unique_columns(ff, ['building_category', 'TEK', 'purpose'])
        if len(df[df.TEK=='TEK21']) > 0:
            logging.warning(f'Detected TEK21 in energy_requirement_original_condition')
        df = df.set_index(['building_category', 'purpose', 'TEK']).sort_index()

        if not 'behavior_factor' in df.columns:
            df['behavior_factor'] = 1.0
        df.loc[:, 'behavior_factor'] = df.loc[:, 'behavior_factor'].fillna(1.0)

        heating_rv_factor = self.get_calibrate_heating_rv().set_index(['building_category', 'purpose']).heating_rv_factor

        df['uncalibrated_kwh_m2'] = df['kwh_m2']
        df['calibrated_kwh_m2'] = heating_rv_factor * df.kwh_m2
        df.loc[df.calibrated_kwh_m2.isna(), 'calibrated_kwh_m2'] = df.loc[df.calibrated_kwh_m2.isna(), 'kwh_m2']
        df['kwh_m2'] = df['calibrated_kwh_m2']
        return df.reset_index()


    def get_energy_req_reduction_per_condition(self) -> pd.DataFrame:
        """
        Get dataframe with shares for reducing the energy requirement of the different building conditions. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement reduction shares for the different building conditions, 
            per building category, TEK and purpose.        
        """
        reduction_per_condition = self.file_handler.get_energy_req_reduction_per_condition()
        if len(reduction_per_condition[reduction_per_condition.TEK=='TEK21']) > 0:
            logging.warning(f'Detected TEK21 in energy_requirement_reduction_per_condition')

        return self.explode_unique_columns(reduction_per_condition,
                                           ['building_category', 'TEK', 'purpose', 'building_condition'])
    
    def get_energy_req_yearly_improvements(self) -> pd.DataFrame:
        """
        Get dataframe with yearly efficiency rates for energy requirement improvements. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        Returns
        -------
        pd.DataFrame
            Dataframe containing yearly efficiency rates (%) for energy requirement improvements,
            per building category, tek and purpose.        
        """
        yearly_improvements = self.file_handler.get_energy_req_yearly_improvements()
        return self.explode_unique_columns(yearly_improvements, ['building_category', 'TEK', 'purpose'])
    
    def get_energy_req_policy_improvements(self) -> pd.DataFrame:
        """
        Get dataframe with total energy requirement improvement in a period related to a policy. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        Returns
        -------
        pd.DataFrame
            Dataframe containing total energy requirement improvement (%) in a policy period,
            per building category, tek and purpose.        
        """
        policy_improvements = self.file_handler.get_energy_req_policy_improvements()
        return self.explode_unique_columns(policy_improvements,
                                           ['building_category', 'TEK', 'purpose'])

    def get_tekandeler(self) -> pd.DataFrame:
        """
        Load input dataframe for "TEK-andeler"

        Rename this to something more appropriate, i.e get_heating_systems

        Returns
        -------
        pd.DataFrame
        """
        df = self.file_handler.get_file(self.file_handler.TEKANDELER)
        if len(df[df.TEK=='TEK21']) > 0:
            logging.warning(f'Detected TEK21 in heating-systems.csv')
        return df

    def get_holiday_home_fuelwood_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["fuelwood"]
        return df
    
    def get_holiday_home_fossilfuel_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["fossilfuel"]
        return df

    def get_holiday_home_electricity_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["electricity"]
        return df

    def get_holiday_home_by_year(self) -> pd.DataFrame:
        return self.file_handler.get_holiday_home_by_year().set_index('year')

    def get_calibrate_heating_rv(self) -> pd.Series:
        df = self.file_handler.get_calibrate_heating_rv()
        df = expand_building_categories(df, unique_columns=['building_category', 'purpose'])
        return df[['building_category', 'purpose', 'heating_rv_factor']]

    def get_calibrate_heating_systems(self) -> pd.DataFrame:
        df = self.file_handler.get_calibrate_heating_systems()
        df = expand_building_categories(df, unique_columns=['building_category', 'to', 'from'])
        return df

    def get_area_per_person(self,
                            building_category: BuildingCategory = None) -> pd.Series:
        """
        Return area_per_person as a pd.Series

        Parameters
        ----------
        building_category: BuildingCategory, optional
            filter for building category
        Returns
        -------
        pd.Series
            float values indexed by building_category, (year)
        """
        df = self.file_handler.get_area_per_person()
        df = df.set_index('building_category')

        if building_category:
            return df.area_per_person.loc[building_category]
        return df.area_per_person

    def validate_database(self):
        missing_files = self.file_handler.check_for_missing_files()
        return True

    def get_heating_systems_shares_start_year(self):
        df = self.file_handler.get_heating_systems_shares_start_year()
        heating_systems_factor = self.get_calibrate_heating_systems()
        calibrated = calibrate_heating_systems(df, heating_systems_factor)

        return calibrated

    def get_heating_systems_efficiencies(self):
        return self.file_handler.get_heating_systems_efficiencies()

    def get_heating_systems_projection(self):
        return self.file_handler.get_heating_systems_projection()

    def explode_unique_columns(self, df, unique_columns):
        df = self.explode_tek_column(df, unique_columns)
        df = self.explode_building_category_column(df, unique_columns)
        return df

    def explode_building_category_column(self, df, unique_columns):
        df = explode_column_alias(df=df, column='building_category',
                                  values=[bc for bc in BuildingCategory if bc.is_residential()],
                                  alias='residential',
                                  de_dup_by=unique_columns)
        df = explode_column_alias(df=df, column='building_category',
                                  values=[bc for bc in BuildingCategory if not bc.is_residential()],
                                  alias='non_residential',
                                  de_dup_by=unique_columns)
        df = explode_column_alias(df=df, column='building_category',
                                  values=[bc for bc in BuildingCategory],
                                  alias='default',
                                  de_dup_by=unique_columns)
        return df

    def explode_tek_column(self, ff, unique_columns):
        df = explode_column_alias(df=ff, column='TEK', values=self.get_tek_list(),
                                  de_dup_by=unique_columns)
        return df


if __name__ == '__main__':
    db = DatabaseManager()
    building_category = BuildingCategory.HOUSE

    a = db.get_energy_req_policy_improvements()
    print(a)
