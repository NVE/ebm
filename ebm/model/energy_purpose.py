import typing

from enum import StrEnum, unique, auto

import pandas as pd

from ebm.model.building_category import BuildingCategory, BEMA_ORDER as building_category_order
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


def transform_energy_need_to_energy_purpose_wide(energy_need: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    df_a = area_forecast.copy()
    df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

    df_e = energy_need.copy().reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

    df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
    df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000
    df.loc[:, ('TEK', 'building_condition')] = ('all', 'all')

    non_residential = [b for b in BuildingCategory if b.is_non_residential()]

    df.loc[df[df['building_category'].isin(non_residential)].index, 'building_category'] = 'non_residential'

    df = df.groupby(by=['building_category', 'purpose', 'year'], as_index=False).sum()
    df = df[['building_category', 'purpose', 'year', 'GWh']]

    df = df.pivot(columns=['year'], index=['building_category', 'purpose'], values=['GWh']).reset_index()
    df = df.sort_values(by=['building_category', 'purpose'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'building_category' else x.map(
                            {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                             'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

    df.insert(2, 'U', 'GWh')
    df.columns = ['building_category', 'purpose', 'U'] + [y for y in range(2020, 2051)]

    return df


def transform_energy_need_to_energy_purpose_long(energy_need: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    df_a = area_forecast.copy()
    df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

    df_e = energy_need.copy().reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

    df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
    df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000

    df = df.groupby(by=['year', 'building_category', 'TEK', 'purpose'], as_index=False).sum()
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
