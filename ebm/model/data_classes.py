import typing
from dataclasses import dataclass


@dataclass
class ScurveParameters:
    building_category: str
    condition: str	
    earliest_age: int
    average_age: int
    rush_years: int	
    last_age: int
    rush_share: float
    never_share: float


@dataclass
class TEKParameters:
    tek: str
    building_year: int
    start_year: int
    end_year: int


@dataclass(frozen=True)
class YearRange:
    """
    A class to represent a period model with a start and end year.

    Attributes
    ----------
    start : int
        The starting year of the period.
    end : int
        The ending year of the period.
    year_range : tuple of int
        A tuple containing all years in the period from start to end (inclusive).

    Methods
    -------
    __post_init__():
        Initializes the years attribute after the object is created.
    __iter__():
        Returns an iterator over the years in the period.
    range() -> tuple of int:
        Returns a tuple of years from start to end (inclusive).


    """

    start: int
    end: int
    year_range: typing.Tuple[int] = tuple()

    def __post_init__(self):
        """
        Initializes the years attribute after the object is created.
        """
        if self.start > self.end:
            raise ValueError(f'Start year {self.start} cannot be greater than end year {self.end}')
        object.__setattr__(self, 'year_range', self.range())

    def __iter__(self) -> typing.Generator[int, None, None]:
        """
        Returns an iterator over the years in the period.

        Yields
        ------
        int
            The next year in the period.
        """
        for y in self.year_range:
            yield y

    def range(self) -> typing.Tuple[int]:
        """
        Returns a tuple of years from start to end for use with indexes and such.

        Returns
        -------
        tuple of int
            Tuple containing all years in sequence from start to end (inclusive).
        """
        return tuple(range(self.start, self.end + 1))
