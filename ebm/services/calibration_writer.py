import typing
from datetime import datetime
import os
import sys


from loguru import logger
import pandas as pd
import win32com.client
from win32com.universal import com_error

from ebm.model import building_category
from ebm.model.energy_purpose import EnergyPurpose


class ComCalibrationReader:
    filename: str
    sheet_name: str
    df: pd.DataFrame

    def __init__(self, workbook_name=None, sheet_name=None):
        wb, sh = os.environ.get('EBM_CALIBRATION_SHEET', '!').split('!')
        self.workbook_name = wb if workbook_name is None else workbook_name
        self.sheet_name = sh if sheet_name is None else sheet_name

    def extract(self) -> pd.DataFrame:
        logger.debug(f'Extract {self.sheet_name} from {self.workbook_name}')
        excel = win32com.client.Dispatch("Excel.Application")

        # Get the currently open workbooks
        workbooks = excel.Workbooks

        # Print the names of the currently open workbooks
        open_workbooks = [w.Name for w in workbooks]
        if self.workbook_name not in open_workbooks:
            raise IOError(f'Did not found open workbook {self.workbook_name}')
        logger.debug(f'Using {self.workbook_name} {self.sheet_name}')

        workbook = workbooks[self.workbook_name]

        # Now you can interact with the workbook, for example, read a cell value
        sheet = []
        try:
            sheet = workbook.Sheets(self.sheet_name)
        except com_error as ex:
            logger.error(f'Error opening {self.sheet_name}')
            for s in workbook.Sheets:
                logger.error(f'Found {s.Name}')
            raise ex

        sheet = workbook.Sheets(self.sheet_name)
        used_range = sheet.UsedRange

        values = used_range.Value
        logger.debug(f'Found {len(values)} rows in {sheet}')

        return used_range.Value

    def transform(self, com_calibration_table: typing.Tuple) -> pd.DataFrame:
        def replace_building_category(row):

            try:
                bc = building_category.from_norsk(row[0])
            except ValueError as value_error:
                if row[0] == 'Yrksebygg':
                    bc = building_category.NON_RESIDENTIAL
                elif row[0] == 'Bolig':
                    bc = building_category.RESIDENTIAL
            erq = 'energy_requirement'
            purpose = EnergyPurpose(row[2]) if row[2].lower() != 'elspesifikt' else EnergyPurpose.ELECTRICAL_EQUIPMENT
            return bc, erq, purpose, row[3], None
        logger.debug(f'Transform {self.sheet_name}')
        data = com_calibration_table[1:]

        data = [replace_building_category(r) for r in data if r[1] == 'Energibehov']

        df = pd.DataFrame(data, columns=['building_category', 'group', 'purpose', 'heating_rv_factor', 'extra'])

        return df

    def load(self):
        logger.debug(f'Save {self.sheet_name} {self.workbook_name} to csv')


class CalibrationResultWriter:
    workbook: str
    sheet: str
    df: pd.DataFrame

    def __init__(self):
        pass

    def extract(self) -> typing.Tuple:
        self.workbook, self.sheet = os.environ.get('EBM_CALIBRATION_OUT').split('!')

        # Create an instance of the Excel application
        excel = win32com.client.Dispatch("Excel.Application")

        # Get the currently open workbooks
        workbooks = excel.Workbooks

        # Print the names of the currently open workbooks
        for workbook in workbooks:
            logger.debug(f"Open Workbook: {workbook.Name}")

        logger.debug(f'Using {self.workbook} {self.sheet}')
        # Access a specific workbook by name
        workbook_name = self.workbook
        workbook = workbooks[workbook_name]

        # Now you can interact with the workbook, for example, read a cell value
        sheet = []
        try:
            sheet = workbook.Sheets(self.sheet)
        except com_error as ex:
            logger.error(f'Error opening {self.sheet}')
            for s in workbook.Sheets:
                logger.error(f'Found {s.Name}')
            raise ex

    def transform(self, df) -> pd.DataFrame:
        self.df = df

    def load(self):
        # Create an instance of the Excel application
        excel = win32com.client.Dispatch("Excel.Application")

        # Get the currently open workbooks
        workbooks = excel.Workbooks

        # Print the names of the currently open workbooks
        for workbook in workbooks:
            logger.debug(f"Open Workbook: {workbook.Name}")

        logger.debug(f'Using {self.workbook} {self.sheet}')
        # Access a specific workbook by name
        workbook_name = self.workbook
        workbook = workbooks[workbook_name]

        # Now you can interact with the workbook, for example, read a cell value
        sheet = []
        try:
            sheet = workbook.Sheets(self.sheet)
        except com_error as ex:
            logger.error(f'Error opening {self.sheet}')
            for s in workbook.Sheets:
                logger.error(f'Found {s.Name}')
            raise ex

        # Residential
        residential_columns = os.environ.get('EBM_CALIBRATION_ENERGY_USAGE_RESIDENTIAL')
        non_residential_columns = os.environ.get('EBM_CALIBRATION_ENERGY_USAGE_NON_RESIDENTIAL')

        first_cell, last_cell = residential_columns.split(':')

        first_column = first_cell[0]
        first_row = int(first_cell[1:])

        for row_number, (k, t) in enumerate(self.df.loc['residential'].items(), start=first_row):
            if k in ('luftluft', 'vannbåren'):
                continue
            column_name = sheet.Cells(row_number, 3).Value
            column_value = self.df.loc['residential'][column_name]
            logger.debug(f'{row_number=} {column_name=} {column_value=}')
            sheet.Cells(row_number, 4).Value = column_value

        first_cell, last_cell = non_residential_columns.split(':')

        first_column = first_cell[0]
        first_row = int(first_cell[1:])

        sheet.Cells(55, 6).Value = datetime.now().isoformat()
        for row_number, (k, t) in enumerate(self.df.loc['commercial'].items(), start=first_row):
            if k in ('luftluft', 'vannbåren'):
                continue
            column_name = sheet.Cells(row_number, 3).Value
            column_value = self.df.loc['commercial'][column_name]
            logger.debug(f'{row_number=} {column_name=} {column_value=}')
            sheet.Cells(row_number, 5).Value = column_value

        # Tag time
        sheet.Cells(55, 7).Value = datetime.now().isoformat()
