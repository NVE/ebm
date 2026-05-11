import os
import pathlib

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from ebm.model.file_handler import FileHandler


def transform_dataframe(dataframe, columns=None, years_to_add=10, title='DataFrame'):
    columns = columns or ['year', 'building_year', 'period_start_year', 'period_end_year']
    df = dataframe.copy()
    for column in columns:
        if column not in df.columns:
            continue
        logger.debug(f'Adding {years_to_add} to {title}.{column}')
        df[column] = df[column].apply(lambda x: x + years_to_add if x != 0 else x)
    return df


def main():
    load_dotenv(pathlib.Path('.env'))

    years_to_add = int(os.environ.get('YEARS_TO_ADD', 10))
    input_path = pathlib.Path(os.environ.get('EBM_INPUT_DIRECTORY', 'input'))
    output_path = pathlib.Path(os.environ.get('EBM_INPUT_ADD_YEARS', f'input{2010+years_to_add}'))
    output_path.mkdir(exist_ok=True)

    logger.debug(f'Loading files from {input_path}')
    logger.debug(f'   Saving files to {output_path}')
    fh = FileHandler(directory=input_path)
    fh.create_missing_input_files()

    files = [file for file in input_path.glob('*.csv') if file.name in fh.files_to_check]
    files = filter(lambda f: f.name in fh.files_to_check, files)
    for file in files:
        output_file = output_path / file.name
        df = pd.read_csv(file)

        if 'holiday' in file.name:
            # Do not transform holiday. Requires special data.
            transformed = df
        else:
            logger.info(f'Transforming {file.name}')
            transformed = transform_dataframe(df, years_to_add=years_to_add, title=file.name)

        if len(transformed.compare(df)) > 0 or not output_file.exists():
            logger.info(f'Writing {output_file}')
            transformed.to_csv(output_file, index=False)
        else:
            logger.debug(f'Skipping unchanged dataframe {output_file}')


if __name__ == '__main__':
    main()
