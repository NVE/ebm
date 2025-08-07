import os
import pathlib
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
    assert 'building_codes.csv' in missing_files
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
    assert 'heating_systems_efficiencies.csv' in missing_files    
    assert 'heating_system_forecast.csv' in missing_files
    assert len(missing_files) == 17, 'Unexpected list length returned from check_for_missing_files'


def test_filehandler_init_supports_alternative_path(tmp_path):
    """
    FileHandler.__init__ must support alternative path for input_directory when the directory parameter is set
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'tupin'
    input_directory.mkdir()

    fh = FileHandler(directory=input_directory.name)
    assert fh.input_directory == pathlib.Path('tupin')
    building_code_id = tmp_path / 'tupin' / 'building_codes.csv'

    with building_code_id.open('w') as open_file:
        open_file.write('building_code\nTEK21')
        open_file.close()

    assert 'building_codes.csv' not in fh.check_for_missing_files()
    assert isinstance(fh.get_building_code_id(), pd.DataFrame)


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

    assert (input_directory / 'building_codes.csv').is_file()
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
    assert (input_directory / 'heating_systems_efficiencies.csv').is_file()
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
