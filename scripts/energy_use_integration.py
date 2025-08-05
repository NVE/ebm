import os
import pathlib

import pandas as pd
import pytest

from ebm import extractors
from ebm.cmd.helpers import load_environment_from_dotenv, configure_loglevel
from ebm.cmd.pipeline import load_config
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_use import calculate_energy_use
from ebm.model.file_handler import FileHandler


def test_energy_use():
    cwd = pathlib.Path(__file__).parent / pathlib.Path(r'../tests/ebm/data')
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

    energy_use_kwh_with_building_group = calculate_energy_use(database_manager=database_manager,
                                                              years=years,
                                                              area_parameters=area_parameters,
                                                              scurve_parameters=scurve_parameters,
                                                              tek_parameters=tek_parameters)

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


def test_energy_use_holiday_home():
    cwd = pathlib.Path(__file__).parent / pathlib.Path(r'../tests/ebm/data')
    os.chdir(cwd)
    load_environment_from_dotenv()

    configure_loglevel(os.environ.get('LOG_FORMAT', None))
    input_path, output_path, years = load_config()
    input_path = pathlib.Path('kalibrert')

    output_path.mkdir(exist_ok=True)

    file_handler = FileHandler(directory=input_path)
    database_manager = DatabaseManager(file_handler=file_handler)

    energy_use_holiday_homes = extractors.extract_energy_use_holiday_homes(database_manager)

    holiday = pd.melt(energy_use_holiday_homes, id_vars=['building_group', 'energy_source'], var_name='year', value_name='kwh')
    holiday = holiday.set_index(['building_group', 'energy_source', 'year'])
    holiday.loc[:, 'kwh'] = holiday.loc[:, 'kwh'] * 1_000_000

    assert holiday.loc[('Fritidsboliger', 'Bio', 2050)].iloc[0] ==  1_510_492_631.9257426
    assert holiday.loc[('Fritidsboliger', 'Fossil', 2050)].iloc[0] == 100_000_000
    assert holiday.loc[('Fritidsboliger', 'Electricity', 2050)].iloc[0] ==  3_156_584_204.2180767


if __name__ == "__main__":
    pytest.main()
