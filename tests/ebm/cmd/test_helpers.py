import os
import pathlib

from ebm.cmd.helpers import configure_json_log


def test_configure_json_log_missing_dotenv(tmp_path):
    os.chdir(tmp_path)
    assert not pathlib.Path('.env').is_file(), 'Expected no .env file in root'
    configure_json_log()


def test_configure_json_log_create_given_log_directory(tmp_path):
    os.chdir(tmp_path)
    expected_log_directory = tmp_path / 'brand-new-log'
    configure_json_log(log_directory=str(expected_log_directory))

    assert expected_log_directory.is_dir(), f'{expected_log_directory} was not created as expected'


def test_configure_json_log_create_default_log_directory(tmp_path):
    """Make sure log is the default when no log directory is found"""
    os.chdir(tmp_path)
    expected_log_directory = tmp_path / 'log'
    configure_json_log(True)

    assert expected_log_directory.is_dir(), f'{expected_log_directory} was not created as expected'


def test_configure_json_log_create_no_log_directory_on_false(tmp_path):
    """Make sure log is the default when no log directory is found"""
    os.chdir(tmp_path)
    expected_log_directory = tmp_path / 'log'
    configure_json_log(False)

    assert not expected_log_directory.is_dir(), f'{expected_log_directory} was created.'
