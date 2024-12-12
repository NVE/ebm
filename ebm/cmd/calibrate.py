import pathlib

from loguru import logger
import pandas as pd

import pyperclip
from dotenv import load_dotenv

from ebm.cmd.run_calculation import calculate_building_category_area_forecast
from ebm.cmd.run_calculation import calculate_building_category_energy_requirements, calculate_heating_systems
from ebm.model import DatabaseManager, FileHandler
from ebm.model.calibrate_heating_rv import default_calibrate_heating_rv
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory

from ebm.heating_systems import HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, HeatingSystems, \
    GRUNNLAST_ENERGIVARE, SPISSLAST_ENERGIVARE, EKSTRALAST_ENERGIVARE, HEATIG_RV_EKSTRALAST, COOLING_KV, OTHER_SV, \
    DHW_TV, TAPPEVANN_ENERGIVARE

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


def transform_by_energy_source(df, energy_class_column, energy_source_column):
    rv_gl = df.loc[:, [energy_class_column, energy_source_column, 'building_group']]
    rv_gl = rv_gl[rv_gl[energy_class_column] > 0]
    rv_gl['typ'] = energy_class_column
    rv_gl = rv_gl.rename(columns={energy_source_column: 'energy_source',
                                  energy_class_column: 'energy_use'})
    rv_gl = rv_gl.reset_index().set_index(['building_category',
                                   'building_condition',
                                   'purpose',
                                   'TEK',
                                   'year',
                                   'heating_systems',
                                   'typ'])
    return rv_gl


def transform_heating_systems(df: pd.DataFrame, calibration_year) -> pd.DataFrame:
    df['building_group'] = 'yrkesbygg'
    df.loc['house', 'building_group'] = 'bolig'
    df.loc['apartment_block', 'building_group'] = 'bolig'

    df['ALWAYS_ELECTRICITY'] = 'Electricity'
    rv_gl = transform_by_energy_source(df, HEATING_RV_GRUNNLAST, GRUNNLAST_ENERGIVARE)
    rv_sl = transform_by_energy_source(df, HEATING_RV_SPISSLAST, SPISSLAST_ENERGIVARE)
    rv_el = transform_by_energy_source(df, HEATIG_RV_EKSTRALAST, EKSTRALAST_ENERGIVARE)
    cooling = transform_by_energy_source(df, COOLING_KV, 'ALWAYS_ELECTRICITY')
    spesifikt_elforbruk = transform_by_energy_source(df, OTHER_SV, 'ALWAYS_ELECTRICITY')
    tappevann = transform_by_energy_source(df, DHW_TV, TAPPEVANN_ENERGIVARE)

    energy_use = pd.concat([rv_gl, rv_sl, rv_el, cooling, spesifikt_elforbruk, tappevann])
    energy_use.loc[energy_use['energy_source'] == 'Solar', 'energy_source'] = 'Electricity'
    energy_use = energy_use.xs(calibration_year, level='year')

    sums = energy_use.groupby(by=['building_group', 'energy_source']).sum() / (10**6)
    df = sums.reset_index()
    df = df.rename(columns={'building_group': 'building_category'})
    df.loc[df.energy_source == 'DH', 'energy_source'] = 'Fjernvarme'
    df.loc[df.energy_source == 'Electricity', 'energy_source'] = 'Elektrisitet'
    df.loc[df.building_category == 'bolig', 'building_category'] = 'residential'
    df.loc[df.building_category == 'yrkesbygg', 'building_category'] = 'non_residential'
    df = df.pivot(index='building_category', columns='energy_source', values='energy_use').reset_index()[
        ['building_category', 'Elektrisitet', 'Fjernvarme', 'Bio', 'Fossil']].set_index(['building_category'], drop=True)

    return df


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


def run_calibration(database_manager,
                    calibration_year,
                    area_forecast: pd.DataFrame = None):
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

    logger.info(f'Using input directory "{input_directory}"')
    logger.info('Extract area forecast')
    area_forecast = extract_area_forecast(database_manager) if area_forecast is None else area_forecast
    logger.info('Extract energy requirements')
    energy_requirements = extract_energy_requirements(area_forecast, database_manager)
    logger.info('Extract heating systems')
    heating_systems = extract_heating_systems(energy_requirements, database_manager)

    shares_start_year = database_manager.get_heating_systems_shares_start_year()
    efficiencies = database_manager.get_heating_systems_efficiencies()
    projection = database_manager.get_heating_systems_projection()

    df = HeatingSystems.calculate_heating_systems_projection(
        heating_systems_shares=shares_start_year,
        heating_systems_efficiencies=efficiencies,
        heating_systems_forecast=projection)

    hf = df.set_index(['building_category', 'TEK', 'heating_systems', 'year'])
    transformed = transform_heating_systems(heating_systems, calibration_year)

    return transformed


def main():
    transformed = run_calibration(DatabaseManager(FileHandler(directory='kalibrering')), calibration_year=2023)
    tabbed = transformed.round(1).to_csv(sep='\t', header=False, index_label=None).replace('.', ',')
    pyperclip.copy(tabbed)


if __name__ == '__main__':
    main()
