import pandas as pd

from ebm.cmd.result_handler import transform_holiday_homes_to_horizontal
from ebm.cmd.run_calculation import calculate_building_category_area_forecast, calculate_energy_use
from ebm.heating_systems_projection import HeatingSystemsProjection
from ebm.model.building_category import BuildingCategory
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


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