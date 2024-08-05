import itertools

from openpyxl import load_workbook
from loguru import logger
import pandas as pd
import rich.pretty

from ebm.services.spreadsheet import iter_cells
from model import BuildingCategory

spreadsheet = 'C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/statiskBEMA_2019.xlsm'
spreadsheet = 'C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/st_bema2019_nybygging.xlsx'

logger.debug(f'Opening {spreadsheet}')
wb = load_workbook(spreadsheet)

sheet = wb[wb.sheetnames[0]] #wb['Nybygging']  # Nybygging


def load_row_series(row=104) -> pd.Series:
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


def load_building_category(start_row_no=97):
    column_letters = list(itertools.islice(iter_cells('E'), 0, 41))
    column_years = [year for year in range(2010, 2051)]
    return {
        'column': pd.Series(data=column_letters,
                            index=column_years),
        'total_floor_area': load_row_series(row=start_row_no),
        'building_growth': load_row_series(row=start_row_no + 1),
        'yearly_demolished_floor_area': load_row_series(row=start_row_no + 5),
        'floor_area_constructed': load_row_series(row=start_row_no + 6),
        'acc_floor_area_constructed': load_row_series(row=start_row_no + 7),
        'construction_rate': load_row_series(row=start_row_no + 11),
        'floor_area_over_population_growth': load_row_series(row=start_row_no + 12)
    }


def load_building_category_df(start_row: int) -> pd.DataFrame:
    foo = load_building_category(start_row)
    return pd.DataFrame(data=foo)


if __name__ == '__main__':
    building_category_rows = {
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

    for building_category, start_row in building_category_rows.items():
        df = load_building_category_df(start_row)
        print('===', '  '.join(building_category.name.split()), '===')
        rich.pretty.pprint(df.transpose())


