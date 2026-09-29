import pandas as pd
import pytest

from ebm.services.spreadsheet import SpreadsheetCell, detect_format_from_values



def test_spreadsheet_cell_first_row():
    assert SpreadsheetCell.first_row("A1:C3") == (
        SpreadsheetCell(row=1, column=1, value=None),
        SpreadsheetCell(row=1, column=2, value=None),
        SpreadsheetCell(row=1, column=3, value=None),
    )

    assert SpreadsheetCell.first_row("B2:B4") == (
        SpreadsheetCell(row=2, column=2, value=None),
    )

    assert SpreadsheetCell.first_row("B2") == (
        SpreadsheetCell(row=2, column=2, value=None),
    )

    with pytest.raises(ValueError):
        SpreadsheetCell.first_row(':B4')


def test_spreadsheet_cell_first_column():
    assert SpreadsheetCell.first_column("A1:C3") == (
        SpreadsheetCell(row=1, column=1, value=None),
        SpreadsheetCell(row=2, column=1, value=None),
        SpreadsheetCell(row=3, column=1, value=None),
    )

    assert SpreadsheetCell.first_column("B2:B4") == (
        SpreadsheetCell(row=2, column=2, value=None),
        SpreadsheetCell(row=3, column=2, value=None),
        SpreadsheetCell(row=4, column=2, value=None),
    )


def test_spreadsheet_submatrix():
    assert SpreadsheetCell.submatrix("A1:C4") == (
        SpreadsheetCell(column=2, row=2, value=None),
        SpreadsheetCell(column=3, row=2, value=None),
        SpreadsheetCell(column=2, row=3, value=None),
        SpreadsheetCell(column=3, row=3,  value=None),
        SpreadsheetCell(column=2, row=4, value=None),
        SpreadsheetCell(column=3, row=4,  value=None),
    )


@pytest.mark.parametrize(('col_name', 'col_values', 'expected_format'), [
    ('building_category', ['house'], ''),
    ('building_code', ['PRE_TEK49'], ''),
    (2020, [941109.5047619069], '# ##0'),
    (2020, [123], '#,##0'),
])
def test_detect_format_from_values_shorter(col_name, col_values, expected_format):
    values = pd.Series(col_values)
    df = pd.DataFrame({
        'building_category': ['house'],
        'building_code': ['PRE_TEK49'],
        'building_condition': ['original_condition'],
        'U': ['m2'],
        2020: values,
    })

    assert detect_format_from_values(col_name=col_name, col_values=values, model=df) == expected_format


