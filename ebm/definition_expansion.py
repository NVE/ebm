import pandas as pd
from loguru import logger


def add_lineno(df: pd.DataFrame) -> pd.DataFrame:
    if "lineno" not in df.columns:
        df["lineno"] = range(2, len(df) + 2)
    return df


def expand_definitions(definitions: pd.DataFrame, *,
                       grouping_columns: list[str] | None=None,
                       drop_helper_columns :bool=True) -> pd.DataFrame:
    """
    Expand compact, grouped definitions into one row per group and year.

    Definitions are authored compactly: a single line may target several building
    categories, building codes or purposes at once by joining them with ``+``
    (``'house+apartment_block'``) or by using an alias (``'default'``,
    ``'residential'``, ``'non_residential'``), and it covers a year range rather
    than a single year. This function resolves aliases, explodes the grouped
    columns and the year range, and applies the precedence rule that decides
    which line wins when several lines target the same group.

    Parameters
    ----------
    definitions : pd.DataFrame
        Grouped definitions, typically one row per line of a user maintained CSV.
        Must contain ``building_category`` and the columns named by
        `grouping_columns`, plus ``start_year`` and ``end_year``. If a ``lineno``
        column is absent it is added, numbering rows from 2 so the values match
        the line numbers of the source file (line 1 being the header).
    grouping_columns : list[str], optional
        Columns that together identify what a definition applies to. Defaults to
        whichever of ``building_category``, ``building_code``, ``purpose`` and
        ``function`` are present. Pass an explicit list for definitions keyed on
        other columns, for example
        ``['building_category', 'building_code', 'heating_systems', 'new_heating_systems']``.
    drop_helper_columns : bool, default True
        If True, drop the intermediate scoring columns ``score`` and
        ``lineno_count`` from the result. The ``lineno``, ``year`` and ``dupe``
        columns are returned in both cases.

    Returns
    -------
    pd.DataFrame
        One row per combination of `grouping_columns` and year, with a fresh
        ``RangeIndex``. Adds ``lineno`` (source line the row came from), ``year``
        (a single year taken from the ``start_year``..``end_year`` range, which
        are both retained) and ``dupe`` (True when several source lines remain in
        conflict for the same group and year). All other input columns are
        carried through unchanged.

    Raises
    ------
    ValueError
        If `definitions` is empty, if ``building_category`` is missing, if any
        column in `grouping_columns` is missing, if ``start_year`` or
        ``end_year`` is missing, if any ``start_year`` exceeds its ``end_year``,
        or if a column being exploded contains missing values.

    See Also
    --------
    collapse_years : Inverse operation, collapsing the per year rows back into ranges.
    summarize_energy_need_improvement_conflicts : Report the lines behind rows flagged by ``dupe``.

    Notes
    -----
    Precedence is "most specific wins": after exploding, each source line is
    scored by how many rows it produced, and for every group only the rows from
    the line with the fewest matches are kept. A line listing a single building
    category therefore overrides a ``default`` line for that category, while
    leaving every other category untouched. Lines that tie on specificity both
    survive and are flagged with ``dupe``.

    Precedence is resolved before the year range is expanded, so the grouping used
    for scoring does not include year.

    Presently, only the grouping columns building_category, building_code, purpose
    supports expansion on `+`.

    `definitions` is not modified.

    Examples
    --------
    A ``residential`` default covering all purposes, overridden for house lighting:

    >>> import pandas as pd
    >>> definitions = pd.DataFrame({
    ...     'building_category': ['residential', 'house'],
    ...     'building_code': ['TEK17', 'TEK17'],
    ...     'purpose': ['default', 'lighting'],
    ...     'start_year': [2020, 2020],
    ...     'end_year': [2021, 2021],
    ...     'value': [1.0, 0.85],
    ... })
    >>> expanded = expand_definitions(definitions)
    >>> expanded.shape
    (24, 9)

    The house lighting rows come from line 3 and carry its value, while the
    remaining 22 rows come from the ``residential`` default on line 2:

    >>> expanded.query("building_category == 'house' and purpose == 'lighting'")[
    ...     ['building_category', 'building_code', 'purpose', 'year', 'value', 'lineno']
    ... ]
       building_category building_code   purpose  year  value  lineno
    22             house         TEK17  lighting  2020   0.85       3
    23             house         TEK17  lighting  2021   0.85       3

    """
    if definitions.empty:
        raise ValueError('Dataframe `definitions` is empty. Cannot expand grouped definitions.')
    missing_columns = [c for c in ['building_category', 'start_year', 'end_year'] if c not in definitions.columns]
    if missing_columns:
        logger_msg = f'definitions columns: {definitions.columns}'
        logger.debug(logger_msg)
        error_msg = (f'DataFrame `definitions` does not contain all required columns. '
                     f'Missing column{"s" if len(missing_columns)!=1 else ""}: {", ".join(missing_columns)}')
        raise ValueError(error_msg)

    group_by = grouping_columns if grouping_columns else build_grouping(definitions)
    missing_grouping_columns = [c for c in group_by if c not in definitions.columns]
    if missing_grouping_columns:
        error_message = ('DataFrame `definitions` does not contain all columns specified in `grouping_columns`. '
                        f'Missing columns: {", ".join(missing_grouping_columns)}.')
        raise ValueError(error_message)

    wrong_dtype = [(c, definitions[c].dtype) for c in group_by if not pd.api.types.is_string_dtype(definitions[c])]
    if wrong_dtype:
        plural = "columns" if len(wrong_dtype)!=1 else "column"
        columns = ", ".join(f"`{c}`({dtype})" for c, dtype in wrong_dtype)
        error_message = f'DataFrame `definitions` {plural} {columns}. Expected dtype string.'
        raise ValueError(error_message)

    stages = [
        (add_lineno, ),
        (replace_building_category_default, ),
        (replace_building_code_default, ),
        (replace_purpose_default, ),
        (explode_building_category, ),
        (explode_building_code, ),
        (explode_purpose, ),
        (select_groups_with_lowest_lineno_count, {'grouping_columns': group_by, 'filter_columns': drop_helper_columns}),
        (explode_years, ),
        (mark_duplicates, {'grouping_columns': group_by}),
    ]
    result = definitions.copy() # work on copy (pandas before 3)

    for i, stage in enumerate(stages):
        stage_function, *parameters = stage
        result = result.pipe(stage_function, **parameters[0]) if parameters else result.pipe(stage_function)

    return result


