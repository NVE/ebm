import itertools
import re
import typing
import string
from dataclasses import dataclass


def split_string_at_first_number(s):
    match = re.search(r'\d', s)
    if match:
        index = match.start()
        return s[:index], s[index:]
    return s, ''


@dataclass
class SpreadsheetCell:
    row: int
    column: int
    value: typing.Union[str, None]

    @classmethod
    def first_row(cls, cell_range):
        first_column, last_column = cls.cell_range_to_cells(cell_range)
        first_column_index = ord(first_column[0]) - ord('A') + 1
        last_column_index = ord(last_column[0]) - ord('A') + 1
        column_range = list(range(first_column_index, last_column_index + 1))
        first_row_index = int(first_column[1])
        return tuple(SpreadsheetCell(column=c, row=first_row_index, value=None) for c in column_range)

    @classmethod
    def cell_range_to_cells(cls, cell_range):
        cell_range = cell_range.upper()
        a1 = cell_range.split(':')[0] if ':' in cell_range else cell_range
        b3 = cell_range.split(':')[1] if ':' in cell_range else cell_range
        if not a1.strip():
            raise ValueError(f'Unexpected cell range {cell_range}. Expected range like A1:B3 or A1.')
        first_column, last_column = split_string_at_first_number(a1), split_string_at_first_number(b3)
        return first_column, last_column

    @classmethod
    def first_column(cls, cell_range):
        first_column, last_column = cls.cell_range_to_cells(cell_range)
        first_column_index = ord(first_column[0]) - ord('A') + 1
        first_row_index = int(first_column[1])
        last_row_index = int(last_column[1])
        row_range = list(range(first_row_index, last_row_index + 1))

        return tuple(SpreadsheetCell(column=first_column_index, row=r, value=None) for r in row_range)


def iter_cells(first_column: str = 'E', left_padding: str = '') -> typing.Generator[str, None, None]:
    """ Returns spreadsheet column names from A up to ZZ
        Parameters:
        - first_column Letter of the first column to return. Default (E)
        - left_padding Padding added in front of single letter columns. Default empty
        Returns:
        - Generator supplying a column name
    """
    if not first_column:
        first_index = 0
    elif first_column.upper() not in string.ascii_uppercase:
        raise ValueError(f'Expected first_column {first_column} in {string.ascii_uppercase}')
    elif len(first_column) != 1:
        raise ValueError(f'Expected first_column of length 1 was: {len(first_column)}')
    else:
        first_index = string.ascii_uppercase.index(first_column.upper())
    for cell in string.ascii_uppercase[first_index:]:
        yield f'{left_padding}{cell}'
    for a, b in itertools.product(string.ascii_uppercase, repeat=2):
        yield a+b
