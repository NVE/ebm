import os
import pathlib
import typing
from typing import TypedDict

import pandas as pd

from ebm.areaforecast.s_curve import calculate_s_curves
from ebm.heating_system_forecast import HeatingSystemsForecast
from ebm.holiday_home_energy import HolidayHomeEnergy
from ebm.model.area import calculate_all_area
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.dataframemodels import PolicyImprovement, YearlyReduction
from ebm.model.energy_requirement import energy_need_improvements
from ebm.model.file_handler import FileHandler


class EbmResult:
    area_forecast_m2: pd.DataFrame
    energy_need_kwh_m2: pd.DataFrame
    heating_systems: pd.DataFrame
    holiday_homes_kwh: pd.DataFrame
    energy_use_kwh: pd.DataFrame

    def __init__(
        self,
        area_forecast_m2: pd.DataFrame | None = None,
        energy_need_kwh_m2: pd.DataFrame | None = None,
        heating_systems: pd.DataFrame | None = None,
        holiday_homes_kwh: pd.DataFrame | None = None,
        energy_use_kwh: pd.DataFrame | None = None,
    ):
        self.area_forecast_m2 = area_forecast_m2
        self.energy_need_kwh_m2 = energy_need_kwh_m2
        self.energy_use_kwh = energy_use_kwh
        self.holiday_homes_kwh = holiday_homes_kwh
        self.heating_systems = heating_systems

    def __str__(self):
        if self.area_forecast_m2 is not None:
            return f'area_forecast with {len(self.area_forecast_m2.m2)} rows'
        return super().__str__()


def load_scurves(
    years: tuple[int, int] | None = (2020, 2050),
    input_directory: pathlib.Path | str | None = None,
    building_code_parameters: pd.DataFrame | pathlib.Path | None = None,
    scurve_parameters: pd.DataFrame | pathlib.Path | None = None,
    **kwargs: pd.DataFrame|pd.Series,
) -> pd.DataFrame:
    dm = DatabaseManager(FileHandler(directory=input_directory))
    years = YearRange(*years) if isinstance(years, tuple) else years
    scurve_parameters = scurve_parameters if scurve_parameters else dm.get_scurve_params()
    building_code_parameters = dm.get_building_codes() if not isinstance(building_code_parameters, pd.DataFrame) else building_code_parameters
    s_curves_by_condition = calculate_s_curves(scurve_parameters, building_code_parameters, years, **kwargs)
    return s_curves_by_condition


class AreaForecastInput(TypedDict, total=False):
    area_parameters: pd.DataFrame | pathlib.Path | None
    building_code_parameters: pd.DataFrame | pathlib.Path | None
    s_curves_by_condition: pd.DataFrame | pathlib.Path | pd.DataFrame | pathlib.Path | None
    population_forecast: pd.DataFrame | pathlib.Path | None
    area_new_residential_buildings: pd.DataFrame | pathlib.Path | None
    new_buildings_residential: pd.DataFrame | pathlib.Path | None
    area_per_person: pd.DataFrame | pathlib.Path | None

    s_curves_by_condition: pd.DataFrame | pathlib.Path | None


class EnergyNeedInput(TypedDict, total=False):
    original_condition: pd.DataFrame | pathlib.Path | None
    calibrate_heating_rv: pd.DataFrame | pathlib.Path | None
    behaviour_factor: pd.DataFrame | pathlib.Path | None
    improvements: pd.DataFrame | pathlib.Path | None
    improvement_building_upgrade: pd.DataFrame | pathlib.Path | None


class RunModelInput(AreaForecastInput, EnergyNeedInput, total=False):
    pass


def ebm_paths(func: typing.Callable) -> typing.Callable:
    def str_to_path(v):
        if isinstance(v, str):
            return pathlib.Path(v)
        return v
    def wrap_ebm_input(*args, **kwargs):
        past_as_str = {k: str_to_path(v) for k, v in kwargs.items()}
        res = func(*args, **past_as_str)
        return res

    return wrap_ebm_input


