import typing
import pandas as pd

from .data_classes import TEKParameters, ScurveParameters
from .scurve import SCurve
from .shares_per_condition import SharesPerCondition

# TODO: 
# - remove _filter_tek_list and _filter_tek_params when the model is updated with new 2020 data.
# - adjust _filter_scurve_params method to not use class constants. Possible solutions:
#       - to avoid filtering df on column names (category and condition), change from Dataframe to Dict - something like this = {'building category', {'condition': Parameters}}  
#       - pass the variables as an input argument for the class (for example as a list). They can be defined outside the class, e.g. in a config
#       - adjust the variables of the ScurveParameters dataclass to match column names, then there is no need to hardcode them.   
# - add model years to a getter method for shares_per_condition dictionary, for user readability


class Buildings():
    """
    Holds all the attributes of a building, with it's associated data and operations.
    """

    # Variables used to filter S-curve params (_filter_scurve_params)
    COL_BUILDING_CATEGORY = 'building_category'
    COL_BUILDING_CONDITION = 'condition'
    COL_EARLIEST_AGE = 'earliest_age_for_measure'
    COL_AVERAGE_AGE = 'average_age_for_measure'
    COL_LAST_AGE = 'last_age_for_measure'
    COL_RUSH_YEARS = 'rush_period_years'
    COL_RUSH_SHARE = 'rush_share'
    COL_NEVER_SHARE = 'never_share'

    def __init__(self, 
                 building_category: str,
                 tek_list: typing.List[str],
                 tek_params: typing.Dict[str, TEKParameters],
                 condition_list: typing.List[str],
                 scurve_params: pd.DataFrame):
        
        self.building_category = building_category
        self.condition_list = condition_list
        self.tek_list = self._filter_tek_list(tek_list)  
        self.tek_params = self._filter_tek_params(tek_params)
        self.scurve_params = self._filter_scurve_params(scurve_params)
        self.scurve_data = self._get_scurve_data()
        self.shares_per_condition = self.get_shares()

    def _filter_tek_list(self, tek_list: typing.List[str]) -> typing.List[str]:
        """
        Filters the provided TEK list based on the building category.

        Parameters:
        - tek_list (List[str]): List of TEK strings to be filtered.

        Returns:
        - filtered_tek_list (List[str]): Filtered list of TEK strings.
        """
        # String variables used to filter the tek_list
        category_apartment = 'apartment_block'
        category_house = 'house'
        commercial_building = 'COM'
        residential_building = 'RES'
        pre_tek49_apartment = 'PRE_TEK49_RES_1950'
        pre_tek49_house = 'PRE_TEK49_RES_1940'

        residential_building_list = [category_apartment, category_house]
        
        if self.building_category in residential_building_list:
            # Filter out all TEKs associated with commercial buildings
            filtered_tek_list = [tek for tek in tek_list if commercial_building not in tek]

            # Further filtering based on the specific residential building category
            if self.building_category == category_apartment:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != pre_tek49_house]
            elif self.building_category == category_house:
                filtered_tek_list = [tek for tek in filtered_tek_list if tek != pre_tek49_apartment]

        else:
            # Filter out all TEKs associated with residential buildings
             filtered_tek_list = [tek for tek in tek_list if residential_building not in tek]

        return filtered_tek_list
    
    def _filter_tek_params(self, tek_params: typing.Dict[str, TEKParameters]):
        """
        Filters the TEK parameters to include only those relevant to the current TEK list.

        This method takes a dictionary of TEK parameters and filters it to include only 
        the parameters for TEKs that are present in the `self.tek_list`. This ensures 
        that only the relevant TEK parameters are used in subsequent calculations.

        Parameters:
        - tek_params (Dict[str, TEKParameters]): A dictionary where the keys are TEK identifiers 
                                                 and the values are TEKParameters objects containing
                                                 the parameters for each TEK.

        Returns:
        - filtered_tek_params (Dict[str, TEKParameters]): A dictionary containing only the TEK parameters
                                                          for the TEKs present in `self.tek_list`.
        """
        filtered_tek_params = {}
        for tek in self.tek_list:
            filtered_tek_params[tek] = tek_params[tek]    

        return filtered_tek_params

    def _filter_scurve_params(self, scurve_params: pd.DataFrame) -> typing.Dict[str, ScurveParameters]:
        """
        Filters S-curve parameters per condition by the building category.

        This method filters a DataFrame containing S-curve parameters to extract data specific to 
        the building category and conditions listed in `self.condition_list`. The filtered data is 
        then converted into a dictionary of `ScurveParameters` dataclass instances, one for each condition.

        Parameters:
        - scurve_params (pd.Dataframe): Dataframe containing the S-Curve parameters.

        Returns:
        - scurve_params (dict): A dictionary where the keys are the conditions (str) and the values are 
                                `ScurveParameters` dataclass instances containing the S-curve parameters.
        """
        filtered_scurve_params = {}

        for condition in self.condition_list:

            # Filter dataframe on building category and condition
            scurve_params_filtered = scurve_params[(scurve_params[self.COL_BUILDING_CATEGORY] == self.building_category) &
                                                   (scurve_params[self.COL_BUILDING_CONDITION] == condition)]

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

            filtered_scurve_params[condition] = scurve_parameters

        return filtered_scurve_params 

    def _get_scurve_data(self) -> typing.Dict:
        """
        Create a dictionary that holds S-curves and the "never share" parameter per building condition. 

        This method uses input S-curve parameters for each building condition (self.scurve_params), 
        calculates the S-curve, and stores the S-curve along with the "never share" parameter in a dictionary.
        The dictionary is used as an input argument in the TEK class. 

        Returns:
        - scurve_data (dict): A dictionary where keys are building conditions (str) and values 
                              are lists containing the S-curve tuple and the "never share" parameter (float).
        """
        scurve_data = {}

        for condition in self.condition_list:

            # Filter S-curve parameters dictionary on condition
            scurve_params_condition = self.scurve_params[condition]
            
            # Calculate the S-curve 
            s = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                       scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share)
            scurve = s.calc_scurve()
            
            # Store the parameters in the dictionary
            scurve_data[condition] = [scurve, scurve_params_condition.never_share]
        
        return scurve_data

    def get_scurve(self, condition: str) -> typing.Dict:
        """
        Get the S-curve data for a specific building condition.

        This method retrieves the S-curve data for a specified building condition from the 
        `scurve_data` dictionary, which contains the precomputed S-curve for each condition.

        Parameters:
        - condition (str): The condition for which to retrieve the S-curve data (e.g., 'Renovation', 'Demolition').

        Returns:
        - scurve (dict): A dictionary containing the S-curve data for the specified condition.
                         The dictionary has 'year' as keys representing the years in the building
                         lifetime and 'scurve' as values representing the corresponding S-curve values.
        """
        scurve_list = self.scurve_data[condition][0]
        year_list = list(range(1, len(scurve_list) + 1))
        scurve = {'year':year_list, 'scurve':scurve_list}
        return scurve

    def get_shares(self) -> typing.Dict:
        """ 
        Calculate the shares per condition for all TEKs in the building category.

        This method initializes the `SharesPerCondition` class with the TEK list, TEK parameters,
        and S-curve data, and retrieves the shares per condition for the building category.

        Returns:
        - shares_condition (dict): A dictionary where the keys are the condition names and the values are
                                   the shares per condition for each TEK.
        """
        shares_condition = SharesPerCondition(self.tek_list, self.tek_params, self.scurve_data).shares_per_condition
        return shares_condition   

    def get_shares_per_condition(self, condition: str) -> typing.Dict:
        """
        Get the shares for a specific condition for all TEKs in the building category.

        This method retrieves the shares for a specified condition from the `shares_per_condition`
        dictionary, which contains the shares per condition for each TEK.

        Parameters:
        - condition (str): The condition for which to retrieve the shares (e.g., 'Renovation', 'Demolition').

        Returns:
        - shares (dict): A dictionary where the keys are the TEKs and the values are the shares for the specified condition.
        """
        shares = self.shares_per_condition[condition]
        return shares
    