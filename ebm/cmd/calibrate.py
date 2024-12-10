import pathlib

from loguru import logger
import pandas as pd
import tkinter as tk

import pyperclip
from dotenv import load_dotenv

from ebm.cmd.run_calculation import calculate_building_category_area_forecast
from ebm.cmd.run_calculation import calculate_building_category_energy_requirements, calculate_heating_systems
from ebm.model import DatabaseManager, FileHandler, building_category
from ebm.model.calibrate_heating_rv import default_calibrate_heating_rv
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory

from ebm.heating_systems import HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST

ELECTRICITY = 'Elektrisitet'
DISTRICT_HEATING = 'Fjernvarme'
BIO = 'Bio'
FOSSIL = 'Fossil'

DOMESTIC_HOT_WATER = 'Tappevann'

HEATPUMP_AIR_SOURCE = 'luftluft'
HEATPUMP_WATER_SOUCE = 'vannbåren'

CALIBRATION_YEAR = 2023

model_period = YearRange(2020, 2050)
start_year = model_period.start
end_year = model_period.end


def extract_area_forecast(database_manager) ->pd.DataFrame:
    area_forecasts = []
    for building_category in BuildingCategory:
        area_forecast_result = calculate_building_category_area_forecast(
            building_category=building_category,
            database_manager=database_manager,
            start_year=start_year,
            end_year=end_year)
        area_forecasts.append(area_forecast_result)

    area_forecast = pd.concat(area_forecasts)
    return area_forecast


def extract_energy_requirements(area_forecast: pd.DataFrame, database_manager) -> pd.DataFrame:
    all_requirement = []

    for building_category in BuildingCategory:
        en_req = calculate_building_category_energy_requirements(
            building_category=building_category,
            area_forecast=area_forecast[area_forecast['building_category'] == building_category],
            database_manager=database_manager,
            start_year=start_year,
            end_year=end_year)
        all_requirement.append(en_req)

    energy_requirement = pd.concat(all_requirement)
    return energy_requirement


def extract_heating_systems(energy_requirements, database_manager) -> pd.DataFrame:
    heating_systems = calculate_heating_systems(energy_requirements=energy_requirements,
                                                database_manager=database_manager)

    # heating_systems[heating_systems['purpose']=='heating_rv']
    return heating_systems


def transform_heating_systems(heating_systems, calibration_year) -> pd.DataFrame:
    # Filter heating_rv
    #heating_systems = heating_systems.loc[
    #    (slice(None), slice(None), 'heating_rv', slice(None), slice(None), slice(None))].copy()

    # Group building_categories
    heating_systems['is_residential'] = building_category.NON_RESIDENTIAL
    heating_systems.loc[['house', 'apartment_block'], 'is_residential'] = building_category.RESIDENTIAL
    grouper = ['Oppvarmingstyper', 'is_residential', 'year']
    year_slice = (slice(None), slice(None), calibration_year)
    df: pd.DataFrame = heating_systems.groupby(by=grouper).sum('gwh').loc[year_slice]

    # Classify energy_source
    if 'energy_source' in df.columns:
        df.drop(columns=['energy_source'], inplace=True)
    df.insert(0, 'energy_source', value=None)

    df[ELECTRICITY] = 0.0
    df[BIO] = 0.0
    df[DISTRICT_HEATING] = 0.0
    df[FOSSIL] = 0.0

    df[HEATPUMP_AIR_SOURCE] = 0.0
    df[HEATPUMP_WATER_SOUCE] = 0.0
    df[DOMESTIC_HOT_WATER] = 0.0

    df.loc[('DH', slice(None)), DISTRICT_HEATING] = df.loc[('DH', slice(None)), HEATING_RV_GRUNNLAST]

    df = _calculate_energy_source(df, 'DH', DISTRICT_HEATING)
    df = _calculate_energy_source(df, 'HP Central heating - DH', ELECTRICITY, DISTRICT_HEATING)
    df = _calculate_energy_source(df, 'DH - Bio', DISTRICT_HEATING, BIO)
    df = _calculate_energy_source(df, 'Gas', FOSSIL)
    df = _calculate_energy_source(df, 'HP Central heating - Gas', ELECTRICITY, FOSSIL)
    df.loc[('HP Central heating - Gas', slice(None)), HEATPUMP_WATER_SOUCE] = df.loc[
        ('HP Central heating - Gas', slice(None)), HEATING_RV_GRUNNLAST]
    df = _calculate_energy_source(df, 'Electricity', ELECTRICITY)
    df = _calculate_energy_source(df, 'Electric boiler', ELECTRICITY)
    df = _calculate_energy_source(df, 'Electric boiler - Solar', ELECTRICITY, ELECTRICITY)
    df = _calculate_energy_source(df, 'Electricity - Bio', ELECTRICITY, BIO)
    df = _calculate_energy_source(df, 'HP - Bio', ELECTRICITY, BIO)
    df.loc[('HP - Bio', slice(None)), HEATPUMP_AIR_SOURCE] = df.loc[('HP - Bio', slice(None)), HEATING_RV_GRUNNLAST]

    df = _calculate_energy_source(df, 'HP - Electricity', ELECTRICITY, ELECTRICITY)
    df.loc[('HP - Electricity', slice(None)), HEATPUMP_AIR_SOURCE] = df.loc[('HP - Electricity', slice(None)), HEATING_RV_GRUNNLAST]

    df = _calculate_energy_source(df, 'HP Central heating - Bio', ELECTRICITY, BIO)
    df.loc[('HP Central heating - Bio', slice(None)), HEATPUMP_WATER_SOUCE] = df.loc[('HP Central heating - Bio', slice(None)), HEATING_RV_GRUNNLAST]

    df = _calculate_energy_source(df, 'HP Central heating', ELECTRICITY)
    df.loc[('HP Central heating', slice(None)), [HEATPUMP_WATER_SOUCE]] = df.loc[slice('HP Central heating', None), HEATING_RV_GRUNNLAST]

    # Filter energy_use

    energy_use = df.groupby(by=['is_residential', 'Oppvarmingstyper']).sum()[[
        ELECTRICITY, DISTRICT_HEATING, BIO, FOSSIL, HEATPUMP_AIR_SOURCE, HEATPUMP_WATER_SOUCE]].copy()

    # Group and sum energy_usage by energy_source
    grouped = energy_use.groupby(by=['is_residential']).sum() / (10 ** 6)

    return grouped


