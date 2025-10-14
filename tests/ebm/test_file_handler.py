import os
import pathlib
import shutil
from unittest.mock import Mock

import pandas as pd
import pandera as pa
import pytest

from ebm.model.file_handler import FileHandler


@pytest.fixture
def tmp_file_handler(tmp_path):
    os.chdir(tmp_path)
    input_directory = tmp_path / 'input'
    input_directory.mkdir()
    file_handler = FileHandler(input_directory)
    file_handler.create_missing_input_files()
    return file_handler

def test_default_data_directory():
    """Return the default data directory: calibrated"""
    expected_directory = pathlib.Path(__file__).parent.parent.parent / 'ebm' / 'data' / 'calibrated'
    assert FileHandler.default_data_directory() == expected_directory


def test_check_for_missing_files_return_list(tmp_path):
    """
    FileHandler.check_for_missing_files must return a list consisting of file names when the files do not exists. The
     list must contain the 7 elements:
        building_codes.csv, building_code_parameters.csv, scurve_parameters.csv, new_buildings_population.csv,
        new_buildings_house_share.csv, construction_building_category_yearly.csv, area_parameters.csv
    """
    os.chdir(tmp_path)
    fh = FileHandler(directory=tmp_path)
    missing_files = set(fh.check_for_missing_files())
    assert 'building_code_parameters.csv' in missing_files
    assert 's_curve.csv' in missing_files
    assert 'population_forecast.csv' in missing_files
    assert 'new_buildings_residential.csv' in missing_files
    assert 'area_new_residential_buildings.csv' in missing_files
    assert 'area.csv' in missing_files
    assert 'energy_need_behaviour_factor.csv' in missing_files
    assert 'energy_need_original_condition.csv' in missing_files
    assert 'improvement_building_upgrade.csv' in missing_files
    assert 'energy_need_improvements.csv' in missing_files
    assert 'holiday_home_energy_consumption.csv' in missing_files
    assert 'holiday_home_stock.csv' in missing_files
    assert 'area_per_person.csv' in missing_files
    assert 'heating_system_initial_shares.csv' in missing_files
    assert 'heating_system_efficiencies.csv' in missing_files
    assert 'heating_system_forecast.csv' in missing_files
    assert len(missing_files) == 16, 'Unexpected list length returned from check_for_missing_files'


def test_check_for_missing_files_raises_file_not_found_error(tmp_path):
    """
    FileHandler.check_for_missing_files is expected to raise an FileNotFoundError if input directory does not exist
    """

    new_directory = tmp_path / 'new_directory'
    fh = FileHandler(directory=new_directory)
    with pytest.raises(FileNotFoundError):
        fh.check_for_missing_files()


def test_check_for_missing_files_raises_not_a_directory_error(tmp_path):
    """
    FileHandler.check_for_missing_files is expected to raise an NotADirectory if input_directory is a file
    """

    new_file = tmp_path / 'new_file'
    new_file.write_text('new_file is a file')
    fh = FileHandler(directory=new_file)

    with pytest.raises(NotADirectoryError):
        fh.check_for_missing_files()


