import inspect
import os
import pathlib
import typing
from functools import wraps
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


def calculate_s_curves_by_condition(
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


def ebm_paths(func):
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        if 'input_directory' in bound.arguments and bound.arguments['input_directory'] is None:
            bound.arguments['input_directory'] = pathlib.Path('input')

        for name, value in bound.arguments.items():
            annotation = sig.parameters[name].annotation
            if (annotation is pathlib.Path or pathlib.Path in typing.get_args(annotation)) and isinstance(value, str):
                bound.arguments[name] = pathlib.Path(value)

        if 'input_directory' in bound.arguments:
            input_directory = bound.arguments['input_directory']
            if input_directory.name.endswith('EBM_INPUT_DIRECTORY'):
                input_directory = pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', default='input'))
                bound.arguments['input_directory'] = input_directory
            if not input_directory.exists():
                raise FileNotFoundError(f'input_directory `{bound.arguments['input_directory']}` does not exist')
            if not input_directory.is_dir():
                raise NotADirectoryError(f'input_directory `{bound.arguments['input_directory'].name}` is not a directory')

        return func(*bound.args, **bound.kwargs)

    return wrapper


@ebm_paths
def calculate_area_forecast(
    years: tuple[int, int] | YearRange | None = (2020, 2050),
    area_parameters: pd.DataFrame | pathlib.Path | str | None = None,
    building_code_parameters: pd.DataFrame | pathlib.Path | str |  None = None,
    population_forecast: pd.DataFrame | pathlib.Path | str | None = None,
    area_new_residential_buildings: pd.DataFrame | pathlib.Path | str | None = None,
    new_buildings_residential: pd.DataFrame | pathlib.Path | str | None = None,
    area_per_person: pd.DataFrame | pathlib.Path | str | None = None,
    input_directory: pathlib.Path | str | None = None,
    s_curves_by_condition: pd.DataFrame | pathlib.Path | str | None = None,
    **kwargs: pd.DataFrame|pd.Series,
) -> pd.DataFrame:

    """
    Calculate forecasted building area by year based on demographic, regulatory,
    and construction parameters.

    This function assembles all required input data—either from explicitly
    provided DataFrames/paths or by loading defaults via the internal database
    manager—and computes forecasted building areas for the specified year range.
    The calculation is delegated to ``calculate_all_area``.

    Parameters
    ----------
    years : tuple[int, int] or YearRange or None, default (2020, 2050)
        Year range for the forecast. If a tuple is provided, it must be
        ``(start_year, end_year)`` and will be converted to a ``YearRange``.
        If ``None``, default behavior depends on downstream loaders.

    area_parameters : pandas.DataFrame or pathlib.Path or str or None, optional
        Parameters describing existing building areas. If not provided as a
        DataFrame, the parameters are loaded from ``input_directory``.

    building_code_parameters : pandas.DataFrame or pathlib.Path or str or None, optional
        Parameters describing building code categories and conditions.
        Loaded from ``input_directory`` if not provided as a DataFrame.

    population_forecast : pandas.DataFrame or pathlib.Path or str or None, optional
        Population forecast data used in area calculations. If not provided,
        construction population data is loaded from the input_directory.

    area_new_residential_buildings : pandas.DataFrame or pathlib.Path or str or None, optional
        Area data for new residential buildings. Loaded from ``input_directory``
        if not provided.

    new_buildings_residential : pandas.DataFrame or pathlib.Path or str or None, optional
        Shares or categories of new residential buildings. Loaded from ``input_directory`` if not provided.

    area_per_person : pandas.DataFrame or str or pathlib.Path or None, optional
        Area-per-person assumptions used to derive residential area demand.
        Loaded from ``input_directory`` if not provided.

    input_directory : pathlib.Path or str or None, optional
        Base directory used for loading input data. If ``None``, the directory
        is taken from the ``EBM_INPUT_DIRECTORY`` environment variable or
        defaults to ``"input"``.

    s_curves_by_condition : pandas.DataFrame or pathlib.Path or str or None, optional
        S-curve parameters by building condition. If not provided as a
        DataFrame, they are loaded using ``calculate_s_curves_by_condition``.

    **kwargs : pandas.DataFrame or pandas.Series
        Additional keyword arguments forwarded to ``calculate_s_curves_by_condition``.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing forecasted building areas for all relevant
        categories and years within the specified range.

    Examples
    --------
    Calculate an area forecast for holiday homes using calibrated input data
    and a predefined year range:

    >>> from ebm.model.data_classes import YearRange
    >>> from energibruksmodell.controllers import calculate_area_forecast
    >>> af = calculate_area_forecast(
    ...     input_directory="../kalibrert",
    ...     years=YearRange(2020, 2050)
    ... )
    ... af.groupby(by=['building_category', 'year'])[['m2']].sum()

    See Also
    --------
    calculate_all_area : Core function performing the area forecast calculation.
    calculate_s_curves_by_condition : Load S-curve parameters for building conditions.

    Notes
    -----
    All inputs that are not explicitly provided as ``pandas.DataFrame`` objects
    are automatically loaded from the input_directory using ``DatabaseManager``.
    The function ensures a consistent year range and parameter set before
    performing the area forecast.

    """
    input_directory = input_directory if isinstance(input_directory, pathlib.Path) else pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    dm = DatabaseManager(FileHandler(directory=input_directory))
    years = YearRange(*years) if isinstance(years, tuple) else years

    if not isinstance(area_parameters, pd.DataFrame):
        area_parameters = dm.get_area_parameters()
    if not isinstance(building_code_parameters, pd.DataFrame):
        building_code_parameters = dm.get_building_codes()
    if not isinstance(s_curves_by_condition, pd.DataFrame):
        s_curves_by_condition = calculate_s_curves_by_condition(years=years,
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
    energy_need_kwh_m2: pd.DataFrame | pathlib.Path | str | None = None,
    area_forecast: pd.DataFrame | pathlib.Path | str | None = None,
    heating_systems_projection: pd.DataFrame | pathlib.Path | str | None = None,
    input_directory: pathlib.Path | str | None = None,
    **kwargs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate annual building energy use based on energy need, area forecast,
    and projected heating system shares.

    This function orchestrates the full energy-use pipeline. Missing inputs
    are computed automatically using corresponding model functions and
    shared configuration arguments.

    Parameters
    ----------
    years : tuple[int, int] or YearRange or None, default YearRange(2020, 2050)
        Year range for the calculation. If a tuple is provided, it is converted
        to a `YearRange` instance.

    energy_need_kwh_m2 : pandas.DataFrame or pathlib.Path or str or None, optional
        Energy need per square meter by building category and year.
        If `None`, the data is calculated using `calculate_energy_need`.

    area_forecast : pandas.DataFrame or pathlib.Path or str or None, optional
        Forecast of building areas by category, condition, and year.
        If `None`, the forecast is calculated using `calculate_area_forecast`.

    heating_systems_projection : pandas.DataFrame or pathlib.Path or str or None, optional
        Projection of heating system shares over time.
        If `None`, the projection is calculated using `calculate_heating_systems`.

    input_directory : pathlib.Path or str or None, optional
        Directory used to resolve input files. If not provided, the value is
        taken from the `EBM_INPUT_DIRECTORY` environment variable, falling back
        to ``"input"``.

    **kwargs : pandas.DataFrame
        Additional keyword arguments passed through to the underlying
        calculation functions. Typically used to override default input data.

    Returns
    -------
    pandas.DataFrame
        Annual energy use in kWh, aggregated by building group, heating system,
        and year.

    Notes
    -----
    The calculation pipeline consists of the following steps:

    1. Compute or load total energy need using energy intensity and area forecast.
    2. Derive heating system parameters from the system projection.
    3. Compute final energy use per building group and heating system.

    The function relies on model components from ``ebm.model.energy_need``,
    ``ebm.model.energy_use``, and
    ``ebm.model.heating_systems_parameter``.

    Examples
    --------
    Calculate energy use using default inputs::

        >>> from energibruksmodell.controllers import calculate_energy_use
        >>> energy_use = calculate_energy_use()

    """
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
    af = calculate_area_forecast(input_directory='kalibrert')
    er: EbmResult = run_model(model_years=YearRange(2020, 2050), input_directory=pathlib.Path('kalibrert'))
    print(
        af,
        er.energy_use_kwh,
        er.heating_systems,
        er.area_forecast_m2,
        er.energy_need_kwh_m2,
    )
    print('fine')


if __name__ == '__main__':
    main()
