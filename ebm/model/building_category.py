from enum import Enum


class BuildingCategory(Enum):
    HOUSE = 1
    APARTMENT_BLOCK = 2
    KINDERGARTEN = 3
    SCHOOL = 4
    UNIVERSITY = 5
    OFFICE = 6
    RETAIL = 7
    HOTEL = 8
    HOSPITAL = 9
    NURSING_HOME = 10
    CULTURE = 11
    SPORTS = 12
    STORAGE_REPAIRS = 13

    def __str__(self):
        return self.name.lower().replace('_', ' ')

    def yearly_construction_floor_area(self):
        if self == BuildingCategory.KINDERGARTEN:
            return 97_574, 90_644, 65_847, 62_022, 79_992,
        if self == BuildingCategory.UNIVERSITY:
            return 112_747, 49_205, 44_100, 34_766, 84_340,
        if self == BuildingCategory.OFFICE:
            return 443_334, 355_103, 649_466, 531_348, 320_478,

        raise NotImplementedError(f'yearly_construction_floor_area does not support category {self.name} (yet)')

    def total_floor_area_2010(self) -> int:
        if self == BuildingCategory.KINDERGARTEN:
            return 1_275_238
        if self == BuildingCategory.SCHOOL:
            return 13_884_666
        if self == BuildingCategory.UNIVERSITY:
            return 2_440_242
        if self == BuildingCategory.OFFICE:
            return 26_769_695
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
        search = category_name.upper().replace(' ', '')
        for building_category in iter(BuildingCategory):
            if search == building_category.name.replace('_', ''):
                return building_category
        raise ValueError(f'No such building category {category_name}')

