import typing

import pandas as pd
from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.building_condition import BuildingCondition
from ebm.model.custom_exceptions import AmbiguousDataError



class EnergyRequirementFilter:
    """
    """
    
    #File names 
    FILE_ORIGINAL_CONDITION = 'energy_requirement_original_condition'
    FILE_REDUCITON_PER_CONDITION = 'energy_requirement_reduction_per_condition'
    FILE_POLICY_IMPROVEMENT = 'energy_requirement_policy_improvements'
    FILE_YEARLY_IMPROVEMENT = 'energy_requirement_yearly_improvements'

    # Column names
    BUILDING_CATEGORY = 'building_category'
    TEK = 'TEK'
    PURPOSE = 'purpose'
    START_YEAR = 'period_start_year'
    END_YEAR = 'period_end_year'
    BUILDING_CONDITION = 'building_condition'
    REDUCTION_SHARE = 'reduction_share'
    KWH_M2 = 'kwh_m2'
    POLICY_IMPROVEMENT = 'improvement_at_period_end'
    YEARLY_IMPROVEMENT = 'yearly_efficiency_improvement'

    DEFAULT = 'default'

    def __init__(self,
                 building_category: BuildingCategory,
                 original_condition,
                 reduction_per_condition,
                 yearly_improvements,
                 policy_improvement):
        def _check_var_type(var: any, var_name: str):
            if not isinstance(var, pd.DataFrame):
                actual_type = type(var)
                msg = f'{var_name} expected to be of type pd.DataFrame. Got: {actual_type}'
                raise TypeError(msg)

        _check_var_type(original_condition, 'energy_requirement_original_condition')
        _check_var_type(reduction_per_condition, 'energy_requirement_reduction_per_condition')
        _check_var_type(policy_improvement, 'energy_requirement_policy_improvements')
        _check_var_type(yearly_improvements, 'energy_requirement_yearly_improvements')

        self.building_category = building_category
        self.original_condition = original_condition
        self.reduction_per_condition = reduction_per_condition
        self.yearly_improvements = yearly_improvements
        self.policy_improvement = policy_improvement

    def _filter_df(self, df: pd.DataFrame, filter_col: str,
                   filter_val: typing.Union[BuildingCategory, EnergyPurpose, str]) -> pd.DataFrame:
        """
         Filters the given DataFrame based on the specified column and value.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to filter.
        filter_col : str
            The column name to apply the filter on.
        filter_val : BuildingCategory, EnergyPurpose, or str
            The value to filter the DataFrame by.

        Returns
        -------
        pd.DataFrame or bool
            The filtered DataFrame or False if the filter value and default value are not found.
        """
        if filter_val in df[filter_col].unique():
            return df[df[filter_col] == filter_val]
        elif self.DEFAULT in df[filter_col].unique():
            return df[df[filter_col] == self.DEFAULT]
        else:
            return False

    def _apply_filter(self,
                      df: pd.DataFrame,
                      building_category: BuildingCategory,
                      tek: str,
                      purpose: EnergyPurpose) -> pd.DataFrame:
        """
        """
        # Filter for exact matches on building category, tek and purpose
        filtered_df = df[
            (df[self.BUILDING_CATEGORY].isin([building_category, self.DEFAULT])) &
            (df[self.TEK].isin([tek, self.DEFAULT])) &
            (df[self.PURPOSE].isin([purpose, self.DEFAULT]))
        ]
        return filtered_df
    
    def _add_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        """
        # Add priority column: 3 means exact match, 0 means all defaults
        df.loc[:, 'priority'] = (
            (df[self.BUILDING_CATEGORY] != self.DEFAULT).astype(int) +
            (df[self.TEK] != self.DEFAULT).astype(int) +
            (df[self.PURPOSE] != self.DEFAULT).astype(int)
        )

        # Sort by priority (descending) to get the best match first
        df = df.sort_values(by='priority', ascending=False)
        return df
    
    def _check_and_resolve_tied_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        """
        # Check if there are ties in the priority
        top_rank = df['priority'].iloc[0]
        tied_rank = df[df['priority'] == top_rank].copy()

        if len(tied_rank) > 1:
            # Add rank columns based on preference order: building_category, TEK, purpose
            tied_rank[f'{self.BUILDING_CATEGORY}_rank'] = (tied_rank[self.BUILDING_CATEGORY] != self.DEFAULT).astype(int)
            tied_rank[f'{self.TEK}_rank'] = (tied_rank[self.TEK] != self.DEFAULT).astype(int)
            tied_rank[f'{self.PURPOSE}_rank'] = (tied_rank[self.PURPOSE] != self.DEFAULT).astype(int)

            # Sort by the ranks to prioritize: building_category, TEK, and purpose
            tied_rank = tied_rank.sort_values(
                by=[f'{self.BUILDING_CATEGORY}_rank', f'{self.TEK}_rank', f'{self.PURPOSE}_rank'],
                ascending=[False, False, False] 
            )

            df = tied_rank
        return df
    
    def get_original_condition(self, tek: str, purpose: EnergyPurpose) -> pd.DataFrame:
        """
        Retrieves a dataframe with the energy requirement (kwh_m2) for original condition.

        If the specified conditions are not found, returns a default DataFrame with a kwh_m2 value of 0.0 and logs an error.

        Parameters
        ----------
        tek: str
        purpose: EnergyPurpose

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns: building_category, TEK, purpose, kwh_m2.
        """
        df = self.original_condition
        
        false_return_value = pd.DataFrame(data={self.BUILDING_CATEGORY: {0: self.building_category},
                                                self.TEK: {0: tek},
                                                self.PURPOSE: {0: purpose},
                                                self.KWH_M2: {0: 0.0}})
        false_error_msg = (f"No energy requirement value (kwh_m2) found for original condition with variables:"
                           f"building_category={self.building_category}, tek={tek} and purpose={purpose}. Calculating with value = 0.")

        df = self._filter_df(df, self.BUILDING_CATEGORY, self.building_category)
        if df is False:
            logger.error(false_error_msg)
            return false_return_value

        df = self._filter_df(df, self.PURPOSE, purpose)
        if df is False:
            logger.error(false_error_msg)
            return false_return_value
        
        df = self._filter_df(df, self.TEK, tek)
        if df is False:
            logger.error(false_error_msg)
            return false_return_value
        
        df.reset_index(drop=True, inplace=True)

        return df

    def get_reduction_per_condition(self, tek: str, purpose: EnergyPurpose) -> pd.DataFrame:
        """
        Retrieves the energy requirement reduction share for the different building conditions.

        If the specified conditions are not found, returns a default DataFrame with zero reduction shares.

        Parameters
        ----------
        tek : str
        purpose : EnergyPurpose

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns: building_condition, reduction_share.
        """
        df = self.reduction_per_condition.copy()

        #TODO: make dataframe more readable (like a dataframe)
        false_return_value = pd.DataFrame(data={self.BUILDING_CONDITION: {0: BuildingCondition.ORIGINAL_CONDITION,
                                                                          1: BuildingCondition.SMALL_MEASURE,
                                                                          2: BuildingCondition.RENOVATION,
                                                                          3: BuildingCondition.RENOVATION_AND_SMALL_MEASURE},
                                                self.REDUCTION_SHARE: {0: 0.0, 1: 0, 2: 0, 3: 0}})
        
        # Filter for exact matches on all columns
        df = self._apply_filter(df, self.building_category, tek, purpose)

        # Return default return value if no match is found
        if df.empty:
            return false_return_value 
        
        # Sort rows by priority to get best match
        df = self._add_priority(df)

        # Check for tied priorities and resolve by sorting after prefered priority
        df = self._check_and_resolve_tied_priority(df)

        # Check for duplicate rows with different reduction_share
        duplicated_rows = df[df.duplicated(subset=[self.BUILDING_CATEGORY, self.TEK, self.PURPOSE, self.BUILDING_CONDITION], keep=False)]
        if not duplicated_rows.empty:
            n_unique_values = duplicated_rows[self.REDUCTION_SHARE].nunique()
            if n_unique_values > 1:
                msg = (
                    f"Conflicting data found for building_category='{self.building_category}', "
                    f"{tek=} and purpose='{purpose}', in file '{self.FILE_REDUCITON_PER_CONDITION}'."
                )
                raise AmbiguousDataError(msg)

        # Get the 4 building conditions with top priority (best match)
        df = df[:4]

        # Iterable object with expected conditions
        expected_conditions = BuildingCondition.existing_conditions()

        # Check if all expected building conditions are present
        missing_conditions = [cond for cond in expected_conditions if cond not in df[self.BUILDING_CONDITION].values]

        if missing_conditions:
            # Log the missing building conditions
            missing_conditions_str = ", ".join(str(cond) for cond in missing_conditions)
            print(f"Error: Missing expected building conditions: {missing_conditions_str}. Returning default values.")

            # Append rows with missing conditions to the dataframe, setting reduction_share to 0
            for cond in missing_conditions:
                df = pd.concat([
                    df,
                    pd.DataFrame({self.BUILDING_CONDITION: [cond], self.REDUCTION_SHARE: [0.0]})
                ])

        df = df[[self.BUILDING_CONDITION, self.REDUCTION_SHARE]]
        df.reset_index(drop=True, inplace=True)

        return df

    def get_policy_improvement(self,
                               tek: str,
                               purpose: EnergyPurpose) -> \
            typing.Union[typing.Tuple[YearRange, float], None]:
        """
        Retrieves the policy improvement period and the energy requirement reduction value.    

        Parameters
        ----------
        tek: str
        purpose: EnergyPurpose

        Returns
        -------
        tuple of (YearRange, float) or None
                A tuple containing the YearRange for the policy improvement period and 
                the improvement value, or None if not found.
        """
        df = self.policy_improvement.copy()

        false_return_value = None

        # Filter for exact matches on all columns
        df = self._apply_filter(df, self.building_category, tek, purpose)

        # Return default return value if no match is found
        if df.empty:
            return false_return_value 
        
        # Sort rows by priority to get best match
        df = self._add_priority(df)

        # Check for tied priorities and resolve by sorting after prefered priority
        df = self._check_and_resolve_tied_priority(df)

        # Check for duplicate rows with conflicting data in the three target columns
        duplicated_rows = df[df.duplicated(subset=[self.BUILDING_CATEGORY, self.TEK, self.PURPOSE], keep=False)]
        if not duplicated_rows.empty:
            n_unique_start = duplicated_rows[self.START_YEAR].nunique()
            n_unique_end = duplicated_rows[self.END_YEAR].nunique()
            n_unique = duplicated_rows[self.POLICY_IMPROVEMENT].nunique()

            # Check if any of the three fields have conflicting values
            if n_unique_start > 1 or n_unique_end > 1 or n_unique > 1:
                msg = (
                    f"Conflicting data found for building_category='{self.building_category}', "
                    f"{tek=} and purpose='{purpose}', in file '{self.FILE_POLICY_IMPROVEMENT}'. "
                )
                raise AmbiguousDataError(msg)

        start = df[self.START_YEAR].iloc[0]
        end = df[self.END_YEAR].iloc[0]
        improvement_value = df[self.POLICY_IMPROVEMENT].iloc[0]

        return YearRange(start, end), improvement_value

    def get_yearly_improvements(self, tek: str, purpose: EnergyPurpose) -> float:
        """
        Retrieves the yearly efficiency rate for energy requirement improvements.   

        If the specified conditions are not found, returns a default value of 0.0.

        Parameters
        ----------
        tek: str
        purpose: EnergyPurpose

        Returns
        -------
        float
            The yearly efficiency rate for energy requirement improvements.
        """
        df = self.yearly_improvements.copy()

        # Default return value if no match is found
        false_return_value = 0.0

        # Filter for exact matches on all columns
        df = self._apply_filter(df, self.building_category, tek, purpose)

        # Return default return value if no match is found
        if df.empty:
            return false_return_value 
        
        # Sort rows by priority to get best match
        df = self._add_priority(df)

        # Check for tied priorities and resolve by sorting after prefered priority
        df = self._check_and_resolve_tied_priority(df)
        
        # Check for duplicate rows with different yearly efficiency improvement 
        duplicated_rows = df[df.duplicated(subset=[self.BUILDING_CATEGORY, self.TEK, self.PURPOSE], keep=False)]
        if not duplicated_rows.empty:
            n_unique_values = duplicated_rows[self.YEARLY_IMPROVEMENT].nunique()
            if n_unique_values > 1:
                msg = (
                    f"Conflicting data found for building_category='{self.building_category}', "
                    f"{tek=} and purpose='{purpose}', in file '{self.FILE_YEARLY_IMPROVEMENT}'."
                )   
                raise AmbiguousDataError(msg)

        eff_rate = df[self.YEARLY_IMPROVEMENT].iloc[0]
        return eff_rate
    
    @staticmethod
    def new_instance(building_category: BuildingCategory, 
                     database_manager: DatabaseManager = None) -> 'EnergyRequirementFilter':
        """
        Creates a new instance of the EnergyRequirementFilter class, using the specified building category
        and an optional database manager.

        If a database manager is not provided, a new DatabaseManager instance will be created.

        Parameters
        ----------
        building_category: BuildingCategory
        database_manager: DatabaseManager

        Returns 
        -------
         EnergyRequirementFilter
             A new instance of EnergyRequirementFilter initialized with data from the specified 
             database manager.
        """
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        original_condition = dm.get_energy_req_original_condition()
        reduction_per_condition = dm.get_energy_req_reduction_per_condition()
        yearly_improvements = dm.get_energy_req_yearly_improvements()
        policy_improvement = dm.get_energy_req_policy_improvements()
        return EnergyRequirementFilter(building_category=building_category,
                                       original_condition=original_condition,
                                       reduction_per_condition=reduction_per_condition,
                                       yearly_improvements=yearly_improvements,
                                       policy_improvement=policy_improvement)

if __name__ == '__main__':
    erf = EnergyRequirementFilter.new_instance(building_category=BuildingCategory.HOUSE)
    print(erf.get_ye)