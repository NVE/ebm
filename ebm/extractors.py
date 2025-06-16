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

    scurve_by_year = building_condition_scurves(scurve_parameters)
    scurve_accumulated = building_condition_accumulated_scurves(scurve_parameters)

    s_curves = pd.concat([scurve_by_year, scurve_accumulated])

    max_age = s_curves.index.get_level_values(level='age').max()
    df_never_share = pd.DataFrame(
        [(row.building_category, idx, row.condition + '_nvr', row.never_share) for idx in range(-max_age, max_age+1) for row in
         scurve_parameters.itertuples()],
        columns=['building_category', 'age', 'building_condition', 'scurve']).sort_values(
        ['building_category', 'building_condition', 'age']).set_index(
        ['building_category', 'age', 'building_condition'])

    s_curves_long = calculate_scurves_by_tek(s_curves, df_never_share, tek_parameters)
    demolition_acc = calculate_demolition_accumulated(s_curves_long, years)

    # ## Load construction
    area_parameters = area_parameters.set_index(['building_category', 'TEK'])
    demolition_by_year = calculate_demolition_by_year(area_parameters, demolition_acc)

    building_category_demolition_by_year = calculate_building_category_demolition_by_year(demolition_by_year)

    construction_by_building_category_and_year = calculate_construction_by_building_category(building_category_demolition_by_year, database_manager, years)

    existing_area = calculate_existing_area(area_parameters, tek_parameters, years)

    total_area_by_year = calculate_total_area_by_year(construction_by_building_category_and_year, existing_area)

    with_area = total_area_by_year.join(demolition_acc, how='left').fillna(0.0).sort_index()

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
    area_by_condition = df[['original_condition', 'demolition_acc', 'shares_small_measure', 'shares_renovation',
                               'renovation_and_small_measure']].multiply(df['area'], axis=0)

    area_unstacked = area_by_condition.rename(columns={'demolition_acc': 'demolition',
                                                       'shares_renovation': 'renovation',
                                                       'shares_small_measure': 'small_measure'}).stack().reset_index()
    area_unstacked = area_unstacked.rename(columns={'level_3': 'building_condition', 0: 'm2'}) # m²

    return area_unstacked


def calculate_demolition_accumulated(s_curves_long, years):
    demolition_acc = s_curves_long
    demolition_acc.loc[demolition_acc.query(f'year<={years.start}').index, 'demolition'] = 0.0
    demolition_acc['demolition_acc'] = demolition_acc.groupby(by=['building_category', 'TEK'])[['demolition']].cumsum()[
        ['demolition']]
    return demolition_acc


def calculate_scurves_by_tek(s_curves, df_never_share, tek_parameters):
    s_curves = pd.concat([s_curves, df_never_share])

    s_curves_by_tek = s_curves.reset_index().join(tek_parameters, how='cross')
    s_curves_by_tek['year'] = s_curves_by_tek['building_year'] + s_curves_by_tek['age']
    s_curves_long = s_curves_by_tek.pivot(index=['building_category', 'TEK', 'year'], columns=['building_condition'],
                                          values='scurve').reset_index()
    s_curves_long = s_curves_long.reset_index().set_index(['building_category', 'TEK', 'year'], drop=True).rename_axis(
        None, axis=1)
    return s_curves_long


def calculate_total_area_by_year(construction_by_building_category_yearly, existing_area):
    total_area_by_year = pd.concat([existing_area.drop(columns=['year_r'], errors='ignore'),
                                    construction_by_building_category_yearly])
    return total_area_by_year


def calculate_existing_area(area_parameters, tek_parameters, years):
    # ## Make area
    # Define the range of years
    index = pd.MultiIndex.from_product(
        [area_parameters.index.get_level_values(level='building_category').unique(), tek_parameters.TEK.unique(),
         years],
        names=['building_category', 'TEK', 'year'])
    # Reindex the DataFrame to include all combinations, filling missing values with NaN
    area = index.to_frame().set_index(['building_category', 'TEK', 'year']).reindex(index).reset_index()
    # Optional: Fill missing values with a default, e.g., 0
    existing_area = pd.merge(left=area_parameters, right=area, on=['building_category', 'TEK'], suffixes=['_r', ''])
    existing_area = existing_area.set_index(['building_category', 'TEK', 'year'])
    return existing_area


def calculate_construction_by_building_category(building_category_demolition_by_year, database_manager, years):
    construction = ConstructionCalculator.calculate_all_construction(
        demolition_by_year=building_category_demolition_by_year,
        database_manager=database_manager,
        period=years)
    logger.warning('Cheating by assuming TEK17')
    construction['TEK'] = 'TEK17'
    construction_by_building_category_yearly = construction.set_index(
        ['building_category', 'TEK', 'year']).accumulated_constructed_floor_area
    construction_by_building_category_yearly.name = 'area'
    return construction_by_building_category_yearly


def calculate_building_category_demolition_by_year(demolition_by_year):
    demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()
    return demolition_by_building_category_year


def calculate_demolition_by_year(area_parameters, demolition_acc):
    demolition_by_year = area_parameters.loc[:, 'area'] * demolition_acc.loc[:, 'demolition']
    demolition_by_year.name = 'demolition'
    demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(2020, 2050))]
    return demolition_by_year


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
    area_forecast = extract_area_forecast(years,
                                          tek_parameters=fh.get_tek_params(),
                                          area_parameters=dm.get_area_parameters(),
                                          scurve_parameters=dm.get_scurve_params(),
                                          database_manager=dm)

    print(area_forecast)

    energy_need_kwh_m2 = extract_energy_need(years, dm)
    print(energy_need_kwh_m2)

    heating_systems_projection = extract_heating_systems_projection(years, dm)
    print(heating_systems_projection)




if __name__ == '__main__':
    main()