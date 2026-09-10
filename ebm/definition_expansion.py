import pandas as pd
from loguru import logger


def add_lineno(df: pd.DataFrame) -> pd.DataFrame:
    if "lineno" not in df.columns:
        df["lineno"] = range(2, len(df) + 2)
    return df


def expand_grouped_definitions(definitions: pd.DataFrame, *, grouping_columns: list[str] | None=None, drop_helper_columns :bool=True) -> pd.DataFrame:
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

    stages = [
        (add_lineno, ),
        (replace_building_category_default, ),
        (replace_building_code_default, ),
        (replace_purpose_default, ),
        (explode_building_category, ),
        (explode_building_code, ),
        (explode_purpose, ),
        #(lambda d: d.reset_index(drop=True), ),
        (select_groups_with_lowest_lineno_count, {'grouping_columns': group_by, 'filter_columns': drop_helper_columns}),
        (explode_years, ),
        (mark_duplicates, {'grouping_columns': group_by}),
    ]
    result = definitions
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


def replace_building_category_default(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_category' not in df.columns:
        return df
    df["building_category"] = df["building_category"].replace(
        "default",
        "house+apartment_block+kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs",
    )
    df["building_category"] = df["building_category"].replace(
        "non_residential",
        "kindergarten+school+university+office+retail+hotel+hospital+nursing_home+culture+sports+storage_repairs",
    )
    df["building_category"] = df["building_category"].replace(
        "residential", "house+apartment_block",
    )
    return df


def replace_building_code_default(df: pd.DataFrame) -> pd.DataFrame:
    if "building_code" not in df.columns:
        return df
    df["building_code"] = df["building_code"].replace(
        "default", "PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17",
    )
    return df


def replace_purpose_default(df: pd.DataFrame) -> pd.DataFrame:
    if "purpose" not in df.columns:
        return df
    df["purpose"] = df["purpose"].replace(
        "default",
        "heating_rv+heating_dhw+cooling+lighting+electrical_equipment+fans_and_pumps",
    )
    return df


def add_lineno_count(df: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    by_group = grouping_columns if grouping_columns else build_grouping(df)
    df["lineno_count"] = df.groupby("lineno")["lineno"].transform("size")
    return df.sort_values(by=["lineno_count", *by_group])


def filter_fewest_lineno_matches(df: pd.DataFrame, grouping_columns: list[str] | None=None) -> pd.DataFrame:
    by_grouping = grouping_columns if grouping_columns else build_grouping(df)
    scored = df.assign(score=-df['lineno_count'])
    q= scored.groupby(by=by_grouping, as_index=False).agg(score=('score', 'max')).merge(scored, on=[*by_grouping, 'score'])
    return q


def select_groups_with_lowest_lineno_count(df: pd.DataFrame, grouping_columns: list[str] | None=None, filter_columns:bool=True) -> pd.DataFrame:
    if 'lineno' not in df.columns:
        raise KeyError('Dataframe must contain a "lineno" column (building_category, building_code, purpose, function)')
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


def group_dupes_on_dupes(dupes: pd.DataFrame) -> pd.DataFrame:
    grouping = build_grouping(dupes)
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
    if 'start_year' in expanded.columns and 'end_year' in expanded.columns:
        df = expanded[(expanded.year >= expanded.start_year) & (expanded.year <= expanded.end_year)]
    else:
        df = expanded.copy()
    grouping = [*build_grouping(df), 'year']
    dupes = df.duplicated(subset=grouping)
    if dupes.any():
        raise ValueError('Duplicate values found for the same group')
    deduped = df.drop(columns=['year']).drop_duplicates()
    return deduped
