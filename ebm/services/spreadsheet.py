import itertools
import pathlib
import typing
import string

import pandas as pd
from openpyxl import load_workbook


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


def calculate_house_floor_area_demolished_by_year() -> pd.DataFrame:
    p = pathlib.Path(
        "C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/st_bema2019_a_hus.xlsx")
    wb = load_workbook(filename=p)
    sheet_ranges = wb.sheetnames
    sheet = wb[sheet_ranges[0]]
    cells = list(iter_cells(first_column='E'))[:41]

    a_hus_revet = pd.DataFrame({'demolition': [sheet[f'{c}656'].value for c in cells]}, index=list(range(2010, 2051)))
    a_hus_revet['demolition'] = a_hus_revet['demolition']
    a_hus_revet['demolition_change'] = a_hus_revet.demolition.diff(1).fillna(0)
    a_hus_revet.index = a_hus_revet.index.rename('year')

    return a_hus_revet
