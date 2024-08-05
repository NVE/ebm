import itertools

from loguru import logger
from openpyxl import load_workbook, Workbook
import pandas as pd

#from ebm.model.building_category import BuildingCategory
from ebm.model import BuildingCategory
from ebm.services.spreadsheet import iter_cells

spreadsheet_location = 'C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/st_bema2019_nybygging.xlsx'

construction_building_category_rows = {
    BuildingCategory.HOUSE: 11,
    BuildingCategory.APARTMENT_BLOCK: 23,
    BuildingCategory.KINDERGARTEN: 41,
    BuildingCategory.SCHOOL: 55,
    BuildingCategory.UNIVERSITY: 69,
    BuildingCategory.OFFICE: 83,
    BuildingCategory.RETAIL: 97,
    BuildingCategory.HOTEL: 111,
    BuildingCategory.HOSPITAL: 125,
    BuildingCategory.NURSING_HOME: 139,
    BuildingCategory.CULTURE: 153,
    BuildingCategory.SPORTS: 167,
    BuildingCategory.STORAGE_REPAIRS: 182
}


def load_row_series(sheet, row=104) -> pd.Series:
    logger.debug(f'loading {row=}')
    title = sheet[f'D{row}'].value
    years = []
    cells = []
    columns = []
    values = []
    for column, year in zip(itertools.islice(iter_cells(first_column='E'), 0, 41), range(2010, 2051)):
        years.append(year)
        cell = f'{column}{row}'
        columns.append(column)
        cells.append(cell)
        values.append(sheet[f'{cell}'].value)

    accumulated_construction = pd.Series(data=values, index=years, name=title)
    accumulated_construction.index.name = 'year'
    return accumulated_construction


def load_building_category(sheet, start_row_no=97):
    column_letters = list(itertools.islice(iter_cells('E'), 0, 41))
    column_years = [year for year in range(2010, 2051)]
    return {
        'column': pd.Series(data=column_letters,
                            index=column_years),
        'total_floor_area': load_row_series(sheet=sheet, row=start_row_no),
        'building_growth': load_row_series(sheet=sheet, row=start_row_no + 1),
        'demolished_floor_area': load_row_series(sheet=sheet, row=start_row_no + 5),
        'constructed_floor_area': load_row_series(sheet=sheet, row=start_row_no + 6),
        'accumulated_constructed_floor_area': load_row_series(sheet=sheet, row=start_row_no + 7),
        'construction_rate': load_row_series(sheet=sheet, row=start_row_no + 11),
        'floor_area_over_population_growth': load_row_series(sheet=sheet, row=start_row_no + 12)
    }


def load_construction_df(sheet, start_row: int) -> pd.DataFrame:
    foo = load_building_category(sheet, start_row)
    return pd.DataFrame(data=foo)


def load_construction_building_category(sheet: Workbook, building_category: BuildingCategory) -> pd.DataFrame:
    logger.debug(building_category)
    b_c = construction_building_category_rows.get(building_category)
    series = load_building_category(sheet, b_c)
    return pd.DataFrame(data=series)


def load_bema_construction(filename=spreadsheet_location):
    wb = load_workbook(filename)
    worksheet_name = 'Nybygging' if 'Nybygging' in wb.sheetnames else wb.sheetnames[0]
    sheet = wb[worksheet_name]  # wb['Nybygging']  # Nybygging

    return sheet

    df = load_construction_df(sheet, start_row)

    print('===', '  '.join(building_category.name.split()), '===')
    rich.pretty.pprint(df.transpose())
    return sheet
