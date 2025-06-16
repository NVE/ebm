import pandas as pd

from loguru import logger

from ebm.cmd.result_handler import transform_holiday_homes_to_horizontal
from ebm.cmd.run_calculation import calculate_energy_use
from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.model.area import building_condition_scurves, building_condition_accumulated_scurves
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


def extract_area_forecast(years: YearRange, scurve_parameters: pd.DataFrame, tek_parameters: pd.DataFrame, area_parameters: pd.DataFrame, database_manager:DatabaseManager):
    logger.debug('Calculating area by condition')
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
    scurve_by_tek = df

    r = scurve_by_tek.reset_index()
    df_p = r.pivot(index=['building_category', 'TEK', 'year'], columns=['building_condition'], values='scurve')
    df_p = df_p.reset_index().set_index(['building_category', 'TEK', 'year'], drop=True).rename_axis(None, axis=1)
    # ## Calculate new cumulative demolition with zero demolition in start year

    df = df_p
    pd.set_option('display.float_format', '{:.6f}'.format)
    df.loc[df.query(f'year<={years.start}').index, 'demolition'] = 0.0
    df['demolition_acc'] = df.groupby(by=['building_category', 'TEK'])[['demolition']].cumsum()[['demolition']]
    # df=df.query(f'year>={years.start}')

    df_p = df

    # ## Load construction
    df_ap = area_parameters.set_index(['building_category', 'TEK'])
    demolition_by_year = (df_ap.loc[:, 'area'] * df.loc[:, 'demolition'])
    demolition_by_year.name = 'demolition'
    demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(2020, 2050))]

    demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()

    # demolition_floor_area.loc[(['apartment_block'], slice(None), [2050])]
    # ## Make area
    # Define the range of years
    index = pd.MultiIndex.from_product(
        [scurve_parameters['building_category'].unique(), tek_parameters.TEK.unique(), years],
        names=['building_category', 'TEK', 'year'])

    # Reindex the DataFrame to include all combinations, filling missing values with NaN
    area = index.to_frame().set_index(['building_category', 'TEK', 'year']).reindex(index).reset_index()

    # Optional: Fill missing values with a default, e.g., 0
    ap_df = area_parameters.set_index(['building_category', 'TEK'])

    existing_area = pd.merge(left=ap_df, right=area, on=['building_category', 'TEK'], suffixes=['_r', ''])
    existing_area = existing_area.set_index(['building_category', 'TEK', 'year'])

    construction = ConstructionCalculator.calculate_all_construction(
        demolition_by_year=demolition_by_building_category_year,
        database_manager=database_manager,
        period=years)

    logger.warning('Cheating by assuming TEK17')
    constructed_tek17 = construction
    constructed_tek17['TEK'] = 'TEK17'
    construction_by_building_category_yearly = constructed_tek17.set_index(
        ['building_category', 'TEK', 'year']).accumulated_constructed_floor_area
    construction_by_building_category_yearly.name = 'area'

    total_area_by_year = pd.concat(
        [existing_area.drop(columns=['year_r'], errors='ignore'), construction_by_building_category_yearly])

    df = total_area_by_year

    with_area = df.join(df_p, how='left').fillna(0.0)

    with_area.index.get_level_values(level='TEK').unique()
    with_area.index.get_level_values(level='building_category').unique()
    with_area.index.get_level_values(level='year').unique()
    with_area = with_area.sort_index()

    # ## set max values

    df = with_area
    df.loc[:, 'renovation_max'] = (1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'renovation_nvr'])
    df.loc[:, 'small_measure_max'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'small_measure_nvr']

    # ## small_measure and renovation to shares_small_measure_total, RN
    # ## SharesPerCondition calc_renovation
    #
    #  - ❌ Ser ut som det er edge case for byggeår.
    #  - ❌ Årene før byggeår må settes til 0 for shares_renovation?
    df.loc[:, 'shares_small_measure_total'] = df.loc[:, ['small_measure_acc', 'small_measure_max']].min(axis=1).clip(lower=0.0)
    df.loc[:, 'shares_renovation_total'] = df.loc[:, ['renovation_acc', 'renovation_max']].min(axis=1).clip(lower=0.0)

    df.loc[:, 'shares_renovation'] = (df.loc[:, 'renovation_max'] -
                                      df.loc[:, 'shares_small_measure_total']).clip(lower=0.0)

    df.loc[:, 'shares_total'] = (df.loc[:, 'shares_small_measure_total'] +
                                 df.loc[:, 'shares_renovation_total']).clip(lower=0.0)

    df.loc[df[df.shares_total < df.renovation_max].index, 'shares_renovation'] = df.loc[df[df.shares_total < df.renovation_max].index, 'shares_renovation_total']

    # ### SharesPerCondition calc_renovation_and_Small_measure
    #  - ❌ Sette til 0 før byggeår
    df.loc[:, 'renovation_and_small_measure'] = (df.loc[:, 'shares_renovation_total'] -
                                                 df.loc[:, 'shares_renovation'])

    # ### SharesPerCondition calc_small_measure
    #  - ❌   sette til 0 før byggeår
    # ```python
    #     construction_year = self.tek_params[tek].building_year
    #     shares.loc[self.period_index <= construction_year] = 0
    # ```
    df.loc[:, 'shares_small_measure'] = (df.loc[:, 'shares_small_measure_total'] -
                                         df.loc[:, 'renovation_and_small_measure'])

    # ### SharesPerCondition calc_original_condition

    df.loc[:, 'original_condition'] = (1.0 -
                                       df.loc[:, 'demolition_acc'] -
                                       df.loc[:, 'shares_renovation'] -
                                       df.loc[:, 'renovation_and_small_measure'] -
                                       df.loc[:, 'shares_small_measure'])

    # ## join calculated scurves on area
    scurved = df

    a_mul = scurved[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation',
                     'renovation_and_small_measure', 'area']]
    area_by_condition = a_mul[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation',
                               'renovation_and_small_measure']].multiply(a_mul['area'], axis=0)

    area_unstacked = area_by_condition.rename(columns={'demolition_acc': 'demolition',
                                                       'shares_renovation': 'renovation',
                                                       'shares_small_measure': 'small_measure'}).stack().reset_index()
    area_unstacked = area_unstacked.rename(columns={'level_3': 'building_condition', 0: 'm2'}) # m²

    return area_unstacked


