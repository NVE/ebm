from ebm import extractors
from ebm.cmd.result_handler import transform_to_sorted_heating_systems
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model import heating_systems_parameter as h_s_param
from ebm.model import energy_need as e_n
from ebm.model import energy_use as e_u

from ebm.model.file_handler import FileHandler
from ebm.s_curve import calculate_s_curves

def calculate_energy_use_wide(ebm_input):
    fh = FileHandler(directory=ebm_input)
    database_manager = DatabaseManager(file_handler=fh)
    years = YearRange(2020, 2050)
    heating_systems_projection = extractors.extract_heating_systems_projection(years, database_manager)  # 📍
    heating_systems_parameter = h_s_param.heating_systems_parameter_from_projection(heating_systems_projection)  # 📌
    building_code_parameters = database_manager.file_handler.get_building_code()  # 📍
    scurve_parameters = database_manager.get_scurve_params()  # 📍
    s_curves_by_condition = calculate_s_curves(scurve_parameters, building_code_parameters, years)  # 📌
    area_parameters = database_manager.get_area_parameters()  # 📍
    area_parameters['year'] = years.start
    area_forecast = extractors.extract_area_forecast(years, s_curves_by_condition, building_code_parameters,
                                                     area_parameters, database_manager)  # 📍
    energy_need_kwh_m2 = extractors.extract_energy_need(years, database_manager)  # 📍
    total_energy_need = e_n.transform_total_energy_need(energy_need_kwh_m2, area_forecast)  # 📌
    building_group_energy_use_kwh = e_u.building_group_energy_use_kwh(heating_systems_parameter, total_energy_need)
    energy_use_holiday_homes = extractors.extract_energy_use_holiday_homes(database_manager)  # 📍

    energy_use_wide = transform_to_sorted_heating_systems(building_group_energy_use_kwh,
                                                          energy_use_holiday_homes,
                                                          building_column='building_group')

    return energy_use_wide
