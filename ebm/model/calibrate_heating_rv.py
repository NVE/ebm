from datetime import datetime
import os
import pathlib
import typing

from loguru import logger
import pandas as pd
import win32com.client
from win32com.universal import com_error


def transform(heating_rv: pd.Series, heating_rv_factor=None) -> pd.Series:
    if heating_rv_factor is None:
        return heating_rv
    calibrated = heating_rv * heating_rv_factor
    calibrated.name = heating_rv.name
    return calibrated


def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'heating_rv_factor': [1.0, 1.0]})
    return df


class EbmCalibration:
    energy_requirement_original_condition: pd.Series
    pass

class ComExcelCalibrationReader:
    """ Extract relevant cells from workbook and sheet and convert
        transform to EbmCalibration or pd.DataFrame?

    """

    com_excel_calibration: typing.Dict
    def extract(self) -> pd.DataFrame:
        """
            Trenger workbook, sheet ?, kan vel hardkode cells i starten
            returnerer dataframe som er 1 til 1 fra excel?

        """

        pass

    def transform(self, df) -> EbmCalibration:
        """ Konvertere dataframe til en som passer kalibrering
            "gruppe", building_category, heating_rv, faktor <--- building_category skal være pakket ut?

        """
        pass


class CalibrationReader:
    def extract(self) -> pd.Series:
        pass

    def transform(self) -> pd.Series:
        pass

    def load(self) -> None:
        pass


class CalibrationWriter:
    pass


class CalibrationResultWriter:
    filename: str
    sheet: str
    df: pd.DataFrame

    def __init__(self):
        pass

    def extract(self):
        workbook_name, sheet_name = os.environ.get('EBM_CALIBRATION_OUT').split('!')
        self.filename = workbook_name
        self.sheet = sheet_name

        # Create an instance of the Excel application
        excel = win32com.client.Dispatch("Excel.Application")

        # Get the currently open workbooks
        workbooks = excel.Workbooks

        # Print the names of the currently open workbooks
        for workbook in workbooks:
            logger.debug(f"Open Workbook: {workbook.Name}")

        logger.debug(f'Using {self.filename} {self.sheet}')
        # Access a specific workbook by name
        workbook_name = self.filename
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

    def transform(self, df):
        self.df = df

    def load(self):
        # Create an instance of the Excel application
        excel = win32com.client.Dispatch("Excel.Application")

        # Get the currently open workbooks
        workbooks = excel.Workbooks

        # Print the names of the currently open workbooks
        for workbook in workbooks:
            logger.debug(f"Open Workbook: {workbook.Name}")

        logger.debug(f'Using {self.filename} {self.sheet}')
        # Access a specific workbook by name
        workbook_name = self.filename
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
