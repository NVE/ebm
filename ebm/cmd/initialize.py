"""Module for setting up input, output and managing default data"""
import argparse
import pathlib
import shutil
import typing

from loguru import logger

from ebm.model.file_handler import FileHandler
DEFAULT_INPUT_OVERRIDE = pathlib.Path('X:\\NAS\\Data\\ebm\\kalibrert\\')


def create_input(file_handler: FileHandler,
                 source_directory: typing.Optional[pathlib.Path]=None) -> bool:
    """
    Create any input file missing in file_handler.input_directory using the default data source.

    Parameters
    ----------
    source_directory :
    file_handler : FileHandler

    Returns
    -------
    bool
    """

    source = file_handler.default_data_directory()

    if source_directory:
        if not source_directory.is_dir():
            raise NotADirectoryError(f'{source_directory} is not a directory')

        source_fh = FileHandler(directory=source_directory)
        missing_files = source_fh.check_for_missing_files()
        if len(missing_files) > 0:
            msg = f'File not found {missing_files[0]}'
            raise FileNotFoundError(msg)
        source = source_directory

    file_handler.create_missing_input_files(source_directory=source)

    return True


def copy_available_calibration_files(source: pathlib.Path, file_handler: FileHandler):
    """

    Copies calibration file from source to file_handler

    Parameters
    ----------
    source : pathlib.Path
    file_handler : FileHandler

    Returns
    -------
    None

    """

    logger.debug(f'Copy calibration files from {source}')
    for calibration_file in [source / FileHandler.CALIBRATE_ENERGY_REQUIREMENT,
                             source / FileHandler.CALIBRATE_ENERGY_CONSUMPTION]:
        if calibration_file.is_file():
            shutil.copy(calibration_file, file_handler.input_directory)


def create_output_directory(output_directory: typing.Optional[pathlib.Path]=None,
                            filename: typing.Optional[pathlib.Path]=None) -> pathlib.Path:
    """
    Creates the output directory if it does not exist. If a filename is supplied its parent will be created.

    Parameters
    ----------
    output_directory : pathlib.Path, optional
        The path to the output directory.
    filename : pathlib.Path, optional
        The name of a file in a directory expected to exist.
    Raises
    -------
    IOError
        The output_directory exists, but it is a file.
    ValueError
        output_directory and filename is empty
    Returns
    -------
    pathlib.Path
        The directory
    """
    if not output_directory and not filename:
        raise ValueError('Both output_directory and filename cannot be None')
    if output_directory and output_directory.is_file():
        raise IOError(f'{output_directory} is a file')

    if output_directory:
        logger.debug(f'Creating output directory {output_directory}')
        output_directory.mkdir(exist_ok=True)
        return output_directory
    elif filename and not filename.is_file():
        logger.debug(f'Creating output directory {filename.parent}')
        filename.parent.mkdir()
        return filename.parent


def init(file_handler: FileHandler) -> pathlib.Path:
    """
    Initialize file_handler with input data from ebm.data or DEFAULT_INPUT_OVERRIDE.

    Parameters
    ----------
    file_handler : FileHandler

    Returns
    -------
    pathlib.Path
    """
    source_directory = file_handler.default_data_directory()
    if DEFAULT_INPUT_OVERRIDE.exists():
        source_directory = DEFAULT_INPUT_OVERRIDE

    create_input(file_handler, source_directory=source_directory)
    copy_available_calibration_files(source_directory, file_handler)
    return file_handler.input_directory


def main() -> int:
    """
    Run module using command line arguments. Currently create_input.

    Returns
    -------
    int

    See Also
    --------
    create_input
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('input', nargs='?', type=pathlib.Path, default='input')
    ap.add_argument('source',nargs='?', type=pathlib.Path, default=FileHandler.default_data_directory())

    arguments = ap.parse_args()

    create_input(FileHandler(directory=arguments.input), source_directory=arguments.source)
    return 0

if __name__ == '__main__':
    main()
