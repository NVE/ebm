import typing
from datetime import datetime
import os

from loguru import logger
import pandas as pd

from ebm.model import building_category
from ebm.model.energy_purpose import EnergyPurpose
from ebm.services.excel_loader import access_excel_sheet
from ebm.services.spreadsheet import SpreadsheetCell


class ComCalibrationReader:
    filename: str
    sheet_name: str
    df: pd.DataFrame

    def __init__(self, workbook_name=None, sheet_name=None):
        wb, sh = os.environ.get('EBM_CALIBRATION_SHEET', '!').split('!')
        self.workbook_name = wb if workbook_name is None else workbook_name
        self.sheet_name = sh if sheet_name is None else sheet_name

    def extract(self) -> pd.DataFrame:
        sheet = access_excel_sheet(self.workbook_name, self.sheet_name)
        used_range = sheet.UsedRange

        values = used_range.Value
        logger.debug(f'Found {len(values)} rows in {sheet}')

        return used_range.Value

    def transform(self, com_calibration_table: typing.Tuple) -> pd.DataFrame:
        def replace_building_category(row):
            for factor_name in row[2].split(' and '):
                try:
                    bc = building_category.from_norsk(row[0])
                except ValueError as value_error:
                    if row[0].lower() in ('yrksebygg', 'yrkesbygg'):
                        bc = building_category.NON_RESIDENTIAL
                    elif row[0].lower() == 'bolig':
                        bc = building_category.RESIDENTIAL
                erq = 'energy_requirement'
                purpose = EnergyPurpose(factor_name) if factor_name.lower() != 'elspesifikt' else EnergyPurpose.ELECTRICAL_EQUIPMENT
                yield bc, erq, purpose, row[3], None

        def handle_rows(rows):
            for row in rows:
                yield from replace_building_category(row)
        logger.debug(f'Transform {self.sheet_name}')
        data = com_calibration_table[1:]

        data = list(handle_rows([r for r in data if r[1] == 'Energibehov']))

        df = pd.DataFrame(data, columns=['building_category', 'group', 'purpose', 'heating_rv_factor', 'extra'])

        return df


class CalibrationResultWriter:
    workbook: str
    sheet: str
    df: pd.DataFrame
    distribution_of_heating_systems_by_building_group: pd.DataFrame

    def __init__(self):
        pass

    def extract(self) -> None:
        self.workbook, self.sheet = os.environ.get('EBM_CALIBRATION_OUT').split('!')
        access_excel_sheet(self.workbook, self.sheet)

    def transform(self, df) -> pd.DataFrame:
        self.df = df
        return df

    def load(self):
        sheet = access_excel_sheet(self.workbook, self.sheet)

        # Residential
        residential_columns = os.environ.get('EBM_CALIBRATION_ENERGY_USAGE_RESIDENTIAL')
        non_residential_columns = os.environ.get('EBM_CALIBRATION_ENERGY_USAGE_NON_RESIDENTIAL')

        first_cell, last_cell = residential_columns.split(':')
        first_row = int(first_cell[1:])
        self.update_energy_use(sheet, first_row, building_category.RESIDENTIAL, 4)

        first_cell, last_cell = non_residential_columns.split(':')
        first_row = int(first_cell[1:])
        self.update_energy_use(sheet, first_row, building_category.NON_RESIDENTIAL, 5)

        first_cell, last_cell = os.environ.get('EBM_CALIBRATION_ENERGY_HEATINGPUMP_RESIDENTIAL').split(':')
        first_row = int(first_cell[1:])
        self.update_pump(sheet, first_row, building_category.RESIDENTIAL, 4)
        self.update_pump(sheet, first_row, building_category.NON_RESIDENTIAL, 5)

        # Tag time
        sheet.Cells(70, 3).Value = datetime.now().isoformat()

    def update_energy_use(self, sheet, first_row, building_category, value_column):
        for row_number, (k, t) in enumerate(self.df.loc[building_category].items(), start=first_row):
            if k in ('luftluft', 'vannbåren'):
                continue
            column_name = sheet.Cells(row_number, 3).Value
            column_value = self.df.loc[building_category][column_name]
            logger.debug(f'{row_number=} {column_name=} {column_value=}')
            sheet.Cells(row_number, value_column).Value = column_value

    def update_pump(self, sheet, first_row, building_category, value_column):
        for row_number, (k, t) in enumerate(self.df.loc[building_category].items(), start=first_row):
            if k not in ('luftluft', 'vannbåren'):
                continue
            column_name = sheet.Cells(row_number-4, 3).Value
            column_value = self.df.loc[building_category][column_name]
            logger.debug(f'{row_number=} {column_name=} {column_value=}')
            sheet.Cells(row_number-4, value_column).Value = column_value


