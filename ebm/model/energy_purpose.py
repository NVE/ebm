import typing

from enum import StrEnum, unique, auto

import pandas as pd

from ebm.model.building_category import BEMA_ORDER as building_category_order
from ebm.model.tek import BEMA_ORDER as tek_order


@unique
class EnergyPurpose(StrEnum):
    HEATING_RV = auto()
    HEATING_DHW = auto()
    FANS_AND_PUMPS = auto()
    LIGHTING = auto()
    ELECTRICAL_EQUIPMENT = auto()
    COOLING = auto()

    @classmethod
    def _missing_(cls, value: str):
        """
        Attempts to create an enum member from a given value by normalizing the string.

        This method is called when a value is not found in the enumeration. It converts the input value 
        to lowercase, replaces spaces and hyphens with underscores, and then checks if this transformed 
        value matches the value of any existing enum member.

        Parameters
        ----------
        value : str
            The input value to convert and check against existing enum members.

        Returns
        -------
        Enum member
            The corresponding enum member if a match is found.

        Raises
        ------
        ValueError
            If no matching enum member is found.
        """
        value = value.lower().replace(' ', '_').replace('-', '_')
        for member in cls:
            if member.value == value:
                return member
        return ValueError(f'Invalid purpose given: {value}')

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @classmethod
    def other(cls) -> typing.Iterable['EnergyPurpose']:
        return [cls.LIGHTING, cls.ELECTRICAL_EQUIPMENT, cls.FANS_AND_PUMPS]

    @classmethod
    def heating(cls) -> typing.Iterable['EnergyPurpose']:
        return [cls.HEATING_RV, cls.HEATING_DHW]

    @classmethod
    def cooling(cls) -> typing.Iterable['EnergyPurpose']:
        return [cls.COOLING]


def group_energy_use_kwh_by_building_group_purpose_year_wide(energy_use_kwh: pd.DataFrame) -> pd.DataFrame:
    df = (energy_use_kwh
          .copy()
          .reset_index()
          .set_index(['building_category', 'building_condition', 'TEK', 'purpose', 'heating_systems', 'load', 'year'])
          .sort_index())

    df.loc[:, 'GWh'] = df.loc[:, 'kwh'] / 1_000_000
    df.loc[:, ('TEK', 'building_condition')] = ('all', 'all')

    df['building_group'] = 'non_residential'
    df.loc['house', 'building_group'] = 'house'
    df.loc['apartment_block', 'building_group'] = 'apartment_block'

    summed = df.groupby(by=['building_group', 'purpose', 'year']).sum().reset_index()
    summed = summed[['building_group', 'purpose', 'year', 'GWh']]

    hz = summed.pivot(columns=['year'], index=['building_group', 'purpose'], values=['GWh']).reset_index()
    hz = hz.sort_values(by=['building_group', 'purpose'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_group' else x.map(
                            tek_order) if x.name == 'TEK' else x.map(
                            {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                             'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

    hz.insert(2, 'U', 'GWh')
    hz.columns = ['building_group', 'purpose', 'U'] + [y for y in range(2020, 2051)]

    return hz.rename(columns={'building_group': 'building_category'})


def group_energy_use_by_year_category_tek_purpose(energy_use_kwh: pd.DataFrame) -> pd.DataFrame:
    df = (energy_use_kwh.copy().reset_index()
          .set_index(['building_category', 'building_condition', 'TEK', 'purpose', 'heating_systems', 'load', 'year'])
          .sort_index())

    df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000

    df = df.reset_index().groupby(by=['year', 'building_category', 'TEK', 'purpose'], as_index=False).sum()
    df = df[['year', 'building_category', 'TEK', 'purpose', 'GWh']]
    df = df.sort_values(by=['year', 'building_category', 'TEK', 'purpose'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'TEK' else x.map(
                            {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                             'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

    df = df.rename(columns={'GWh': 'energy_use [GWh]'})

    df.reset_index(inplace=True, drop=True)
    return df
