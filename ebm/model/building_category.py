from enum import unique, StrEnum

import pandas as pd
from loguru import logger


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

    def is_commercial(self) -> bool:
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
    if row['building_category'] == 'commercial':
        commercial = [b for b in BuildingCategory if b.is_commercial()]
        values = {k: [v] * len(commercial) for k, v in row.to_dict().items() if k != 'building_category'}
        return pd.DataFrame({
            'building_category': commercial,
            **values
        })
    elif row['building_category'] == 'residential':
        residential = [b for b in BuildingCategory if b.is_residential()]
        values = {k: [v] * len(residential) for k, v in row.to_dict().items() if k != 'building_category'}
        return pd.DataFrame({
            'building_category': residential,
            **values
        })
    else:
        return row


# Apply the function to each row and concatenate the results
def expand_building_categories(df):
    return pd.concat([expand_building_category(row) for _, row in df.iterrows()], ignore_index=True)