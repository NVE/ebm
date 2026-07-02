import os
import pathlib
import sys

import numpy as np
import pandas as pd
from pandas import DataFrame

from energibruksmodell.helpers import bema_sort, group_non_residential, group_residential, filter_by_start_end_year
from loguru import logger

from ebm.cmd.helpers import configure_loglevel, load_environment_from_dotenv
from ebm.model.data_classes import YearRange


def score_building_group_default(building_categories):
    default_building_categories = building_categories.assign(building_group='default').assign(score=0.1).assign(num=len(building_categories))
    return default_building_categories


def score_building_group_residential(building_categories):
    building_category_count = len(building_categories)
    building_groups = building_categories.pipe(group_non_residential, building_group='non_residential').pipe(group_residential, building_group='residential')
    building_groups = building_groups.merge(building_groups.groupby(['building_group'], as_index=False).agg(num=('building_category', 'count')), on=['building_group'])
    building_groups = building_groups.assign(score=np.maximum(0.1, 1.0-(building_groups.num/building_category_count)))
    return building_groups


def score_building_category_specific(building_categories):
    specific_building_categories = building_categories.assign(building_group='none').assign(score=1.0).assign(num=1)
    specific_building_categories['building_group'] = specific_building_categories['building_category']
    return specific_building_categories


def score_building_category_all(specific_building_categories: pd.DataFrame, building_groups: pd.DataFrame, default_building_categories: pd.DataFrame) -> pd.DataFrame:
    all_building_categories = pd.concat([specific_building_categories, building_groups, default_building_categories])
    return all_building_categories


def score_building_code_specific(building_codes):
    specific_building_codes = building_codes.assign(score=1.0).assign(num=1)
    specific_building_codes['code_group'] = specific_building_codes['building_code']
    return specific_building_codes


def score_building_code_group_default(building_codes):
    default_building_codes = building_codes.assign(code_group='default').assign(score=0.15).assign(num=8)
    return default_building_codes


