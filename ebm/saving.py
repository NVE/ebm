from loguru import logger
import numpy as np
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
    """
        Compute construction-related energy changes based on reduced energy intensity.

        Parameters
        ----------
        energy_need_net_construction : pandas.DataFrame
            DataFrame containing at least the following columns:
            - reduced_kwh_m2 : float
                Energy need after reductions (kWh per m²).
            - m2 : float
                Original total area (m²).
            - net_construction_m2 : float
                Net area change due to construction (m²). Positive values reduce
                effective area; negative values increase it.

        Returns
        -------
        pandas.DataFrame
            Copy of the input DataFrame with three additional columns:
            - reduced_construction_kwh : float
                Energy after applying net construction area change
                (reduced_kwh_m2 * (m2 - net_construction_m2)).
            - net_construction_kwh : float
                Energy need of the constructed area (reduced_kwh_m2 * m2).

        Notes
        -----
        - No clamping is applied; if net_construction_m2 > m2, the reduced energy
          may become negative. Validate upstream if needed.
        - Assumes all required columns exist and are numeric.

        Examples
        --------
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "kwh_m2": [120.0, 95.5],
        ...     "m2": [1000.0, 2500.0],
        ...     "net_construction_m2": [200.0, -100.0],
        ... })
        >>> reduced_construction_kwh(df)[[
        ...     "original_construction_kwh",
        ...     "reduced_construction_kwh",
        ...     "net_construction_kwh"
        ... ]]
           original_construction_kwh  reduced_construction_kwh  net_construction_kwh
        0                    120000.0                  96000.0                           24000.0
        1                    238750.0                 248525.0                           -9775.0
        """

    df = energy_need_net_construction.copy()
    df['original_construction_kwh'] = df.kwh_m2 * df.m2
    df['reduced_construction_kwh'] = df.kwh_m2 * (df.m2 - df.net_construction_m2)
    df['net_construction_kwh'] = df.original_construction_kwh - df.reduced_construction_kwh

    return df


def reduction_policy_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate energy need changed by yearly reduction in KWh.

    Parameters
    ----------
    energy_need : pd.DataFrame
        Must include the columns:
            - original_kwh_m2
            - m2
            - reduction_policy
            - reduction_yearly
            - reduction_condition

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two new columns:
        - reduction_policy_kwh_m2: Difference per m²
        - reduction_policy_kwh: Difference for total area
    """
    err = _make_exception_message_for_missing_columns(energy_need)
    if err:
        raise err

    df = _reduced_column_kwh(energy_need.copy(), 'policy', {'reduction_yearly', 'reduction_condition'})

    return df


def reduction_yearly_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate energy need changed by condition in KWh.

    Parameters
    ----------
    energy_need : pd.DataFrame
        Must include the columns:
            - original_kwh_m2
            - m2
            - reduction_yearly
            - reduction_policy
            - reduction_condition

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two new columns:
        - reduction_yearly_kwh_m2: Difference per m²
        - reduction_yearly_kwh: Difference for total area
    """
    err = _make_exception_message_for_missing_columns(energy_need)
    if err:
        raise err

    df = _reduced_column_kwh(energy_need.copy(), 'yearly', {'reduction_policy', 'reduction_condition'})

    return df

REQUIRED_COLS = {
    "reduction_condition",
    "reduction_policy",
    "reduction_yearly",
    "calibrated_kwh_m2",
    "m2",
}


