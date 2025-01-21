import pathlib

from loguru import logger
import pandas as pd

from ebm.cmd.run_calculation import calculate_building_category_area_forecast, \
    calculate_building_category_energy_requirements, calculate_heating_systems
from ebm.model.calibrate_heating_systems import transform_heating_systems
from ebm.model.building_condition import BEMA_ORDER as building_condition_order
from ebm.model.building_category import BEMA_ORDER as building_category_order
from ebm.model.tek import BEMA_ORDER as tek_order



def transform_model_to_horizontal(model):
    hz = model.reset_index().copy()
    value_column = 'energy_requirement' if 'energy_requirement' in hz.columns else 'm2'
    hz = hz.groupby(by=['building_category', 'TEK', 'building_condition', 'year'], as_index=False).sum()[
        ['building_category', 'TEK', 'building_condition', 'year', value_column]]
    hz = hz.pivot(columns=['year'], index=['building_category', 'TEK', 'building_condition'], values=[
        value_column]).reset_index()

    hz = hz.sort_values(by=['building_category', 'TEK', 'building_condition'],
                        key=lambda x: x.map(building_category_order) if x.name == 'building_category' else x.map(
                            tek_order) if x.name == 'TEK' else x.map(
                            building_condition_order) if x.name == 'building_condition' else x)
    hz.columns = ['building_category', 'TEK', 'building_condition'] + [y for y in range(2020, 2051)]

    return hz


def transform_heating_systems_to_horizontal(model: pd.DataFrame):
    hs2 = model
    d = []
    for year in range(2020, 2051):
        energy_source_by_building_group = transform_heating_systems(hs2, year)
        energy_source_by_building_group['year'] = year
        d.append(energy_source_by_building_group)
    r = pd.concat(d)
    r2 = r.reset_index()[['building_category', 'energy_source', 'year', 'energy_use']]
    hz = r2.pivot(columns=['year'], index=['building_category', 'energy_source'],
                  values=['energy_use']).reset_index()

    hz.columns = ['building_category', 'energy_source'] + [y for y in range(2020, 2051)]
    return hz


def write_result(output_file, csv_delimiter, output, sheet_name='area forecast'):
    logger.debug(f'Writing to {output_file}')
    if str(output_file) == '-':
        try:
            print(output.to_markdown())

        except ImportError:
            print(output.to_string())
    elif output_file.suffix == '.csv':
        output.to_csv(output_file, sep=csv_delimiter)
        logger.info(f'Wrote {output_file}')
    else:
        excel_writer = pd.ExcelWriter(output_file, engine='openpyxl')
        output.to_excel(excel_writer, sheet_name=sheet_name, merge_cells=False, freeze_panes=(1, 3))
        excel_writer.close()
        logger.info(f'Wrote {output_file}')


def write_horizontal_excel(output_file: pathlib.Path, model: pd.DataFrame, sheet_name='Sheet 1'):
    more_options = {'mode': 'w'}
    if output_file.is_file():
        more_options = {'if_sheet_exists': 'replace', 'mode': 'a'}

    with pd.ExcelWriter(output_file, engine='openpyxl', **more_options) as writer:
        model.to_excel(writer, sheet_name=sheet_name, index=False, startcol=2)


def write_tqdm_result(output_file, output, csv_delimiter=','):
    try:
        from tqdm import tqdm
    except ImportError:
        # When tqdm is not installed we use write_result instead
        write_result(output_file, csv_delimiter, output)
        return

    logger.debug(f'Writing to {output_file}')
    if str(output_file) == '-':
        try:
            print(output.to_markdown())
        except ImportError:
            print(output.to_string())
            return
    logger.info('reset index')
    output = output.reset_index()
    logger.info('resat index')
    with tqdm(total=len(output), desc="Writing to spreadsheet") as pbar:
        if output_file.suffix == '.csv':
            for i in range(0, len(output), 100):  # Adjust the chunk size as needed
                building_category = output.iloc[i].building_category
                pbar.update(100)
                output.iloc[i:i + 100].to_csv(output_file, mode='a', header=(i == 0), index=False, sep=csv_delimiter)
                pbar.display(f'Writing {building_category}')
            pbar.display(f'Wrote {output_file}')
        else:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as excel_writer:
                for i in range(0, len(output), 100):  # Adjust the chunk size as needed
                    building_category = output.iloc[i].name[0] if 'building_category' not in output.columns else output.building_category.iloc[i]
                    pbar.set_description(f'Writing {building_category}')
                    output.iloc[i:i + 100].to_excel(excel_writer, startrow=i, header=(i == 0), merge_cells=False)
                    pbar.update(100)
                pbar.set_description(f'Closing {output_file}')


class EbmDefaultHandler:
    def extract_model(self, arguments, building_category, building_conditions, database_manager, step_choice):
        area_forecast_result = calculate_building_category_area_forecast(
            building_category=building_category,
            database_manager=database_manager,
            start_year=arguments.start_year,
            end_year=arguments.end_year)
        df = area_forecast_result
        df = df.set_index(['building_category', 'TEK', 'building_condition', 'year'])
        if building_conditions:
            df = df.loc[:, :, [str(s) for s in building_conditions]]
        if arguments.tek:
            tek_in_index = [t for t in arguments.tek if any(df.index.isin([t], level=1))]
            df = df.loc[:, tek_in_index, :]
        if 'energy-requirements' in step_choice or 'heating-systems' in step_choice:
            energy_requirements_result = calculate_building_category_energy_requirements(
                building_category=building_category,
                area_forecast=df,
                database_manager=database_manager,
                start_year=arguments.start_year,
                end_year=arguments.end_year)
            df = energy_requirements_result

            if 'heating-systems' in step_choice:
                df = calculate_heating_systems(energy_requirements=energy_requirements_result,
                                               database_manager=database_manager)
        return df

    def write_result(self, output_file, csv_delimiter, model):
        write_tqdm_result(output_file, model, csv_delimiter)
