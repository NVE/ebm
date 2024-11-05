import typing
from dataclasses import dataclass

import pandas as pd


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
    subset(offset: int = 0, length: int = -1) -> 'YearRange':
        Creates a subset YearRange of this year range.
    to_index() -> pd.Index:
        Converts the year_range to a pandas Index.

    Examples
    --------
    Slice pandas DataFrame with YearRange.

    >>> df = pd.DataFrame(data=['first', 'b', 'c', 'd', 'last'],
    ...                   index=[2010, 2011, 2012, 2013, 2014])
    >>> years = YearRange(2011, 2013)
    >>> df.loc[years]
          0
    2011  b
    2012  c
    2013  d
    >>>

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

    def __len__(self):
        return len(self.year_range)

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

    def subset(self, offset: int = 0, length: int = -1) -> 'YearRange':
        """
        Creates a subset YearRange of this year range.

        Parameters
        ----------
        offset : int
            How many years to skip after the first year.
        length : int, optional
            How many years to return after the offset. When -1, all remaining years are returned. Default: -1

        Returns
        -------
        year_range : YearRange

        Raises
        ------
        ValueError
            When `offset` is less than 0 or `offset` is greater than the number of years in the YearRange.

        Examples
        --------
        >>> YearRange(2010, 2016).subset(2,3)
        YearRange(start=2012, end=2014, year_range=(2012, 2013, 2014))
        >>> YearRange(2010, 2016).subset(2,-1)
        YearRange(start=2012, end=2016, year_range=(2012, 2013, 2014, 2015, 2016))
        >>> YearRange(2010, 2016).subset(3)
        YearRange(start=2013, end=2016, year_range=(2013, 2014, 2015, 2016))

        """
        if offset < 0:
            raise ValueError(f'Offset cannot be negative: {offset}')
        if offset + self.start > self.end:
            raise ValueError(f'Offset is out of range: {offset=} >= {len(self)}')
        start_year = self.start + offset
        last_year = start_year + length - 1 if length > 0 and start_year + length < self.end else self.end
        return YearRange(start_year, last_year)

    def to_index(self) -> pd.Index:
        """
        Converts the year_range to a pandas Index.

        Returns
        -------
        pd.Index
            Pandas Index object containing the years in the range.
        """
        return pd.Index(self.year_range, name='year')

    def __getitem__(self, key: int | slice) -> pd.Index:
        """
        Returns a pandas Index object for the specified slice of the year range.

        Parameters
        ----------
        key : int | slice
            The index or slice of the year range to return.

        Returns
        -------
        pd.Index
            A pandas Index object containing the specified years.
        """
        if isinstance(key, int):
            return pd.Index([self.year_range[key]])
        elif isinstance(key, slice):
            return pd.Index(self.year_range[key])
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
