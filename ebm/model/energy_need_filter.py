from typing import Optional

import pandas as pd
from loguru import logger

from ebm.model.building_category import BuildingCategory
from ebm.model.column_operations import replace_column_alias
from ebm.model.energy_purpose import EnergyPurpose


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
