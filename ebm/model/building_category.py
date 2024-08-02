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
        if self == BuildingCategory.SCHOOL:
            return 281_884, 206_298, 224_638, 295_082, 256_470,
        if self == BuildingCategory.RETAIL:
            return 555_903, 586_000, 640_545, 636_006, 687_111
        if self == BuildingCategory.HOTEL:
            return 166_371,	157_465, 133_144,69_857, 174_050
        if self == BuildingCategory.HOSPITAL:
            return 67_455, 33_747, 9_477, 30_942, 10_821
        if self == BuildingCategory.NURSING_HOME:
            return 69_803, 60_648, 47_932, 84_639, 90_631
        if self == BuildingCategory.CULTURE:
            return 43_646, 72_625, 73_971, 50_951, 47_282
        if self == BuildingCategory.SPORTS:
            return 137_744, 146_106, 173_818, 185_307, 119_111
        if self == BuildingCategory.STORAGE_REPAIRS:
            return 33_755, 33_755, 33_755, 33_755, 33_755,

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
        if self == BuildingCategory.RETAIL:
            return 30_378_557
        if self == BuildingCategory.HOTEL:
            return 5_714_517
        if self == BuildingCategory.HOSPITAL:
            return 4_752_999
        if self == BuildingCategory.NURSING_HOME:
            return 5_215_597
        if self == BuildingCategory.CULTURE:
            return 2_899_338
        if self == BuildingCategory.SPORTS:
            return 2_323_323
        if self == BuildingCategory.STORAGE_REPAIRS:
            return 29_328_483

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

