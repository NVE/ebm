#!/usr/bin/env python
# coding: utf-8
import itertools
import os
import pathlib

from loguru import logger
import pandas as pd

from ebm.cmd.helpers import load_environment_from_dotenv
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model.area import building_condition_scurves, building_condition_accumulated_scurves
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager, FileHandler
from ebm.model.construction import ConstructionCalculator


def calculate_area_by_condition(years: YearRange, scurve_parameters, tek_parameters, area_parameters,
                                database_manager):
    scurve_normal = building_condition_scurves(scurve_parameters)
    scurve_acc = building_condition_accumulated_scurves(scurve_parameters)
    s_curves = pd.concat([scurve_normal, scurve_acc])

    df_never_share = pd.DataFrame(
        [(r.building_category, i, r.condition + '_nvr', r.never_share) for i in range(-130, 131) for r in
         scurve_parameters.itertuples()],
        columns=['building_category', 'age', 'building_condition', 'scurve']).sort_values(
        ['building_category', 'building_condition', 'age']).set_index(
        ['building_category', 'age', 'building_condition'])

    s_df = pd.concat([s_curves, df_never_share])

    df = s_df.reset_index().join(tek_parameters, how='cross')
    df['year'] = df['building_year'] + df['age']
    scurve_by_tek = df.copy()

    # In[442]:
    r = scurve_by_tek.reset_index()
    df_p = r.pivot(index=['building_category', 'TEK', 'year'], columns=['building_condition'], values='scurve')
    df_p = df_p.reset_index().set_index(['building_category', 'TEK', 'year'], drop=True).rename_axis(None, axis=1)
    # ## Calculate new cumulative demolition with zero demolition in start year
    # In[446]:

    df = df_p.copy()
    pd.set_option('display.float_format', '{:.6f}'.format)
    df.loc[df.query(f'year<={years.start}').index, 'demolition'] = 0.0
    df['demolition_acc'] = df.groupby(by=['building_category', 'TEK'])[['demolition']].cumsum()[['demolition']]
    # df=df.query(f'year>={years.start}')

    df_p = df.copy()

    # ## Load construction
    # In[447]:
    df_ap = area_parameters.set_index(['building_category', 'TEK']).copy()
    demolition_by_year = (df_ap.loc[:, 'area'] * df.loc[:, 'demolition'])
    demolition_by_year.name = 'demolition'
    demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(2020, 2050))]

    # In[448]:
    demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()

    # demolition_floor_area.loc[(['apartment_block'], slice(None), [2050])]
    # ## Make area
    # In[450]:

    # Define the range of years
    # Create a MultiIndex with all combinations of cat_a, cat_b, and year
    index = pd.MultiIndex.from_product(
        [scurve_parameters['building_category'].unique(), tek_parameters.TEK.unique(), years],
        names=['building_category', 'TEK', 'year'])
    # Reindex the DataFrame to include all combinations, filling missing values with NaN
    area = index.to_frame().set_index(['building_category', 'TEK', 'year']).reindex(index).reset_index()
    # Optional: Fill missing values with a default, e.g., 0
    # df_full['value'] = df_full['value'].fillna(0)
    ap_df = area_parameters.set_index(['building_category', 'TEK'])

    existing_area = pd.merge(left=ap_df, right=area, on=['building_category', 'TEK'], suffixes=['_r', ''])
    existing_area = existing_area.set_index(['building_category', 'TEK', 'year'])

    construction = ConstructionCalculator.calculate_all_construction(
        demolition_by_year=demolition_by_building_category_year,
        database_manager=database_manager,
        period=years)

    logger.warning('Cheating by assuming TEK17')
    constructed_tek17 = construction.copy()
    constructed_tek17['TEK'] = 'TEK17'
    construction_by_building_category_yearly = constructed_tek17.set_index(
        ['building_category', 'TEK', 'year']).accumulated_constructed_floor_area
    construction_by_building_category_yearly.name = 'area'

    # In[457]:
    total_area_by_year = pd.concat([existing_area.drop(columns=['year_r'], errors='ignore'), construction_by_building_category_yearly])

    df = total_area_by_year.copy()

    with_area = df.join(df_p, how='left').fillna(0.0)

    # In[461]:
    with_area.loc[(['university'], ['TEK17'], slice(None))]
    # In[462]:
    with_area = df.join(df_p, how='left').fillna(0.0)

    with_area.index.get_level_values(level='TEK').unique()
    with_area.index.get_level_values(level='building_category').unique()
    with_area.index.get_level_values(level='year').unique()
    with_area = with_area.sort_index()

    # ## set max values

    df = with_area.copy()
    df.loc[:, 'renovation_max'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'renovation_nvr']
    df.loc[:, 'small_measure_max'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'small_measure_nvr']

    # In[465]:
    # hus=df.query('building_category=="house" and year > 2018')
    # hus.loc[:, 'sm2'] = hus['small_measure_acc'] - hus['demolition_acc']
    # hus[['sm2', 'small_measure_max']]
    # ## small_measure and renovation to shares_small_measure_total, RN
    # ## SharesPerCondition calc_renovation
    #
    #  - ❌ Ser ut som det er edge case for byggeår.
    #  - ❌ Årene før byggeår må settes til 0 for shares_renovation?
    df.loc[:, 'shares_small_measure_total'] = df.loc[:, ['small_measure_acc', 'small_measure_max']].min(axis=1).clip(lower=0.0)
    df.loc[:, 'shares_renovation_total'] = df.loc[:, ['renovation_acc', 'renovation_max']].min(axis=1).clip(lower=0.0)
    df.loc[:, 'shares_renovation'] = (df.loc[:, 'renovation_max'] - df.loc[:, 'shares_small_measure_total']).clip(lower=0.0)
    df.loc[:, 'shares_total'] = (df.loc[:, 'shares_small_measure_total'] + df.loc[:, 'shares_renovation_total']).clip(lower=0.0)

    # SharesPerCondition -> calc_renovation 273:285
    df.loc[df[df.shares_total < df.renovation_max].index, 'shares_renovation'] = df.loc[
        df[df.shares_total < df.renovation_max].index, 'shares_renovation_total']

    # ### SharesPerCondition calc_renovation_and_Small_measure
    #
    #  - ❌ Sette til 0 før byggeår
    #
    #
    df.loc[:, 'renovation_and_small_measure'] = df.loc[:, 'shares_renovation_total'] - df.loc[:, 'shares_renovation']
    df.loc[:, ['renovation_and_small_measure', 'shares_small_measure_total', 'shares_renovation_total',
               'shares_renovation']].query(
        'building_category=="house" and TEK=="TEK49" and year >= 2020 and year <=2050')

    # ### SharesPerCondition calc_small_measure
    #
    #  - ❌   sette til 0 før byggeår
    # ```python
    #     construction_year = self.tek_params[tek].building_year
    #     shares.loc[self.period_index <= construction_year] = 0
    # ```
    df.loc[:, 'shares_small_measure'] = df.loc[:, 'shares_small_measure_total'] - df.loc[:, 'renovation_and_small_measure']

    # ### SharesPerCondition calc_original_condition

    df.loc[:, 'original_condition'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'shares_renovation'] - df.loc[:, 'renovation_and_small_measure'] - df.loc[:, 'shares_small_measure']

    # ## join calculated scurves on area
    scurved = df.copy()
    # sca.loc[:, ['demolition', 'shares_small_measure_total', 'RN', 'both']] * sca['area', 'area', 'area', 'area']]

    a_mul = scurved[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation', 'renovation_and_small_measure', 'area']]
    area_by_condition = a_mul[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation', 'renovation_and_small_measure']].multiply(a_mul['area'], axis=0)

    # # SUMS
    # In[475]:
    return area_by_condition

def dataframe_to_excel(area_unstacked, target_file):
    def increment_filename(filename: pathlib.Path):
        yield filename
        for i in itertools.count(1):
            yield filename.parent / f'{filename.stem}-{i}{filename.suffix}'

    for output_file in increment_filename(target_file):
        logger.debug(f'Writing to {output_file}')
        try:
            area_unstacked.to_excel(output_file, merge_cells=False, index=False)
        except IOError as io_error:
            logger.debug(io_error)
            logger.debug(f'IOError writing to {output_file}')
        else:
            logger.info(f'Wrote {output_file.absolute()}')
            break


def main():
    load_environment_from_dotenv()
    configure_loglevel(log_format=os.environ.get('LOG_FORMAT'))

    years = YearRange(2020, 2050)
    dm = DatabaseManager(FileHandler(directory='t2734_input'))

    scurve_parameters = dm.get_scurve_params()

    area_parameters = dm.get_area_parameters()
    area_parameters['year'] = years.start

    tek_parameters = dm.file_handler.get_tek_params()

    area_by_condition = calculate_area_by_condition(years, scurve_parameters, tek_parameters, area_parameters, dm)

    area_unstacked = area_by_condition.rename(columns={'demolition_acc': 'demolition',
                                                       'shares_renovation': 'renovation',
                                                       'shares_small_measure': 'small_measure'}).stack().reset_index()
    area_unstacked = area_unstacked.rename(columns={'level_3': 'building_condition', 0: 'm²'})

    dataframe_to_excel(area_unstacked, pathlib.Path('output/area_dataframes.xlsx'))



if __name__ == '__main__':
    main()