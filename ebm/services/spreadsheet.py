import dataclasses
import itertools
import typing
import string
from dataclasses import dataclass

from openpyxl.utils.cell import cols_from_range, coordinate_to_tuple, get_column_letter


@dataclass
class SpreadsheetCell:
    """
    A class to represent a cell in a spreadsheet.

    Attributes
    ----------
    column : int
        The column number of the cell.
    row : int
        The row number of the cell.
    value : object
        The value contained in the cell.

    Methods
    -------
    spreadsheet_cell() -> str
        Returns the cell's address in A1 notation.
    replace(**kwargs) -> 'SpreadsheetCell'
        Returns a new SpreadsheetCell with updated attributes.
    first_row(cell_range) -> tuple
        Returns the first row of cells in the given range.
    first_column(cell_range) -> tuple
        Returns the first column of cells in the given range.
    submatrix(cell_range) -> tuple
        Returns the submatrix excluding the first row and column.
    """

    column: int
    row: int
    value: object

    def spreadsheet_cell(self) -> str:
        """
        Returns the cell's address in A1 notation.

        Returns
        -------
        str
            The cell's address in A1 notation.
        """
        return f'{get_column_letter(self.column)}{self.row}'

    def replace(self, **kwargs) -> 'SpreadsheetCell':
        """
        Returns a new SpreadsheetCell with updated attributes.

        Parameters
        ----------
        **kwargs : dict
            The attributes to update.

        Returns
        -------
        SpreadsheetCell
            A new SpreadsheetCell with updated attributes.
        """
        return dataclasses.replace(self, **kwargs)

    @classmethod
    def first_row(cls, cell_range):
        """
        Returns the first row of cells in the given range.

        Parameters
        ----------
        cell_range : str
            The range of cells in A1 notation.

        Returns
        -------
        tuple
            A tuple of SpreadsheetCell objects representing the first row.
        """
        table = list(cols_from_range(cell_range))
        first_row = [coordinate_to_tuple(rows[0]) for rows in table]
        return tuple(SpreadsheetCell(column=cell[1], row=cell[0], value=None) for cell in first_row)

    @classmethod
    def first_column(cls, cell_range):
        """
        Returns the first column of cells in the given range.

        Parameters
        ----------
        cell_range : str
            The range of cells in A1 notation.

        Returns
        -------
        tuple
            A tuple of SpreadsheetCell objects representing the first column.
        """
        table = list(cols_from_range(cell_range))
        first_column = [coordinate_to_tuple(cell) for cell in table[0]]
        return tuple(SpreadsheetCell(column=cell[1], row=cell[0], value=None) for cell in first_column)

    @classmethod
    def submatrix(cls, cell_range):
        """
        Returns the submatrix excluding the first row and column.

        Parameters
        ----------
        cell_range : str
            The range of cells in A1 notation.

        Returns
        -------
        tuple
            A tuple of SpreadsheetCell objects representing the submatrix.

        Examples
        --------
        the_range = "A1:C3"
        submatrix = SpreadsheetCell.submatrix(the_range)
        for cell in submatrix:
            print(cell.spreadsheet_cell(), cell.column, cell.row)

        B2 2 2
        C2 3 2
        B3 2 3
        C3 3 3
        """
        table = list(cols_from_range(cell_range))
        first_column = [coordinate_to_tuple(cell) for cell in table[0]]
        first_row = [coordinate_to_tuple(cols[0]) for cols in table]
        box = []
        for row in table:
            for column in row:
                row_idx, column_idx = coordinate_to_tuple(column)
                if (row_idx, column_idx) not in first_column and (row_idx, column_idx) not in first_row:
                    box.append(SpreadsheetCell(column=column_idx, row=row_idx, value=None))

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
