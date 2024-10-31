import os
import pathlib

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
        TEK_ID.csv, TEK_parameters.csv, scurve_parameters.csv, new_buildings_population.csv,
        new_buildings_house_share.csv, construction_building_category_yearly.csv, area_parameters.csv
    """
    os.chdir(tmp_path)
    fh = FileHandler(directory=tmp_path)
    missing_files = fh.check_for_missing_files()
    assert 'TEK_ID.csv' in missing_files
    assert 'TEK_parameters.csv' in missing_files
    assert 'scurve_parameters.csv' in missing_files
    assert 'new_buildings_population.csv' in missing_files
    assert 'new_buildings_house_share.csv' in missing_files
    assert 'construction_building_category_yearly.csv' in missing_files
    assert 'area_parameters.csv' in missing_files
    assert 'energy_requirement_original_condition.csv' in missing_files
    assert 'energy_requirement_reduction_per_condition.csv' in missing_files
    assert 'energy_requirement_yearly_improvements.csv' in missing_files
    assert 'energy_requirement_policy_improvements.csv' in missing_files
    assert 'heating_systems.csv' in missing_files
    assert len(missing_files) == 12, 'Unexpected list length returned from check_for_missing_files'


def test_filehandler_init_supports_alternative_path(tmp_path):
    """
    FileHandler.__init__ must support alternative path for input_directory when the directory parameter is set
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'tupin'
    input_directory.mkdir()

    fh = FileHandler(directory=input_directory.name)
    assert fh.input_directory == pathlib.Path('tupin')
    tek_id = tmp_path / 'tupin' / 'TEK_ID.csv'

    with tek_id.open('w') as open_file:
        open_file.write('TEK\nTEK21')
        open_file.close()

    assert 'TEK_ID.csv' not in fh.check_for_missing_files()
    assert isinstance(fh.get_tek_id(), pd.DataFrame)


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
    TEK_ID.csv, TEK_parameters.csv, scurve_parameters.csv, new_buildings_population.csv,
        new_buildings_house_share.csv, construction_building_category_yearly.csv, area_parameters.csv
    """
    os.chdir(tmp_path)

    input_directory = tmp_path / 'input'
    input_directory.mkdir()

    fh = FileHandler(input_directory)
    fh.create_missing_input_files()

    assert (input_directory / 'TEK_ID.csv').is_file()
    assert (input_directory / 'TEK_parameters.csv').is_file()
    assert (input_directory / 'scurve_parameters.csv').is_file()
    assert (input_directory / 'new_buildings_population.csv').is_file()
    assert (input_directory / 'new_buildings_house_share.csv').is_file()
    assert (input_directory / 'construction_building_category_yearly.csv').is_file()
    assert (input_directory / 'area_parameters.csv').is_file()
    assert (input_directory / 'energy_requirement_original_condition.csv').is_file()
    assert (input_directory / 'energy_requirement_reduction_per_condition.csv').is_file()
    assert (input_directory / 'energy_requirement_yearly_improvements.csv').is_file()
    assert (input_directory / 'energy_requirement_policy_improvements.csv').is_file()


def test_filehandler_validate_created_input_file(tmp_file_handler):
    tmp_file_handler.validate_input_files()


@pytest.mark.parametrize('input_file_name', [FileHandler.AREA_PARAMETERS,
                                             FileHandler.TEK_PARAMS,
                                             FileHandler.CONSTRUCTION_BUILDING_CATEGORY_AREA,
                                             FileHandler.CONSTRUCTION_BUILDING_CATEGORY_SHARE,
                                             FileHandler.CONSTRUCTION_POPULATION,
                                             FileHandler.SCURVE_PARAMETERS])
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
    df = tmp_file_handler.get_file(FileHandler.AREA_PARAMETERS)
    df.loc[0, 'building_category'] = 'småhus'
    df.loc[0, 'TEK'] = 'TAKK42'
    df.loc[0, 'area'] = -1
    df.to_csv(tmp_file_handler.input_directory / FileHandler.AREA_PARAMETERS)

    with pytest.raises(pa.errors.SchemaErrors):
        tmp_file_handler.validate_input_files()


if __name__ == "__main__":
    pytest.main()