class HeatingSystemsDistributionWriter:
    """
    A class to handle the extraction, transformation, and loading of heating systems distribution data in a
    open Excel spreadsheet.

    Attributes
    ----------
    workbook : str
        The name of the workbook.
    sheet : str
        The name of the sheet.
    df : pd.DataFrame
        The DataFrame containing the data.
    cells_to_update : typing.List[SpreadsheetCell]
        List of cells to update.
    rows : typing.List[SpreadsheetCell]
        List of row header cells.
    columns : typing.List[SpreadsheetCell]
        List of column header cells.

    Methods
    -------
    extract() -> typing.Tuple[typing.List[SpreadsheetCell], typing.List[SpreadsheetCell]]
        Extracts the target cells and initializes row and column headers.
    transform(df) -> typing.Iterable[SpreadsheetCell]
        Transforms the DataFrame into a list of SpreadsheetCell objects to update.
    load()
        Loads the updated values into the Excel sheet.
    """
    workbook: str
    sheet: str
    target_cells: str
    df: pd.DataFrame
    cells_to_update: typing.List[SpreadsheetCell]
    rows: typing.List[SpreadsheetCell]
    columns: typing.List[SpreadsheetCell]

    def __init__(self,
                 excel_filename=None,
                 workbook='Kalibreringsark.xlsx',
                 sheet='Ut',
                 target_cells=None):
        """
        Initializes the HeatingSystemsDistributionWriter with empty lists for cells to update, rows, and columns.

        Parameters
        ----------
        excel_filename : str, optional
            Name of the target spreadsheet. If there is no ! and sheet name in excel_filename, the parameter sheet is
                used instead
        workbook : str, optinal
            Optional name of the spreadsheet to used for reading and writing. (default is 'Kalibreringsark.xlsx')
        sheet : str, optional
            Optional name of the sheet used for reading and writing. (default is 'Ut')
        target_cells : str, optional
            A range of cells that contain the data to update from the dataframe


        """

        self.workbook, self.sheet = os.environ.get('EBM_CALIBRATION_OUT', f'{workbook}{sheet}').split('!')

        self.workbook = workbook
        self.sheet = sheet
        self.target_cells = target_cells
        if not target_cells:
            self.target_cells = target_cells = os.environ.get('EBM_CALIBRATION_ENERGY_HEATING_SYSTEMS_DISTRIBUTION')

        if excel_filename:
            if '!' in excel_filename:
                self.workbook, self.sheet = excel_filename.split('!')
            else:
                self.workbook = excel_filename
        self.cells_to_update = []
        self.rows = []
        self.columns = []

    def extract(self) -> typing.Tuple[
            typing.Dict[int, SpreadsheetCell],
            typing.Dict[int, SpreadsheetCell],
            typing.Iterable[SpreadsheetCell]]:
        """
        Extracts the target cells and initializes row and column headers.

        Returns
        -------
        typing.Tuple[
            typing.Dict[int, SpreadsheetCell],
            typing.Dict[int, SpreadsheetCell],
            typing.Iterable[SpreadsheetCell]]

            A tuple containing lists of row, column header cells and cells to update.
        """
        # Create an instance of the Excel application
        sheet = access_excel_sheet(self.workbook, self.sheet)

        # Make index of columns and rows
        first_row = SpreadsheetCell.first_row(self.target_cells)
        self.columns = {cell.column: cell.replace(value=sheet.Cells(cell.row, cell.column).Value) for cell in first_row[1:]}

        first_column = SpreadsheetCell.first_column(self.target_cells)
        self.rows = {cell.row: cell.replace(value=sheet.Cells(cell.row, cell.column).Value) for cell in first_column[1:]}

        # Initialize value cells
        self.values = SpreadsheetCell.submatrix(self.target_cells)

        return self.rows, self.columns, self.values

    def transform(self, df: pd.DataFrame) -> typing.Iterable[SpreadsheetCell]:
        """
       Transforms the DataFrame into a list of SpreadsheetCell objects to update.

       Parameters
       ----------
       df : pd.DataFrame
           The DataFrame containing the data.

       Returns
       -------
       typing.Iterable[SpreadsheetCell]
           An iterable of SpreadsheetCell objects to update.
        """
        self.cells_to_update = []
        for cell in self.values:
            try:
                row_header = self.columns[cell.column].value
                column_header = self.rows[cell.row].value
                if row_header not in df.index:
                    raise KeyError(f'"{row_header}" not found')
                elif (row_header, column_header) not in df.index:
                    raise KeyError(f'"{column_header}" not found')
                value = df.loc[(row_header, column_header), 'TEK_shares']
            except KeyError as ex:
                logger.error(f'KeyError {str(ex)} while loading data for {cell.spreadsheet_cell()}')
                value = f'KeyError {str(ex)}'
            self.cells_to_update.append(SpreadsheetCell(row=cell.row, column=cell.column, value=value))

        return self.cells_to_update

    def load(self):
        """
        Loads the updated values into the Excel sheet defined in obj.workbook and obj.sheet.
        """
        sheet = access_excel_sheet(self.workbook, self.sheet)

        # Update cells
        for cell_to_update in self.cells_to_update:
            sheet.Cells(cell_to_update.row, cell_to_update.column).Value = cell_to_update.value

        # Tag time
        sheet.Cells(33, 2).Value = datetime.now().isoformat()
