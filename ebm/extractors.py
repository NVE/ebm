import pandas as pd
from loguru import logger

from ebm import s_curve
from ebm.model import area
from ebm.cmd.result_handler import transform_holiday_homes_to_horizontal
from ebm.cmd.run_calculation import calculate_energy_use
from ebm.heating_systems_projection import HeatingSystemsProjection

from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


def extract_area_forecast(years: YearRange, scurve_parameters: pd.DataFrame, tek_parameters: pd.DataFrame, area_parameters: pd.DataFrame, database_manager:DatabaseManager):
    logger.debug('Calculating area by condition')

    s_curves_by_condition = calculate_s_curves(scurve_parameters, tek_parameters, years)

    # write_scurve(s_curves_by_condition)

    area_parameters = area_parameters.set_index(['building_category', 'TEK'])

    demolition_floor_area_by_year = area.calculate_demolition_floor_area_by_year(area_parameters, s_curves_by_condition.s_curve_demolition)

    building_category_demolition_by_year = area.sum_building_category_demolition_by_year(demolition_floor_area_by_year)

    construction_by_building_category_and_year = area.calculate_construction_by_building_category(building_category_demolition_by_year, database_manager, years)

    existing_area = area.calculate_existing_area(area_parameters, tek_parameters, years)

    total_area_floor_by_year = area.merge_total_area_by_year(construction_by_building_category_and_year, existing_area)

    floor_area_forecast = area.multiply_s_curves_with_floor_area(s_curves_by_condition, total_area_floor_by_year)

    return floor_area_forecast


def write_scurve(s_curves_by_condition):
    try:
        output_file = 'output/s_curves.xlsx'
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            s_curves_by_condition.to_excel(writer, sheet_name='s_curves_by_condition', merge_cells=False)  # 💾
            # s_curve_demolition.to_excel(writer, sheet_name='s_curve_demolition', merge_cells=False) # 💾
    except IOError as ex:
        logger.exception(ex)
        logger.info(f'There was an IOError while writing to {output_file}. Moving on!')


def calculate_s_curves(scurve_parameters, tek_parameters, years):
    s_curves = s_curve.scurve_parameters_to_scurve(scurve_parameters)
    df_never_share = s_curve.scurve_parameters_to_never_share(s_curves, scurve_parameters)

    s_curves_with_tek = s_curve.merge_s_curves_and_tek(s_curves, df_never_share, tek_parameters)

    cumulative_demolition = s_curve.accumulate_demolition(s_curves_with_tek, years)
    s_curve_demolition = s_curve.transform_demolition(cumulative_demolition, years)

    s_curve_cumulative_demolition = s_curve.transform_to_cumulative_demolition(cumulative_demolition, years)
    s_curve_renovation_never_share = s_curve.renovation_never_share(s_curves_with_tek, years)
    s_curve_small_measure_never_share = s_curve.small_measure_never_share(s_curves_with_tek, years)
    s_curve_cumulative_small_measure = s_curve.cumulative_small_measure(s_curves_with_tek, years)
    s_curve_cumulative_renovation = s_curve.cumulative_renovation(s_curves_with_tek, years)

    s_curve_renovation_max = s_curve.renovation_max(s_curve_cumulative_demolition, s_curve_renovation_never_share)
    s_curve_small_measure_max = s_curve.small_measure_max(s_curve_cumulative_demolition,
                                                          s_curve_small_measure_never_share)

    s_curve_small_measure_total = s_curve.trim_max_value(s_curve_cumulative_small_measure, s_curve_small_measure_max)
    s_curve_renovation_total = s_curve.trim_max_value(s_curve_cumulative_renovation, s_curve_renovation_max)
    scurve_total = s_curve.total(s_curve_renovation_total, s_curve_small_measure_total)

    s_curve_renovation = s_curve.renovation_from_small_measure(s_curve_renovation_max, s_curve_small_measure_total)
    s_curve_renovation = s_curve.trim_renovation_from_renovation_total(s_curve_renovation, s_curve_renovation_max,
                                                                       s_curve_renovation_total, scurve_total)

    s_curve_renovation_and_small_measure = s_curve.renovation_and_small_measure(s_curve_renovation,
                                                                                s_curve_renovation_total)

    s_curve_small_measure = s_curve.small_measure(s_curve_renovation_and_small_measure, s_curve_small_measure_total)

    s_curve_original_condition = s_curve.original_condition(s_curve_cumulative_demolition, s_curve_renovation,
                                                            s_curve_renovation_and_small_measure,
                                                            s_curve_small_measure)

    s_curves_by_condition = s_curve.transform_to_dataframe(s_curve_cumulative_demolition,
                                                           s_curve_original_condition,
                                                           s_curve_renovation,
                                                           s_curve_renovation_and_small_measure,
                                                           s_curve_small_measure,
                                                           s_curve_demolition)

    return s_curves_by_condition


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