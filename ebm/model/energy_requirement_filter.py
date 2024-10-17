import typing

import pandas as pd
from loguru import logger

from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.building_condition import BuildingCondition


class EnergyRequirementFilter:
    """
    """
    
    # Column names
    BUILDING_CATEGORY = 'building_category'
    TEK = 'TEK'
    PURPOSE = 'purpose'
    START_YEAR = 'period_start_year'
    END_YEAR = 'period_end_year'
    BUILDING_CONDITION = 'building_condition'
    REDUCTION_SHARE = 'reduction_share'

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
        _check_var_type(policy_improvement, 'energy_requirement_policy_improvement')
        _check_var_type(yearly_improvements, 'energy_requirement_yearly_improvements')

        self.building_category = building_category
        self.original_condition = original_condition
        self.reduction_per_condition = reduction_per_condition
        self.yearly_improvements = yearly_improvements
        self.policy_improvement = policy_improvement

    def _filter_df(self, df: pd.DataFrame, filter_col: str,
                   filter_val: typing.Union[BuildingCategory, EnergyPurpose, str]) -> pd.DataFrame:
        """
        """
        if filter_val in df[filter_col].unique():
            return df[df[filter_col] == filter_val]
        elif self.DEFAULT in df[filter_col].unique():
            return df[df[filter_col] == self.DEFAULT]
        else:
            return False
    
    #TODO: should this return a dataframe or just the kwh_m2 value?
    def get_original_condition(self, tek, purpose) -> pd.DataFrame:
        """
        Returns a dataframe with original condition energy use for a building_category
        filtered by tek and purpose

        Parameters
        ----------
        tek
        purpose

        Returns
        -------
        pd.DataFrame
            columns: building_category, TEK, purpose, kwh_m2
        """
        df = self.original_condition
        
        false_return_value = pd.DataFrame(data={'building_category': {0: self.building_category},
                                  'TEK': {0: tek},
                                  'purpose': {0: purpose},
                                  'kwh_m2': {0: 0.0}})
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
        Returns energy use reduction for building condition

        Parameters
        ----------
        tek : str
        purpose : str

        Returns
        -------
        pd.DataFrame
            columns building_condition, reduction_share
        """
        df = self.reduction_per_condition

        false_return_value = pd.DataFrame(data={self.BUILDING_CONDITION: {0: BuildingCondition.ORIGINAL_CONDITION,
                                                                          1: BuildingCondition.SMALL_MEASURE,
                                                                          2: BuildingCondition.RENOVATION,
                                                                          3: BuildingCondition.RENOVATION_AND_SMALL_MEASURE},
                                                self.REDUCTION_SHARE: {0: 0.0, 1: 0, 2: 0, 3: 0}})
        
        df = self._filter_df(df, self.BUILDING_CATEGORY, self.building_category)
        if df is False:
            return false_return_value

        df = self._filter_df(df, self.PURPOSE, purpose)
        if df is False:
            return false_return_value
        
        df = self._filter_df(df, self.TEK, tek)
        if df is False:
            return false_return_value
        
        df = df[[self.BUILDING_CONDITION, self.REDUCTION_SHARE]]
        df.reset_index(drop=True, inplace=True)

        return df

    def get_policy_improvement(self,
                               tek: str,
                               purpose: typing.Union[EnergyPurpose, str]) -> \
            typing.Union[typing.Tuple[YearRange, float], None]:
        df = self.policy_improvement

        false_return_value = None

        df = self._filter_df(df, self.BUILDING_CATEGORY, self.building_category)
        if df is False:
            return false_return_value
        
        df = self._filter_df(df, self.PURPOSE, purpose)
        if df is False:
            return false_return_value

        df = self._filter_df(df, self.TEK, tek)
        if df is False:
            return false_return_value

        start = df.period_start_year.iloc[0]
        end = df.period_end_year.iloc[0]
        improvement_value = df.improvement_at_period_end.iloc[0]

        return YearRange(start, end), improvement_value

    def get_yearly_improvements(self, tek: str, purpose: EnergyPurpose) -> float:
        df = self.yearly_improvements

        false_return_value = 0.0

        df = self._filter_df(df, self.BUILDING_CATEGORY, self.building_category)
        if df is False:
            return false_return_value

        df = self._filter_df(df, self.PURPOSE, purpose)
        if df is False:
            return false_return_value
        
        df = self._filter_df(df, self.TEK, tek)
        if df is False:
            return false_return_value
        
        eff_rate = df.yearly_efficiency_improvement.iloc[0]
        return eff_rate