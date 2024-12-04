from enum import unique, StrEnum

import pandas as pd
from loguru import logger

RESIDENTIAL = 'residential'
NON_RESIDENTIAL = 'non_residential'

@unique
class BuildingCategory(StrEnum):
    HOUSE = 'house'
    APARTMENT_BLOCK = 'apartment_block'
    KINDERGARTEN = 'kindergarten'
    SCHOOL = 'school'
    UNIVERSITY = 'university'
    OFFICE = 'office'
    RETAIL = 'retail'
    HOTEL = 'hotel'
    HOSPITAL = 'hospital'
    NURSING_HOME = 'nursing_home'
    CULTURE = 'culture'
    SPORTS = 'sports'
    STORAGE_REPAIRS = 'storage_repairs'

    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

    def yearly_construction_floor_area(self):
        logger.warning('Using static yearly_construction_floor_area')
        raise NotImplementedError(f'yearly_construction_floor_area does not support category {self.name} (yet)')

    def is_residential(self) -> bool:
        return self == BuildingCategory.HOUSE or self == BuildingCategory.APARTMENT_BLOCK

    def is_non_residential(self) -> bool:
        return not self.is_residential()

    @staticmethod
    def from_string(category_name: str) -> 'BuildingCategory':
        """Create an enum object from category name
        Args:
            category_name (str)

        Returns:
              building_category (BuildingCategory (Enum))

        Raises:
            ValueError: category_name not found in BuildingCategory
        """
        search = category_name.lower().replace(' ', '').replace('_', '')
        for building_category in iter(BuildingCategory):
            if search == building_category.value.lower().replace('_', ''):
                return building_category
        raise ValueError(f'No such building category {category_name}')


def from_norsk(norsk: str) -> BuildingCategory:
    if norsk.lower() == 'småhus':
        return BuildingCategory.HOUSE
    if norsk.lower() == 'leilighet':
        return BuildingCategory.APARTMENT_BLOCK
    if norsk.lower() == 'barnehage':
        return BuildingCategory.KINDERGARTEN
    if norsk.lower() == 'kontor':
        return BuildingCategory.OFFICE
    if norsk.lower() == 'skole':
        return BuildingCategory.SCHOOL
    if norsk.lower() == 'universitet':
        return BuildingCategory.UNIVERSITY
    if norsk.lower() == 'sykehjem':
        return BuildingCategory.NURSING_HOME
    if norsk.lower() == 'sykehus':
        return BuildingCategory.HOSPITAL
    if norsk.lower() == 'hotell':
        return BuildingCategory.HOTEL
    if norsk.lower() == 'idrettsbygg':
        return BuildingCategory.SPORTS
    if norsk.lower() == 'forretningsbygg':
        return BuildingCategory.RETAIL
    if norsk.lower() == 'kulturbygg':
        return BuildingCategory.CULTURE
    return BuildingCategory.from_string(norsk)


def expand_building_category(row):
    if row['building_category'] == NON_RESIDENTIAL:
        commercial = [b for b in BuildingCategory if b.is_non_residential()]
        values = {k: [v] * len(commercial) for k, v in row.to_dict().items() if k != 'building_category'}
        return pd.DataFrame({
            'building_category': commercial,
            **values
        })
    elif row['building_category'] == RESIDENTIAL:
        residential = [b for b in BuildingCategory if b.is_residential()]
        values = {k: [v] * len(residential) for k, v in row.to_dict().items() if k != 'building_category'}
        return pd.DataFrame({
            'building_category': residential,
            **values
        })
    else:
        return row


# Apply the function to each row and concatenate the results
def expand_building_categories(df: pd.DataFrame):
    """
    Transform dataframe so that building_categories within groups (residential/non-esidential) are unpacked
    into all containing categories. Duplicates categories are removed. Specific categories with values area
    preferred over category groups when there is a conflict.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    df = df.drop_duplicates(subset=['building_category'], ignore_index=True, keep='last')
    rows = [row for _, row in df.iterrows()]
    expanded_groups = list(filter(lambda bc: bc.building_category in (RESIDENTIAL, NON_RESIDENTIAL), rows))

    specific = df[~df.building_category.isin([RESIDENTIAL, NON_RESIDENTIAL])]
    specific_building_categories = specific.building_category.unique()

    expanded = [expand_building_category(row) for row in expanded_groups]
    filtered = list(filter(lambda bc: not bc.building_category.isin(specific_building_categories).any(), expanded))

    return pd.concat(filtered + [specific])
