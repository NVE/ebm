from loguru import logger
import pandas as pd

from ebm.cmd.run_calculation import calculate_building_category_area_forecast
from ebm.cmd.run_calculation import calculate_building_category_energy_requirements, calculate_heating_systems
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory

from ebm.heating_systems import (HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, GRUNNLAST_ENERGIVARE, SPISSLAST_ENERGIVARE,
                                 EKSTRALAST_ENERGIVARE, HEATIG_RV_EKSTRALAST, COOLING_KV, OTHER_SV, DHW_TV,
                                 TAPPEVANN_ENERGIVARE, HEAT_PUMP, HP_ENERGY_SOURCE)

ELECTRICITY = 'Elektrisitet'
DISTRICT_HEATING = 'Fjernvarme'
BIO = 'Bio'
FOSSIL = 'Fossil'

DOMESTIC_HOT_WATER = 'Tappevann'

HEATPUMP_AIR_SOURCE = 'Luft/luft'
HEATPUMP_WATER_SOUCE = 'Vannbåren varme'

CALIBRATION_YEAR = 2023

model_period = YearRange(2020, 2050)
start_year = model_period.start
end_year = model_period.end


def extract_area_forecast(database_manager) -> pd.DataFrame:
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
    df = df.reindex()
    df['building_group'] = 'yrkesbygg'
    df.loc[('house', slice(None),slice(None),slice(None),slice(None), slice(None),), 'building_group'] = 'bolig'
    df.loc[('apartment_block', slice(None),slice(None),slice(None), slice(None), slice(None),), 'building_group'] = 'bolig'
    # df.loc['apartment_block', 'building_group'] = 'bolig'

    df['ALWAYS_ELECTRICITY'] = 'Electricity'
    rv_gl = transform_by_energy_source(df, HEATING_RV_GRUNNLAST, GRUNNLAST_ENERGIVARE)
    rv_sl = transform_by_energy_source(df, HEATING_RV_SPISSLAST, SPISSLAST_ENERGIVARE)
    rv_el = transform_by_energy_source(df, HEATIG_RV_EKSTRALAST, EKSTRALAST_ENERGIVARE)
    cooling = transform_by_energy_source(df, COOLING_KV, 'ALWAYS_ELECTRICITY')
    spesifikt_elforbruk = transform_by_energy_source(df, OTHER_SV, 'ALWAYS_ELECTRICITY')
    tappevann = transform_by_energy_source(df, DHW_TV, TAPPEVANN_ENERGIVARE)
    rv_hp = transform_by_energy_source(df, HEAT_PUMP, HP_ENERGY_SOURCE)

    energy_use = pd.concat([rv_gl, rv_sl, rv_el, cooling, spesifikt_elforbruk, tappevann, rv_hp])
    energy_use.loc[energy_use['energy_source'] == 'Solar', 'energy_source'] = 'Electricity'
    energy_use = energy_use.xs(calibration_year, level='year')

    sums = energy_use.groupby(by=['building_group', 'energy_source']).sum() / (10**6)
    df = sums.reset_index()
    df = df.rename(columns={'building_group': 'building_category'})
    df.loc[df.energy_source == 'DH', 'energy_source'] = 'Fjernvarme'
    df.loc[df.energy_source == 'Electricity', 'energy_source'] = 'Elektrisitet'
    df.loc[df.building_category == 'bolig', 'building_category'] = 'Bolig'
    df.loc[df.building_category == 'yrkesbygg', 'building_category'] = 'Yrkesbygg'
    return df.set_index(['building_category', 'energy_source'])


def transform_pumps(df: pd.DataFrame, calibration_year) -> pd.DataFrame:
    df['building_group'] = 'Yrkesbygg'
    df.loc['house', 'building_group'] = 'Bolig'
    df.loc['apartment_block', 'building_group'] = 'Bolig'

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


class DistributionOfHeatingSystems:
    @staticmethod
    def transform(df):
        df = df.reset_index()
        df['building_group'] = 'Yrkesbygg'

        df = df[df['building_category'] != 'storage_repairs']
        df.loc[df['building_category'].isin(['apartment_block']), 'building_group'] = 'Boligblokk'
        df.loc[df['building_category'].isin(['house']), 'building_group'] = 'Småhus'

        distribution_of_heating_systems_by_building_group = df.groupby(by=['building_group', 'heating_systems'])[
            ['TEK_shares']].mean()
        return distribution_of_heating_systems_by_building_group


