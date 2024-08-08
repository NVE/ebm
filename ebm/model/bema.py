import itertools
import typing

from loguru import logger
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd

from ebm.model import BuildingCategory
from ebm.services.spreadsheet import iter_cells


def load_row_series(worksheet: Worksheet, row: int = 104) -> pd.Series:
    """ Load a row starting from column E and continue for 40 columns (2010 - 2050)
        series title is read from column D
               Args:
                   worksheet (Worksheet) the worksheet to retrieve
                   row (int) row number to read

               Returns:
                     row_series (pd.Series)
    """
    logger.debug(f'loading {row=}')
    title = worksheet[f'D{row}'].value
    years = list(range(2010, 2051))
    columns = list(itertools.islice(iter_cells(first_column='E'), 0, 41))

    values = []
    for column, year in zip(columns, years):
        cell_address = f'{column}{row}'
        values.append(worksheet[f'{cell_address}'].value)

    row_series = pd.Series(
        data=values,
        index=years,
        name=title)

    row_series.index.name = 'year'
    return row_series


def load_building_category_from_rows(worksheet: Worksheet, start_row_no: int = 97) -> typing.Dict[str, pd.Series]:
    """ Load rows related to building_category construction  using start_row from worksheet. The function
        assume the worksheet is formatted like `BEMA 2019-Tekniske kommentarer.XLSM`. With `house` starting at E11
        then reading the other rows relative to 11.

            Args:
                worksheet (Worksheet) the worksheet to retrieve
                start_row_no (int)

            Returns:
                  construction (typing.Dict[str, pd.Series])
                    keys:
                        - column (example E)
                        - total_floor_area
                        - demolished_floor_area
                        - constructed_floor_area
                        - accumulated_constructed_floor_area
                        - construction_rate
                        - floor_area_over_population_growth
            """
    column_letters = list(itertools.islice(iter_cells('E'), 0, 41))
    column_years = [year for year in range(2010, 2051)]
    return {
        'column': pd.Series(data=column_letters, index=column_years),
        'total_floor_area': load_row_series(worksheet=worksheet, row=start_row_no),
        'building_growth': load_row_series(worksheet=worksheet, row=start_row_no + 1),
        'demolished_floor_area': load_row_series(worksheet=worksheet, row=start_row_no + 5),
        'constructed_floor_area': load_row_series(worksheet=worksheet, row=start_row_no + 6),
        'accumulated_constructed_floor_area': load_row_series(worksheet=worksheet, row=start_row_no + 7),
        'construction_rate': load_row_series(worksheet=worksheet, row=start_row_no + 11),
        'floor_area_over_population_growth': load_row_series(worksheet=worksheet, row=start_row_no + 12)
    }


def load_construction_building_category(worksheet: Worksheet, building_category: BuildingCategory) -> pd.DataFrame:
    """ Load rows related to construction for the supplied building_category from worksheet. The function
        assume the worksheet is formatted like `BEMA 2019-Tekniske kommentarer.xlsm`. With `house` starting at E11
        `kindergarten` at E41 and so on.

            Args:
                worksheet (Worksheet) the worksheet to retrieve
                building_category (BuildingCategory)

            Returns:
                  construction_df (pd.DataFrame)
                    index:
                        - year
                    columns:
                        - column (example E)
                        - total_floor_area
                        - demolished_floor_area
                        - constructed_floor_area
                        - accumulated_constructed_floor_area
                        - construction_rate
                        - floor_area_over_population_growth


            Raises:
                KeyError: Invalid building_category
            """
    start_rows_construction_building_category = {
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

    logger.debug(f'Loading rows for {building_category=}')
    building_category_rows = start_rows_construction_building_category.get(building_category)

    dict_of_series = load_building_category_from_rows(worksheet, building_category_rows)
    return pd.DataFrame(data=dict_of_series)
