import pytest

from ebm.services.spreadsheet import SpreadsheetCell


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

