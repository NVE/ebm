import os
import pathlib

import pandas as pd

from loguru import logger

from ebm import extractors
from ebm.cmd.helpers import load_environment_from_dotenv
from ebm.cmd.result_handler import transform_model_to_horizontal, transform_to_sorted_heating_systems
from ebm.cmd.run_calculation import configure_loglevel
import ebm.model.area as a_f
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
import ebm.model.energy_need as e_n
from ebm.model import energy_purpose as e_p
from ebm.model import energy_use as e_u
from ebm.model.file_handler import FileHandler
import ebm.model.heating_systems_parameter as h_s_param
from ebm.model import heat_pump as h_p
from ebm.model.heating_systems_share import transform_heating_systems_share_long, transform_heating_systems_share_wide
from ebm.services.spreadsheet import make_pretty, add_top_row_filter


def main():
    load_environment_from_dotenv()

    configure_loglevel(os.environ.get('LOG_FORMAT', None))

    years = YearRange(2020, 2050)
    input_path = pathlib.Path('kalibar')
    output_path = pathlib.Path('t2775_output')
    output_path.mkdir(exist_ok=True)
    file_handler = FileHandler(directory=input_path)
    database_manager = DatabaseManager(file_handler=file_handler)

    logger.info('Area to area.xlsx')
    logger.debug('Extract area')
    area_forecast = extractors.extract_area_forecast(years, database_manager) # 📍

    logger.debug('Transform fane 1 (wide)')
    existing_area_by_building_category = a_f.group_existing_area_by_building_category(area_forecast)
    area_wide = transform_model_to_horizontal(existing_area_by_building_category)
    area_wide = area_wide.drop(columns=['TEK', 'building_condition'])

    logger.debug('Transform fane 2 (long')

    existing_area = area_forecast['year,building_category,TEK,building_condition,m2'.split(',')].copy()
    existing_area = existing_area.query('building_condition!="demolition"')

    existing_area = existing_area.groupby(by='year,building_category,TEK'.split(','))[['m2']].sum().rename(columns={'m2': 'area'})

    area_long = existing_area.reset_index().insert(0, 'U', 'm2')

    logger.debug('Write file area.xlsx')

    area_output = output_path / 'area.xlsx'

    with pd.ExcelWriter(area_output, engine='xlsxwriter') as writer:
        area_wide.to_excel(writer, sheet_name='wide', index=False) # 💾
        area_long.to_excel(writer, sheet_name='long', index=False) # 💾
    logger.debug(f'Adding top row filter to {area_output}')
    make_pretty(area_output)
    add_top_row_filter(workbook_file=area_output, sheet_names=['long'])

    logger.info(f'Wrote {area_output}')

    logger.info('Energy use to energy_purpose')
    logger.debug('Extract energy_use ❌')
    energy_need_kwh_m2 = extractors.extract_energy_need(years, database_manager) # 📍
    total_energy_need = e_n.transform_total_energy_need(energy_need_kwh_m2, area_forecast)

    logger.debug('Transform fane 1')
    energy_purpose_wide = e_p.transform_energy_need_to_energy_purpose_wide(energy_need=energy_need_kwh_m2, area_forecast=area_forecast)
    logger.debug('Transform fane 2')
    energy_purpose_long = e_p.transform_energy_need_to_energy_purpose_long(energy_need=energy_need_kwh_m2, area_forecast=area_forecast)

    logger.debug('Write file energy_purpose.xlsx')
    energy_purpose_output = output_path / 'energy_purpose.xlsx'

    with pd.ExcelWriter(energy_purpose_output, engine='xlsxwriter') as writer:
        energy_purpose_wide.to_excel(writer, sheet_name='wide', index=False) # 💾
        energy_purpose_long.to_excel(writer, sheet_name='long', index=False) # 💾
    make_pretty(energy_purpose_output)
    logger.debug(f'Adding top row filter to {energy_purpose_output}')
    add_top_row_filter(workbook_file=energy_purpose_output, sheet_names=['long'])
    logger.info(f'Wrote {energy_purpose_output.name}')

    logger.info('Heating_system_share')

    heating_systems_projection = extractors.extract_heating_systems_projection(years, database_manager) # 📍
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
        heating_systems_share_long.to_excel(writer, sheet_name='long', merge_cells=False) # 💾
        heating_systems_share_wide.to_excel(writer, sheet_name='wide', merge_cells=False, index=False) # 💾

    make_pretty(heating_system_share_file)
    logger.debug(f'Adding top row filter to {heating_system_share_file}')
    add_top_row_filter(workbook_file=heating_system_share_file, sheet_names=['long'])
    logger.info(f'Wrote {heating_system_share_file.name}')

    logger.info('heat_prod_hp')

    logger.debug('Transform heating_system_parameters')
    heating_systems_parameter = h_s_param.heating_systems_parameter_from_projection(heating_systems_projection)
    logger.debug('Transform to hp')

    expanded_heating_systems_parameter = h_s_param.expand_heating_system_parameters(heating_systems_parameter)
    air_air = h_p.air_source_heat_pump(expanded_heating_systems_parameter)
    district_heating = h_p.district_heating_heat_pump(expanded_heating_systems_parameter)

    production = h_p.heat_pump_production(total_energy_need, air_air, district_heating)

    heat_prod_hp_wide = h_p.heat_prod_hp_wide(production)

    logger.debug('Write file heat_prod_hp.xlsx')
    heat_prod_hp_file = output_path / 'heat_prod_hp.xlsx'

    with pd.ExcelWriter(heat_prod_hp_file, engine='xlsxwriter') as writer:
        heat_prod_hp_wide.to_excel(writer, sheet_name='wide', index=False) # 💾
    make_pretty(heat_prod_hp_file)
    logger.info(f'Wrote {heat_prod_hp_file.name}')


    logger.info('Energy_use')

    logger.debug('Transform energy_use_kwh')
    energy_use_kwh = e_u.building_group_energy_use_kwh(heating_systems_parameter, total_energy_need) # 📍

    logger.debug('Transform fane 1')
    energy_use_gwh_by_building_group = e_u.energy_use_gwh_by_building_group(energy_use_kwh)

    logger.debug('Transform fane 2')
    logger.debug('Group by category, year, product')

    column_order = ['year', 'building_category', 'TEK', 'energy_product', 'kwh']
    energy_use_long = energy_use_kwh[column_order].groupby(
        by=['building_category', 'TEK', 'energy_product', 'year']).sum() / 1_000_000
    energy_use_long = energy_use_long.reset_index()[column_order].rename(columns={'kwh': 'energy_use'})

    logger.debug('Extract holiday homes 1')
    energy_use_holiday_homes = extractors.extract_energy_use_holiday_homes(database_manager) # 📍

    logger.debug('Transform fane 1')

    logger.debug('Group by group, product year')

    energy_use_wide = transform_to_sorted_heating_systems(energy_use_gwh_by_building_group, energy_use_holiday_homes,
                                                          building_column='building_group')
    logger.debug('Write file energy_use')

    energy_use_file = output_path / 'energy_use.xlsx'

    with pd.ExcelWriter(energy_use_file, engine='xlsxwriter') as writer:
        energy_use_long.to_excel(writer, sheet_name='long', index=False) # 💾
        energy_use_wide.to_excel(writer, sheet_name='wide', index=False) # 💾
    make_pretty(energy_use_file)
    logger.debug(f'Adding top row filter to {energy_use_file}')
    add_top_row_filter(workbook_file=energy_use_file, sheet_names=['long'])
    logger.info(f'Wrote {energy_use_file.name}')

    area_change = a_f.transform_area_forecast_to_area_change(area_forecast=area_forecast)

    logger.info('demolition_construction')
    logger.debug('Transform demolition_construction')
    demolition_construction_long = a_f.transform_demolition_construction(energy_use_kwh, area_change)
    demolition_construction_long = demolition_construction_long.rename(columns={'m2': 'Area [m2]',
                                                                      'gwh': 'Energy use [GWh]'})
    demolition_construction_file = output_path / 'demolition_construction.xlsx'
    logger.debug('Write file demolition_construction.xlsx')
    with pd.ExcelWriter(demolition_construction_file, engine='xlsxwriter') as writer:
        demolition_construction_long.to_excel(writer, sheet_name='long', index=False) # 💾
    make_pretty(demolition_construction_file)
    logger.debug(f'Adding top row filter to {demolition_construction_file}')
    add_top_row_filter(workbook_file=demolition_construction_file, sheet_names=['long'])
    logger.info(f'Wrote {demolition_construction_file.name}')

    logger.info('❌ raw data')
    logger.debug('❌ area')
    logger.debug('❌ energy_need')
    logger.debug('❌ energy_use')


if __name__ == '__main__':
    main()

