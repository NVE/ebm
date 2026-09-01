try:
    import pandera.pandas as pa
except ImportError:
    import pandera as pa

from pandas import DataFrame
from loguru import logger

from ebm.validators import add_lineno
from ebm.validators4061 import (
    explode_years,
    explode_building_category,
    explode_building_code,
    explode_purpose,
    mark_duplicates,
    select_groups_with_lowest_lineno_count,
    group_dupes_on_dupes,
    group_duplicated_lineno_summary,
    merge_duplicate_lineno_summary_with_definitions,
    replace_building_category_default,
    replace_building_code_default,
    replace_purpose_default,
)


def expand_energy_need_improvements(energy_need_improvements: DataFrame, *, by_grouping: list[str]=None, drop_helper_columns :bool=True) -> DataFrame:
    stages = [
        (add_lineno, ),
        (replace_building_category_default, ),
        (replace_building_code_default, ),
        (replace_purpose_default, ),
        (explode_building_category, ),
        (explode_building_code, ),
        (explode_purpose, ),
        (lambda d: d.reset_index(drop=True), ),
        (select_groups_with_lowest_lineno_count, {'by_grouping': by_grouping, 'filter_columns': drop_helper_columns}),
        (explode_years, ),
        (mark_duplicates, {'by_grouping': by_grouping}),
    ]
    results = {}
    for i, stage in enumerate(stages):
        stage_name = stage[0].__name__
        logger.debug(f'Stage {i}: {stage_name}')
        func, *parameters = stage
        if parameters:
            result = energy_need_improvements.pipe(func, **parameters[0])
        else:
            result = energy_need_improvements.pipe(func)

        results[stage_name] = result
        energy_need_improvements = result

    return energy_need_improvements


def transform_expanded_energy_need_improvements(expanded_energy_need_improvements) -> pa.DataFrameSchema:
    yearly = expanded_energy_need_improvements.pipe(explode_years)
    marked_duplicated = yearly.pipe(mark_duplicates)
    return marked_duplicated


def summarize_energy_need_improvement_conflicts(energy_need_improvements_yearly: DataFrame, energy_need_improvements) -> DataFrame:
    dedeuped_dupes_on_dupes = group_dupes_on_dupes(energy_need_improvements_yearly)
    _df = dedeuped_dupes_on_dupes[
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
    ][dedeuped_dupes_on_dupes["lineno_y"] > dedeuped_dupes_on_dupes["lineno_x"]]

    grouped_duplicated_lineno_summary = _df.pipe(group_duplicated_lineno_summary)
    conflicts = grouped_duplicated_lineno_summary.pipe(
        merge_duplicate_lineno_summary_with_definitions,
        energy_need_improvements=energy_need_improvements,
    )
    return conflicts
