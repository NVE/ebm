import os
import pathlib

import dotenv
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.cmd.result_handler import transform_model_to_horizontal, transform_holiday_homes_to_horizontal, \
    transform_to_sorted_heating_systems
from ebm.cmd.run_calculation import configure_loglevel, calculate_building_category_area_forecast, calculate_energy_use
from ebm.energy_consumption import EnergyConsumption
from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement
from ebm.model.file_handler import FileHandler
from ebm.model.building_category import BEMA_ORDER as building_category_order
from ebm.model.tek import BEMA_ORDER as tek_order
from ebm.model import heat_pump as h_p
from ebm.model import energy_use as e_u
from ebm.services.spreadsheet import make_pretty, add_top_row_filter


def extract_energy_need(years: YearRange, dm: DatabaseManager) -> pd.DataFrame:
    er_calculator = EnergyRequirement.new_instance(period=years, calibration_year=2023,
                                                   database_manager=dm)
    energy_need = er_calculator.calculate_for_building_category(database_manager=dm)

    energy_need = energy_need.set_index(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])

    return energy_need


def extract_area_change(area_forecast: pd.DataFrame) -> pd.DataFrame:
    df = area_forecast[area_forecast.TEK=='TEK17'].copy()

    df = df.set_index(['building_category', 'TEK', 'year', 'building_condition']).unstack()
    df.columns=df.columns.get_level_values(1)
    df['total']=df.sum(axis=1)
    df['m2'] = df['total'] - df['total'].shift()

    df['demolition_construction'] = 'construction'

    construction = df[['demolition_construction','m2']].copy()
    construction['m2'] = construction['m2'].clip(lower=np.nan)

    demolition = area_forecast[area_forecast['building_condition']==BuildingCondition.DEMOLITION].copy()
    demolition.loc[:, 'demolition_construction'] = 'demolition'
    demolition.loc[:, 'm2'] = -demolition.loc[:, 'm2']

    area_change = pd.concat([
        demolition[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']],
        construction.reset_index()[['building_category', 'TEK', 'year', 'demolition_construction', 'm2']]
    ])
    return area_change


def extract_area_forecast(years: YearRange, dm: DatabaseManager) -> pd.DataFrame:
    forecasts: pd.DataFrame | None = None

    for building_category in BuildingCategory:
        forecast = calculate_building_category_area_forecast(building_category, dm, years.start, years.end)
        forecast['building_category'] = building_category
        if forecasts is None:
            forecasts = forecast
        else:
            forecasts = pd.concat([forecasts, forecast])

    return forecasts


def transform_energy_need_to_energy_purpose_wide(energy_need: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    df_a = area_forecast.copy()
    df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

    df_e = energy_need.copy().reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

    df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
    df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000
    df.loc[:, ('TEK', 'building_condition')] = ('all', 'all')

    non_residential = [b for b in BuildingCategory if b.is_non_residential()]

    df.loc[df[df['building_category'].isin(non_residential)].index, 'building_category'] = 'non_residential'

    df = df.groupby(by=['building_category', 'purpose', 'year'], as_index=False).sum()
    df = df[['building_category', 'purpose', 'year', 'GWh']]

    df = df.pivot(columns=['year'], index=['building_category', 'purpose'], values=['GWh']).reset_index()
    df = df.sort_values(by=['building_category', 'purpose'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'building_category' else x.map(
                            {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                             'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

    df.insert(2, 'U', 'GWh')
    df.columns = ['building_category', 'purpose', 'U'] + [y for y in range(2020, 2051)]

    return df


def transform_energy_need_to_energy_purpose_long(energy_need: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    df_a = area_forecast.copy()
    df_a = df_a.query('building_condition!="demolition"').reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'year'], drop=True)

    df_e = energy_need.copy().reset_index().set_index(
        ['building_category', 'building_condition', 'TEK', 'purpose', 'year'])

    df = df_e.join(df_a)[['m2', 'kwh_m2']].reset_index()
    df.loc[:, 'GWh'] = (df['m2'] * df['kwh_m2']) / 1_000_000

    df = df.groupby(by=['year', 'building_category', 'TEK', 'purpose'], as_index=False).sum()
    df = df[['year', 'building_category', 'TEK', 'purpose', 'GWh']]
    df = df.sort_values(by=['year', 'building_category', 'TEK', 'purpose'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'TEK' else x.map(
                            {'heating_rv': 1, 'heating_dhw': 2, 'fans_and_pumps': 3, 'lighting': 4,
                             'electrical_equipment': 5, 'cooling': 6}) if x.name == 'purpose' else x)

    df = df.rename(columns={'GWh': 'energy_use [GWh]'})

    df.reset_index(inplace=True, drop=True)
    return df


def extract_heating_systems_projection(years: YearRange, database_manager: DatabaseManager) -> pd.DataFrame:
    projection_period = YearRange(2023, 2050)
    hsp: pd.DataFrame = HeatingSystemsProjection.new_instance(projection_period, database_manager)
    df: pd.DataFrame = hsp.calculate_projection()
    df = hsp.pad_projection(df, YearRange(2020, 2022))

    heating_system_projection = df.copy()
    return heating_system_projection


def extract_heating_systems(heating_system_projection: pd.DataFrame, energy_need: pd.DataFrame) -> pd.DataFrame:
    calculator = EnergyConsumption(heating_system_projection.copy())

    calculator.heating_systems_parameters = calculator.grouped_heating_systems()

    df = calculator.calculate(energy_need)

    return df


def transform_heating_systems_share_long(heating_systems_projection: pd.DataFrame) -> pd.DataFrame:
    df = heating_systems_projection.copy()

    fane2_columns = ['building_category', 'heating_systems', 'year', 'TEK_shares']

    df.loc[~df['building_category'].isin(['house', 'apartment_block']), 'building_category'] = 'non_residential'

    mean_tek_shares_yearly = df[fane2_columns].groupby(by=['year', 'building_category', 'heating_systems']).mean()
    return mean_tek_shares_yearly


def transform_heating_systems_share_wide(heating_systems_share_long: pd.DataFrame) -> pd.DataFrame:
    value_column = 'TEK_shares'
    df = heating_systems_share_long.copy().reset_index()
    df = df.pivot(columns=['year'], index=['building_category', 'heating_systems'], values=[value_column]).reset_index()

    df = df.sort_values(by=['building_category', 'heating_systems'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x)
    df.insert(2, 'U', value_column)
    df['U'] = '%'

    df.columns = ['building_category', 'heating_systems', 'U'] + [y for y in range(2020, 2051)]
    return df


def heating_systems_parameter_from_projection(heating_systems_projection: pd.DataFrame) -> pd.DataFrame:
    calculator = EnergyConsumption(heating_systems_projection.copy())

    return calculator.grouped_heating_systems()


def extract_energy_use_kwh(heating_systems_parameter: pd.DataFrame, energy_need: pd.DataFrame) -> pd.DataFrame:
    df = e_u.all_purposes(heating_systems_parameter)
    df.loc[:, 'building_group'] = 'yrkesbygg'
    df.loc[df.building_category.isin(['house', 'apartment_block']), 'building_group'] = 'bolig'

    efficiency_factor = e_u.efficiency_factor(df)
    energy_use_kwh = e_u.energy_use_kwh(energy_need=energy_need, efficiency_factor=efficiency_factor)

    return energy_use_kwh


def transform_demolition_construction(energy_use: pd.DataFrame, area_change: pd.DataFrame) -> pd.DataFrame:
    df = energy_use[energy_use['building_condition']=='renovation_and_small_measure']

    energy_use_m2 = df.groupby(by=['building_category', 'building_condition', 'TEK', 'year'], as_index=False).sum()[['building_category',  'TEK', 'year', 'kwh_m2']]

    dem_con = pd.merge(left=area_change, right=energy_use_m2, on=['building_category', 'TEK', 'year'])
    dem_con['gwh'] = (dem_con['kwh_m2'] * dem_con['m2']) / 1_000_000
    return dem_con[['year', 'demolition_construction', 'building_category', 'TEK', 'm2', 'gwh']]


def main():
    env_file = pathlib.Path(dotenv.find_dotenv(usecwd=True))
    if env_file.is_file():
        logger.debug(f'Loading environment from {env_file}')
        load_dotenv(pathlib.Path('.env').absolute())
    else:
        logger.debug(f'.env not found in {env_file.absolute()}')

    configure_loglevel(os.environ.get('LOG_FORMAT', None))

    years = YearRange(2020, 2050)
    input_path = pathlib.Path('kalibar')
    output_path = pathlib.Path('t2775_output')
    output_path.mkdir(exist_ok=True)
    file_handler = FileHandler(directory=input_path)
    database_manager = DatabaseManager(file_handler=file_handler)

    logger.info('Area to area.xlsx')

    logger.debug('Extract area_change')
    forecasts = extract_area_forecast(years,  database_manager)

    logger.debug('Extract area')

    logger.debug('Transform fane 1 (wide)')

    df = forecasts.copy()

    df = df.query('building_condition!="demolition"')
    df.loc[:, 'TEK'] = 'all'
    df.loc[:, 'building_condition'] = 'all'

    df = transform_model_to_horizontal(df).drop(columns=['TEK', 'building_condition'])

    area_wide = df.copy()

    logger.debug('Transform fane 2 (long')

    df = forecasts['year,building_category,TEK,building_condition,m2'.split(',')].copy()
    df = df.query('building_condition!="demolition"')

    df = df.groupby(by='year,building_category,TEK'.split(','))[['m2']].sum().rename(columns={'m2': 'area'})
    df.insert(0, 'U', 'm2')
    area_long = df.reset_index()

    logger.debug('Write file area.xlsx')

    area_output = output_path / 'area.xlsx'

    with pd.ExcelWriter(area_output, engine='xlsxwriter') as writer:
        area_wide.to_excel(writer, sheet_name='wide', index=False)
        area_long.to_excel(writer, sheet_name='long', index=False)
    logger.debug(f'Adding top row filter to {area_output}')
    make_pretty(area_output)
    add_top_row_filter(workbook_file=area_output, sheet_names=['long'])

    logger.info(f'Wrote {area_output}')
    logger.info('Energy use to energy_purpose')
    logger.debug('Extract energy_use')

    energy_need_kwh_m2 = extract_energy_need(years, database_manager)

    total_energy_need = forecasts.reset_index().set_index(['building_category', 'TEK', 'building_condition', 'year']).merge(energy_need_kwh_m2, left_index=True, right_index=True)

    total_energy_need['energy_requirement'] = total_energy_need.kwh_m2 * total_energy_need.m2

    logger.debug('Transform fane 1')
    energy_purpose_wide = transform_energy_need_to_energy_purpose_wide(energy_need=energy_need_kwh_m2, area_forecast=forecasts)
    logger.debug('Transform fane 2')
    energy_purpose_long = transform_energy_need_to_energy_purpose_long(energy_need=energy_need_kwh_m2, area_forecast=forecasts)

    logger.debug('Write file energy_purpose.xlsx')
    energy_purpose_output = output_path / 'energy_purpose.xlsx'

    with pd.ExcelWriter(energy_purpose_output, engine='xlsxwriter') as writer:
        energy_purpose_wide.to_excel(writer, sheet_name='wide', index=False)
        energy_purpose_long.to_excel(writer, sheet_name='long', index=False)
    make_pretty(energy_purpose_output)
    logger.debug(f'Adding top row filter to {energy_purpose_output}')
    add_top_row_filter(workbook_file=energy_purpose_output, sheet_names=['long'])
    logger.info(f'Wrote {energy_purpose_output.name}')

    logger.info('Heating_system_share')

    heating_systems_projection = extract_heating_systems_projection(years, database_manager)
    logger.debug('Transform fane 2')
    heating_systems_share = transform_heating_systems_share_long(heating_systems_projection)
    logger.debug('Transform fane 1')
    heating_systems_share_wide = transform_heating_systems_share_wide(heating_systems_share)
    heating_systems_share_long = heating_systems_share.rename(columns={'TEK_shares': 'Share',
                                                                  'heating_systems': 'Heating system'})
    heating_systems_share_wide = heating_systems_share_wide.rename(columns={'heating_systems':'Heating technology'})

    logger.debug('Write file heating_system_share.xlsx')
    heating_system_share_file = output_path / 'heating_system_share.xlsx'

    with pd.ExcelWriter(heating_system_share_file, engine='xlsxwriter') as writer:
        heating_systems_share_long.to_excel(writer, sheet_name='long', merge_cells=False)
        heating_systems_share_wide.to_excel(writer, sheet_name='wide', merge_cells=False, index=False)

    make_pretty(heating_system_share_file)
    logger.debug(f'Adding top row filter to {heating_system_share_file}')
    add_top_row_filter(workbook_file=heating_system_share_file, sheet_names=['long'])
    logger.info(f'Wrote {heating_system_share_file.name}')

    logger.info('heat_prod_hp')

    logger.debug('Extract heating_system_parameters')
    heating_systems_parameter = heating_systems_parameter_from_projection(heating_systems_projection)
    logger.debug('Transform to hp')

    df = heating_systems_parameter
    df = df.assign(**{'heating_system': df['heating_systems'].str.split('-')}).explode('heating_system')
    df['heating_system'] = df['heating_system'].str.strip()
    df['load_share'] = df['Grunnlast andel']

    air_air = h_p.air_source_heat_pump(df)
    district_heating = h_p.district_heating_heat_pump(df)
    production = h_p.heat_pump_production(total_energy_need, air_air, district_heating)

    heat_prod_hp_wide = h_p.heat_prod_hp_wide(production)
    heat_prod_hp_wide.columns = ['building_group', 'hp_source'] + [c for c in heat_prod_hp_wide.columns.get_level_values(1)[2:]]

    logger.debug('Write file heat_prod_hp.xlsx')
    heat_prod_hp_file = output_path / 'heat_prod_hp.xlsx'

    with pd.ExcelWriter(heat_prod_hp_file, engine='xlsxwriter') as writer:
        heat_prod_hp_wide.to_excel(writer, sheet_name='wide', index=False)
    make_pretty(heat_prod_hp_file)
    logger.info(f'Wrote {heat_prod_hp_file.name}')

    logger.info('Energy_use')

    logger.debug('Extract energy_use_kwh')
    energy_use_kwh = extract_energy_use_kwh(heating_systems_parameter, total_energy_need)

    logger.debug('Transform fane 2')
    logger.debug('Group by category, year, product')
    column_order = ['year', 'building_category', 'TEK', 'energy_product', 'kwh']
    energy_use_by_product = energy_use_kwh[column_order].groupby(
        by=['building_category', 'TEK', 'energy_product', 'year']).sum() / 1_000_000
    energy_use_long = energy_use_by_product.reset_index()[column_order].rename(columns={'kwh': 'energy_use'})

    logger.debug('Extract holiday homes 1')
    energy_use_holiday_homes = extract_energy_use_holiday_homes(database_manager)

    logger.debug('Transform fane 1')

    logger.debug('Group by group, product year')
    energy_use_by_building_group = energy_use_kwh[['building_group', 'year', 'energy_product', 'kwh']].groupby(
        by=['building_group', 'energy_product', 'year']).sum() / 1_000_000

    energy_use_wide = energy_use_by_building_group.reset_index().pivot(columns=['year'], index=['building_group', 'energy_product'], values=['kwh'])
    energy_use_wide = energy_use_wide.reset_index()
    energy_use_wide.columns = ['building_group', 'energy_source'] + [c for c in energy_use_wide.columns.get_level_values(1)[2:]]

    energy_use_wide = transform_to_sorted_heating_systems(energy_use_wide, energy_use_holiday_homes,
                                                          building_column='building_group')

    logger.debug('Write file energy_use')

    energy_use_file = output_path / 'energy_use.xlsx'

    with pd.ExcelWriter(energy_use_file, engine='xlsxwriter') as writer:
        energy_use_long.to_excel(writer, sheet_name='long', index=False)
        energy_use_wide.to_excel(writer, sheet_name='wide', index=False)
    make_pretty(energy_use_file)
    logger.debug(f'Adding top row filter to {energy_use_file}')
    add_top_row_filter(workbook_file=energy_use_file, sheet_names=['long'])
    logger.info(f'Wrote {energy_use_file.name}')

    logger.debug('✅ transform demolition_construction')
    demolition_construction_long = transform_demolition_construction(energy_use_kwh, area_change)
    demolition_construction_long = demolition_construction_long.rename(columns={'m2': 'Area [m2]',
                                                                      'gwh': 'Energy use [GWh]'})
    demolition_construction_file = output_path / 'demolition_construction.xlsx'

    logger.debug('Write file demolition_construction.xlsx')
    with pd.ExcelWriter(demolition_construction_file, engine='xlsxwriter') as writer:
        demolition_construction_long.to_excel(writer, sheet_name='long', index=False)
    make_pretty(demolition_construction_file)
    logger.debug(f'Adding top row filter to {demolition_construction_file}')
    add_top_row_filter(workbook_file=demolition_construction_file, sheet_names=['long'])
    logger.info(f'Wrote {demolition_construction_file.name}')

    logger.info('❌ Ekstra resultater som skrives etter behov')
    logger.debug('❌ area')
    logger.debug('❌ energy_need')
    logger.debug('❌ energy_use')


def extract_energy_use_holiday_homes(database_manager):
    df = transform_holiday_homes_to_horizontal(calculate_energy_use(database_manager)).copy()
    df = df.rename(columns={'building_category': 'building_group'})
    df.loc[df.energy_source=='Elektrisitet', 'energy_source'] = 'Electricity'
    df.loc[df.energy_source=='fossil', 'energy_source'] = 'Fossil'
    return df


if __name__ == '__main__':
    main()