def _calculate_energy_source(df, heating_type, primary_source, secondary_source=None):
    if secondary_source and primary_source == secondary_source:
        df.loc[(heating_type, slice(None)), primary_source] = df.loc[(heating_type, slice(None)), HEATING_RV_GRUNNLAST] + \
             df.loc[(heating_type, slice(None)), HEATING_RV_SPISSLAST]

        return df
    df.loc[(heating_type, slice(None)), primary_source] = df.loc[(heating_type, slice(None)), HEATING_RV_GRUNNLAST]
    if secondary_source:
        df.loc[(heating_type, slice(None)), secondary_source] = df.loc[
            (heating_type, slice(None)), HEATING_RV_SPISSLAST]

    return df


def sort_heating_systems_by_energy_source(transformed):
    custom_order = [ELECTRICITY, BIO, FOSSIL, DISTRICT_HEATING]

    unsorted = transformed.reset_index()
    unsorted['energy_source'] = pd.Categorical(unsorted['energy_source'], categories=custom_order, ordered=True)
    df_sorted = unsorted.sort_values(by=['energy_source'])
    df_sorted = df_sorted.set_index([('energy_source', '')])

    return df_sorted


def create_heating_rv(database_manager):
    file_handler: FileHandler = database_manager.file_handler
    heating_rv = file_handler.input_directory / 'calibrate_heating_rv.xlsx'
    if not heating_rv.is_file():
        logger.info(f'Creating {heating_rv}')
        df = default_calibrate_heating_rv()
        df.to_excel(heating_rv)


def run_calibration(database_manager, calibration_year):
    """

    Parameters
    ----------
    database_manager : ebm.model.database_manager.DatabaseManager

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    load_dotenv(pathlib.Path('.env'))

    calibration_directory = pathlib.Path('kalibrering')
    input_directory = database_manager.file_handler.input_directory

    logger.info(f'Using {input_directory}')
    area_forecast = extract_area_forecast(database_manager)
    energy_requirements = extract_energy_requirements(area_forecast, database_manager)
    heating_systems = extract_heating_systems(energy_requirements, database_manager)
    
    transformed = transform_heating_systems(heating_systems, calibration_year)
    tabbed = transformed.round(1).to_csv(sep='\t', header=False, index_label=None).replace('.', ',')
    print(tabbed)
    pyperclip.copy(tabbed)
    return transformed


def main():
    run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023)


if __name__ == '__main__':
    main()
