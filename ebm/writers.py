import pathlib
from typing import NotRequired, TypedDict

import pandas as pd
from loguru import logger

from ebm.services.spreadsheet import add_top_row_filter, make_pretty


class SheetDefinition(TypedDict):
    content: pd.DataFrame
    name: NotRequired[str]
    top_row_filter: NotRequired[bool]


def write_pretty_excel(target: pathlib.Path, dataframes: list[SheetDefinition], top_row_filter: bool=False) -> list[pathlib.Path]:
    output_files = _write_excel(target, dataframes, top_row_filter=top_row_filter)
    for output_file in output_files:
        logger.debug('Make {} pretty', output_file)
        make_pretty(output_file)
        filter_sheets = [v.get('name') for v in dataframes if v.get('top_row_filter', top_row_filter) == True]
        if filter_sheets or top_row_filter == True:
            logger.debug('Adding top row filter to {} in {}', ', '.join(filter_sheets), output_file)
            add_top_row_filter(workbook_file=output_file, sheet_names=filter_sheets)
        logger.success('Wrote {}', output_file)
    return output_files


def write_excel(target: pathlib.Path, dataframes: list[SheetDefinition], **kwargs) -> list[pathlib.Path]:
    output_files = _write_excel(target, dataframes, **kwargs)
    for output_file in output_files:
        logger.success('Wrote {}', output_file)
    return output_files


def _write_excel(target: pathlib.Path, dataframes: list[SheetDefinition], **kwargs) -> list[pathlib.Path]:
    area_output = target.with_suffix('.xlsx')
    if not area_output.parent.is_dir():
        raise NotADirectoryError(f'{area_output.parent} is not a directory')

    with pd.ExcelWriter(area_output, engine='xlsxwriter') as writer:
        for v in dataframes:
            df = v['content']
            sheet_name = v.get('name', 'Sheet1')
            if isinstance(df.index, pd.MultiIndex):
                msg = f'Dataframe {sheet_name} intended for {area_output.name} has a MultiIndex'
                logger.warning(msg)
                logger.debug('Resetting index for dataframe {} intended for {}', sheet_name, area_output.name)
                df = df.reset_index()
            logger.debug('Writing sheet {} to {}', sheet_name, area_output)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    
    return [area_output]

