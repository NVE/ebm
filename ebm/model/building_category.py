from enum import unique, StrEnum

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

#    def __str__(self):
#        return self.name.lower().replace('_', ' ')

    def yearly_construction_floor_area(self):
        logger.warning('Using static yearly_construction_floor_area')
        raise NotImplementedError(f'yearly_construction_floor_area does not support category {self.name} (yet)')

    def is_residential(self) -> bool:
        return self == BuildingCategory.HOUSE or self == BuildingCategory.APARTMENT_BLOCK
    
    #TODO: remove
    def total_floor_area_2010(self) -> int:
        logger.warning('Using static total_floor_area_2010')
        if self == BuildingCategory.KINDERGARTEN:
            return 1275238
        if self == BuildingCategory.SCHOOL:
            return 13884666
        if self == BuildingCategory.UNIVERSITY:
            return 2440242
        if self == BuildingCategory.OFFICE:
            return 26769695
        if self == BuildingCategory.RETAIL:
            return 30378557
        if self == BuildingCategory.HOTEL:
            return 5714517
        if self == BuildingCategory.HOSPITAL:
            return 4752999
        if self == BuildingCategory.NURSING_HOME:
            return 5215597
        if self == BuildingCategory.CULTURE:
            return 2899338
        if self == BuildingCategory.SPORTS:
            return 2323323
        if self == BuildingCategory.STORAGE_REPAIRS:
            return 29328483

        raise NotImplementedError(f'total_floor_area_2010 does not support building category {self.name} (yet)')

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