def reduction_condition_kwh(energy_need: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate energy need changed by condition in KWh.

    Parameters
    ----------
    energy_need : pd.DataFrame
        Must include the columns:
            - calibrated_kwh_m2
            - m2
            - reduction_yearly
            - reduction_policy
            - reduction_condition

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two new columns:
        - reduction_condition_kwh_m2: Difference per m²
        - reduction_condition_kwh: Difference for total area
    """
    err = _make_exception_message_for_missing_columns(energy_need)
    if err:
        raise err

    df = _reduced_column_kwh(energy_need.copy(), 'condition', {'reduction_yearly', 'reduction_policy'})

    return df


def _reduced_column_kwh(df: pd.DataFrame, operational_column: str, other_columns: set[str]) -> pd.DataFrame:
    if f'reduction_{operational_column}' in other_columns:
        raise ValueError('Operational column condition also present in other columns')
    if any(df[['calibrated_kwh_m2', *other_columns]].isna()):
        logger.warning('NaN in column')
    diff_kwh_m2 = (
            df[['calibrated_kwh_m2', *other_columns]].fillna(1.0).prod(axis=1)
            * (1 - df[f'reduction_{operational_column}'].fillna(1.0))
    )
    df[f"reduction_{operational_column}_kwh"] = np.round((diff_kwh_m2 * df["m2"]).fillna(0), 4)
    df[f"reduction_{operational_column}_kwh_m2"] = np.round(diff_kwh_m2.fillna(0), 4)

    df[f"reduced_{operational_column}_kwh_m2"] = np.round(diff_kwh_m2.fillna(0), 4)
    df[f"reduced_{operational_column}_kwh"] = np.round((diff_kwh_m2 * df["m2"]).fillna(0), 4)
    return df


def _make_exception_message_for_missing_columns(energy_need: pd.DataFrame) -> Exception | None:
    missing: list[str] = [c for c in REQUIRED_COLS if c not in energy_need.columns]
    if missing:
        msg = f'Required {"columns" if len(missing) > 1 else "column"} {", ".join(sorted(missing))} missing from energy need dataframe'
        return ValueError(msg)
    return None


reduction_condition_kwh.required_columns = REQUIRED_COLS

def household_size(df: pd.DataFrame, household_size: pd.Series) -> pd.DataFrame:
    df = df.merge(household_size, on=['year'])
    return df


def flat_household_size(dm: DatabaseManager, period: YearRange=YearRange(2020, 2050)) -> pd.DataFrame:
    from ebm.cmd.run_calculation import calculate_building_category_area_forecast  # noqa: PLC0415

    fh_flat = FileHandler(directory=dm.file_handler.input_directory)
    dm_flat = DatabaseManager(file_handler=fh_flat)

    construction_population = fh_flat.get_construction_population()
    construction_population['household_size'] = construction_population.loc[
        construction_population.query(f'year=={period.start}').index, 'household_size'].iloc[0]

    fh_flat.get_construction_population = lambda: construction_population
    area_flat = calculate_building_category_area_forecast(database_manager=dm_flat, start_year=period.start, end_year=period.end)

    area_flat.rename(columns={'m2': 'm2_flat_household_size'})

    flat_household_size = dm_flat.get_construction_population()[['household_size']].rename(columns={'household_size': 'flat_household_size'})

    area_flat = area_flat.merge(flat_household_size, on=['year'], suffixes=(None, '_flat'))
    return area_flat


def m2_household_ch(area_flat: pd.DataFrame, area_forecast: pd.DataFrame) -> pd.DataFrame:
    area_both = area_flat.merge(
        area_forecast[['building_category', 'building_code', 'year', 'building_condition', 'household_size', 'net_construction', 'm2']],
        on=['building_category', 'building_code', 'year', 'building_condition'],
        suffixes=('_flat', None),
    )

    area_both['m2_household_ch'] = area_both['m2_flat'] - area_both.m2

    return area_both


def reduced_household_size_kwh(df: pd.DataFrame, area_flat: pd.DataFrame) -> pd.DataFrame:
    df_c = df.merge(
        area_flat[['building_category', 'building_code', 'year', 'building_condition', 'flat_household_size', 'm2']],
        on=['building_category', 'building_code', 'year', 'building_condition'],
        suffixes=(None, '_flat'),
    ).copy()

    df_c['m2_household_ch'] = df_c['m2'] - df_c.m2_flat
    df_c['m2_org'] = df_c['m2']
    df_c['household_size_original_kwh'] = df_c.m2 * df_c.reduced_kwh_m2
    df_c['reduced_household_size_kwh'] = df_c.m2_flat * df_c.reduced_kwh_m2
    df_c['reduction_household_size_kwh'] = df_c['household_size_original_kwh'] - df_c['reduced_household_size_kwh']

    return df_c


def reduction_by_year(filtered_df: pd.DataFrame) -> pd.DataFrame:
    kwh = (
        filtered_df.query('year>=2020')
        .groupby(by=['year'])[
            [
                'net_construction_kwh',
                'reduced_household_size_kwh',
                'reduction_policy_kwh',
                'reduction_yearly_kwh',
                'reduction_condition_kwh',
            ]
        ]
        .sum()
    )
    kwh.loc[
        :,
        ['reduction_policy_kwh', 'reduction_yearly_kwh', 'reduction_condition_kwh'],
    ] = kwh.loc[:, ['reduction_policy_kwh', 'reduction_yearly_kwh', 'reduction_condition_kwh']] * -1

    return kwh


def sum_savings_by_year(kwh: pd.DataFrame) -> pd.DataFrame:
    kwh['total_nedgang'] = kwh.reduction_policy_kwh + kwh.reduction_yearly_kwh + kwh.reduction_condition_kwh
    kwh['total_oppgang'] = kwh.net_construction_kwh + kwh.reduced_household_size_kwh
    kwh['total'] = kwh.total_nedgang + kwh.total_oppgang
    return kwh
