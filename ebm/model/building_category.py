import typing
from enum import EnumType, StrEnum, unique

import pandas as pd
from loguru import logger

RESIDENTIAL = 'residential'
NON_RESIDENTIAL = 'non_residential'


class MyEnumType(EnumType):
    def __contains__(cls, value):
        return value in cls._value2member_map_


@unique
class BuildingCategory(StrEnum, metaclass=MyEnumType):
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
    STORAGE = 'storage_repairs'

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
    if norsk.lower()  in ('leilighet', 'boligblokk'):
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


def expand_building_category(row: pd.Series) -> pd.DataFrame:
    """
        Expand a row of data based on the building category into multiple rows,
        each representing a specific sub-category of either residential or non-residential buildings.

        Parameters
        ----------
        row : pd.Series
            A pandas Series containing the data for a single row, including a 'building_category' field.

        Returns
        -------
        pd.DataFrame
            A DataFrame with expanded rows for each sub-category of the building category.
    """
    if row['building_category'] in BuildingCategory:
        return pd.DataFrame([row.to_dict()])
    if row['building_category'] == NON_RESIDENTIAL:
        categories = [b for b in BuildingCategory if b.is_non_residential()]
    elif row['building_category'] == RESIDENTIAL:
        categories = [b for b in BuildingCategory if b.is_residential()]

    values = {k: [v] * len(categories) for k, v in row.to_dict().items() if k != 'building_category'}

    return pd.DataFrame({
        'building_category': categories,
        **values
    })


# Apply the function to each row and concatenate the results
def expand_building_categories(df: pd.DataFrame, unique_columns: typing.List[str] = None):
    """
    Transform input dataframe so that building_category within groups (residential/non-residential) are unpacked
    into all containing categories. Duplicates categories are removed. Specific categories with values area
    preferred over category groups when there is a conflict.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
    unique_columns : str
        list of column names that should be treated as joint unique. default: ['building_category']


    Returns
    -------
    pandas.core.frame.DataFrame
    """
    if unique_columns:
        df = df.drop_duplicates(subset=unique_columns, ignore_index=True, keep='last')
    groups = df[df.building_category.isin([RESIDENTIAL, NON_RESIDENTIAL])]
    specific = df[~df.building_category.isin(groups.building_category)]

    expanded_groups = [expand_building_category(row) for _, row in groups.iterrows()]

    filtered = [d[~d.building_category.isin(specific.building_category)] for d in expanded_groups]

    return pd.concat(filtered + [specific]).reindex()


def collapse_building_category(building_category: pd.Series) -> pd.Series:
    """
    Replace building category labels with building group labels where appropriate.

    This function takes a pandas Series containing building category strings
    separated by either "+" or ",". It normalizes token case, applies a set of
    category‑collapse rules, and returns a new Series with collapsed category
    labels.

    building groups implemented:
     - residential
         house, apartment_block
     - non_residential
         culture, hospital, hotel, kindergarten, nursing_home, office, retail, school, sports, storage_repairs, university
     - default
         All of the above

    Parameters
    ----------
    building_category : pd.Series
        Series of building category strings. Each value must be a
            string containing tokens separated by either ``"+"`` or `","``.
            Tokens may contain arbitrary casing; they are normalized to lowercase.

    Returns
    -------
    pd.Series
        series with building categories collapsed into groups

    Examples
    --------
    >>> import pandas as pd
    >>> collapse_building_category(pd.Series(["house+apartment_block"]))
    0    residential
    dtype: object

    >>> collapse_building_category(pd.Series(
    ...     ["culture+hospital+hotel+kindergarten+nursing_home+office+retail"
    ...      "+school+sports+storage_repairs+university"]
    ... ))
    0    non_residential
    dtype: object
    """
    def normalize(val: str) -> str:
        split_token = '+' if '+' in val else ','
        tokens = [t.strip().lower() for t in val.split(split_token)]
        to_remove = set()
        to_add = set()
        if 'apartment_block' in set(tokens) and 'house' in set(tokens):
            to_remove.add('apartment_block')
            to_remove.add('house')
            to_add.add('residential')
        if {'culture', 'hospital', 'hotel', 'kindergarten', 'nursing_home', 'office', 'retail', 'school', 'sports', 'storage_repairs', 'university'}.issubset(tokens):
            to_add.add('non_residential')
            to_remove.update({'culture', 'hospital', 'hotel', 'kindergarten', 'nursing_home', 'office', 'retail', 'school', 'sports', 'storage_repairs', 'university'})
        if {'residential', 'non_residential'}.issubset(to_add):
            to_add.remove('residential')
            to_add.remove('non_residential')
            to_add.add('default')

        return split_token.join(list(to_add) + [t for t in tokens if t not in to_remove])

    s = building_category.astype(str).copy()

    return s.apply(normalize)


