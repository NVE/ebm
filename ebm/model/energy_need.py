import pandas as pd

from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_requirement import EnergyRequirement


def extract_energy_need(years: YearRange, dm: DatabaseManager) -> pd.DataFrame:
    er_calculator = EnergyRequirement.new_instance(period=years, calibration_year=2023,
                                                   database_manager=dm)
    energy_need = er_calculator.calculate_for_building_category(database_manager=dm)

    energy_need = energy_need.set_index(['building_category', 'TEK', 'purpose', 'building_condition', 'year'])

    return energy_need


def transform_total_energy_need(energy_need_kwh_m2, area_forecast):
    total_energy_need = area_forecast.reset_index().set_index(
        ['building_category', 'TEK', 'building_condition', 'year']).merge(energy_need_kwh_m2, left_index=True,
                                                                          right_index=True)
    total_energy_need['energy_requirement'] = total_energy_need.kwh_m2 * total_energy_need.m2
    return total_energy_need
