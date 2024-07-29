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