def score_building_code_all(building_code_specific: pd.DataFrame, building_code_default: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([building_code_specific, building_code_default])


def find_conflict_linenos(df, grouping=None, lineno_column=None, drop_non_conflicts=True):
    if lineno_column is None:
        if 'lineno' not in df.columns:
            msg = f'Parameter lineno_column is None and df has no columns named `lineno`'
            raise KeyError(msg)
        lineno_column = 'lineno'
    if lineno_column not in df.columns:
        msg = f'Column `{lineno_column}` not found in dataframe when searching for conflicts'
        raise KeyError(msg)

    default_grouping = [
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'year',
        'score',
        'high_score',
    ]

    grouping = grouping if grouping is not None else [c for c in default_grouping if c in df.columns]
    if not grouping:
        raise ValueError('No valid grouping columns found')

    grouped = (df
        .groupby(by=grouping)[[lineno_column, 'start_year', 'end_year']]
        .agg(start_year=('start_year', 'first'),
             end_year=('end_year', 'first'),
             cnt=(lineno_column, 'count'),
             conflict_linenos=(lineno_column, lambda x: list(x)))
    )
    grouped['conflict_count'] = (grouped.cnt -1).clip(0)
    grouped = grouped.drop(columns=['cnt'])

    if not drop_non_conflicts:
        return grouped.reset_index()
    return grouped[grouped.conflict_count >= 1].reset_index()


def explode_conflict_linenos(df):
    if 'conflict_linenos' not in df.columns:
        raise KeyError('df missing required column `conflict_linenos`')
    df = df.assign(conflict_lineno=df.conflict_linenos).explode('conflict_lineno')
    df = df.assign(definition_lineno=df.conflict_linenos).explode('definition_lineno')
    df = df[df.conflict_lineno!=df.definition_lineno]
    return df.drop(columns=['conflict_linenos'])


def drop_duplicated_conflict_lines(df):
    required_columns = ['definition_lineno', 'conflict_lineno', 'year', 'years']
    missing_columns = [c for c in required_columns if not c in df.columns]
    if missing_columns:
        msg = f'Dataframe missing required columns {missing_columns}'
        raise KeyError(msg)

    df['dupe_min'] = df[['definition_lineno', 'conflict_lineno']].min(axis=1)
    df['dupe_max'] = df[['definition_lineno', 'conflict_lineno']].max(axis=1)

    df['duplicated'] = df.duplicated(['dupe_min', 'dupe_max', 'years'], keep='first')

    return df[((df.new_period==True) & (~df['duplicated']))].drop(columns=['dupe_min', 'dupe_max', 'duplicated', 'new_period'])


def group_years(df, grouping, year_column='year'):
    def year_group(r):
        #lambda r: f"{r['min']}-{r['max']}" if r['min'] != r['max'] else str(r['min'])
        return f"{r['min']}-{r['max']}" if r['min'] != r['max'] else str(r['min'])
    df = df.sort_values(grouping + [year_column])
    df['expect_year']=df.groupby(grouping)[year_column].shift()+1
    df['new_period'] = df['expect_year'] != df[year_column]
    df['period'] = df['new_period'].cumsum()

    df = (df.merge((df
                .groupby(['period'])
                .agg(min=(year_column, 'min'), max=(year_column, 'max'))
                .apply(year_group, axis=1).rename('years').reset_index()),
            on='period'))
    return df[grouping + [year_column] + ['period', 'new_period', 'years']]


def merge_building_category_code_score(all_building_categories: pd.DataFrame, all_building_codes: pd.DataFrame) -> pd.DataFrame:
    building_category_code_score = all_building_categories.rename(columns={'score': 'building_category_score'}).merge(all_building_codes.rename(columns={'score': 'building_code_score'}), how='cross', suffixes=['_building_category', '_building_code'])
    building_category_code_score['num'] = building_category_code_score['num_building_category'] + building_category_code_score['num_building_code' ]
    building_category_code_score['score'] = building_category_code_score['building_category_score'] * building_category_code_score['building_code_score']
    return building_category_code_score.pipe(bema_sort).sort_values(['score'], kind='stable', ascending=False)


def merge_energy_need_improvements_with_score(energy_need_improvements_csv: DataFrame,
                                              building_category_code_score: DataFrame) -> DataFrame:
    df = energy_need_improvements_csv.merge(building_category_code_score,
                                              left_on=['building_category', 'building_code'],
                                              right_on=['building_group', 'code_group'],
                                              suffixes=['', '_org'])
    return df[['_energy_need_improvements_csv',
                   'building_category', 'building_code',
                   'purpose', 'function', 'start_year',  'end_year',
                   'value',
                   'building_group', 'num_building_category',
                   'code_group', 'num_building_code',
                   'building_category_org', 'building_code_org',
                   'score',
                   'building_category_score', 'building_code_score', 'num'
            ]]


def detect_conflicts(df_years):
    required_columns = [
        '_energy_need_improvements_csv',
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'year',
        'score',
    ]

    if missing_columns := [column for column in required_columns if column not in df_years.columns]:
        raise ValueError(f'Missing required columns: {", ".join(missing_columns)}')

    df = df_years.rename(columns={'_energy_need_improvements_csv': 'lineno'})
    filtered_by_start_end_year = df.pipe(filter_by_start_end_year)
    conflict_linenos =  filtered_by_start_end_year.pipe(find_conflict_linenos)
    exploded_linenos = conflict_linenos.pipe(explode_conflict_linenos)
    return exploded_linenos


def group_conflict_rows(conflicting_line_pairs_by_year, energy_need_improvements_csv):
    _periodical= make_energy_need_improvements_periodical(conflicting_line_pairs_by_year, energy_need_improvements_csv)
    _periodical

    _deduped_conflict_rows = _periodical.merge(
        energy_need_improvements_csv['building_category,building_code,purpose,function,start_year,value,end_year,_energy_need_improvements_csv'.split(',')].add_suffix('_conflict'),
        left_on=['conflict_lineno'],
        right_on=['_energy_need_improvements_csv_conflict'],
        suffixes=['', '_conflict']).pipe(
            drop_duplicated_conflict_lines
    )
    return _deduped_conflict_rows


def make_energy_need_improvements_periodical(df_years, energy_need_improvements_csv):
    required_columns = [
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'year',
        'score',
        'definition_lineno',
        'conflict_lineno',
    ]
    if missing_columns := [column for column in required_columns if column not in df_years.columns]:
        raise ValueError(f'Missing required columns: {", ".join(missing_columns)}')

    group_by_columns = ['building_category_org', 'building_code_org', 'purpose', 'function', 'definition_lineno',
               'conflict_lineno']
    grouped_by_year = (df_years
        .reset_index()
        .pipe(group_years, grouping=group_by_columns)
    )
    improvement_columns = [
        'building_category',
        'building_code',
        'purpose','function',
        'start_year','value',
        'end_year',
        '_energy_need_improvements_csv',
    ]

    grouped_by_year = grouped_by_year.merge(
        energy_need_improvements_csv[improvement_columns].add_suffix('_definition'),
        left_on=['definition_lineno'],
        right_on=['_energy_need_improvements_csv_definition'],
        suffixes=['', '_definition'])
    return grouped_by_year

def mark_high_score(df: pd.DataFrame) -> pd.DataFrame:
    """Tag rows that have the highest score within each definition group.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe that must include the columns
        ``building_category_org``, ``building_code_org``, ``purpose``,
        ``function``, and ``score``.

    Returns
    -------
    pandas.DataFrame
        A copy-like dataframe with an added boolean column, ``high_score``,
        where ``True`` marks rows whose ``score`` equals the group maximum.
        Ties are marked as ``True`` for all tied rows.

    Raises
    ------
    ValueError
        If any required columns are missing from ``df``.
    """
    group_cols = ['building_category_org', 'building_code_org', 'purpose', 'function']
    required_columns = group_cols + ['score']
    if missing_columns := [c for c in required_columns if c not in df.columns]:
        msg = f'Missing required columns {", ".join(missing_columns)}'
        raise ValueError(msg)
    max_score = df.groupby(group_cols)['score'].transform('max')
    high_score = np.isclose(df['score'], max_score, rtol=1e-12, atol=1e-12)
    return df.assign(high_score=high_score)


def format_grouped_conflict_rows(_df):
    _df = _df[_df.definition_lineno < _df.conflict_lineno]
    # [['building_category_org', 'building_code_org', 'purpose', 'function', 'definition_lineno', 'conflict_line', 'years', 'start_year_conflict', 'end_year_conflict', 'start_year_definition', 'end_year_definition']]

    _lines = []

    _prev = None
    for _conflict in _df.itertuples():
        _conflict_count = 0
        _header_text = f'Category {_conflict.building_category_org}, Code {_conflict.building_code_org} Row {_conflict.definition_lineno} overlaps with row  {_conflict.conflict_lineno} ({_conflict.years})).'
        _definition_text = f'  definition:  {_conflict.definition_lineno:3}: {", ".join([str(getattr(_conflict, c)) for c in _df.columns if c.endswith("_definition") and not c.endswith("_csv_definition")])}'
        _definition_text = f'  definition:  {_conflict.definition_lineno:3}: {", ".join([str(getattr(_conflict, c)) for c in _df.columns if c.endswith("_definition") and not c.endswith("_csv_definition")])}'
        _conflict_text = f'    conflict:  {_conflict.conflict_lineno:3}: {", ".join([str(getattr(_conflict, c)) for c in _df.columns if c.endswith("_conflict") and not c.endswith("_csv_conflict")])}'

        if _prev is None or (_prev.definition_lineno != _conflict.definition_lineno):
            _prev = _conflict
            _lines.append(_header_text)
            _lines.append(_definition_text)
        _lines.append(_conflict_text)
    return _lines


def prepare_energy_need_improvements(df: pd.DataFrame):
    missing_columns = [
        c for c in ['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year', 'value'] if c not in df.columns
    ]
    if missing_columns:
        msg = f'Missing columns in input dataframe: {missing_columns}'
        raise ValueError(msg)

    cleaned = df[df.high_score].drop_duplicates(
        subset=['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year'], keep='first'
    )[['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year', 'value']]

    return cleaned.rename(columns={'building_category_org': 'building_category', 'building_code_org': 'building_code'}).pipe(bema_sort)


def main() -> None:
    load_environment_from_dotenv()
    configure_loglevel(log_format=os.environ.get('LOG_FORMAT', None))

    logger.debug(f'Starting {sys.executable} {__file__}')

    input_directory = pathlib.Path(r'C:\dev\ws\root\task\4061\input-periode-overlapp')
    input_directory = pathlib.Path(r'C:\dev\ws\root\task\4061\input-med-flere-perioder')
    input_directory = pathlib.Path(r'C:\dev\ws\root\task\4061\overlapping-tek17')
    energy_need_improvements_csv = pd.read_csv(input_directory / 'energy_need_improvements.csv')
    building_code_parameters_csv = pd.read_csv(input_directory / 'building_code_parameters.csv')
    # Spreadsheets typically starts counting at 1
    # Spreadsheets typically has a header row so that we should add 2 that the first row is identified as 2.

    energy_need_original_condition_csv = pd.read_csv(input_directory / 'energy_need_original_condition.csv')

    energy_need_improvements_csv = pd.read_csv(input_directory / 'energy_need_improvements.csv')
    energy_need_improvements_csv['_energy_need_improvements_csv'] = range(2, len(energy_need_improvements_csv) + 2)

    # 🛠️
    building_categories = pd.DataFrame({'building_category': energy_need_original_condition_csv.building_category.unique()})

    # 🛠️
    building_code_parameters_csv['building_code_parameters_csv'] = range(2, len(building_code_parameters_csv) + 2)
    building_codes = building_code_parameters_csv[['building_code', 'building_code_parameters_csv']]

    # 🛠️
    building_category_scores = score_building_category_all(
        score_building_category_specific(building_categories),
        score_building_group_residential(building_categories),
        score_building_group_default(building_categories)
    )

    # 🛠️
    building_code_scores = score_building_code_all(
        score_building_code_specific(building_codes),
        score_building_code_group_default(building_codes),
    )

    # 🛠️
    building_category_code_score = merge_building_category_code_score(building_category_scores, building_code_scores)

    # 🛠️
    energy_need_improvements_score = merge_energy_need_improvements_with_score(energy_need_improvements_csv, building_category_code_score)
    
    energy_need_improvements_high_score =  energy_need_improvements_score.pipe(mark_high_score)

    year_range = YearRange(2020, 2050)

    # 🛠️
    energy_need_improvements_yearly = year_range.cross_join(energy_need_improvements_high_score)
    #conflicts = detect_conflicts(energy_need_improvements_yearly)

    # 🛠️
    #df = make_energy_need_improvements_periodical(conflicts, energy_need_improvements_csv)
    df = energy_need_improvements_high_score.rename(columns={'_energy_need_improvements_csv': 'definition_lineno'})
    display_columns = ['building_category', 'building_code',
                       'building_category_org', 'building_code_org', 'purpose', 'function',
                       'start_year', 'value', 'end_year', 'score', 'high_score', 'definition_lineno']

    duplicate_columns = display_columns[2:-3]
    display_df = df[df.high_score][display_columns].drop_duplicates(duplicate_columns).query('building_category_org=="apartment_block"').pipe(bema_sort).iloc[::-1]
    print(display_df.to_markdown())




if __name__ == '__main__':
    main()
