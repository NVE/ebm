import os
import pathlib

import pytest

from ebm import extractors
from ebm.cmd.helpers import load_environment_from_dotenv
from ebm.cmd.pipeline import load_config
from ebm.cmd.run_calculation import configure_loglevel
from ebm.model import bema
from ebm.model import energy_need as e_n
from ebm.model import energy_use as e_u
from ebm.model import heating_systems_parameter as h_s_param
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler
from ebm.s_curve import calculate_s_curves


def test_energy_use():
    cwd = pathlib.Path(r'../tests/ebm/data')
    os.chdir(cwd)
    load_environment_from_dotenv()

    configure_loglevel(os.environ.get('LOG_FORMAT', None))
    input_path, output_path, years = load_config()
    input_path = pathlib.Path('kalibrert')

    output_path.mkdir(exist_ok=True)

    file_handler = FileHandler(directory=input_path)
    database_manager = DatabaseManager(file_handler=file_handler)

    scurve_parameters = database_manager.get_scurve_params() # 📍

    area_parameters = database_manager.get_area_parameters() # 📍
    area_parameters['year'] = years.start

    tek_parameters = database_manager.file_handler.get_building_code() # 📍

    s_curves_by_condition = calculate_s_curves(scurve_parameters, tek_parameters, years) # 📌
    energy_need_kwh_m2 = extractors.extract_energy_need(years, database_manager)  # 📍
    heating_systems_projection = extractors.extract_heating_systems_projection(years, database_manager)  # 📍
    area_forecast = extractors.extract_area_forecast(years, s_curves_by_condition, tek_parameters, area_parameters, database_manager) # 📍
    total_energy_need = e_n.transform_total_energy_need(energy_need_kwh_m2, area_forecast)  # 📌
    heating_systems_parameter = h_s_param.heating_systems_parameter_from_projection(heating_systems_projection) # 📌
    energy_use_kwh_with_building_group = e_u.building_group_energy_use_kwh(heating_systems_parameter, total_energy_need)  # 📌

    building_group_energy_use_by_year = energy_use_kwh_with_building_group[['building_group', 'energy_product', 'year', 'kwh']].groupby(
        by=['building_group', 'energy_product', 'year']).sum()

    assert building_group_energy_use_by_year.loc[('bolig', 'Bio', 2020)].iloc[0] ==  4_788_825_216.425719
    assert building_group_energy_use_by_year.loc[('bolig', 'Bio', 2023)].iloc[0] == 4_757_203_300.271702
    assert building_group_energy_use_by_year.loc[('bolig', 'Bio', 2050)].iloc[0] == 3_390_632_536.1343603
    assert building_group_energy_use_by_year.loc[('bolig', 'Solar', 2023)].iloc[0] == 2_079_170.9996649974
    assert building_group_energy_use_by_year.loc[('bolig', 'Solar', 2050)].iloc[0] == 1_805_491.7126416897
    assert building_group_energy_use_by_year.loc[('bolig', 'DH', 2023)].iloc[0] ==  1_873_218_107.0187275
    assert building_group_energy_use_by_year.loc[('bolig', 'DH', 2050)].iloc[0] ==  2_482_497_950.4832416
    assert building_group_energy_use_by_year.loc[('bolig', 'Electricity', 2023)].iloc[0] == 37_088_406_609.24847
    assert building_group_energy_use_by_year.loc[('bolig', 'Electricity', 2050)].iloc[0] == 34_092_268_470.395252

    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Bio', 2023)].iloc[0] ==  101_346_044.63769531
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Bio', 2050)].iloc[0] ==  91_622_027.80740257
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Solar', 2023)].iloc[0] ==  864_815.1822786080
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Solar', 2050)].iloc[0] ==  781_837.3273693894
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'DH', 2023)].iloc[0] ==   4_426_506_223.131906
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'DH', 2050)].iloc[0] ==   4_672_303_519.084109
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Electricity', 2023)].iloc[0] ==  24_414_448_636.34977
    assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Electricity', 2050)].iloc[0] ==  20_626_689_875.071304

    # assert building_group_energy_use_by_year.loc[('yrkesbygg', 'Fossil', 2050)].iloc[0] == np.nan
    # assert building_group_energy_use_by_year.loc[('Fritidsboliger', 'Bio', 2050)].iloc[0] ==  1_510_492_631.92574
    # assert building_group_energy_use_by_year.loc[('Fritidsboliger', 'Fossil', 2050)].iloc[0] == 100_00_000
    # assert building_group_energy_use_by_year.loc[('Fritidsboliger', 'Electricity', 2050)].iloc[0] ==  3_156_584_204.21808



if __name__ == "__main__":
    pytest.main()
