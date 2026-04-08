import os
import pathlib

import pytest
from energibruksmodell.controllers import ebm_paths


def test_string_kwargs_are_left_untouched():
    @ebm_paths
    def func(*, file:str):
        return file

    result = func(file="data/input.txt")

    assert isinstance(result, str)
    assert result == 'data/input.txt'


def test_non_string_kwargs_are_untouched():
    @ebm_paths
    def func(*, value):
        return value

    obj = pathlib.Path("already/a/path")
    result = func(value=obj)

    assert result is obj


def test_mixed_kwargs():
    @ebm_paths
    def func(*, path:pathlib.Path | str, count:int):
        return path, count

    path, count = func(path="data/file.csv", count=5)

    assert count == 5
    assert isinstance(path, pathlib.Path)
    assert path == pathlib.Path("data/file.csv")


def test_positional_args_are_not_modified():
    """
    Test positional args are not modified.

    It is not clear that this is the correct behaviour, but it is how it works currently.
    """
    @ebm_paths
    def func(a, b):
        return a, b

    a, b = func("not/touched.txt", 123)

    assert a == "not/touched.txt"
    assert b == 123


def test_kwargs_only_are_processed():
    @ebm_paths
    def func(*args, **kwargs):
        return kwargs

    result = func(x="a/b/c", y=10)

    assert result["x"] == "a/b/c"
    assert result["y"] == 10


def test_ebm_paths_sets_default_value_input_for_input_directory(tmp_path):
    """ ebm_path annotation raise FileNotFoundError when path input_directory does not exist """
    @ebm_paths
    def func(input_directory: pathlib.Path | str | None = 'input'):
        return input_directory
    input = pathlib.Path(tmp_path) / 'input'
    input.mkdir()
    os.chdir(input.parent)

    result = func()
    assert result.name == 'input'


def test_ebm_paths_sets_default_value_from_environ(tmp_path):
    """ ebm_path annotation raise FileNotFoundError when path input_directory does not exist """
    @ebm_paths
    def func(input_directory: pathlib.Path | str | None = '$EBM_INPUT_DIRECTORY'):
        return input_directory

    os.environ['EBM_INPUT_DIRECTORY'] = 'from_environ'
    cd = pathlib.Path(tmp_path)
    os.chdir(cd)
    (cd / 'from_environ').mkdir()

    result = func()
    assert result.name == 'from_environ'


def test_ebm_paths_raise_file_not_found_error_on_missing_input_directory():
    """ ebm_path annotation raise FileNotFoundError when path input_directory does not exist """
    @ebm_paths
    def func(input_directory: pathlib.Path | str):
        return input_directory

    with pytest.raises(FileNotFoundError, match='input_directory `missing_input` does not exist'):
        func(input_directory='missing_input')


def test_ebm_paths_raise_not_a_directory_when_input_directory_is_a_file(tmp_path):
    """ ebm_path annotation raise FileNotFoundError when path input_directory does not exist """
    @ebm_paths
    def func(input_directory: pathlib.Path | str):
        return input_directory
    a_file = pathlib.Path(tmp_path) / 'a_file'

    a_file.write_text('some content')

    with pytest.raises(NotADirectoryError, match='input_directory `a_file` is not a directory'):
        func(input_directory=a_file)
