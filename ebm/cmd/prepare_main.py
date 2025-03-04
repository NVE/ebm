"""Functions used to make __main__ run"""
import argparse
import os
import pathlib
import sys
import textwrap
import typing
from dataclasses import dataclass
from typing import List

from loguru import logger

from ebm.__version__ import version

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from ebm.services.files import file_is_writable

TEK = """PRE_TEK49
PRE_TEK49
TEK49
TEK69
TEK87
TEK97
TEK07
TEK10
TEK17
TEK21""".strip().split('\n')


@dataclass
class EbmArguments:
    """Prototype for an argument or configuation class to be used by main. Its purpose is improved readability."""
    model_years: YearRange
    output_filename: pathlib.Path
    building_categories: typing.List[BuildingCategory]
    building_conditions = typing.List[BuildingCondition]
    tek_filter: typing.List[str]
    force_overwrite: bool
    open_after_writing: bool
    horizontal_years: bool
    input_directory: pathlib.Path
    create_input: bool
    csv_delimiter: str


def make_arguments(program_name, default_path: pathlib.Path) -> argparse.Namespace:
    """
    Create and parse command-line arguments for the area forecast calculation.

    Parameters
    ----------
    program_name : str
        Name of this program
    default_path : pathlib.Path
        Default path for the output file.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.

    Notes
    -----
    The function sets up an argument parser with various options including version, debug mode,
    filename, force write, open file after writing, CSV delimiter, building categories,
    creating default input, start year, and end year.
    """

    default_building_categories: List[str] = [str(b) for b in iter(BuildingCategory)]

    arg_parser = argparse.ArgumentParser(prog=program_name,
                                         description=f'Calculate EBM energy use {version}',
                                         formatter_class=argparse.RawTextHelpFormatter
                                         )
    arg_parser.add_argument('--version', '-v', action='version', version=f'{program_name} {version}')
    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
    arg_parser.add_argument('step', type=str, nargs='?',
                            choices=['area-forecast',
                                     'energy-requirements',
                                     'heating-systems',
                                     'energy-use'],
                            default='energy-use',
                            help="""
The calculation step you want to run. The steps are sequential. Any prerequisite to the chosen step will run 
    automatically.""")
    arg_parser.add_argument('output_file', nargs='?', type=pathlib.Path, default=default_path,
                            help=textwrap.dedent(
                                f'''The location of the file you want to be written. default: {default_path}
    If the file already exists the program will terminate without overwriting. 
    Use "-" to output to the console instead'''))
    arg_parser.add_argument('--categories', '--building-categories', '-c',
                            nargs='*', type=str, default=default_building_categories,
                            help=textwrap.dedent(f"""
                                   One or more of the following building categories: 
                                       {", ".join(default_building_categories)}. 
                                       The default is to use all categories."""
                                                 ))
    arg_parser.add_argument('--input', '--input-directory', '-i',
                            nargs='?',
                            type=pathlib.Path,
                            default=pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input')),
                            help='path to the directory with input files')
    arg_parser.add_argument('--force', '-f', action='store_true',
                            help='Write to <filename> even if it already exists')
    arg_parser.add_argument('--open', '-o', action='store_true',
                            help='Open <filename> with default application after writing. (Usually Excel)')
    arg_parser.add_argument('--csv-delimiter', '--delimiter', '-e', type=str, default=',',
                            help='A single character to be used for separating columns when writing csv. ' +
                                 'Default: "," Special characters like ; should be quoted ";"')
    arg_parser.add_argument('--create-input', action='store_true',
                            help='''
Create input directory containing all required files in the current working directory''')
    arg_parser.add_argument('--start-year', nargs='?', type=int,
                            default=os.environ.get('EBM_START_YEAR', 2020),
                            help=argparse.SUPPRESS)
    arg_parser.add_argument('--end-year', nargs='?', type=int,
                            default=os.environ.get('EBM_END_YEAR', 2050),
                            help=argparse.SUPPRESS)

    arg_parser.add_argument('--horizontal-years', '--horizontal', '--horisontal', action='store_true',
                            help='Show years horizontal (left to right)')

    arguments = arg_parser.parse_args()
    return arguments


RETURN_CODE_OK = 0
RETURN_CODE_FILE_EXISTS = 1
RETURN_CODE_FILE_NOT_ACCESSIBLE = 2


def check_output_file_status(output_file: pathlib.Path,
                             force: bool=False,
                             default_path: pathlib.Path = None,
                             program_name: str='ebm') -> int:
    """
    Checks if the output file exists and that it is writable. If force is true the output_file will be opened for
    appending. A permission denied at that point is an indication that the file is already open by another process.

    The following values may be returned
        - 0 RETURN_CODE_OK
        - 1 RETURN_CODE_FILE_NOT_ACCESSIBLE
        - 2 RETURN_CODE_FILE_EXISTS

    Parameters
    ----------
    output_file : pathlib.Path
    force : bool
    default_path : pathlib.Path
    program_name : str

    Returns
    -------
    int
    """
    default_path = default_path if default_path else pathlib.Path('output/ebm_output.xlsx')

    if output_file.is_file() and output_file != default_path and not force:
        # If the file already exists and is not the default, display error and exit unless --force was used.
        logger.error(f'{output_file}. already exists.')
        print(f"""
    You can overwrite the {output_file}. by using --force: {program_name} {' '.join(sys.argv[1:])} --force
    """.strip(),
              file=sys.stderr)
        return RETURN_CODE_FILE_EXISTS
    if output_file.name != '-' and not file_is_writable(output_file):
        # logger.error(f'{output_file} is not writable')
        return RETURN_CODE_FILE_NOT_ACCESSIBLE
    return RETURN_CODE_OK
