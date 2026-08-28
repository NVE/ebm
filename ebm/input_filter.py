from typing import Optional

import numpy as np
import pandas
import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.column_operations import replace_column_alias
from ebm.model.energy_purpose import EnergyPurpose
from energibruksmodell.helpers import bema_sort, filter_by_start_end_year, group_non_residential, group_residential
from loguru import logger


def score_building_group_default(building_categories: pd.DataFrame) -> pd.DataFrame:
    default_building_categories = building_categories.assign(building_group='default').assign(score=0.1).assign(num=len(building_categories))
    return default_building_categories


def score_building_group_residential(building_categories: pd.DataFrame) -> pd.DataFrame:
    building_category_count = len(building_categories)
    building_groups = (building_categories
                       .pipe(group_non_residential, building_group='non_residential')
                       .pipe(group_residential, building_group='residential')
    )
    building_groups = (building_groups
                       .merge((building_groups
                                    .groupby(['building_group'], as_index=False)
                                    .agg(num=('building_category', 'count')))
                              , on=['building_group']))

    building_groups = building_groups.assign(score=np.maximum(0.1, 1.0-(building_groups.num/building_category_count)))
    return building_groups


def score_building_category_specific(building_categories: pd.DataFrame) -> pd.DataFrame:
    specific_building_categories = building_categories.assign(building_group='none').assign(score=1.0).assign(num=1)
    specific_building_categories['building_group'] = specific_building_categories['building_category']
    return specific_building_categories


def score_building_category(building_categories: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        score_building_category_specific(building_categories),
        score_building_group_residential(building_categories),
        score_building_group_default(building_categories),
    ])


def score_building_code(building_codes: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        score_building_code_specific(building_codes),
        score_building_code_group_default(building_codes),
    ])


def score_building_code_specific(building_codes: pd.DataFrame) -> pd.DataFrame:
    specific_building_codes = building_codes.assign(score=1.0).assign(num=1)
    specific_building_codes['code_group'] = specific_building_codes['building_code']
    return specific_building_codes


def score_building_code_group_default(building_codes: pd.DataFrame) -> pd.DataFrame:
    default_building_codes = building_codes.assign(code_group='default').assign(score=0.15).assign(num=8)
    return default_building_codes


def find_conflict_linenos(df: pd.DataFrame, grouping: list[str]|None=None, lineno_column:str|None=None, drop_non_conflicts: bool=True) -> pd.DataFrame:
    if lineno_column is None:
        if 'lineno' not in df.columns:
            msg = 'Parameter lineno_column is None and df has no columns named `lineno`'
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


def explode_conflict_linenos(df: pd.DataFrame) -> pd.DataFrame:
    if 'conflict_linenos' not in df.columns:
        raise KeyError('df missing required column `conflict_linenos`')
    df = df.assign(conflict_lineno=df.conflict_linenos).explode('conflict_lineno')
    df = df.assign(definition_lineno=df.conflict_linenos).explode('definition_lineno')
    df = df[df.conflict_lineno!=df.definition_lineno]
    return df.drop(columns=['conflict_linenos'])


