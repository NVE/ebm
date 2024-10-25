import itertools
import os
import typing

import pandas as pd
from loguru import logger
from openpyxl.worksheet.worksheet import Worksheet

from ebm.__main__ import calculate_building_category_area_forecast
from ebm.model import BuildingCategory, DatabaseManager
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import (calculate_energy_requirement_reduction_by_condition,
                                          calculate_energy_requirement_reduction,
                                          calculate_lighting_reduction)
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
    area_existing = area_forecast.loc[~area_forecast.TEK.isin(['TEK10', 'TEK17', 'TEK21'])][
        ['year', 'building_category', 'building_condition', 'TEK', 'area']]
    #tek10_before_2020 = area_forecast.loc[area_forecast.TEK.isin(['TEK10'])][
    #    ['year', 'building_category', 'building_condition', 'TEK', 'area']]

    return area_existing.set_index(['building_category', 'TEK', 'building_condition', 'year'])

    area_2019 = tek10_before_2020.loc[(tek10_before_2020['year'] == 2019) & (
                tek10_before_2020['building_condition'] == 'original_condition'), 'area'].values

    # Update the area for all rows in tek10_before_2020 to the area from 2019
    tek10_before_2020.loc[(tek10_before_2020['year'] > 2019) & (
            tek10_before_2020['building_condition'] == 'original_condition'), 'area'] = area_2019[0]
    tek10_before_2020.loc[(tek10_before_2020['year'] > 2019) & (
            tek10_before_2020['building_condition'] != 'original_condition'), 'area'] = 0.0
    existing_area = pd.concat([area_existing, tek10_before_2020])

    return existing_area.set_index(['building_category', 'TEK', 'building_condition', 'year'])


def filter_transition_area(area_forecast: pd.DataFrame, tek_name='TEK10') -> pd.DataFrame:
    df = area_forecast.query(f'TEK == "{tek_name}"')
    df = df.reset_index()

    # Lag filter for byggningskategori og tilstand
    logger.warning('Assuming building_category kindergarten')
    filter_building_category = df.building_category == 'kindergarten'
    filter_original_condition = df.building_condition == 'original_condition'

    tr = df.copy()

    area_2019 = df.loc[filter_building_category & filter_original_condition & (tr.year == 2019), 'area'].iloc[0]

    tr = tr.set_index(['building_category', 'TEK', 'year'])
    s = tr.groupby(by=['building_category', 'TEK', 'year']).sum()['area'] - area_2019

    tr.loc[:, 'area_n'] = s
    tr.loc[tr['building_condition'] != 'original_condition', 'area'] = 0
    tr.loc[tr.index.get_level_values('year') > 2019, 'area'] = area_2019
    tr.loc[(tr.index.get_level_values('year') < 2020) & ~(filter_original_condition), 'area'] = 0.0

    tr = tr.reset_index().set_index(['building_category', 'TEK', 'building_condition', 'year'])
    after_2019 = tr.index.get_level_values('year') > 2019
    tr.loc[after_2019, 'area'] = tr.loc[after_2019, 'area'] - tr.loc[after_2019, 'area_n']

    return tr


def filter_future_area(area_forecast: pd.DataFrame, tek_name) -> pd.DataFrame:
    future_tek = area_forecast.query(f'TEK == "{tek_name}"').copy().reset_index()

    if 'index' in future_tek.columns.names:
        future_tek = future_tek.drop(columns=['index'])

    future_tek = future_tek.set_index(['building_category', 'TEK', 'building_condition', 'year'])
    return future_tek


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
    existing_heating_rv_by_year.name = 'kwh_m2'
    return existing_heating_rv_by_year


def load_heating_reduction(purpose='heating_rv'):
    def make_zero_reduction():
        r = [{'building_condition': condition, 'reduction_share': 0} for condition in BuildingCondition if condition != BuildingCondition.DEMOLITION]
        return r
    heating_reduction = pd.read_csv('input/energy_requirement_reduction_per_condition.csv')
    if purpose != 'heating_rv':
        return pd.DataFrame(data=make_zero_reduction())

    heating_reduction = heating_reduction[heating_reduction.TEK == 'default'][['building_condition', 'reduction_share']]
    return heating_reduction


def load_energy_by_floor_area(building_category, purpose='heating_rv'):
    energy_by_floor_area = pd.read_csv('input/energy_requirement_original_condition.csv')
    df = energy_by_floor_area[(energy_by_floor_area.building_category == building_category) &
                              (energy_by_floor_area.purpose == purpose)]
    return df


