import dataclasses
import itertools
import typing
import string
from dataclasses import dataclass

from openpyxl.utils.cell import cols_from_range, coordinate_to_tuple, get_column_letter


@dataclass
class SpreadsheetCell:
    column: int
    row: int
    value: object

    def spreadsheet_cell(self) -> str:
        return f'{get_column_letter(self.column)}{self.row}'

    def replace(self, **kwargs) -> 'SpreadsheetCell':
        obj = dataclasses.replace(self)
        if 'value' in kwargs:
            obj.value = kwargs.get('value')
        return obj

    @classmethod
    def first_row(cls, cell_range):
        table = list(cols_from_range(cell_range))
        first_row = [coordinate_to_tuple(cols[0]) for cols in table]
        return tuple(SpreadsheetCell(column=c[1], row=c[0], value=None) for c in first_row)

    @classmethod
    def first_column(cls, cell_range):
        table = list(cols_from_range(cell_range))
        first_column = [coordinate_to_tuple(cell) for cell in table[0]]
        return tuple(SpreadsheetCell(column=cell[1], row=cell[0], value=None) for cell in first_column)

    @classmethod
    def submatrix(cls, cell_range):
        table = list(cols_from_range(cell_range))
        first_column = [coordinate_to_tuple(cell) for cell in table[0]]
        first_row = [coordinate_to_tuple(cols[0]) for cols in table]
        box = []
        for row in table:
            for column in row:
                r, c = coordinate_to_tuple(column)
                if (r, c) not in first_column and (r, c) not in first_row:
                    box.append(SpreadsheetCell(column=c, row=r, value=None))

        return tuple(sorted(box, key=lambda k: (k.row, k.column)))


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