@ebm_paths
def calculate_area_forecast(
    years: tuple[int, int] | YearRange | None = (2020, 2050),
    area_parameters: pd.DataFrame | pathlib.Path | YearRange | None = None,
    building_code_parameters: pd.DataFrame | pathlib.Path | None = None,
    population_forecast: None = None,
    area_new_residential_buildings: None = None,
    new_buildings_residential: None = None,
    area_per_person: None = None,
    input_directory: pathlib.Path | str | None = None,
    s_curves_by_condition: pd.DataFrame | pathlib.Path | None = None,
    **kwargs: pd.DataFrame|pd.Series,
) -> pd.DataFrame:
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    dm = DatabaseManager(FileHandler(directory=input_directory))
    years = YearRange(*years) if isinstance(years, tuple) else years

    if not isinstance(area_parameters, pd.DataFrame):
        area_parameters = dm.get_area_parameters()
    if not isinstance(building_code_parameters, pd.DataFrame):
        building_code_parameters = dm.get_building_codes()
    if not isinstance(s_curves_by_condition, pd.DataFrame):
        s_curves_by_condition = load_scurves(years=years,
                                             input_directory=input_directory,
                                             building_code_parameters=building_code_parameters,
                                             **kwargs)

    if not isinstance(area_per_person, pd.DataFrame):
        area_per_person = dm.get_area_per_person()
    if not isinstance(area_new_residential_buildings, pd.DataFrame):
        area_new_residential_buildings = dm.get_area_new_residential_buildings()

    if not isinstance(population_forecast, pd.DataFrame):
        population_forecast = dm.get_construction_population()
    if not isinstance(new_buildings_residential, pd.DataFrame):
        new_buildings_residential = dm.get_new_buildings_category_share()

    df = calculate_all_area(area_new_residential_buildings, area_parameters, area_per_person,
                            building_code_parameters, population_forecast, new_buildings_residential,
                            s_curves_by_condition, years)

    return df


@ebm_paths
def calculate_energy_use(
    years: tuple[int, int] | YearRange | None = YearRange(2020, 2050),  # noqa: B008
    energy_need_kwh_m2: pd.DataFrame | pathlib.Path | None = None,
    area_forecast: pd.DataFrame | pathlib.Path | None = None,
    heating_systems_projection: pd.DataFrame | pathlib.Path | None = None,
    input_directory: pathlib.Path | str | None = None,
    **kwargs: pd.DataFrame,
) -> pd.DataFrame:
    from ebm.model import energy_need as e_n  # noqa: PLC0415
    from ebm.model import energy_use as e_u  # noqa: PLC0415
    from ebm.model import heating_systems_parameter as h_s_param  # noqa: PLC0415

    years = YearRange(*years) if isinstance(years, tuple) else years
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))

    if area_forecast is None:
        area_forecast = calculate_area_forecast(years=years, input_directory=input_directory, **kwargs)
    if energy_need_kwh_m2 is None:
        energy_need_kwh_m2 = calculate_energy_need(years=years, input_directory=input_directory, **kwargs)
    if heating_systems_projection is None:
        heating_systems_projection = calculate_heating_systems(years=years, input_directory=input_directory, **kwargs)

    total_energy_need = e_n.transform_total_energy_need(
        energy_need_kwh_m2,
        area_forecast.set_index(['building_category', 'building_code', 'building_condition', 'year']),
    )  # 📌
    heating_systems_parameter = h_s_param.heating_systems_parameter_from_projection(heating_systems_projection)  # 📌
    energy_use_kwh = e_u.building_group_energy_use_kwh(heating_systems_parameter, total_energy_need)  # 📌
    return energy_use_kwh