def load_area_forecast(building_category: BuildingCategory = BuildingCategory.KINDERGARTEN) -> pd.DataFrame:
    dm = DatabaseManager()
    area = calculate_building_category_area_forecast(building_category=building_category,
                                                     database_manager=dm,
                                                     start_year=2010,
                                                     end_year=2050)

    data = {'building_category': [], 'TEK': [], 'building_condition': [], 'year': [], 'area': []}
    for tek, item in area.items():
        for condition, years in item.items():
            if condition == BuildingCondition.DEMOLITION:
                continue
            for year, area in enumerate(years, start=2010):
                data.get('building_category').append(building_category)
                data.get('TEK').append(tek)
                data.get('building_condition').append(condition)
                data.get('year').append(year)
                data.get('area').append(area)

    area_forecast = pd.DataFrame(data=data)
    return area_forecast


def distribute_energy_requirement_over_area(area_forecast, requirement_by_condition):
    area_requirements = pd.merge(left=area_forecast,
                                 right=requirement_by_condition,
                                 on=['building_category', 'TEK', 'building_condition', 'year']).copy()
    area_requirements = area_requirements.set_index(['building_category', 'TEK', 'building_condition', 'year'])
    existing_area = filter_existing_area(area_forecast)
    existing_heating_rv_by_year = calculate_area_distribution(area_requirements, existing_area)
    return existing_heating_rv_by_year


def calculate_heating_reduction(building_category=BuildingCategory.KINDERGARTEN, purpose='heating_rv'):
    heating_reduction = load_heating_reduction(purpose)

    heating_rv_requirements = load_energy_by_floor_area(building_category, purpose=purpose)

    requirement_by_condition = calculate_energy_requirement_reduction_by_condition(
        energy_requirements=heating_rv_requirements,
        condition_reduction=heating_reduction)
   # return requirement_by_condition
    heating_reduction = pd.merge(left=requirement_by_condition,
                                 right=pd.DataFrame({'year': YearRange(2010, 2050).year_range}),
                                 how='cross')
    return heating_reduction


def calculate_electrical_equipment(building_category, heating_reduction, purpose):
    # By default there is no heating_reduction defined for fans n pumps

    # heating_reduction.reduction = 0
    lighting = load_energy_by_floor_area(building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name = 'year'
    energy_requirement = pd.Series([requirement_by_condition['kwh_m2'].iloc[0]] * 41, index=idx,
                                   name='kwh_m2')
    light_requirements = calculate_energy_requirement_reduction(energy_requirements=energy_requirement,
                                                                yearly_reduction=0.01,
                                                                reduction_period=YearRange(2020, 2050))
    merged = pd.merge(
        requirement_by_condition[['building_category', 'TEK', 'building_condition']],
        pd.DataFrame({'kwh_m2': light_requirements, 'year': light_requirements.index.values}),
        how='cross')

    return merged


def calculate_lighting(building_category, purpose):
    heating_reduction = load_heating_reduction(purpose)

    # heating_reduction.reduction = 0
    lighting = load_energy_by_floor_area(building_category=building_category, purpose=purpose)
    requirement_by_condition = pd.merge(lighting, heating_reduction, how='cross')

    idx = YearRange(2010, 2050).to_index()
    idx.name = 'year'
    energy_requirement = pd.Series([requirement_by_condition['kwh_m2'].iloc[0]] * 41, index=idx,
                                   name='kwh_m2')
    end_year_requirement = requirement_by_condition['kwh_m2'].iloc[0] * (1-0.6)
    light_requirements = calculate_lighting_reduction(
            energy_requirement=energy_requirement,
            yearly_reduction=0.005,
            end_year_energy_requirement=end_year_requirement,
            interpolated_reduction_period=YearRange(2018, 2030),
            year_range=YearRange(2010, 2050))
    merged = pd.merge(
        requirement_by_condition[['building_category', 'TEK', 'building_condition']],
        pd.DataFrame({'kwh_m2': light_requirements, 'year': light_requirements.index.values}),
        how='cross')
    return merged


def beregne_energibehov(building_category = BuildingCategory.KINDERGARTEN):
    area_forecast = load_area_forecast(building_category=building_category)

    return pd.DataFrame({
        'heating_rv': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category)),
        'fans_and_pumps': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category, purpose='fans_and_pumps')),
        'heating_dhw': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category,
                purpose='heating_dhw')),
        'lighting': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_lighting(building_category, 'lighting')),
        'electrical_equipment': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_electrical_equipment(
                building_category=building_category,
                heating_reduction=load_heating_reduction('electrical_equipment'),
                purpose='electrical_equipment')),
        'cooling': distribute_energy_requirement_over_area(
            area_forecast=area_forecast,
            requirement_by_condition=calculate_heating_reduction(
                building_category=building_category,
                purpose='cooling'))
        })