def test_filehandler_init_supports_alternative_path(tmp_path):
    """
    FileHandler.__init__ must support alternative path for input_directory when the directory parameter is set
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'tupni'
    input_directory.mkdir()

    fh = FileHandler(directory=input_directory.name)
    assert fh.input_directory == pathlib.Path('tupni')
    building_code_id = tmp_path / 'tupni' / 'area_per_person.csv'

    with building_code_id.open('w') as open_file:
        open_file.write('building_category,area_per_person\nkindergarten,0.6')
        open_file.close()

    assert 'area_per_person.csv' not in fh.check_for_missing_files()
    assert isinstance(fh.get_area_per_person(), pd.DataFrame)


def test_filehandler_init_coerce_input_directory_to_pathlib_path(tmp_path):
    """
    FileHandler.__init__ should change the directory parameter to pathlib.Path when it is of another type (str)
    """
    os.chdir(tmp_path)

    fh = FileHandler(directory='special_input')
    assert isinstance(fh.input_directory, pathlib.Path)


def test_filehandler_init_support_input_directory_from_environment_variable(tmp_path):
    """
    FileHandler.__init__ must read input_directory from environment variable EBM_INPUT_DIRECTORY when the parameter
        directory is None and EBM_INPUT_DIRECTORY is set.
    """
    os.environ['EBM_INPUT_DIRECTORY'] = str(tmp_path / 'special_directory_from_env')

    fh = FileHandler(directory=None)
    assert fh.input_directory == pathlib.Path(tmp_path) / 'special_directory_from_env'


def test_filehandler_create_missing_input_files(tmp_path):
    """
    FileHAndler.create_missing_input must create required files in <input_directory> when called:
    building_codes.csv, building_code_parameters.csv, scurve_parameters.csv, population.csv,
        new_buildings_house_share.csv, construction_building_category_yearly.csv, area_parameters.csv
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'input'
    input_directory.mkdir()

    fh = FileHandler(input_directory)
    fh.create_missing_input_files()

    assert (input_directory / 'building_code_parameters.csv').is_file()
    assert (input_directory / 's_curve.csv').is_file()
    assert (input_directory / 'population_forecast.csv').is_file()
    assert (input_directory / 'new_buildings_residential.csv').is_file()
    assert (input_directory / 'area_new_residential_buildings.csv').is_file()
    assert (input_directory / 'area.csv').is_file()
    assert (input_directory / 'energy_need_original_condition.csv').is_file()
    assert (input_directory / 'improvement_building_upgrade.csv').is_file()
    assert (input_directory / 'energy_need_improvements.csv').is_file()
    assert (input_directory / 'holiday_home_energy_consumption.csv').is_file()
    assert (input_directory / 'heating_system_initial_shares.csv').is_file()
    assert (input_directory / 'heating_system_efficiencies.csv').is_file()
    assert (input_directory / 'heating_system_forecast.csv').is_file()


