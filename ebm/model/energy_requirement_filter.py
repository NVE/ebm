import typing

import pandas as pd
from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.building_condition import BuildingCondition
from ebm.model.exceptions import AmbiguousDataError

class EnergyRequirementFilter:
    """
    Filters and retrieves energy requirement data based on building category, TEK, and energy purpose.
    """
    
    # Namne of constructor arguments 
    VAR_ORIGINAL_CONDITION = 'original_condition'
    VAR_REDUCITON_PER_CONDITION = 'reduction_per_condition'
    VAR_POLICY_IMPROVEMENT = 'policy_improvement'
    VAR_YEARLY_IMPROVEMENT = 'yearly_improvements'

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

    # Expected string for default
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
                msg = f"Constructor argument '{var_name}' expected to be of type pd.DataFrame. Got: {actual_type}"
                raise TypeError(msg)

        _check_var_type(original_condition, self.VAR_ORIGINAL_CONDITION)
        _check_var_type(reduction_per_condition, self.VAR_REDUCITON_PER_CONDITION)
        _check_var_type(policy_improvement, self.VAR_POLICY_IMPROVEMENT)
        _check_var_type(yearly_improvements, self.VAR_YEARLY_IMPROVEMENT)

        self.building_category = building_category
        self.original_condition = original_condition
        self.reduction_per_condition = reduction_per_condition
        self.yearly_improvements = yearly_improvements
        self.policy_improvement = policy_improvement

    def _apply_filter(self,
                      df: pd.DataFrame,
                      building_category: BuildingCategory,
                      tek: str,
                      purpose: EnergyPurpose) -> pd.DataFrame:
        """
        Filters the Dataframe for exact matches or 'default' for building_cateogry,
        tek and purpose. 

        Parameters
        ----------
        df: pd.DataFrame
            The DataFrame to filter. Must contain following cols:
            'building_category', 'tek' and 'purpose'
        building_category: BuildingCategory
        tek: str
        purpose: EnergyPurpose

        Returns
        -------
        pd.DataFrame
            The filtered DataFrame.
        """
        filtered_df = df[
            (df[self.BUILDING_CATEGORY].isin([building_category, self.DEFAULT])) &
            (df[self.TEK].isin([tek, self.DEFAULT])) &
            (df[self.PURPOSE].isin([purpose, self.DEFAULT]))
        ]
        return filtered_df
    
    def _add_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts rows in the Dataframe according to highest priority to ensure best match
        on 'building_category', 'tek' and 'purpose'.

        Highest priority is given to exact matches on 'building_category', 'tek' and 
        'purpose' and not 'default'. Priority is ranked from 0 to 3. 3 means exact match, 
        and 0 means all defaults. 

        Parameters
        ----------
        df : pd.DataFrame
        
        Returns
        -------
        pd.DataFrame
            Dataframe sorted with best match on 'building_category', 'tek' and 'purpose' first.
        """
        df.loc[:, 'priority'] = (
            (df[self.BUILDING_CATEGORY] != self.DEFAULT).astype(int) +
            (df[self.TEK] != self.DEFAULT).astype(int) +
            (df[self.PURPOSE] != self.DEFAULT).astype(int)
        )

        df = df.sort_values(by='priority', ascending=False)
        return df
    
    def _check_and_resolve_tied_priority(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Checks and resolves ties in priority according to a pre-defined preferance order, 
        where priority is given to best match in this order: building_category, tek and purpose. 

        Parameters
        ----------
        df : pd.DataFrame
        
        Returns
        -------
        pd.DataFrame
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
    
    def _check_conflicting_data(self, 
                                df: pd.DataFrame, 
                                subset_cols: typing.List[str],
                                conflict_col: str,
                                error_msg: str):
        """
        Checks for conflicting data in rows matching subset columns and raises an error if found.
        
        Parameters
        ----------
        df : pd.DataFrame
        subset_cols : list of str 
        conflict_col : str 
        error_msg : str
        """
        duplicated_rows = df[df.duplicated(subset=subset_cols, keep=False)]
        if not duplicated_rows.empty and duplicated_rows[conflict_col].nunique() > 1:
            raise AmbiguousDataError(error_msg)
    
    def get_original_condition(self, tek: str, purpose: EnergyPurpose) -> float:
        """
        Retrieves the energy requirement (kwh_m2) for a building in it's original condition based 
        on the specified TEK and purpose, and the building category set in the class instance.

        If the specified conditions are not found, returns a default kwh_m2 value of 0.0 and logs an error.

        Parameters
        ----------
        tek: str
        purpose: EnergyPurpose

        Returns
        -------
        float
            The energy requirement (kwh_m2) for original condition for a building category, 
            tek and purpose. 
        """
        df = self.original_condition.copy()
        
        false_return_value = 0.0
        false_error_msg = (
            f"No data found in '{self.VAR_ORIGINAL_CONDITION}' dataframe for building_category={self.building_category},"
            f"tek={tek} and purpose={purpose}. Calculating with value = 0."
            )

         # Filter for exact matches on all columns
        df = self._apply_filter(df, self.building_category, tek, purpose)

        # Return default return value if no match is found
        if df.empty:
            logger.error(false_error_msg)
            return false_return_value 
        
        # Sort rows by priority to get best match
        df = self._add_priority(df)

        # Check for tied priorities and resolve by sorting after prefered priority
        df = self._check_and_resolve_tied_priority(df)
        
        # Check for duplicate rows with different energy requirement (kwh_m2)
        error_msg = (
            f"Conflicting data found in '{self.VAR_ORIGINAL_CONDITION}' dataframe for "
            f"building_category='{self.building_category}', {tek=} and purpose='{purpose}'."
            ) 
        self._check_conflicting_data(df,
                                     [self.BUILDING_CATEGORY, self.TEK, self.PURPOSE],
                                     self.KWH_M2,
                                     error_msg)
        
        df.reset_index(drop=True, inplace=True)
        khw_m2 = df[self.KWH_M2].iloc[0]
        return khw_m2

    def get_reduction_per_condition(self, tek: str, purpose: EnergyPurpose) -> pd.DataFrame:
        """
        Retrieves the energy requirement reduction share for different building conditions
        according to the specified TEK and purpose, and the building category defined in 
        the class instance.

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

        false_return_value = pd.DataFrame([
            [BuildingCondition.ORIGINAL_CONDITION, 0.0],
            [BuildingCondition.SMALL_MEASURE, 0.0],
            [BuildingCondition.RENOVATION, 0.0],
            [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.0]
        ], columns=[self.BUILDING_CONDITION, self.REDUCTION_SHARE])
        
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
        error_msg = (
            f"Conflicting data found in '{self.VAR_REDUCITON_PER_CONDITION}' dataframe for "
            f"building_category='{self.building_category}', {tek=} and purpose='{purpose}'."
            )         
        self._check_conflicting_data(df,
                                     [self.BUILDING_CATEGORY, self.TEK, self.PURPOSE, self.BUILDING_CONDITION],
                                     self.REDUCTION_SHARE,
                                     error_msg)

        # Get the 4 building conditions with top priority (best match)
        df = df.drop_duplicates(subset=[self.BUILDING_CONDITION], keep='first')

        # Iterable object with expected conditions
        expected_conditions = BuildingCondition.existing_conditions()

        # Check if all expected building conditions are present
        missing_conditions = [cond for cond in expected_conditions if cond not in df[self.BUILDING_CONDITION].values]

        if missing_conditions:
            # Log the missing building conditions
            missing_conditions_str = ", ".join(str(cond) for cond in missing_conditions)
            msg = (
                f"Missing building conditions: {missing_conditions_str} in '{self.VAR_REDUCITON_PER_CONDITION}' "
                f"dataframe for building_category='{self.building_category}', {tek=} and purpose='{purpose}'. "
                f"Returning conditions with value = 0."
            )
            logger.error(msg)

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
        Retrieves the policy improvement period and energy requirement reduction based on the 
        specified TEK, purpose, and the building category set in the class instance. 

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

        # Check for duplicate rows with conflicting data in the three value columns
        error_msg = (
            f"Conflicting data found in '{self.VAR_POLICY_IMPROVEMENT}' dataframe for "
            f"building_category='{self.building_category}', {tek=} and purpose='{purpose}'."
            )        
        for conflict_col in [self.START_YEAR, self.END_YEAR, self.POLICY_IMPROVEMENT]:
            self._check_conflicting_data(df,
                                        [self.BUILDING_CATEGORY, self.TEK, self.PURPOSE],
                                        conflict_col,
                                        error_msg)

        start = df[self.START_YEAR].iloc[0]
        end = df[self.END_YEAR].iloc[0]
        improvement_value = df[self.POLICY_IMPROVEMENT].iloc[0]
        return YearRange(start, end), improvement_value

    def get_yearly_improvements(self, tek: str, purpose: EnergyPurpose) -> float:
        """
        Retrieves the yearly efficiency rate for energy requirement improvements based on the 
        specified TEK and purpose, as well as the building category set in the class instance.   

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
        error_msg = (
            f"Conflicting data found in '{self.VAR_YEARLY_IMPROVEMENT}' dataframe for "
            f"building_category='{self.building_category}', {tek=} and purpose='{purpose}'."
            )    
        self._check_conflicting_data(df,
                                     [self.BUILDING_CATEGORY, self.TEK, self.PURPOSE],
                                     self.YEARLY_IMPROVEMENT,
                                     error_msg)

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
        yearly_improvements = dm.get_energy_need_yearly_improvements()
        policy_improvement = dm.get_energy_req_policy_improvements()
        return EnergyRequirementFilter(building_category=building_category,
                                       original_condition=original_condition,
                                       reduction_per_condition=reduction_per_condition,
                                       yearly_improvements=yearly_improvements,
                                       policy_improvement=policy_improvement)
    