import pandas as pd

from loguru import logger

from ebm.cmd.result_handler import transform_holiday_homes_to_horizontal
from ebm.cmd.run_calculation import calculate_building_category_area_forecast, calculate_energy_use
from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.model.area import building_condition_scurves, building_condition_accumulated_scurves
from ebm.model.building_category import BuildingCategory
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement
from ebm.model.file_handler import FileHandler


def extract_area_forecast2(years: YearRange, database_manager: DatabaseManager):
    input_directory = database_manager.file_handler.input_directory

    scurve_parameters_path = input_directory / 'scurve_parameters.csv'
    scurve_parameters = pd.read_csv(scurve_parameters_path)
    # area_parameters = area_parameters.query('building_category=="house"')

    # ### area_parameters
    area_parameters_path = input_directory / 'area_parameters.csv'
    area_parameters = pd.read_csv(area_parameters_path)
    area_parameters['year'] = years.start
    area_parameters = area_parameters[['building_category', 'TEK', 'year', 'area']]

    # ### tek_parameters
    tek_parameters_path = input_directory / 'tek_parameters.csv'
    tek_parameters = pd.read_csv(tek_parameters_path)
    tek_parameters = tek_parameters[['TEK', 'period_start_year', 'building_year', 'period_end_year']]

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
    df.query('building_category=="house" and TEK=="PRE_TEK49" and year > 2018')
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
    ap_df

    existing_area = pd.merge(left=ap_df, right=area, on=['building_category', 'TEK'], suffixes=['_r', ''])
    existing_area = existing_area.set_index(['building_category', 'TEK', 'year'])

    dm = DatabaseManager(FileHandler(directory=input_directory))
    construction = ConstructionCalculator.calculate_all_construction(
        demolition_by_year=demolition_by_building_category_year,
        database_manager=dm,
        period=years)

    logger.warning('Cheating by assuming TEK17')
    constructed_tek17 = construction.copy()
    constructed_tek17['TEK'] = 'TEK17'
    construction_by_building_category_yearly = constructed_tek17.set_index(
        ['building_category', 'TEK', 'year']).accumulated_constructed_floor_area
    construction_by_building_category_yearly.name = 'area'
    construction_by_building_category_yearly

    # In[457]:
    total_area_by_year = pd.concat([existing_area.drop(columns=['year_r'], errors='ignore'), construction_by_building_category_yearly])

    # In[459]:
    df = total_area_by_year.copy()

    # ## Join area into df_p
    # In[460]:

    with_area = df.join(df_p, how='left').fillna(0.0)

    # In[461]:
    with_area.loc[(['university'], ['TEK17'], slice(None))]
    # In[462]:
    with_area = df.join(df_p, how='left').fillna(0.0)
    # with_area.loc[(slice(None), slice(['culture']))]

    with_area.index.get_level_values(level='TEK').unique()
    with_area.index.get_level_values(level='building_category').unique()
    with_area.index.get_level_values(level='year').unique()
    with_area = with_area.sort_index()

    #
    # ## set max values
    # In[464]:
    # df = df_p.copy()
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
    # In[466]:
    df.loc[:, 'shares_small_measure_total'] = df.loc[:, ['small_measure_acc', 'small_measure_max']].min(axis=1).clip(lower=0.0)
    df.loc[:, 'shares_renovation_total'] = df.loc[:, ['renovation_acc', 'renovation_max']].min(axis=1).clip(lower=0.0)
    df.loc[:, 'shares_renovation'] = (df.loc[:, 'renovation_max'] - df.loc[:, 'shares_small_measure_total']).clip(lower=0.0)
    df.loc[:, 'shares_total'] = (df.loc[:, 'shares_small_measure_total'] + df.loc[:, 'shares_renovation_total']).clip(lower=0.0)

    # SharesPerCondition -> calc_renovation 273:285
    df.loc[df[df.shares_total < df.renovation_max].index, 'shares_renovation'] = df.loc[
        df[df.shares_total < df.renovation_max].index, 'shares_renovation_total']

    # df.loc[:, 'sr2'] = df.loc[:, ['shares_total', 'renovation_max']].min(axis=1).clip(lower=0.0)

    # ### SharesPerCondition calc_renovation_and_Small_measure
    #
    #  - ❌ Sette til 0 før byggeår
    #
    #
    # In[467]:
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
    # In[468]:
    df.loc[:, 'shares_small_measure'] = df.loc[:, 'shares_small_measure_total'] - df.loc[:,
                                                                                  'renovation_and_small_measure']
    # and TEK=="PRE_TEK49" and year >= 2020 and year <=2050
    df.loc[:, ['shares_small_measure_total', 'renovation_and_small_measure', 'shares_small_measure']].query(
        'building_category=="house"')  # .query("building_category=='house' and year>=2020 and year <=2050 and TEK=='TEK49'"
    # ### SharesPerCondition calc_original_condition
    # In[469]:
    df.loc[:, 'original_condition'] = 1.0 - df.loc[:, 'demolition_acc'] - df.loc[:, 'shares_renovation'] - df.loc[:, 'renovation_and_small_measure'] - df.loc[:, 'shares_small_measure']

    # ## join calculated scurves on area
    # In[472]:
    scurved = df.copy()
    scurved.loc[(slice(None), ['TEK17'], slice(None))]
    # In[474]:
    # sca.loc[:, ['demolition', 'shares_small_measure_total', 'RN', 'both']] * sca['area', 'area', 'area', 'area']]

    a_mul = scurved[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation', 'renovation_and_small_measure', 'area']]
    area_by_condition = a_mul[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation', 'renovation_and_small_measure']].multiply(a_mul['area'], axis=0)

    # # SUMS
    # In[475]:

    area_unstacked = area_by_condition.rename(columns={'demolition_acc': 'demolition',
                                                       'shares_renovation': 'renovation',
                                                       'shares_small_measure': 'small_measure'}).stack().reset_index()
    area_unstacked = area_unstacked.rename(columns={'level_3': 'building_condition', 0: 'm2'}) # 'm²'

    return area_unstacked



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