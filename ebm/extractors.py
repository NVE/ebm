import pandas as pd
from loguru import logger

from ebm import s_curve
from ebm.cmd.result_handler import transform_holiday_homes_to_horizontal
from ebm.cmd.run_calculation import calculate_energy_use
from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.model.construction import ConstructionCalculator
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


def extract_area_forecast(years: YearRange, scurve_parameters: pd.DataFrame, tek_parameters: pd.DataFrame, area_parameters: pd.DataFrame, database_manager:DatabaseManager):
    logger.debug('Calculating area by condition')

    s_curves = s_curve.transform_scurve_parameters_to_scurve(scurve_parameters)
    df_never_share = s_curve.transform_scurve_parameters_never_share(s_curves, scurve_parameters)

    s_curves_with_tek = s_curve.merge_s_curves_and_tek(s_curves, df_never_share, tek_parameters)
    cumulative_demolition = s_curve.accumulate_demolition(s_curves_with_tek, years)

    s_curve_cumulative_demolition = s_curve.calculate_s_curve_cumulative_demolition(cumulative_demolition, years)
    s_curve_demolition = s_curve.calculate_s_curve_demolition(cumulative_demolition, years)
    s_curve_renovation_never_share = s_curve.calculate_s_curve_renovation_never_share(s_curves_with_tek, years)
    s_curve_small_measure_never_share = s_curve.calculate_s_curve_small_measure_never_share(s_curves_with_tek, years)
    s_curve_cumulative_small_measure = s_curve.calculate_s_curve_cumulative_small_measure(s_curves_with_tek, years)
    s_curve_cumulative_renovation = s_curve.calculate_s_curve_cumulative_renovation(s_curves_with_tek, years)

    s_curve_renovation_max = s_curve.calculate_s_curve_renovation_max(s_curve_cumulative_demolition, s_curve_renovation_never_share)
    s_curve_small_measure_max = s_curve.calculate_s_curve_small_measure_max(s_curve_cumulative_demolition,
                                                                    s_curve_small_measure_never_share)


    s_curve_small_measure_total = s_curve.trim_scurve_max_value(s_curve_cumulative_small_measure, s_curve_small_measure_max)

    s_curve_renovation_total = s_curve.trim_scurve_max_value(s_curve_cumulative_renovation, s_curve_renovation_max)

    scurve_total = s_curve.calculate_s_curve_total(s_curve_renovation_total, s_curve_small_measure_total)

    s_curve_renovation = s_curve.calculate_s_curve_renovation_from_small_measure(s_curve_renovation_max, s_curve_small_measure_total)

    # Filter rows where shares_total is smaller than scurve_renovation_max and merge those values into scurve_renovation
    s_curve_renovation = s_curve.trim_s_curve_renovation_from_renovation_total(s_curve_renovation, s_curve_renovation_max,
                                                                       s_curve_renovation_total, scurve_total)


    s_curve_renovation_and_small_measure = s_curve.calculate_s_curve_renovation_and_small_measure(s_curve_renovation, s_curve_renovation_total)

    s_curve_small_measure = s_curve.calculate_s_curve_small_measure(s_curve_renovation_and_small_measure, s_curve_small_measure_total)

    s_curve_original_condition = s_curve.calculate_s_curve_original_condition(s_curve_cumulative_demolition, s_curve_renovation,
                                                                      s_curve_renovation_and_small_measure,
                                                                      s_curve_small_measure)

    s_curves_by_condition = pd.DataFrame({
        'original_condition': s_curve_original_condition,
        'demolition': s_curve_cumulative_demolition,
        'small_measure': s_curve_small_measure,
        'renovation': s_curve_renovation,
        'renovation_and_small_measure': s_curve_renovation_and_small_measure
    })

    area_parameters = area_parameters.set_index(['building_category', 'TEK'])

    demolition_floor_area_by_year = calculate_demolition_floor_area_by_year(area_parameters, s_curve_demolition)

    building_category_demolition_by_year = sum_building_category_demolition_by_year(demolition_floor_area_by_year)

    construction_by_building_category_and_year = calculate_construction_by_building_category(building_category_demolition_by_year, database_manager, years)

    existing_area = calculate_existing_area(area_parameters, tek_parameters, years)

    total_area_floor_by_year = merge_total_area_by_year(construction_by_building_category_and_year, existing_area)

    floor_area_forecast = multiply_s_curves_with_floor_area(s_curves_by_condition, total_area_floor_by_year)

    return floor_area_forecast


def multiply_s_curves_with_floor_area(s_curves_by_condition, with_area):
    floor_area_by_condition = s_curves_by_condition.multiply(with_area['area'], axis=0)
    floor_area_forecast = floor_area_by_condition.stack().reset_index()
    floor_area_forecast = floor_area_forecast.rename(columns={'level_3': 'building_condition', 0: 'm2'})  # m²
    return floor_area_forecast


def merge_total_area_by_year(construction_by_building_category_yearly, existing_area):
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


def sum_building_category_demolition_by_year(demolition_by_year):
    demolition_by_building_category_year = demolition_by_year.groupby(by=['building_category', 'year']).sum()
    return demolition_by_building_category_year


def calculate_demolition_floor_area_by_year(
        area_parameters: pd.DataFrame, s_curve_cumulative_demolition: pd.Series) -> pd.Series:
    demolition_by_year = area_parameters.loc[:, 'area'] * s_curve_cumulative_demolition.loc[:]
    demolition_by_year.name = 'demolition'
    demolition_by_year = demolition_by_year.to_frame().loc[(slice(None), slice(None), slice(2020, 2050))]
    return demolition_by_year.demolition


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