def extract_energy_need(years: YearRange, dm: DatabaseManager) -> pd.DataFrame:
    er_calculator = EnergyRequirement.new_instance(period=years, calibration_year=2023,
                                                   database_manager=dm)
    energy_need = er_calculator.calculate_for_building_category(database_manager=dm)

    energy_need = energy_need.set_index(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])

    return energy_need


def extract_heating_systems_projection(years: YearRange, database_manager: DatabaseManager) -> pd.DataFrame:
    projection_period = YearRange(2023, 2050)
    hsp = HeatingSystemsProjection.new_instance(projection_period, database_manager)
    df: pd.DataFrame = hsp.calculate_projection()
    df = hsp.pad_projection(df, YearRange(2020, 2022))

    heating_system_projection = df.copy()
    return heating_system_projection


def extract_energy_use_holiday_homes(database_manager):
    df = transform_holiday_homes_to_horizontal(calculate_energy_use(database_manager)).copy()
    df = df.rename(columns={'building_category': 'building_group'})
    df.loc[df.energy_source=='Elektrisitet', 'energy_source'] = 'Electricity'
    df.loc[df.energy_source=='fossil', 'energy_source'] = 'Fossil'
    return df


def main():
    from ebm.model.file_handler import FileHandler
    fh = FileHandler(directory='input')
    dm = DatabaseManager(fh)
    years = YearRange(2020, 2050)
    area_forecast = extract_area_forecast(years, dm=dm)

    print(area_forecast)

    energy_need_kwh_m2 = extract_energy_need(years, dm)
    print(energy_need_kwh_m2)

    heating_systems_projection = extract_heating_systems_projection(years, dm)
    print(heating_systems_projection)




if __name__ == '__main__':
    main()