@ebm_paths
def calculate_energy_need(
    years: tuple[int, int] | YearRange | None = YearRange(2020, 2050),  # noqa: B008
    original_condition: pd.DataFrame | pathlib.Path | None = None,
    calibrate_heating_rv: pd.DataFrame | pathlib.Path | None = None,
    behaviour_factor: pd.DataFrame | pathlib.Path | None = None,
    improvements: pd.DataFrame | pathlib.Path | None = None,
    improvement_building_upgrade: pd.DataFrame | pathlib.Path | None = None,
    input_directory: pathlib.Path | str | None = None,
    **kwargs: pd.DataFrame|pd.Series,
) -> EbmResult:
    if ni := [p for p in ['calibrate_heating_rv', 'behaviour_factor'] if locals()[p] is not None]:
        msg = f'Parameter{"s" if len(ni) == 1 else ""} {", ".join(ni)} not implemented'
        raise NotImplementedError(msg)
    years = YearRange(*years) if isinstance(years, tuple) else years
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    dm = DatabaseManager(FileHandler(directory=input_directory))

    energy_need_original_condition = original_condition if original_condition is not None else dm.get_energy_req_original_condition()
    improvement_building_upgrade_csv = improvement_building_upgrade if improvement_building_upgrade is not None else dm.get_energy_req_reduction_per_condition()

    if improvements is not None:
        energy_need_improvements_policy = PolicyImprovement.from_energy_need_yearly_improvements(improvements)
    else:
        energy_need_improvements_policy = dm.get_energy_need_policy_improvement()

    if improvements is not None:
        energy_need_yearly_reduction = YearlyReduction.from_energy_need_yearly_improvements(improvements)
    else:
        energy_need_yearly_reduction = dm.get_energy_need_yearly_improvements()

    energy_need_kwh_m2 =  energy_need_improvements(
        energy_need_original_condition=energy_need_original_condition,
        improvement_building_upgrade=improvement_building_upgrade_csv,
        energy_need_improvements_policy=energy_need_improvements_policy,
        energy_need_yearly_reduction=energy_need_yearly_reduction)

    return energy_need_kwh_m2.set_index(['building_category', 'building_code', 'purpose', 'building_condition', 'year'])


@ebm_paths
def calculate_heating_systems(
    years: tuple[int, int] | YearRange | None = YearRange(2020, 2050),  # noqa: B008
    heating_system_initial_shares: pd.DataFrame | pathlib.Path | None = None,
    heating_system_initial_forecast: pd.DataFrame | pathlib.Path | None = None,
    heating_system_efficiencies: pd.DataFrame | pathlib.Path | None = None,
    building_code_parameters: pd.DataFrame | pathlib.Path | None = None,
    input_directory: pathlib.Path | str | None = None,
    **kwargs: pd.DataFrame|pd.Series,
) -> pd.DataFrame:
    from ebm.model import heating_systems_parameter as h_s_param  # noqa: PLC0415

    years = YearRange(*years) if isinstance(years, tuple) else years
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    dm = DatabaseManager(FileHandler(directory=input_directory))

    shares_start_year = dm.get_heating_systems_shares_start_year() if heating_system_initial_shares is None else heating_system_initial_shares
    efficiencies = heating_system_efficiencies if heating_system_efficiencies is not None else dm.get_heating_system_efficiencies()
    projection = heating_system_initial_forecast if heating_system_initial_forecast is not None else dm.get_heating_system_forecast()
    building_code_list = building_code_parameters if building_code_parameters is not None else dm.get_building_code_list()

    hsf = HeatingSystemsForecast(
        shares_start_year=shares_start_year,
        efficiencies=efficiencies,
        forecast=projection,
        building_code_list=building_code_list,
        period=years.subset(3),
    )
    hs: pd.DataFrame = hsf.calculate_forecast()
    df = hsf.pad_projection(hs, YearRange(2020, 2022))
    return h_s_param.heating_systems_parameter_from_projection(df)


