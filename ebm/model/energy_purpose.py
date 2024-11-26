import typing

from enum import StrEnum, unique, auto


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
