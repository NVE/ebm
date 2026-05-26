import pathlib

import pytest

from ebm.cmd import prepare_main


def test_resolve_output_directory_for_energy_use_accepts_existing_directory(tmp_path: pathlib.Path):
    output_directory = tmp_path / 'output2'
    output_directory.mkdir()

    assert prepare_main.resolve_output_directory_for_energy_use(output_directory) == output_directory


def test_resolve_output_directory_for_energy_use_accepts_missing_suffixless_path(tmp_path: pathlib.Path):
    output_directory = tmp_path / 'output2'

    assert prepare_main.resolve_output_directory_for_energy_use(output_directory) == output_directory
    assert not output_directory.exists()


def test_resolve_output_directory_for_energy_use_rejects_existing_file(tmp_path: pathlib.Path):
    output_file = tmp_path / 'output2'
    output_file.write_text('already a file')

    with pytest.raises(NotADirectoryError, match='energy-use output must be a directory'):
        prepare_main.resolve_output_directory_for_energy_use(output_file)


def test_resolve_output_directory_for_energy_use_rejects_file_like_path(tmp_path: pathlib.Path):
    output_file = tmp_path / 'output2.xlsx'

    with pytest.raises(NotADirectoryError, match='file-like path'):
        prepare_main.resolve_output_directory_for_energy_use(output_file)


def test_resolve_output_directory_for_energy_use_rejects_console_output():
    with pytest.raises(ValueError, match='does not support writing output to the console'):
        prepare_main.resolve_output_directory_for_energy_use(pathlib.Path('-'))