import pathlib
import sys

import pytest
from unittest.mock import MagicMock, patch

from ebm.cmd import initialize
from ebm.model.file_handler import FileHandler
from ebm.__version__ import version


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch) -> pathlib.Path:
    monkeypatch.chdir(tmp_path)
    return pathlib.Path(tmp_path)


def test_init_return_input_directory(tmp_cwd: pathlib.Path):
    assert initialize.init(FileHandler(directory=tmp_cwd)) == tmp_cwd


def test_init_call_create_output(tmp_cwd):
    fh = FileHandler(directory=tmp_cwd)
    fh.default_data_directory = lambda: pathlib.Path('data_dir')

    output_directory = tmp_cwd / 'output'
    assert not output_directory.is_dir()

    with patch('ebm.cmd.initialize.create_input') as create_input_mock:
        initialize.init(fh)
        assert output_directory.is_dir()


def test_init_call_create_input(tmp_cwd: pathlib.Path):
    fh = FileHandler(directory=tmp_cwd)
    fh.default_data_directory = lambda: pathlib.Path('data_dir')
    with patch('ebm.cmd.initialize.create_input') as create_input_mock:
        initialize.init(fh)
        create_input_mock.assert_called_with(fh, source_directory=pathlib.Path('data_dir'))


def test_init_call_create_input_using_default_override_if_exists(tmp_cwd: pathlib.Path):
    # Keep default input override so that it can be reset later
    #  It might be better to change tmp_cwd fixture to handle the reset
    old = initialize.DEFAULT_INPUT
    fh = FileHandler(directory=tmp_cwd)

    override_path = tmp_cwd / 'load_from_here'
    override_path.mkdir()

    initialize.DEFAULT_INPUT = override_path
    with patch('ebm.cmd.initialize.create_input') as create_input_mock:
        initialize.init(fh)
        create_input_mock.assert_called_with(fh, source_directory=override_path)

    # Reset default input override
    initialize.DEFAULT_INPUT = old


@patch('ebm.cmd.initialize.create_input')
@patch('ebm.cmd.initialize.copy_available_calibration_files')
def test_init_call_create_input_using_source_directory(mock_create_input,
                                                       mock_copy_available_calibration_files,
                                                       tmp_cwd: pathlib.Path):
    fh = FileHandler(directory=tmp_cwd)

    source_directory = tmp_cwd / 'load_from_here'
    source_directory.mkdir()

    initialize.init(fh, source_directory=source_directory)
    mock_create_input.assert_called_with(fh, source_directory=source_directory)
    mock_copy_available_calibration_files.assert_called_with(fh, source_directory=source_directory)

    # Reset default input override


def test_create_input_with_default_data_source():
    mock_file_handler = MagicMock(spec=FileHandler)
    mock_file_handler.input_directory = pathlib.Path('input-test')
    mock_file_handler.default_data_directory = lambda: pathlib.Path('DEFAULT_DATA_SOURCE')

    with patch('ebm.cmd.initialize.copy_available_calibration_files') as copy_available_calibration_files:
        initialize.create_input(mock_file_handler)
        mock_file_handler.create_missing_input_files.assert_called_once()
        mock_file_handler.create_missing_input_files.assert_called_with(source_directory=pathlib.Path('DEFAULT_DATA_SOURCE'))
        copy_available_calibration_files.assert_not_called()


def test_create_input_with_optional_source_directory(tmp_cwd: pathlib.Path):
    input_directory = tmp_cwd / 'input-test'
    input_directory.mkdir()

    file_handler = FileHandler(input_directory)

    the_source = tmp_cwd / 'optional-source'
    the_source.mkdir()
    for f in file_handler.files_to_check:
        input_file = the_source / f
        input_file.write_text(f)

    mock_file_handler = MagicMock(spec=FileHandler)
    mock_file_handler.input_directory = input_directory

    initialize.create_input(mock_file_handler, source_directory=the_source)
    mock_file_handler.create_missing_input_files.assert_called_with(source_directory=the_source)


@pytest.mark.parametrize("filename", ['calibrate_heating_rv.xlsx', 'calibrate_heating_rv.csv', 'calibrate_energy_consumption.xlsx', 'calibrate_energy_consumption.csv'])
def test_copy_available_calibration_files(tmp_cwd:pathlib.Path, filename: str):
    input_directory = tmp_cwd / 'input-test'
    input_directory.mkdir()

    the_source = tmp_cwd / 'optional-source'
    the_source.mkdir()

    calibration_file = the_source / filename
    calibration_file.write_text(filename)

    mock_file_handler = MagicMock(spec=FileHandler)
    mock_file_handler.input_directory = input_directory

    initialize.copy_available_calibration_files(mock_file_handler, the_source)

    assert (input_directory / filename).is_file(), f'{filename} not found in input directory'


def test_create_input_with_optional_source_directory_raise_error_on_missing_files(tmp_cwd: pathlib.Path):
    mock_file_handler = MagicMock(spec=FileHandler)
    mock_file_handler.input_directory = tmp_cwd / 'input-test'

    the_source = tmp_cwd / 'alternate-source'
    with pytest.raises(NotADirectoryError):
        initialize.create_input(mock_file_handler, source_directory=the_source)

    the_source.mkdir()

    with pytest.raises(FileNotFoundError):
        initialize.create_input(mock_file_handler, source_directory=the_source)


def test_create_output_directory(tmp_cwd: pathlib.Path):
    output_directory = tmp_cwd / 'output'
    result = initialize.create_output_directory(output_directory)
    assert result == output_directory
    assert result.is_dir()

    output_file = tmp_cwd / 'putout' / 'ebm_output.txt'
    initialize.create_output_directory(filename=output_file)
    filename_result = initialize.create_output_directory(filename=output_file)
    assert filename_result == output_file.parent
    assert filename_result.is_dir()


def test_create_output_directory_twice_sould_work_without_raising_exception(tmp_cwd: pathlib.Path):
    """Creating the same directory twice is fine as long as the directory exists in the end"""
    output_directory = tmp_cwd / 'output'
    assert initialize.create_output_directory(output_directory).is_dir()
    assert initialize.create_output_directory(output_directory).is_dir()


def test_create_output_directory_raises_io_error_when_output_directory_is_a_file(tmp_cwd: pathlib.Path):
    """When the parameter output_directory is a file, create_output_directory should raise an IOError"""
    parent = tmp_cwd / 'putout'
    output_file = parent / 'ebm_output.txt'
    parent.mkdir()
    output_file.write_text('This is a file')
    with pytest.raises(IOError, match='^.*is a file'):
        initialize.create_output_directory(output_directory=output_file)


def test_create_output_raises_value_error_on_empty_arguments():
    with pytest.raises(ValueError):
        initialize.create_output_directory(output_directory=None, filename=None)


@pytest.mark.skipif(sys.platform != "win32", reason="Test only runs on Windows")
def test_default_input_override():
    expected_path = f'X:\\NAS\\Data\\ebm\\default-input-{".".join(version.split(".")[:2])}'
    assert initialize.DEFAULT_INPUT == pathlib.Path(expected_path)


if __name__ == "__main__":
    pytest.main()
