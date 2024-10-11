import itertools
import os
import typing

import pandas as pd
from loguru import logger
from openpyxl.worksheet.worksheet import Worksheet

from ebm.model import BuildingCategory
from ebm.services.spreadsheet import iter_cells

START_ROWS_CONSTRUCTION_BUILDING_CATEGORY = {
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


def load_construction_building_category(building_category: BuildingCategory,
                                        spreadsheet: str = '', worksheet: str = 'Nybygging') -> pd.DataFrame:
    """ Load rows related to construction for the supplied building_category from worksheet. The function
        assume the worksheet is formatted like `BEMA 2019-Tekniske kommentarer.xlsm`. With `house` starting at E11
        `kindergarten` at E41 and so on.

            Args:
                building_category (BuildingCategory)
                spreadsheet (str) spreadsheet file
                worksheet (str) worksheet name, default(Nybygging)

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
    filename = spreadsheet if spreadsheet else os.environ.get('BEMA_SPREADSHEET')

    start_row = START_ROWS_CONSTRUCTION_BUILDING_CATEGORY.get(building_category) - 1
    end_row = start_row + 13

    rows_to_skip = [i for i in range(3, 350) if i >= end_row or i < start_row]
    more_rows = [0, 1, start_row + 2, start_row + 3, start_row + 4, start_row + 8, start_row + 9, start_row + 10]
    rows_to_skip = more_rows + rows_to_skip
    logger.debug(f'{filename=} {start_row=}')
    names = ['year', 'total_floor_area', 'building_growth', 'demolished_floor_area', 'constructed_floor_area',
             'accumulated_constructed_floor_area', 'construction_rate', 'floor_area_over_population_growth']
    df = pd.read_excel(filename,
                       usecols='D:AS',
                       header=None,
                       skiprows=rows_to_skip,
                       sheet_name=worksheet)

    # Switch columns and rows of the dataframe then set index to year
    df_transposed = df.transpose().iloc[1:].copy()
    df_transposed.columns = names
    df_transposed.year = df_transposed.year.astype(int)
    df_transposed = df_transposed.set_index('year')

    return df_transposed


def filter_existing_area(area_forecast: pd.DataFrame) -> pd.DataFrame:
    """

    Filter area_forecast to only include TEK and year defined as existing. The cut-off value is TEK10 for 2020 and later
        in addition to any TEK beyond TEK10.

    Parameters
    ----------
    area_forecast : pd.DataFrame
        DataFrame with columns year, building_category, TEK, building_condition, area

    Returns
    -------
    pd.Series
        pct percentage of total floor area by year, building_category, TEK and building_condition

    """
    area_forecast = area_forecast.reset_index()
    area_existing = area_forecast.reset_index().loc[~area_forecast.TEK.isin(['TEK10', 'TEK17', 'TEK21'])][
        ['year', 'building_category', 'building_condition', 'TEK', 'area']]
    tek10_before_2020 = area_forecast.loc[area_forecast.TEK.isin(['TEK10'])][
        ['year', 'building_category', 'building_condition', 'TEK', 'area']]

    area_2019 = tek10_before_2020.loc[(tek10_before_2020['year'] == 2019) & (
                tek10_before_2020['building_condition'] == 'original_condition'), 'area'].values

    # Update the area for all rows in tek10_before_2020 to the area from 2019
    tek10_before_2020.loc[(tek10_before_2020['year'] > 2019) & (
            tek10_before_2020['building_condition'] == 'original_condition'), 'area'] = area_2019[0]
    tek10_before_2020.loc[(tek10_before_2020['year'] > 2019) & (
            tek10_before_2020['building_condition'] != 'original_condition'), 'area'] = 0.0
    existing_area = pd.concat([area_existing, tek10_before_2020])

    return existing_area.set_index(['building_category', 'TEK', 'building_condition', 'year'])


def calculate_area_distribution(area_requirements: pd.DataFrame, existing_area: pd.DataFrame) -> pd.Series:
    """
    Calculate the distribution of building_conditions (pct) and recalculate area_requirements.kwh_m2 based
        on area distribution (adjusted).

    Parameters
    ----------
    area_requirements : pd.DataFrame
        Pandas Dataframe with building_category, year and kwh_m2
    existing_area : pd.DataFrame
        Pandas Dataframe with building_category, year, area

    Returns
    -------
    pd.DataFrame
        building_category, year indexed dataframe with the sum of all kwh_m2 adjusted by relative area

    """
    total_area = existing_area.groupby(level=['building_category', 'year']).sum()[['area']]
    existing_area['pct'] = existing_area.area / total_area.area
    area_requirements['adjusted'] = existing_area.pct * area_requirements.kwh_m2
    existing_heating_rv_by_year = area_requirements.groupby(level=['building_category', 'year'])['adjusted'].sum()
    return existing_heating_rv_by_year
