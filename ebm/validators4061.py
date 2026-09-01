from pandas import DataFrame

try:
    import pandera.pandas as pa
except ImportError:
    import pandera as pa

import pandas as pd
from ebm.validators import check_default_building_category_with_group, check_default_building_code, check_default_energy_purpose



def build_grouping(df: pd.DataFrame) -> list:
    return [c for c in ['building_category', 'building_code', 'purpose', 'function'] if c in df.columns]


def explode_building_category(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_category' not in df.columns:
        raise ValueError(r"Dataframe must contain a 'building_category' column")
    return explode_on_plus(df, column_name='building_category')


def explode_building_code(df: pd.DataFrame) -> pd.DataFrame:
    if 'building_code' not in df.columns:
        return df
    # df['building_code'] = df['building_code'].str.replace("default", 'PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17')

    return explode_on_plus(df, column_name='building_code')


def explode_purpose(df: pd.DataFrame) -> pd.DataFrame:
    if 'purpose' not in df.columns:
        return df
    # df['purpose'] = df['purpose'].str.replace( "default", 'heating_rv+heating_dhw+cooling+lighting+electrical_equipment+fans_and_pumps' )
    df = explode_on_plus(df, column_name='purpose')

    return df


def explode_on_plus(df: DataFrame, column_name: str) -> DataFrame:
    if df[column_name].isnull().any():
        raise ValueError(f"Dataframe '{column_name}' cannot be empty")
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
                    range(int(row["start_year"]), int(row["end_year"]) + 1)
                ),
                axis=1,
            )
        }
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
        "residential", "house+apartment_block"
    )
    return df


def replace_building_code_default(df: pd.DataFrame) -> pd.DataFrame:
    if "building_code" not in df.columns:
        return df
    df["building_code"] = df["building_code"].replace(
        "default", "PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17"
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


def add_lineno_count(df: pd.DataFrame, by_grouping=None) -> pd.DataFrame:
    by_group = build_grouping(df) if not by_grouping else by_grouping
    df["lineno_count"] = df.groupby("lineno")["lineno"].transform("size")
    return df.sort_values(by=["lineno_count"] + by_group)


def filter_fewest_lineno_matches(df: pd.DataFrame) -> pd.DataFrame:
    by_grouping = build_grouping(df)
    scored = df.assign(score=-df['lineno_count'])
    q= scored.groupby(by=by_grouping, as_index=False).agg(score=('score', 'max')).merge(scored, on=by_grouping + ['score'])
    return q

def select_groups_with_lowest_lineno_count(df: pd.DataFrame, by_grouping=None, filter_columns=True) -> pd.DataFrame:
    if 'lineno' not in df.columns:
        raise KeyError('Dataframe must contain a "lineno" column (building_category, building_code, purpose, function)')
    original_columns = df.columns
    fewest_lineno_matches = df.pipe(add_lineno_count).pipe(filter_fewest_lineno_matches)
    by_group = by_grouping if by_grouping else build_grouping(fewest_lineno_matches)
    columns_to_use_from_matches = by_group + ['score', 'lineno', 'lineno_count']
    columns_to_merge_matches = by_group + ['lineno']
    df = fewest_lineno_matches[columns_to_use_from_matches].merge(df, on=columns_to_merge_matches)
    if not filter_columns:
        return df
    return df[original_columns]


def mark_duplicates(df: pd.DataFrame, by_grouping: list[str]=None) -> pd.DataFrame:
    by_grouping = build_grouping(df) if not by_grouping else by_grouping
    _df = df.copy()
    _df['dupe'] = _df.duplicated(subset=by_grouping + ['year'], keep=False)
    return _df.reset_index(drop=True)


def group_dupes_on_dupes(dupes: pd.DataFrame) -> pd.DataFrame:
    grouping = build_grouping(dupes)
    dupes_on_dupe = dupes.merge(dupes, on=grouping)
    dedeuped_dupes_on_dupes = dupes_on_dupe[(dupes_on_dupe['year_x'] == dupes_on_dupe['year_y']) & (dupes_on_dupe['lineno_x'] != dupes_on_dupe['lineno_y'])][
        grouping + ['lineno_x', 'lineno_y', 'year_x', 'year_y', 'value_x', 'value_y']
    ]

    return dedeuped_dupes_on_dupes

energy_need_improvements_yearly_schema = pa.DataFrameSchema(
    parsers = [
        pa.Parser(explode_years),
        pa.Parser(mark_duplicates),
    ],
    columns={
        'building_category': pa.Column(str, checks=pa.Check(check_default_building_category_with_group)),
        'building_code': pa.Column(str, checks=pa.Check(check_default_building_code, element_wise=True)),
        'purpose':pa.Column(str, checks=pa.Check(check_default_energy_purpose)),
        'function': pa.Column(str, checks=pa.Check(lambda x: x.isin(['yearly_reduction', 'improvement_at_end_year']))),
        'year':pa.Column(int, coerce=True),
        'value': pa.Column(float, coerce=True, checks=[pa.Check.between(min_value=0.0, include_min=True, max_value=1.0, include_max=True)]),
        'dupe': pa.Column(bool, coerce=True, default=False),
    },
    unique=['lineno', 'building_category', 'building_code', 'purpose', 'function', 'year', 'value'],
)

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
        .assign(all_cnt=lambda df: df['building_categories_cnt'] + df['building_codes_cnt'] + df['purposes_cnt'] + df['functions_cnt'])
    )

    return _df


def merge_duplicate_lineno_summary_with_definitions(merged_original: pd.DataFrame, energy_need_improvements: pd.DataFrame) -> pd.DataFrame:
    df_original = energy_need_improvements.rename(columns={c: c + '_original' for c in energy_need_improvements.columns})
    df_duplicate = energy_need_improvements.rename(columns={c: c + '_duplicate' for c in energy_need_improvements.columns})

    merged_original = (merged_original.merge(df_original, left_on='lineno', right_on='lineno_original', how='left'))
    merged_duplicate = merged_original.merge(df_duplicate, left_on='duplicate_lineno', right_on='lineno_duplicate', how='left', suffixes=('_original', '_duplicate'))

    return merged_duplicate.reset_index(drop=True).sort_values(by=['lineno_original', 'duplicate_lineno'])


def expanded_energy_need_improvements_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        parsers=[
            pa.Parser(replace_building_category_default),
            pa.Parser(replace_building_code_default),
            pa.Parser(replace_purpose_default),
            pa.Parser(explode_building_category),
            pa.Parser(explode_building_code),
            pa.Parser(explode_purpose),
            pa.Parser(lambda c: c.reset_index(drop=True)),
    ],
    columns={
        'lineno': pa.Column(int, coerce=True),
        'building_category': pa.Column(str, checks=pa.Check(check_default_building_category_with_group)),
        'building_code': pa.Column(str, checks=pa.Check(check_default_building_code, element_wise=True)),
        'purpose':pa.Column(str, checks=pa.Check(check_default_energy_purpose)),
        'value': pa.Column(float, coerce=True, checks=[pa.Check.between(min_value=0.0, include_min=True, max_value=1.0, include_max=True)],)
    },
)