def summarize_energy_need_improvement_conflicts(exploded_definition: pd.DataFrame, original_definition: pd.DataFrame) -> pd.DataFrame:
    required_columns = ('building_category', 'building_code', 'purpose', 'function', 'lineno')
    exploded_missing = [c for c in (*required_columns, 'year') if c not in exploded_definition.columns]
    if exploded_missing:
        msg=f'Dataframe exploded_definition is missing {", ".join(exploded_missing)} column(s)'
        raise ValueError(msg)
    original_missing = [c for c in required_columns if c not in original_definition.columns]
    if original_missing:
        msg = f'Dataframe original_definition is missing {", ".join(original_missing)} column(s)'
        raise ValueError(msg)

    deduped_dupes_on_dupes = group_dupes_on_dupes(exploded_definition)
    _df = deduped_dupes_on_dupes[
        [
            "building_category",
            "building_code",
            "purpose",
            "function",
            "year_x",
            "year_y",
            "lineno_x",
            "lineno_y",
        ]
    ][deduped_dupes_on_dupes["lineno_y"] > deduped_dupes_on_dupes["lineno_x"]]

    grouped_duplicated_lineno_summary = _df.pipe(group_duplicated_lineno_summary)
    conflicts = grouped_duplicated_lineno_summary.pipe(
        merge_duplicate_lineno_summary_with_definitions,
        energy_need_improvements=original_definition,
    )
    return conflicts


def build_grouping(df: pd.DataFrame) -> list[str]:
    return [c for c in ['building_category', 'building_code', 'purpose', 'function'] if c in df.columns]


