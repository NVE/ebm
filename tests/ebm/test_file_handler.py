import os
import pathlib

import pandas as pd

from ebm.model.file_handler import FileHandler


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
    assert len(missing_files) == 7, 'Unexpected list length returned from check_for_missing_files'


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


