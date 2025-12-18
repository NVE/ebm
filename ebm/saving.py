import pandas as pd

from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.file_handler import FileHandler


def energy_need_net_construction(energy_need: pd.DataFrame, net_construction: pd.DataFrame) -> pd.DataFrame:
    df_ec = energy_need.reset_index().merge(
        net_construction,
        left_on=['building_category', 'building_code', 'building_condition', 'year'],
        right_on=['building_category', 'building_code', 'building_condition', 'year'],
    )
    return df_ec


def reduced_construction_kwh(energy_need_net_construction: pd.DataFrame) -> pd.DataFrame:
    energy_need_net_construction['original_construction_kwh'] = energy_need_net_construction.reduced_kwh_m2 * energy_need_net_construction.m2
    energy_need_net_construction['reduced_construction_kwh'] = energy_need_net_construction.reduced_kwh_m2 * (
        energy_need_net_construction.m2 - energy_need_net_construction.net_construction_m2
    )
    energy_need_net_construction['original_reduced_construction_kwh'] = (
        energy_need_net_construction.original_construction_kwh - energy_need_net_construction.reduced_construction_kwh
    )

    return energy_need_net_construction


def reduced_policy_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    energy_need['reduced_policy_kwh_m2'] = energy_need['reduction_policy'] * energy_need['kwh_m2']
    energy_need['reduction_policy_kwh_m2'] = energy_need['kwh_m2'] - energy_need['reduced_policy_kwh_m2']
    energy_need['reduced_policy_kwh'] = energy_need['reduced_policy_kwh_m2'] * energy_need['m2']
    energy_need['reduction_policy_kwh'] = energy_need['reduction_policy_kwh_m2'] * energy_need['m2']

    return energy_need


def reduced_yearly_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    energy_need['reduced_yearly_kwh_m2'] = energy_need['reduction_yearly'] * energy_need['kwh_m2']
    energy_need['reduction_yearly_kwh_m2'] = energy_need['kwh_m2'] - energy_need['reduced_yearly_kwh_m2']
    energy_need['reduced_yearly_kwh'] = energy_need['reduced_yearly_kwh_m2'] * energy_need['m2']
    energy_need['reduction_yearly_kwh'] = energy_need['reduction_yearly_kwh_m2'] * energy_need['m2']

    return energy_need


def reduced_condition_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    energy_need['reduced_condition_kwh_m2'] = energy_need.kwh_m2 * energy_need.reduction_condition
    energy_need['reduced_condition_kwh'] = (energy_need.kwh_m2 - energy_need.reduced_condition_kwh_m2) * energy_need['m2']
    energy_need['original_reduced_condition_kwh'] = energy_need.kwh - energy_need.reduced_condition_kwh

    return energy_need


def household_size(df: pd.DataFrame, household_size: pd.Series) -> pd.DataFrame:
    df = df.merge(household_size, on=['year'])
    return df


def flat_household_size(df: pd.DataFrame = None) -> pd.DataFrame:
    import pathlib  # noqa: I001, PLC0415
    from ebm.cmd.run_calculation import calculate_building_category_area_forecast  # noqa: PLC0415

    input_path_flat = pathlib.Path('flat-husholdning')
    dm_flat = DatabaseManager(file_handler=FileHandler(directory=input_path_flat))

    period = YearRange(2020, 2050)

    area_flat = calculate_building_category_area_forecast(database_manager=dm_flat, start_year=period.start, end_year=period.end)

    area_flat.rename(columns={'m2': 'm2_flat_household_size'})

    flat_household_size = dm_flat.get_construction_population()[['household_size']].rename(columns={'household_size': 'flat_household_size'})

    area_flat = area_flat.merge(flat_household_size, on=['year'], suffixes=(None, '_flat'))
    return area_flat


def m2_household_ch(area_flat: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    area_both = area_flat.merge(
        area_forecast[['building_category', 'building_code', 'year', 'building_condition', 'm2']],
        on=['building_category', 'building_code', 'year', 'building_condition'],
        suffixes=(None, 'org'),
    )

    area_both['m2_household_ch'] = area_both['m2'] - area_both.m2org

    return area_both


def reduced_household_size_kwh(df: pd.DataFrame, area_flat: pd.DataFrame) -> pd.DataFrame:
    df_c = df.merge(
        area_flat[['building_category', 'building_code', 'year', 'building_condition', 'flat_household_size', 'm2']],
        on=['building_category', 'building_code', 'year', 'building_condition'],
        suffixes=(None, '_flat'),
    ).copy()

    df_c['m2_household_ch'] = df_c['m2'] - df_c.m2_flat
    df_c['household_size_original_kwh'] = df_c.m2_household_ch * df_c.kwh_m2
    df_c['reduced_household_size_kwh'] = df_c.m2_household_ch * df_c.reduced_kwh_m2

    return df_c


def reduction_by_year(filtered_df: pd.DataFrame) -> pd.DataFrame:
    kwh = (
        filtered_df.query('year>=2020')
        .groupby(by=['year'])[
            [
                'original_reduced_construction_kwh',
                'reduced_household_size_kwh',
                'reduction_policy_kwh',
                'reduction_yearly_kwh',
                'reduced_condition_kwh',
            ]
        ]
        .sum()
    )
    kwh.loc[
        :,
        ['reduction_policy_kwh', 'reduction_yearly_kwh', 'reduced_condition_kwh'],
    ] = kwh.loc[:, ['reduction_policy_kwh', 'reduction_yearly_kwh', 'reduced_condition_kwh']] * -1

    return kwh


def sum_savings_by_year(kwh: pd.DataFrame) -> pd.DataFrame:
    kwh['total_nedgang'] = kwh.reduction_policy_kwh + kwh.reduction_yearly_kwh + kwh.reduced_condition_kwh
    kwh['total_oppgang'] = kwh.original_reduced_construction_kwh + kwh.reduced_household_size_kwh
    kwh['total'] = kwh.total_nedgang + kwh.total_oppgang
    return kwh