def test_filehandler_create_missing_input_files_from_source_directory(tmp_path):
    """
    FileHAndler.create_missing_input must create required files in FileHandler.input_directory sourced
    from source_directory
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'target' / 'input'
    input_directory.mkdir(parents=True)

    source_directory = tmp_path / 'source'
    source_directory.mkdir()

    fh = FileHandler(input_directory)

    for input_file in fh.files_to_check:
        (source_directory / input_file).write_text(input_file + ' from ' + str(source_directory))

    fh.create_missing_input_files(source_directory=source_directory)

    for file_to_check in fh.files_to_check:
        assert (input_directory / file_to_check).is_file(), f'{file_to_check} is not a file in {source_directory}'
        actual_text = (input_directory / file_to_check).read_text()
        expected_text = file_to_check + ' from ' + str(source_directory)
        assert actual_text == expected_text, f'{file_to_check} does not contain {expected_text}'

@pytest.mark.parametrize('extension', ['.xlsx', '.csv'])
def test_filehandler_is_calibrated(tmp_file_handler: FileHandler, extension):
    """Make sure is_calibrated return True when it finds two files with appropriate file extensions"""
    assert not tmp_file_handler.is_calibrated(), 'Expected check_calibrated to return False when missing 2 calibrated files'

    calibrate_energy_consumption = tmp_file_handler.input_directory / tmp_file_handler.CALIBRATE_ENERGY_CONSUMPTION
    calibrate_energy_consumption.with_suffix(extension).write_text('calibrated')
    assert not tmp_file_handler.is_calibrated(), 'Expected check_calibrated to return False when missing 1 calibrated file'

    calibrate_energy_requirement = tmp_file_handler.input_directory / tmp_file_handler.CALIBRATE_ENERGY_REQUIREMENT
    calibrate_energy_requirement.with_suffix(extension).write_text('calibrated')

    assert tmp_file_handler.is_calibrated(), 'Expected check_calibrated to return True'


@pytest.mark.parametrize('extension', ['.xlsx', '.csv'])
def test_get_calibrate_heating_rv(tmp_file_handler: FileHandler, extension: str):
    file = tmp_file_handler.input_directory / tmp_file_handler.CALIBRATE_ENERGY_REQUIREMENT

    directory = pathlib.Path(__file__).parent / pathlib.Path(r'../ebm/data/kalibrert')
    source_file = directory / f'calibrate_heating_rv{extension}'

    shutil.copy(source_file, file.with_suffix(extension))

    df: pd.DataFrame = tmp_file_handler.get_calibrate_heating_rv()

    assert 'building_category' in df.columns
    assert 'purpose' in df.columns
    assert 'heating_rv_factor' in df.columns
    assert len(df) == 0, 'Expected empty calibration file'


@pytest.mark.parametrize('extension', ['.xlsx', '.csv'])
def test_get_calibrate_heating_systems(tmp_file_handler: FileHandler, extension: str):
    file = tmp_file_handler.input_directory / tmp_file_handler.CALIBRATE_ENERGY_CONSUMPTION

    directory = pathlib.Path(__file__).parent / pathlib.Path(r'../ebm/data/kalibrert')
    source_file = directory / f'calibrate_energy_consumption{extension}'

    shutil.copy(source_file, file.with_suffix(extension))

    df: pd.DataFrame = tmp_file_handler.get_calibrate_heating_systems()

    assert 'building_category' in df.columns
    assert 'to' in df.columns
    assert 'from' in df.columns
    assert 'factor' in df.columns
    assert len(df) == 39, 'Expected 39 rows in calibration file'


def test_filehandler_validate_created_input_file(tmp_file_handler):
    tmp_file_handler.validate_input_files()


@pytest.mark.parametrize('input_file_name', [FileHandler.AREA,
                                             FileHandler.BUILDING_CODE_PARAMS,
                                             FileHandler.AREA_NEW_RESIDENTIAL_BUILDINGS,
                                             FileHandler.NEW_BUILDINGS_RESIDENTIAL,
                                             FileHandler.POPULATION_FORECAST,
                                             FileHandler.S_CURVE])
def test_validate_input_file_validates_expected_files(tmp_file_handler, input_file_name):
    """
    Ensure all files are validated in validate_input_files()

    This implementation works by deleting the file to test deleting the input_file_name and look for FileNotFoundError
    """
    assert 'Temp' in tmp_file_handler.input_directory.parts or 'tmp' in tmp_file_handler.input_directory.parts, \
        'Temp or tmp not found in path. Refusing to run test'

    tmp_file_handler.create_missing_input_files()

    input_file = tmp_file_handler.input_directory / input_file_name
    input_file.unlink()
    with pytest.raises(FileNotFoundError, match=f'.*{input_file_name}'):
        tmp_file_handler.validate_input_files()


def test_filehandler_validate_created_input_file_raises_schemaerrors_on_fail(tmp_file_handler):
    """
     Ensure pa.DataFrameSchema::validate is invoked lazy by checking for SchemaErrors
    (as opposed to SchemaError without a trailing s)
     """
    df = tmp_file_handler.get_file(FileHandler.AREA)
    df.loc[0, 'building_category'] = 'småhus'
    df.loc[0, 'building_code'] = 'TAKK42'
    df.loc[0, 'area'] = -1
    df.to_csv(tmp_file_handler.input_directory / FileHandler.AREA)

    with pytest.raises(pa.errors.SchemaErrors):
        tmp_file_handler.validate_input_files()


def test_filehandler_get_area_per_person_calls_get_file(tmp_path):
    fh = FileHandler(directory=tmp_path)
    fh.get_file = Mock(return_value='FROM_FILE')

    assert fh.get_area_per_person() == 'FROM_FILE'
    fh.get_file.assert_called_with('area_per_person.csv')


if __name__ == "__main__":
    pytest.main()
