import argparse
import os
import pathlib
import sys
import typing

from dotenv import load_dotenv
from loguru import logger
import pandas as pd


DEFAULT_SOURCE = pathlib.Path('C:/Users/lfep/work_space/Energibruksmodell/ebm/data/heating_systems_projection.xlsx')

def add_number_to_filename(file: pathlib.Path):
    if not file.exists():
        return file
    logger.debug(f'{file} exists. Incrementing filename.')
    counter = 1
    new_file = file.with_stem(f"{file.stem}_{counter}")
    while new_file.exists():
        counter += 1
        new_file = file.with_stem(f"{file.stem}_{counter}")
    logger.debug(f'{new_file=}')
    return new_file


def xlsx_to_csv(source, target):
    logger.debug(f'Converting {source} to {target}')
    df = pd.read_excel(source)
    df.to_csv(target, sep=',', encoding='utf-8', index=False)

    return True


def csv_to_xlsx(source, target):
    logger.debug(f'Converting {source} to {target}')
    df = pd.read_csv(source)
    df.to_excel(target, index=False)

    return True


def any_to_other(file_path: typing.Union[pathlib.Path, str], allow_overwrite=False):
    source = file_path if isinstance(file_path, pathlib.Path) else pathlib.Path(file_path)
    logger.debug(f'{source=}')
    if not source.is_file():
        raise FileNotFoundError(f'Source file {DEFAULT_SOURCE} not found')
    if source.suffix not in ['.xlsx', '.csv']:
        raise ValueError(f'Unknown file suffix {source.suffix}')

    # Default is converting from xlsx to csv
    convert_function = xlsx_to_csv
    target = source.with_suffix('.csv')

    if source.suffix == '.csv':
        # Convert from csv to xlsx instead
        target = source.with_suffix('.xlsx')
        convert_function = csv_to_xlsx

    if not allow_overwrite:
        target = add_number_to_filename(target)

    if convert_function(source, target):
        print(f'Wrote {source} to {target}')
    else:
        print('Uh, something went wrong?', sys.stderr)


def main():
    load_dotenv(pathlib.Path('.env'))
    argp = argparse.ArgumentParser()
    argp.add_argument('filename', type=str, default=os.environ.get('CONVERT_ANY_TO_OTHER', ''))

    arguments = argp.parse_args()

    source_path = pathlib.Path(arguments.filename)

    any_to_other(source_path, allow_overwrite=source_path.parent.name in ['data'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
