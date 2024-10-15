import typing

import pandas as pd
from ebm.model import BuildingCategory
from ebm.model.data_classes import YearRange


class EnergyRequirementFilter:
    def __init__(self,
                 building_category: BuildingCategory,
                 energy_requirement_original_condition,
                 energy_requirement_reduction_per_condition,
                 energy_requirement_yearly_improvements,
                 energy_requirement_policy_improvement):
        self.building_category = building_category
        self.energy_requirement_policy_improvement = energy_requirement_policy_improvement
        self.energy_requirement_yearly_improvements = energy_requirement_yearly_improvements
        self.energy_requirement_reduction_per_condition = energy_requirement_reduction_per_condition
        if not isinstance(energy_requirement_original_condition, pd.DataFrame):
            actual_type = type(energy_requirement_original_condition)
            msg = f'energy_requirement_original_condition is expected to be pd.DataFrame. Got: {actual_type}'
            raise TypeError(msg)
        self.original_condition = energy_requirement_original_condition

    def get_original_condition(self, tek, purpose) -> pd.DataFrame:
        """
        Returns a dataframe with original condition energy use for a building_category
            filtered by tek and purpose
building_category	TEK	purpose	kwh_m2
286	kindergarten	PRE_TEK49_COM	heating_rv	170.3831314118222
292	kindergarten	TEK07	heating_rv	91.60795310210064
298	kindergarten	TEK10	heating_rv	74.22534704119848
304	kindergarten	TEK17	heating_rv	74.22534704119848
310	kindergarten	TEK21	heating_rv	74.22534704119848
316	kindergarten	TEK49_COM	heating_rv	170.3831314118222
322	kindergarten	TEK69_COM	heating_rv	170.3831314118222
328	kindergarten	TEK87_COM	heating_rv	138.9320403843025
334	kindergarten	TEK97_COM	heating_rv	111.3845937143784

        Parameters
        ----------
        tek
        purpose

        Returns
        -------
        pd.DataFrame (pd.Series ?)
            with column kwh_m2 indexed(?) by building_category, TEK, purpose
        """
        df = self.original_condition[(self.original_condition.building_category == self.building_category) & (
                    self.original_condition.TEK == tek) & (self.original_condition.purpose == purpose)]
        if len(df):
            return df
        return pd.DataFrame(data={'building_category': {286: self.building_category,
  292: self.building_category,
  298: self.building_category,
  304: self.building_category,
  310: self.building_category,
  316: self.building_category,
  322: self.building_category,
  328: self.building_category,
  334: self.building_category},
 'TEK': {286: 'PRE_TEK49_COM',
  292: 'TEK07',
  298: 'TEK10',
  304: 'TEK17',
  310: 'TEK21',
  316: 'TEK49_COM',
  322: 'TEK69_COM',
  328: 'TEK87_COM',
  334: 'TEK97_COM'},
 'purpose': {286: 'heating_rv',
  292: 'heating_rv',
  298: 'heating_rv',
  304: 'heating_rv',
  310: 'heating_rv',
  316: 'heating_rv',
  322: 'heating_rv',
  328: 'heating_rv',
  334: 'heating_rv'},
 'kwh_m2': {286: 170.3831314118222,
  292: 91.60795310210064,
  298: 74.22534704119848,
  304: 74.22534704119848,
  310: 74.22534704119848,
  316: 170.3831314118222,
  322: 170.3831314118222,
  328: 138.9320403843025,
  334: 111.3845937143784}})

    def get_reduction_per_condition(self, purpose: str, tek: str) -> pd.DataFrame:
        """
        Returns energy use reduction for building condition

        Parameters
        ----------
        purpose : str
        tek : str

        Returns
        -------
        pd.DataFrame
            columns building_condition, reduction

        """
        if purpose == 'heating_rv':
            return pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                1: 'small_measure',
                                2: 'renovation',
                                3: 'renovation_and_small_measure'},
         'reduction': {0: 0.0, 1: 0.07, 2: 0.2, 3: 0.25}})

        return pd.DataFrame(data={'building_condition': {0: 'original_condition',
                                1: 'small_measure',
                                2: 'renovation',
                                3: 'renovation_and_small_measure'},
         'reduction': {0: 0.0, 1: 0, 2: 0, 3: 0}})

    def get_policy_improvement(self, tek, purpose) -> typing.Union[typing.Tuple[YearRange, typing.Union[float, None]]]:
        if purpose == 'lighting':
            return YearRange(2018, 2030), 0.6
        return YearRange(2010, 2050), None

    def get_yearly_improvements(self, tek, purpose) -> float:
        if purpose == 'electrical_equipment':
            return 0.01
        if purpose == 'lighting':
            return 0.005
        return 0.0