def drop_duplicated_conflict_lines(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ['definition_lineno', 'conflict_lineno']
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        msg = f'Dataframe missing required columns {missing_columns}'
        raise KeyError(msg)

    df['dupe_min'] = df[['definition_lineno', 'conflict_lineno']].min(axis=1)
    df['dupe_max'] = df[['definition_lineno', 'conflict_lineno']].max(axis=1)

    df['duplicated'] = df.duplicated(['dupe_min', 'dupe_max', 'years'], keep='first')

    return df[(df.new_period & (~df['duplicated']))].drop(columns=['dupe_min', 'dupe_max', 'duplicated', 'new_period'])


def combine_category_code_scores(all_building_categories: pd.DataFrame, all_building_codes: pd.DataFrame) -> pd.DataFrame:
    building_categories = all_building_categories.rename(columns={'score': 'building_category_score'})
    building_codes = all_building_codes.rename(columns={'score': 'building_code_score'})

    building_category_code_score = building_categories.merge(building_codes, how='cross', suffixes=['_building_category', '_building_code'])
    building_category_code_score['num'] = building_category_code_score['num_building_category'] + building_category_code_score['num_building_code' ]
    building_category_code_score['score'] = building_category_code_score['building_category_score'] * building_category_code_score['building_code_score']
    return building_category_code_score.pipe(bema_sort).sort_values(['score'], kind='stable', ascending=False)


def score_energy_need_improvements(energy_need_improvements_csv: pd.DataFrame,
                                   building_category_code_score: pd.DataFrame) -> pd.DataFrame:
    df = energy_need_improvements_csv.merge(building_category_code_score,
                                              left_on=['building_category', 'building_code'],
                                              right_on=['building_group', 'code_group'],
                                              suffixes=['', '_org'])
    return df[['lineno',
                   'building_category', 'building_code',
                   'purpose', 'function', 'start_year',  'end_year',
                   'value',
                   'building_group', 'num_building_category',
                   'code_group', 'num_building_code',
                   'building_category_org', 'building_code_org',
                   'score',
                   'building_category_score', 'building_code_score', 'num',
            ]]


def detect_conflicts(df_years: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        'lineno',
        'building_category_org',
        'building_code_org',
        'purpose',
        'function',
        'year',
        'score',
    ]

    if missing_columns := [column for column in required_columns if column not in df_years.columns]:
        msg = f'Missing required columns: {", ".join(missing_columns)}'
        raise ValueError(msg)

    filtered_by_start_end_year = df_years.pipe(filter_by_start_end_year)
    conflict_linenos =  filtered_by_start_end_year.pipe(find_conflict_linenos)
    exploded_linenos = conflict_linenos.pipe(explode_conflict_linenos)
    return exploded_linenos


def group_conflict_rows(conflicting_line_pairs_by_year: pd.DataFrame, energy_need_improvements_csv: pd.DataFrame) -> pd.DataFrame:
    _periodical= make_energy_need_improvements_periodical(conflicting_line_pairs_by_year, energy_need_improvements_csv)

    _deduped_conflict_rows = _periodical.merge(
        energy_need_improvements_csv[['building_category', 'building_code', 'purpose', 'function', 'start_year', 'value', 'end_year', 'lineno']].add_suffix('_conflict'),
        left_on=['conflict_lineno'],
        right_on=['lineno_conflict'],
        suffixes=['', '_conflict']).pipe(
            drop_duplicated_conflict_lines,
    )
    return _deduped_conflict_rows


def make_energy_need_improvements_periodical(df_years: pd.DataFrame, energy_need_improvements_csv: pd.DataFrame) -> pd.DataFrame:
    def group_years(df, grouping, year_column='year'):  # noqa: ANN001, ANN202
        def year_group(r):  # noqa: ANN202
            # lambda r: f"{r['min']}-{r['max']}" if r['min'] != r['max'] else str(r['min'])
            return f'{r["min"]}-{r["max"]}' if r['min'] != r['max'] else str(r['min'])

        df = df.sort_values([*grouping, year_column])
        df['expect_year'] = df.groupby(grouping)[year_column].shift() + 1
        df['new_period'] = df['expect_year'] != df[year_column]
        df['period'] = df['new_period'].cumsum()

        df = df.merge(
            (df.groupby(['period']).agg(min=(year_column, 'min'), max=(year_column, 'max')).apply(year_group, axis=1).rename('years').reset_index()),
            on='period',
        )
        return df[[*grouping, year_column, 'period', 'new_period', 'years']]

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
        msg = f'Missing required columns: {", ".join(missing_columns)}'
        raise ValueError(msg)

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
        'lineno',
    ]

    grouped_by_year = grouped_by_year.merge(
        energy_need_improvements_csv[improvement_columns].add_suffix('_definition'),
        left_on=['definition_lineno'],
        right_on=['lineno_definition'],
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


def format_grouped_conflict_rows(_df: pd.DataFrame) -> list[str]:
    _df = _df[_df.definition_lineno < _df.conflict_lineno]
    # [['building_category_org', 'building_code_org', 'purpose', 'function', 'definition_lineno', 'conflict_line', 'years', 'start_year_conflict', 'end_year_conflict', 'start_year_definition', 'end_year_definition']]

    _lines = []

    _prev = None
    for _conflict in _df.itertuples():
        _header_text = f'Category {_conflict.building_category_org}, Code {_conflict.building_code_org} Row {_conflict.definition_lineno} overlaps with row  {_conflict.conflict_lineno} ({_conflict.years})).'
        _definition_text = f'  definition:  {_conflict.definition_lineno:3}: {", ".join([str(getattr(_conflict, c)) for c in _df.columns if c.endswith("_definition") and not c.endswith("_csv_definition")])}'
        _conflict_text = f'    conflict:  {_conflict.conflict_lineno:3}: {", ".join([str(getattr(_conflict, c)) for c in _df.columns if c.endswith("_conflict") and not c.endswith("_csv_conflict")])}'

        if _prev is None or (_prev.definition_lineno != _conflict.definition_lineno):
            _prev = _conflict
            _lines.append(_header_text)
            _lines.append(_definition_text)
        _lines.append(_conflict_text)
    return _lines


def prepare_energy_need_improvements(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [
        c for c in ['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year', 'value'] if c not in df.columns
    ]
    if missing_columns:
        msg = f'Missing columns in input dataframe: {missing_columns}'
        raise ValueError(msg)

    cleaned = df[df.high_score].drop_duplicates(
        subset=['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year'], keep='first',
    )[['building_category_org', 'building_code_org', 'purpose', 'function', 'start_year', 'end_year', 'value']]

    return cleaned.rename(columns={'building_category_org': 'building_category', 'building_code_org': 'building_code'}).pipe(bema_sort)


def load_energy_need_improvements(building_categories=None, yearly_improvements=None, year_range=None,
                                  building_codes=None):
    building_category_scores = score_building_category(building_categories)
    building_code_scores = score_building_code(building_codes)
    building_category_code_score = combine_category_code_scores(building_category_scores, building_code_scores)
    energy_need_improvements_high_score = score_energy_need_improvements(yearly_improvements, building_category_code_score).pipe(mark_high_score)
    energy_need_improvements_yearly = year_range.cross_join(energy_need_improvements_high_score)
    prepared_energy_need_improvements = prepare_energy_need_improvements(energy_need_improvements_yearly)
    return prepared_energy_need_improvements.reset_index(drop=True)


def de_dupe_dataframe(df: pd.DataFrame, unique_columns: Optional[list[str]]=None) -> pd.DataFrame:
    """
    Drops duplicate rows in df based on building_category, TEK and purpose
    same as
        df.drop_duplicates(unique_columns)
    Parameters
    ----------
    df : pd.DataFrame
    unique_columns : list[str], optional
                     default= ['building_category', 'building_code', 'purpose']

    Returns
    -------
    pd.DataFrame

    """
    de_dupe_by = unique_columns if unique_columns else ['building_category', 'building_code', 'purpose']

    de_duped = df.drop_duplicates(de_dupe_by)
    return de_duped


def explode_dataframe(df: pd.DataFrame, building_code_list:Optional[list[str]]=None, dedupe_columns=None) -> pd.DataFrame:
    """
    Explode column aliases for building_category, TEK, purpose in dataframe.

    default in building_category is replaced with all options from BuildingCategory enum
    default in TEK is replaced with all elements in optional building_code_list parameter
    default in purpose is replaced with all options from EnergyPurpose enum

    Parameters
    ----------
    df : pd.DataFrame
    building_code_list : list of TEK to replace default, Optional
               default TEK49 PRE_TEK49 PRE_TEK49_RES_1950 TEK69 TEK87 TEK97 TEK07 TEK10 TEK17

    Returns
    -------
    pd.DataFrame

    """
    if not building_code_list:
        logger.debug('No building_code_list provided for explode_dataframe. Using default.')
        building_code_list = 'TEK49 PRE_TEK49 TEK69 TEK87 TEK97 TEK07 TEK10 TEK17'.split(' ')
    # expand building_category
    dedupe_columns = ['building_category', 'building_code', 'purpose'] if dedupe_columns is None else dedupe_columns

    df['_row'] = df.index.values + 1
    df['_building_category'] = df['building_category']
    df['_building_code'] = df['building_code']
    df['_purpose'] = df['purpose']

    df = replace_column_alias(df,
                              column='building_category',
                              values={'default': [b for b in BuildingCategory],
                                      'residential': [b for b in BuildingCategory if b.is_residential()],
                                      'non_residential': [b for b in BuildingCategory if not b.is_residential()]})
    # expand tek
    df = replace_column_alias(df, 'building_code', values=building_code_list, alias='default')

    # expand purpose
    df = replace_column_alias(df, 'purpose', values=[p for p in EnergyPurpose], alias='default')

    # Add priority column and sort
    df['bc_priority'] = df.building_category.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
    df['t_priority'] = df.building_code.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
    df['p_priority'] = df.purpose.apply(lambda x: 0 if '+' not in x else len(x.split('+')))

    if not 'priority' in df.columns:
        df['priority'] = 0
    df['priority'] = df.bc_priority + df.t_priority + df.p_priority

    # Explode
    df = (df
          .assign(_categories=df['building_category'])
          .assign(_codes=df['building_code'])
          .assign(_purps=df['purpose'])
    )
    df = df.assign(**{'building_category': df['building_category'].str.split('+'), }).explode('building_category')
    df = df.assign(**{'building_code': df['building_code'].str.split('+')}).explode('building_code')
    df = df.assign(**{'purpose': df['purpose'].str.split('+'), }).explode('purpose')
    # dedupe
    deduped = df.sort_values(by=['building_category', 'building_code', 'purpose', 'priority'])
    deduped['dupe'] = deduped.duplicated(dedupe_columns, keep='first')
    return deduped


def dedupe_and_merge_by_priority(df: pd.DataFrame) -> pd.DataFrame:

    """
    Deduplicate building records by selecting the highest-priority row per group.

    For each unique combination of ``building_category``, ``building_code``,
    ``purpose``, and ``function``, the row with the lowest numeric ``priority``
    value is selected. All non-key, non-private columns from the winning row
    are preserved in the result.

    Sorting is stable, so when multiple rows share the same priority, the
    original row order is used to break ties.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing building metadata. Must include the
        following columns:

        - ``building_category``
        - ``building_code``
        - ``purpose``
        - ``function``
        - ``priority``

    Returns
    -------
    pandas.DataFrame
        A deduplicated DataFrame with one row per unique
        (building_category, building_code, purpose, function) combination.
        The output excludes the ``priority`` column and includes all other
        non-private columns from the
        selected row.

    Raises
    ------
    ValueError
        If one or more required columns are missing from the input DataFrame.

    Notes
    -----
    - Lower numeric values indicate higher priority.
    - The function uses a stable sort (``mergesort``) to ensure deterministic
      behavior when priorities are equal.
    - Columns whose names start with an underscore (``_``) are excluded from
      the output.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "building_category": ["A", "A"],
    ...     "building_code": ["X1", "X1"],
    ...     "purpose": ["lighting", "lighting"],
    ...     "function": ["yearly_reduction", "yearly_reduction"],
    ...     "priority": [2, 1],
    ...     "area": [1000, 1200]
    ... })
    >>> dedupe_and_merge_by_priority(df)
      building_category building_code purpose function  area
    0                 A           X1   lighting yearly_reduction  1200
    """
    required_columns = {'building_category', 'building_code', 'purpose', 'priority', 'function'}
    if not required_columns.issubset(df.columns):
        msg = f'Column {", ".join(sorted(required_columns.difference(set(df.columns))))} not in DataFrame'
        raise ValueError(msg)

    columns_to_merge_on = ['building_category', 'building_code', 'purpose', 'function', 'priority']
    other_columns = [c for c in df.columns if c not in columns_to_merge_on]

    df_sorted = df.sort_values(['building_category', 'building_code', 'purpose', 'priority'],
                               kind='mergesort',
                               ascending=[True, True, True, True])
    winners = df_sorted.drop_duplicates(subset=['building_category', 'building_code', 'purpose', 'function'])[columns_to_merge_on]

    df = winners.merge(df_sorted, on=columns_to_merge_on)
    return df[['building_category', 'building_code', 'purpose', 'function'] + other_columns].drop_duplicates()