def explode_building_category(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_category' not in df.columns:
        raise ValueError(r"Dataframe must contain a 'building_category' column")
    return explode_on_plus(df, column_name='building_category')


def explode_building_code(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_code' not in df.columns:
        return df

    return explode_on_plus(df, column_name='building_code')


def explode_purpose(df: pd.DataFrame) -> pd.DataFrame:
    if 'purpose' not in df.columns:
        return df
    df = explode_on_plus(df, column_name='purpose')

    return df


def explode_on_plus(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if df[column_name].isna().any():
        warning_msg = f"Dataframe '{column_name}' contains {df[column_name].isna().sum()} NaN values"
        logger.warning(warning_msg)
        msg = f"Dataframe '{column_name}' cannot be empty"
        raise ValueError(msg)
    df[column_name] = df[column_name].str.strip('+')
    df = df.assign(**{column_name: df[column_name].str.split(r"\++", regex=True)})
    df[column_name] = df[column_name].apply(lambda x: list(dict.fromkeys(v for v in x if v)))
    df = df.explode(column_name)
    return df


def explode_years(df: pd.DataFrame) -> pd.DataFrame:
    if 'start_year' not in df.columns:
        raise ValueError("Dataframe must contain a 'start_year' column")
    if 'end_year' not in df.columns:
        raise ValueError("Dataframe must contain a 'end_year' column")
    if (df.start_year > df.end_year).any():
        raise ValueError("start_year must be less than or equal to end_year")

    df = df.assign(
        **{
            "year": df.apply(
                lambda row: list(
                    range(int(row["start_year"]), int(row["end_year"]) + 1),
                ),
                axis=1,
            ),
        },
    ).explode("year")
    df["year"] = df["year"].astype(int)
    return df

def _replace_alias(column_value: str, alias: str, replacement:list[str]) -> str:
    try:
        return "+".join(replacement if token==alias else token for token in column_value)
    except TypeError:
        return column_value

def replace_building_category_default(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_category' not in df.columns:
        return df

    residential_replacement = [
        'house',
        'apartment_block',
    ]
    non_residential_replacement = [
        "kindergarten",
        "school",
        "university",
        "office",
        "retail",
        "hotel",
        "hospital",
        "nursing_home",
        "culture",
        "sports",
        "storage_repairs",
    ]
    default_replacement = residential_replacement + non_residential_replacement

    df = df.assign(
        building_category=df.building_category.str.split('+').apply(
            lambda s: _replace_alias(s, 'default', '+'.join(default_replacement))))
    df = df.assign(
        building_category=df.building_category.str.split('+').apply(
            lambda s: _replace_alias(s, 'residential', '+'.join(residential_replacement))))
    df = df.assign(
        building_category=df.building_category.str.split('+').apply(
            lambda s: _replace_alias(s, 'non_residential', '+'.join(non_residential_replacement))))

    return df



def replace_building_code_default(df: pd.DataFrame) -> pd.DataFrame:
    if "building_code" not in df.columns:
        return df
    default_replacement = ['PRE_TEK49', 'TEK49', 'TEK69', 'TEK87', 'TEK97', 'TEK07', 'TEK10', 'TEK17']
    df = df.assign(building_code=df['building_code'].str.split('+').apply(lambda s: _replace_alias(s, 'default', '+'.join(default_replacement))))
    return df


def replace_purpose_default(df: pd.DataFrame) -> pd.DataFrame:
    if "purpose" not in df.columns:
        return df
    default_replacement = [
        'heating_rv',
        'heating_dhw',
        'cooling',
        'lighting',
        'electrical_equipment',
        'fans_and_pumps',
    ]
    df = df.assign(purpose=df['purpose'].str.split('+').apply(lambda s: _replace_alias(s, 'default', '+'.join(default_replacement))))
    return df


def add_lineno_count(df: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    by_group = grouping_columns if grouping_columns else build_grouping(df)
    df["lineno_count"] = df.groupby("lineno")["lineno"].transform("size")
    return df.sort_values(by=["lineno_count", *by_group])


def filter_fewest_lineno_matches(df: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    by_grouping = grouping_columns if grouping_columns else build_grouping(df)
    scored = df.assign(score=-df['lineno_count'])
    q= scored.groupby(by=by_grouping, as_index=False, dropna=False).agg(score=('score', 'max')).merge(scored, on=[*by_grouping, 'score'])
    return q


def select_groups_with_lowest_lineno_count(df: pd.DataFrame, grouping_columns: list[str] | None=None, filter_columns:bool=True) -> pd.DataFrame:
    grouping_columns = grouping_columns if grouping_columns else build_grouping(df)
    if 'lineno' not in df.columns:
        msg = f'Dataframe must contain a "lineno" column {grouping_columns}'
        raise KeyError(msg)
    original_columns = df.columns
    fewest_lineno_matches = df.pipe(add_lineno_count, grouping_columns=grouping_columns).pipe(filter_fewest_lineno_matches, grouping_columns=grouping_columns)
    by_group = grouping_columns if grouping_columns else build_grouping(fewest_lineno_matches)
    columns_to_use_from_matches = [*by_group, 'score', 'lineno', 'lineno_count']
    columns_to_merge_matches = [*by_group, 'lineno']
    df = fewest_lineno_matches[columns_to_use_from_matches].merge(df, on=columns_to_merge_matches)
    if not filter_columns:
        return df
    return df[original_columns]


def mark_duplicates(df: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    by_grouping = grouping_columns if grouping_columns else build_grouping(df)
    _df = df.copy()
    _df['dupe'] = _df.duplicated(subset=[*by_grouping, 'year'], keep=False)
    return _df.reset_index(drop=True)


def group_dupes_on_dupes(dupes: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    grouping = grouping_columns if grouping_columns else build_grouping(dupes)
    dupes_on_dupe = dupes.merge(dupes, on=grouping)
    deduped_dupes_on_dupes = dupes_on_dupe[(dupes_on_dupe['year_x'] == dupes_on_dupe['year_y']) & (dupes_on_dupe['lineno_x'] != dupes_on_dupe['lineno_y'])][
        [*grouping, 'lineno_x', 'lineno_y', 'year_x', 'year_y', 'value_x', 'value_y']
    ]

    return deduped_dupes_on_dupes


def group_duplicated_lineno_summary(df: pd.DataFrame) -> pd.DataFrame:
    _df = df.copy()
    if 'lineno_x' in df.columns and 'lineno' not in df.columns:
        _df = df.rename(columns={'lineno_x': 'lineno', 'lineno_y': 'duplicate_lineno'})
    elif 'duplicate_lineno' not in _df.columns and 'lineno_y' in _df.columns:
        _df = _df.rename(columns={'lineno_y': 'duplicate_lineno'})

    _df = (
        _df.groupby(by=['lineno', 'duplicate_lineno'], as_index=False)
        .agg(
            building_categories=('building_category', lambda r: '+'.join(r.unique().tolist())),
            building_categories_cnt=('building_category', lambda r: len(r.unique())),
            building_codes=('building_code', lambda r: '+'.join(r.unique())),
            building_codes_cnt=('building_code', lambda r: len(r.unique())),
            purposes=('purpose', lambda r: '+'.join(r.unique().tolist())),
            purposes_cnt=('purpose', lambda r: len(r.unique())),
            functions=('function', lambda r: '+'.join(r.unique().tolist())),
            functions_cnt=('function', lambda r: len(r.unique())),
        )
        .assign(all_cnt=lambda d: d['building_categories_cnt'] + d['building_codes_cnt'] + d['purposes_cnt'] + d['functions_cnt'])
    )

    return _df


def merge_duplicate_lineno_summary_with_definitions(merged_original: pd.DataFrame, energy_need_improvements: pd.DataFrame) -> pd.DataFrame:
    df_original = energy_need_improvements.rename(columns={c: c + '_original' for c in energy_need_improvements.columns})
    df_duplicate = energy_need_improvements.rename(columns={c: c + '_duplicate' for c in energy_need_improvements.columns})

    merged_original = (merged_original.merge(df_original, left_on='lineno', right_on='lineno_original', how='left'))
    merged_duplicate = merged_original.merge(df_duplicate,
                                             left_on='duplicate_lineno',
                                             right_on='lineno_duplicate',
                                             how='left',
                                             suffixes=('_original', '_duplicate'))

    return merged_duplicate.reset_index(drop=True).sort_values(by=['lineno_original', 'duplicate_lineno'])


def collapse_years(expanded: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse per year rows back into the year ranges they were expanded from.

    This is the inverse of the year explosion performed by `expand_definitions`.
    The ``year`` column is dropped and the rows that only differed by year are
    deduplicated, leaving one row per distinct combination of values. The
    ``start_year`` and ``end_year`` columns are not recomputed: they are carried
    through from the expanded frame, so the result describes the same ranges the
    definitions were authored with.

    Parameters
    ----------
    expanded : pd.DataFrame
        Expanded definitions, typically the output of `expand_definitions`. Must
        contain a ``year`` column. If both ``start_year`` and ``end_year`` are
        present, rows whose ``year`` falls outside that range are discarded
        before collapsing.

    Returns
    -------
    pd.DataFrame
        The input without the ``year`` column and without duplicate rows.

    Raises
    ------
    ValueError
        If two rows share the same group and ``year``, where the group is
        whichever of ``building_category``, ``building_code``, ``purpose`` and
        ``function`` are present. Such rows are in conflict and cannot be
        collapsed into a single range.
    AttributeError
        If `expanded` has no ``year`` column.

    See Also
    --------
    expand_definitions : Inverse operation, expanding year ranges into one row per year.

    Notes
    -----
    Deduplication considers every column except ``year``, not just the grouping
    columns. Rows that differ in any other column, for example ``value``, are
    therefore kept apart, which is what keeps consecutive periods of the same
    group as separate rows.

    Because ``start_year`` and ``end_year`` are passed through rather than
    derived from the observed years, a round trip only reproduces the original
    ranges if those columns were retained during expansion.

    `expanded` is not modified.

    Examples
    --------
    Two years of an unchanged value collapse into a single row, while a period
    with a different value stays separate:

    >>> import pandas as pd
    >>> expanded = pd.DataFrame({
    ...     'building_category': ['house', 'house', 'house'],
    ...     'purpose': ['lighting', 'lighting', 'lighting'],
    ...     'start_year': [2020, 2020, 2022],
    ...     'end_year': [2021, 2021, 2022],
    ...     'year': [2020, 2021, 2022],
    ...     'value': [1.0, 1.0, 0.5],
    ... })
    >>> collapse_years(expanded)
      building_category   purpose  start_year  end_year  value
    0             house  lighting        2020      2021    1.0
    2             house  lighting        2022      2022    0.5

    """
    if 'start_year' in expanded.columns and 'end_year' in expanded.columns:
        df = expanded[(expanded.year >= expanded.start_year) & (expanded.year <= expanded.end_year)]
    else:
        df = expanded.copy()
    deduped = df.drop(columns=['year']).drop_duplicates()
    return deduped.reset_index(drop=True)


def format_lines(_df: pd.DataFrame) -> list[str]:
    def format_conflict_values(row: pd.DataFrame, suffix: str) -> str:
        return ", ".join(
            str(getattr(row, column))
            for column in _df.columns
            if column.endswith(suffix)
            and not any(
                column.endswith(skip) for skip in ("_csv_definition", "_csv_conflict")
            )
        )

    lines = [""]
    previous_lineno = None

    for conflict in _df.itertuples():
        max_length_building_categories_list = 2
        all_building_categories_count = 13
        max_length_building_codes_list = 3
        all_building_codes_count = 8

        building_categories = (
            (
                f"({conflict.building_categories_cnt} total)"
                if conflict.building_categories_cnt > max_length_building_categories_list
                else conflict.building_categories
            )
            if conflict.building_categories_cnt < all_building_categories_count
            else "(all)"
        )
        building_codes = (
            (
                f"({conflict.building_codes_cnt} total)"
                if conflict.building_codes_cnt > max_length_building_codes_list
                else conflict.building_codes
            )
            if conflict.building_codes_cnt < all_building_codes_count
            else "(all)"
        )

        header = (
            f"Row {conflict.lineno:>3} overlaps with row {conflict.duplicate_lineno:>3}, "
            f"Category {building_categories}, "
            f"Code {building_codes} "
            f"Purpose {conflict.purposes}, "
        )

        extra_lines = []
        if max_length_building_codes_list < conflict.building_codes_cnt < all_building_codes_count:
            extra_lines.append(
                f"  building_codes={conflict.building_codes.replace('+', ' ')}",
            )
        if max_length_building_categories_list < conflict.building_categories_cnt < all_building_categories_count:
            extra_lines.append(
                f"  building_categories={conflict.building_categories.replace('+', ' ')}",
            )

        definition = (
            f"  definition {conflict.lineno:>3}: "
            f"{format_conflict_values(conflict, '_original')}"
        )
        duplicate = (
            f"    conflict {conflict.duplicate_lineno:>3}: "
            f"{format_conflict_values(conflict, '_duplicate')}"
        )

        if previous_lineno is None or previous_lineno != conflict.lineno:
            previous_lineno = conflict.lineno
            lines.append("")
            lines.append(header)
            lines.extend(extra_lines)
            lines.append(definition)

        lines.append(duplicate)
    return lines
