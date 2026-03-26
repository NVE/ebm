import pandas as pd
from loguru import logger

from ebm.areaforecast.s_curve import calculate_s_curves
from ebm.heating_system_forecast import HeatingSystemsForecast
from ebm.holiday_home_energy import calculate_energy_use, transform_holiday_homes_to_horizontal
from ebm.model.area import calculate_all_area
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import calculate_for_building_category


def extract_area_forecast(years: YearRange,
                          s_curves_by_condition: pd.DataFrame,
                          building_code_parameters: pd.DataFrame, area_parameters: pd.DataFrame,
                          database_manager:DatabaseManager) -> pd.DataFrame:
    logger.debug('Calculating area by condition')

    area_per_person = database_manager.get_area_per_person()
    area_new_residential_buildings = database_manager.get_area_new_residential_buildings()
    construction_population = database_manager.get_construction_population()
    new_buildings_category_share = database_manager.get_new_buildings_category_share()

    df = calculate_all_area(area_new_residential_buildings, area_parameters, area_per_person,
                            building_code_parameters, construction_population, new_buildings_category_share,
                            s_curves_by_condition, years)

    return df


def extract_energy_need(years: YearRange, dm: DatabaseManager) -> pd.DataFrame:
    energy_need = calculate_for_building_category(database_manager=dm)

    energy_need = energy_need.set_index(['building_category', 'building_code', 'purpose', 'building_condition', 'year'])

    return energy_need


def extract_heating_systems_forecast(years: YearRange, database_manager: DatabaseManager) -> pd.DataFrame:
    forecast_period = YearRange(2023, 2050)
    hsp = HeatingSystemsForecast.new_instance(forecast_period, database_manager)
    df: pd.DataFrame = hsp.calculate_forecast()
    df = hsp.pad_projection(df, YearRange(2020, 2022))

    heating_system_forecast = df.copy()
    return heating_system_forecast


def extract_energy_use_holiday_homes(database_manager: DatabaseManager) -> pd.DataFrame:
    df = transform_holiday_homes_to_horizontal(calculate_energy_use(database_manager)).copy()
    df = df.rename(columns={'building_category': 'building_group'})
    df.loc[df.energy_source=='Elektrisitet', 'energy_source'] = 'Electricity'
    df.loc[df.energy_source=='fossil', 'energy_source'] = 'Fossil'
    return df


def main() -> None:  # noqa: D103
    from ebm.model.file_handler import FileHandler   # noqa: I001, PLC0415
    fh = FileHandler(directory='input')
    dm = DatabaseManager(fh)
    years = YearRange(2020, 2050)

    building_code_parameters = fh.get_building_code()
    scurve_params = dm.get_scurve_params()
    s_curves_by_condition = calculate_s_curves(scurve_params, building_code_parameters, years)

    area_forecast = extract_area_forecast(years,
                                          building_code_parameters=building_code_parameters,
                                          area_parameters=dm.get_area_parameters(),
                                          s_curves_by_condition=s_curves_by_condition,
                                          database_manager=dm)

    print(area_forecast)

    energy_need_kwh_m2 = extract_energy_need(years, dm)
    print(energy_need_kwh_m2)

    heating_systems_projection = extract_heating_systems_forecast(years, dm)
    print(heating_systems_projection)


if __name__ == '__main__':
    main()