@ebm_paths
def calculate_holiday_homes(
    years: tuple[int, int] | YearRange | None = (2020, 2050),
    population_forecast: None = None,
    holiday_home_energy_consumption: pd.DataFrame | pathlib.Path | None = None,
    holiday_home_stock: pd.DataFrame | pathlib.Path | None = None,
    input_directory: pathlib.Path | str | None = None,
    **kwargs:  pd.DataFrame|pd.Series,
) -> pd.DataFrame:
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    dm = DatabaseManager(FileHandler(directory=input_directory))
    population_forecast = population_forecast if population_forecast is not None else dm.get_construction_population().population
    holiday_home_stock = holiday_home_stock if holiday_home_stock is not None else dm.get_holiday_home_by_year()

    if holiday_home_energy_consumption is not None:
        electricity_usage_stats = holiday_home_energy_consumption.set_index('year')['fossilfuel']
    else:
        electricity_usage_stats = dm.get_holiday_home_electricity_consumption()

    if holiday_home_energy_consumption is not None:
        fuelwood_usage_stats = holiday_home_energy_consumption.set_index('year')['fuelwood']
    else:
        fuelwood_usage_stats = dm.get_holiday_home_fuelwood_consumption()

    if holiday_home_energy_consumption is not None:
        fossil_fuel_usage_stats = holiday_home_energy_consumption.set_index('year')['fossilfuel']
    else:
        fossil_fuel_usage_stats = dm.get_holiday_home_fuelwood_consumption()

    hhe = HolidayHomeEnergy(population_forecast, holiday_home_stock, electricity_usage_stats, fuelwood_usage_stats, fossil_fuel_usage_stats)

    el, wood, fossil = [e_u for e_u in hhe.calculate_energy_usage()]
    df = pd.DataFrame(data=[el, wood, fossil])
    df.insert(0, 'building_category', 'holiday_home')
    df.insert(1, 'energy_type', 'n/a')
    df['building_category'] = 'holiday_home'
    df['energy_type'] = ('electricity', 'fuelwood', 'fossil')
    output = df.reset_index().rename(columns={'index': 'unit'})
    output = output.set_index(['building_category', 'energy_type', 'unit'])
    return output


def run_model(input_directory: pathlib.Path | str | None=None, model_years: YearRange=YearRange(2020, 2050),
              **kwargs: AreaForecastInput) -> EbmResult:  # noqa: B008
    if isinstance(input_directory, str):
        input_directory = pathlib.Path(input_directory)
    elif input_directory is None:
        input_directory = pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))

    years = YearRange(*model_years) if isinstance(model_years, tuple) else model_years
    area_forecast = calculate_area_forecast(years=years, input_directory=input_directory)
    energy_need = calculate_energy_need(years=years, input_directory=input_directory)
    heating_systems = calculate_heating_systems(years=years, input_directory=input_directory)
    holiday_homes = calculate_holiday_homes(years=years, input_directory=input_directory)
    energy_use = calculate_energy_use(years=years, input_directory=input_directory)
    return EbmResult(
        area_forecast_m2=area_forecast,
        energy_need_kwh_m2=energy_need,
        heating_systems=heating_systems,
        holiday_homes_kwh=holiday_homes,
        energy_use_kwh=energy_use,
    )


def main() -> None:
    #af = calculate_area_forecast(input_directory=pathlib.Path('kalibrert'))
    af = calculate_area_forecast(input_directory='kalibrert')
    er: EbmResult = run_model(model_years=YearRange(2020, 2050), input_directory=pathlib.Path('kalibrert'))
    #er2: EbmResult = run_model(model_years=YearRange(2020, 2050), input_directory=pathlib.Path('kalibrert'))
    #er3: EbmResult = run_model(model_years=YearRange(2020, 2050), input_directory=pathlib.Path('kalibrert'))
    #er4: EbmResult = run_model(model_years=YearRange(2020, 2050), input_directory=pathlib.Path('kalibrert'))
    print(
        af,
        er.energy_use_kwh,
        er.heating_systems,
        er.area_forecast_m2,
        er.energy_need_kwh_m2,
      #  er2.holiday_homes_kwh,
      #  er3.holiday_homes_kwh,
      #  er4.holiday_homes_kwh,
    )
    print('fine')


if __name__ == '__main__':
    main()
