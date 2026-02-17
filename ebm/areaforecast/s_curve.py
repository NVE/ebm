import numpy as np
import pandas as pd
from loguru import logger
from pandas import Series

from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange


def original_condition(s_curve_cumulative_demolition, s_curve_renovation,
                       s_curve_renovation_and_small_measure, s_curve_small_measure):
    """
    Calculates buildings remaining as original condition by subtracting every other condition

    Parameters
    ----------
    s_curve_cumulative_demolition : pandas.Series
    s_curve_renovation : pandas.Series
    s_curve_renovation_and_small_measure : pandas.Series
    s_curve_small_measure : pandas.Series

    Returns
    -------
    pandas.Series
        buildings remaining as original condition
    """
    return (1.0 -
            s_curve_cumulative_demolition -
            s_curve_renovation -
            s_curve_renovation_and_small_measure -
            s_curve_small_measure).rename('s_curve_original_condition')


def small_measure(s_curve_renovation_and_small_measure: Series, s_curve_small_measure_total: Series) -> Series:
    """
    Calculates the remaining small measure share by subtracting renovation and small measure values from
    the total small measure curve.

    Parameters
    ----------
    s_curve_renovation_and_small_measure : Series
    s_curve_small_measure_total : Series

    Returns
    -------
    Series
        s_curve_small_measure

    Notes
    -----
    - This function currently does not implement logic to zero out values before the building year.
    - Assumes both input Series are aligned on the index year.
    """

    # ### SharesPerCondition calc_small_measure
    #  - ❌   sett til 0 før byggeår
    # ```python
    #     construction_year = self.building_code_params[tek].building_year
    #     shares.loc[self.period_index <= construction_year] = 0
    # ```

    return (s_curve_small_measure_total - s_curve_renovation_and_small_measure).rename('small_measure')


def renovation_and_small_measure(s_curve_renovation: Series, s_curve_renovation_total: Series) -> Series:
    """
    Calculates the remaining renovation_and_small_measure share by subtracting renovation
    from the total renovation total curve.

    Parameters
    ----------
    s_curve_renovation : pandas.Series
        A time series representing the S-curve of exclusive renovation condition.

    s_curve_renovation_total : pandas.Series
        A time series representing the total S-curve for the total renovation condition.

    Returns
    -------
    pandas.Series
        A time series representing the difference between the total and renovation-only S-curves.
        Values before the building year should be set to 0 (not yet implemented).

    Notes
    -----
    - This function currently does not implement logic to zero out values before the building year.
    - Assumes both input Series are aligned on index year.
    """
    # ### SharesPerCondition calc_renovation_and_small_measure
    #  - ❌ Sett til 0 før byggeår

    return s_curve_renovation_total - s_curve_renovation


def trim_renovation_from_renovation_total(s_curve_renovation: Series,
                                          s_curve_renovation_max: Series,
                                          s_curve_renovation_total: Series,
                                          scurve_total: Series) -> Series:
    """
    Adjust the renovation S-curve by incorporating values from the total renovation curve
    where the total share is less than the maximum renovation share.

    This function identifies time points where the total S-curve (`scurve_total`) is less than
    the maximum renovation S-curve (`s_curve_renovation_max`). For those points, it replaces
    the corresponding values in `s_curve_renovation` with values from `s_curve_renovation_total`.

    Parameters
    ----------
    s_curve_renovation : pandas.Series
        The original renovation S-curve to be adjusted.

    s_curve_renovation_max : pandas.Series
        The maximum allowed values for the renovation S-curve.

    s_curve_renovation_total : pandas.Series
        The total renovation S-curve including all measures.

    scurve_total : pandas.Series
        The actual total S-curve values to compare against the max renovation curve.

    Returns
    -------
    pandas.Series
        The adjusted renovation S-curve with values merged from the total renovation curve
        where the total share is less than the maximum renovation share.

    Notes
    -----
    - Assumes all input Series are aligned on the index year.
    """

    adjusted_values = np.where(scurve_total < s_curve_renovation_max,
                               s_curve_renovation_total,
                               s_curve_renovation)
    trimmed_renovation = pd.Series(adjusted_values, index=s_curve_renovation.index).rename('renovation')
    return trimmed_renovation


def renovation_from_small_measure(s_curve_renovation_max: Series, s_curve_small_measure_total: Series) -> Series:
    """
    Calculate the renovation S-curve by subtracting small measures from the max renovation curve.

    Parameters
    ----------
    s_curve_renovation_max : pandas.Series
        The maximum yearly values for the renovation S-curve.

    s_curve_small_measure_total : pandas.Series
        The yearly total S-curve for small measures.

    Returns
    -------
    pandas.Series
        The resulting renovation S-curve with values clipped at 0
    """
    # ## small_measure and renovation to scurve_small_measure_total, RN
    # ## SharesPerCondition calc_renovation
    #
    #  - ❌ Ser ut som det er edge case for byggeår.
    #  - ❌ Årene før byggeår må settes til 0 for scurve_renovation?
    s_curve_renovation = (s_curve_renovation_max - s_curve_small_measure_total).clip(lower=0.0)
    return s_curve_renovation.rename('s_curve_renovation')


def total(s_curve_renovation_total: Series, s_curve_small_measure_total: Series) -> Series:
    """
    Calculates the yearly sum of renovation and small_measure

    Parameters
    ----------
    s_curve_renovation_total : pandas.Series
    s_curve_small_measure_total : pandas.Series

    Returns
    -------
    pandas.Series
        yearly sum of renovation and small_measure
    """

    return (s_curve_small_measure_total + s_curve_renovation_total).clip(lower=0.0).rename('s_curve_total')


def trim_max_value(s_curve_cumulative_small_measure: Series, s_curve_small_measure_max: Series) ->Series:
    s_curve_cumulative_small_measure_max = s_curve_cumulative_small_measure.combine(s_curve_small_measure_max, min)
    return s_curve_cumulative_small_measure_max.clip(0) # type: ignore


def small_measure_max(s_curve_cumulative_demolition: Series, s_curve_small_measure_never_share: Series):
    """
    Calculates the maximum possible value for small_measure condition

    Parameters
    ----------
    s_curve_cumulative_demolition : pandas.Series
    s_curve_small_measure_never_share : pandas.Series

    Returns
    -------
    pandas.Series
        Yearly maximum possible value for small_measure
    """
    return 1.0 - s_curve_cumulative_demolition - s_curve_small_measure_never_share


def renovation_max(s_curve_cumulative_demolition: Series, s_curve_renovation_never_share: Series):
    """
    Calculates the maximum possible value for renovation condition

    Parameters
    ----------
    s_curve_cumulative_demolition : pandas.Series
    s_curve_renovation_never_share : pandas.Series

    Returns
    -------
    pandas.Series
        Yearly maximum possible value for renovation
    """
    return 1.0 - s_curve_cumulative_demolition - s_curve_renovation_never_share


def cumulative_renovation(s_curves_with_building_code: Series, years: YearRange) -> Series:
    """
    Return the  yearly cumulative sum of renovation condition.


    Parameters
    ----------
    s_curves_with_building_code : pandas.Series
    years : pandas.Series

    Returns
    -------
    pandas.Series
        cumulative sum of renovation

    Notes
    -----
    NaN values are replaced by float 0.0
    """
    return s_curves_with_building_code.renovation_acc.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)


def cumulative_small_measure(s_curves_with_building_code: Series, years: YearRange) -> Series:
    """
    Return the  yearly cumulative sum of small_measure condition.


    Parameters
    ----------
    s_curves_with_building_code : pandas.Series
    years : YearRange

    Returns
    -------
    pandas.Series
        cumulative sum of small_measure

    Notes
    -----
    NaN values are replaced by float 0.0
    """
    s_curve_cumulative_small_measure = s_curves_with_building_code.small_measure_acc.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)
    return s_curve_cumulative_small_measure


def transform_demolition(demolition: Series, years: YearRange) -> Series:
    """
    Filter yearly demolition for years
    Parameters
    ----------
    demolition : pandas.Series
    years : YearRange

    Returns
    -------
    demolition for years

    """
    return demolition.demolition.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)


def transform_to_cumulative_demolition(cumulative_demolition: pd.DataFrame, years:YearRange) -> Series:
    """
    Filter yearly cumulative demolition for years
    Parameters
    ----------
    cumulative_demolition : pandas.DataFrame
    years : YearRange

    Returns
    -------
    pandas.Series
        cumulative demolition for years

    """
    s_curve_cumulative_demolition = cumulative_demolition.demolition_acc.loc[
        (slice(None), slice(None), list(years.year_range))].fillna(0.0)
    return s_curve_cumulative_demolition


def pad_s_curve_age(s_curves: pd.DataFrame, scurve_parameters: pd.DataFrame) -> pd.DataFrame:
    """
    Transform scurve_parameters with s_curve to never_share.
    Parameters
    ----------
    s_curves : pandas.DataFrame
    scurve_parameters : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame

    Notes
    -----
    Age is padded from -max age to 0

    """
    max_age = s_curves.index.get_level_values(level='age').max()
    df_never_share = pd.DataFrame(
        # noinspection PyTypeChecker
        [(row.building_category, idx, row.condition + '_never_share', row.never_share) for idx in range(-max_age, max_age + 1)
         for row in
         scurve_parameters.itertuples()],
        columns=['building_category', 'age', 'building_condition', 'scurve']).sort_values(
        ['building_category', 'building_condition', 'age']).set_index(
        ['building_category', 'age', 'building_condition'])
    return df_never_share


def scurve_from_s_curve_parameters(scurve_parameters: pd.DataFrame) -> pd.DataFrame:
    """
    Create scurve new dataframe from scurve_parameters using ebm.model.area.building_condition_scurves and
        ebm.model.area.building_condition_accumulated_scurves

    Each row represent a building_category and building_condition at a certain age.

    Parameters
    ----------
    scurve_parameters : pandas.DataFrame

    Notes
    -----
    Filters out age greater than 130 when last_age is not 150 for backwards compatability. Subject to change.

    Returns
    -------
    pandas.DataFrame
    """
    df = scurve_rates(translate_scurve_parameter_to_shortform(scurve_parameters))
    df_age = scurve_rates_with_age(df)

    df = scurve_rates_to_long(df_age.query('age<=130 or last_age==150'))
    return df


def accumulate_demolition(s_curves_long: pd.DataFrame, years: YearRange) -> pd.DataFrame:
    """
    Sets demolition in year 0 (2020) to 0.0 and sums up the yearly demolition using years

    Parameters
    ----------
    s_curves_long : pandas.DataFrame
    years : YearRange

    Returns
    -------
    pandas.DataFrame
    """
    demolition_acc = s_curves_long
    demolition_acc.loc[demolition_acc.query(f'year<={years.start}').index, 'demolition'] = 0.0
    demolition_acc['demolition_acc'] = demolition_acc.groupby(by=['building_category', 'building_code'])[['demolition']].cumsum()[
        ['demolition']]

    return demolition_acc

# noinspection PyTypeChecker
def merge_s_curves_and_building_code(s_curves: pd.DataFrame, df_never_share: pd.DataFrame, building_code_parameters: pd.DataFrame) -> pd.DataFrame:
    """
    Cross merge s_curves and df_never_share with all building_code in building_code_parameters

    Parameters
    ----------
    s_curves : pandas.DataFrame
    df_never_share : pandas.DataFrame
    building_code_parameters : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """
    s_curves = pd.concat([s_curves, df_never_share])

    s_curves_by_building_code = s_curves.reset_index().join(building_code_parameters, how='cross')
    s_curves_by_building_code['year'] = s_curves_by_building_code['building_year'] + s_curves_by_building_code['age']
    s_curves_long = s_curves_by_building_code.pivot(index=['building_category', 'building_code', 'year', 'age'],
                                          columns=['building_condition'],
                                          values='scurve').reset_index()
    s_curves_long = (s_curves_long
        .reset_index(drop=True)
        .set_index(['building_category', 'building_code', 'year'], drop=True)
        .rename_axis(None, axis=1))
    return s_curves_long


def rates_grouped_by_period(rates: pd.Series) -> pd.DataFrame:
    return (
    rates[rates != rates.shift(1)]
    .to_frame(name='share')
    .reset_index()
    .join(
        rates[rates != rates.shift(-1)]
        .to_frame(name='share')
        .reset_index()
        .rename(columns={'age': 'end_age'})['end_age']
    )
    [['age', 'end_age', 'share']]
    .rename(columns={'age': 'start_age'})
    .assign(years=lambda x: x.end_age - x.start_age + 1)
    #.assign(period=lambda x: ['early_years', 'pre_rush', 'rush', 'post_rush', 'last_years'][:len(x)])
    #.assign(period=lambda x: ['early_years', 'pre_rush', 'rush', 'post_rush', 'last_years'][:len(x)])
)


def transform_to_dataframe(s_curve_cumulative_demolition: Series, s_curve_original_condition: Series, s_curve_renovation: Series,
                           s_curve_renovation_and_small_measure: Series, s_curve_small_measure: Series, s_curve_demolition: Series) -> pd.DataFrame:
    """
    Creates a pandas DataFrame from the parameters

    Parameters
    ----------
    s_curve_cumulative_demolition : pandas.Series
    s_curve_original_condition : pandas.Series
    s_curve_renovation : pandas.Series
    s_curve_renovation_and_small_measure : pandas.Series
    s_curve_small_measure : pandas.Series
    s_curve_demolition : pandas.Series

    Returns
    -------
    pandas.DataFrame
    """
    s_curves_by_condition = pd.DataFrame({
        'original_condition': s_curve_original_condition,
        'demolition': s_curve_cumulative_demolition,
        'small_measure': s_curve_small_measure,
        'renovation': s_curve_renovation,
        'renovation_and_small_measure': s_curve_renovation_and_small_measure,
        's_curve_demolition': s_curve_demolition
    })
    return s_curves_by_condition


def transform_to_long(s_curves_by_condition: pd.DataFrame) -> pd.DataFrame:
    """
    
    Parameters
    ----------
    s_curves_by_condition : pandas.DataFrame 

    Returns
    -------
    pandas.DataFrame
        transformed to long, on condition for each row
    """
    df_long = s_curves_by_condition.stack().to_frame(name='s_curve')

    df_long.index.names = ['building_category', 'building_code', 'year', 'building_condition']
    return df_long


def calculate_s_curves(scurve_parameters: pd.DataFrame,
                       building_code_parameters: pd.DataFrame,
                       years: YearRange,
                       **kwargs: pd.DataFrame|pd.Series) -> pd.DataFrame:

    s_curves_with_building_code = calculate_scurves_with_building_code(building_code_parameters, scurve_parameters, years)

    return normalize_scurve_conditions(s_curves_with_building_code, years, *kwargs)


def normalize_scurve_conditions(s_curves_with_building_code, years, **kwargs):
    s_curves_with_demolition_acc = accumulate_demolition(s_curves_with_building_code, years)
    s_curve_demolition = s_curves_with_building_code.demolition
    s_curve_cumulative_demolition = transform_to_cumulative_demolition(s_curves_with_demolition_acc, years)
    s_curve_renovation_never_share = s_curves_with_building_code.renovation_never_share
    s_curve_small_measure_never_share = kwargs.get('small_measure_never_share',
                                                   s_curves_with_building_code.small_measure_never_share)
    s_curve_cumulative_small_measure = kwargs.get('cumulative_small_measure',
                                                  cumulative_small_measure(s_curves_with_building_code, years))
    s_curve_cumulative_renovation = cumulative_renovation(s_curves_with_building_code, years)
    s_curve_renovation_max = renovation_max(s_curve_cumulative_demolition, s_curve_renovation_never_share)
    s_curve_small_measure_max = kwargs.get('s_curve_small_measure_max', small_measure_max(s_curve_cumulative_demolition,
                                                                                          s_curve_small_measure_never_share))
    s_curve_small_measure_total = trim_max_value(s_curve_cumulative_small_measure, s_curve_small_measure_max)
    s_curve_renovation_total = trim_max_value(s_curve_cumulative_renovation, s_curve_renovation_max)
    scurve_total = total(s_curve_renovation_total, s_curve_small_measure_total)
    s_curve_renovation_from_small_measure = renovation_from_small_measure(s_curve_renovation_max,
                                                                          s_curve_small_measure_total)
    s_curve_renovation = trim_renovation_from_renovation_total(s_curve_renovation=s_curve_renovation_from_small_measure,
                                                               s_curve_renovation_max=s_curve_renovation_max,
                                                               s_curve_renovation_total=s_curve_renovation_total,
                                                               scurve_total=scurve_total)
    s_curve_renovation_and_small_measure = renovation_and_small_measure(s_curve_renovation, s_curve_renovation_total)
    s_curve_small_measure = small_measure(s_curve_renovation_and_small_measure, s_curve_small_measure_total)
    s_curve_original_condition = original_condition(s_curve_cumulative_demolition, s_curve_renovation,
                                                    s_curve_renovation_and_small_measure,
                                                    s_curve_small_measure)
    s_curves_by_condition = transform_to_dataframe(s_curve_cumulative_demolition,
                                                   s_curve_original_condition,
                                                   s_curve_renovation,
                                                   s_curve_renovation_and_small_measure,
                                                   s_curve_small_measure,
                                                   s_curve_demolition)
    s_curves_by_condition['original_condition'] = s_curve_original_condition
    s_curves_by_condition['demolition'] = s_curve_cumulative_demolition
    s_curves_by_condition['small_measure'] = s_curve_small_measure
    s_curves_by_condition['renovation'] = s_curve_renovation
    s_curves_by_condition['renovation_and_small_measure'] = s_curve_renovation_and_small_measure
    s_curves_by_condition[
        's_curve_sum'] = s_curve_original_condition + s_curve_cumulative_demolition + s_curve_small_measure + s_curve_renovation + s_curve_renovation_and_small_measure
    s_curves_by_condition['s_curve_demolition'] = s_curve_demolition
    s_curves_by_condition['s_curve_cumulative_demolition'] = s_curve_cumulative_demolition
    s_curves_by_condition['s_curve_small_measure_total'] = s_curve_small_measure_total
    s_curves_by_condition['s_curve_small_measure_max'] = s_curve_small_measure_max
    s_curves_by_condition['s_curve_cumulative_small_measure'] = s_curve_cumulative_small_measure
    s_curves_by_condition['s_curve_small_measure_never_share'] = s_curve_small_measure_never_share
    s_curves_by_condition['scurve_total'] = scurve_total
    s_curves_by_condition['s_curve_renovation_max'] = s_curve_renovation_max
    s_curves_by_condition['s_curve_cumulative_renovation'] = s_curve_cumulative_renovation
    s_curves_by_condition['s_curve_renovation_total'] = s_curve_renovation_total
    s_curves_by_condition['renovation_never_share'] = s_curve_renovation_never_share
    s_curves_by_condition['age'] = s_curves_with_building_code['age']
    # s_curves_by_condition.to_excel('output\s_curves_by_condition.xlsx', merge_cells=False)
    return s_curves_by_condition


def calculate_scurves_with_building_code(building_code_parameters, scurve_parameters, years):
    # Transform s_curve_parameters into long form with each row representing a building_condition at a certain age
    s_curves = scurve_from_s_curve_parameters(scurve_parameters)
    df_never_share = pad_s_curve_age(s_curves, scurve_parameters)
    s_curves_with_building_code = merge_s_curves_and_building_code(s_curves, df_never_share, building_code_parameters)
    s_curves_with_building_code = s_curves_with_building_code.loc[(slice(None), slice(None), [y for y in years])]
    return s_curves_with_building_code


def make_s_curve_parameters(earliest_age: int|None=None, average_age: int|None=None, last_age: int|None=None, rush_years: int|None=None, rush_share: float|None=None, never_share: float|None=None, building_lifetime: int=130,  building_category: str | None = 'unknown', condition: str | None = 'unknown') -> pd.DataFrame:
    errors = []
    if earliest_age < 0:
        logger.warning(f'Expected value above zero for {earliest_age=}')
        errors.append('earliest_age')
    if average_age < 0:
        logger.warning(f'Expected value above zero for {average_age=}')
        errors.append('average_age')
    if last_age < 0:
        logger.warning(f'Expected value above zero for {last_age=}')
        errors.append('last_age')
    if rush_share < 0:
        logger.warning(f'Expected value above zero for {rush_share=}')
        errors.append('rush_share')
    if never_share < 0:
        logger.warning(f'Expected value above zero for {never_share=}')
        errors.append('never_share')
    if errors:
        msg = f'Illegal value for {" ".join(errors)}'
        raise ValueError(msg)

    pre_rush_years = (average_age - earliest_age - (rush_years / 2))
    if pre_rush_years == 0:
        msg = f'average_age={average_age}, leaves no room for a pre rush period'
        logger.warning(msg)
    post_rush_years = (last_age - average_age - (rush_years / 2))
    if post_rush_years == 0:
        msg = f'last_age={last_age}, leaves no room for a post rush period'
        logger.warning(msg)

    df = pd.DataFrame([{
        'building_category': building_category, 'building_condition': condition,
        'earliest_age_for_measure': earliest_age, 'average_age_for_measure': average_age,
        'rush_period_years': rush_years, 'last_age_for_measure': last_age, 'rush_share': rush_share,
        'never_share': never_share}],
    )
    return df


def translate_scurve_parameter_to_shortform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        'condition': 'building_condition',
        'earliest_age_for_measure': 'earliest_age',
        'average_age_for_measure': 'average_age',
        'rush_period_years': 'rush_period',
        'last_age_for_measure': 'last_age',
        'rush_share': 'rush_share',
        'never_share': 'never_share',
    })
    return df


def scurve_rates_to_long(scurve_rates: pd.DataFrame) -> pd.DataFrame:
    share = scurve_rates.rate.to_frame().reset_index()
    share = share.rename(columns={'rate': 'scurve'})

    share_acc = scurve_rates.rate_acc.to_frame().reset_index()
    share_acc.building_condition = share_acc.building_condition + '_acc'
    share_acc = share_acc.rename(columns={'rate_acc': 'scurve'})

    df = pd.concat([share, share_acc]).set_index(['building_category', 'age', 'building_condition'])
    return df


def scurve_rates_with_age(df: pd.DataFrame) -> pd.DataFrame:
    # Define age range
    max_age = max(int(df.total_span.max()), 130)+1
    ages = np.arange(1, max_age)  # 1 to 129

    # Expand DataFrame for each age
    df_expanded = df.loc[df.index.repeat(len(ages))].copy()
    df_expanded['age'] = np.tile(ages, len(df))

    df = df_expanded

    # Compute rates using new column names
    df['pre_rush_rate'] = (1 - df['rush_share'] - df['never_share']) * (
            0.5 / (df['average_age'] - df['earliest_age'] - (df['rush_period'] / 2))
    )
    df['rush_rate'] = df['rush_share'] / df['rush_period']
    df['post_rush_rate'] = (1 - df['rush_share'] - df['never_share']) * (
            0.5 / (df['last_age'] - df['average_age'] - (df['rush_period'] / 2))
    )

    # Determine rate for each age
    conditions = [
        df['age'] < df['earliest_age'],
        df['age'] < (df['average_age'] - df['rush_period'] / 2),
        df['age'] < (df['average_age'] + df['rush_period'] / 2),
        df['age'] < df['last_age'],
    ]

    choices = [
        0.0,
        df['pre_rush_rate'],
        df['rush_rate'],
        df['post_rush_rate'],
    ]

    df['rate'] = np.select(conditions, choices, default=0.0)

    # Compute cumulative sum of rates by category and condition
    df['rate_acc'] = df.groupby(by=['building_category', 'building_condition'])[['rate']].cumsum()

    # Reset index and set multi-index
    df = df.reset_index().set_index(['building_category', 'building_condition', 'age'])

    return df


def scurve_rates(s_curve_parameters: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate s-curve rate from dataframe.

    Parameters
    ----------
    s_curve_parameters : pd.DataFrame
        A pandas dataframe with average_age, earliest_age, rush_period, last_age, rush_share and never_share

    Returns
    -------
    pd.DataFrame
        With columns rate, total_share indexed by building_category, building_condition and age

    """
    df = s_curve_parameters.assign(
        post_start_age=s_curve_parameters.average_age + (s_curve_parameters.rush_period / 2),
        pre_end_age=s_curve_parameters.average_age - (s_curve_parameters.rush_period / 2),
        pre_start_age=s_curve_parameters.earliest_age,
        pre_period=lambda x: x.pre_end_age - x.pre_start_age,
        post_end_age=s_curve_parameters.last_age,
        post_period=lambda x: x.post_end_age - x.post_start_age,
        total_span=lambda x: x.earliest_age + x.pre_period + x.rush_period + x.post_period,
        rush_rate=lambda x: x.rush_share / x.rush_period,
        measure_share=lambda x: 1.0 - x.never_share,
        remaining_share=lambda x: 1.0 - (x.never_share + x.rush_share),
        pre_share=lambda x: x.remaining_share / 2,
        pre_rate=lambda x: x.pre_share / x.pre_period,
        post_share=lambda x: x.remaining_share / 2,
        post_rate=lambda x: x.post_share / x.post_period,
        total_share=lambda x: x.pre_share + x.rush_share + x.post_share + x.never_share,
    )

    return df


def pause_building_condition_rates(s_curve_building_code:pd.DataFrame,
                                   period: YearRange|tuple[int, int]|int,
                                   conditions: list[str]|None=None) -> pd.DataFrame:

    """
    Apply a pause (deferral) to selected building condition rates and accumulate the results.

    This function is a convenience wrapper that first shifts the specified building
    condition rate columns forward in time for a given pause period—simulating a
    deferral of activity—and then recomputes cumulative (running) totals using
    ``accumulate_building_condition_rates``.

    Internally, it applies two operations:

    1. ``shift_building_condition_rates``:
       Shifts selected condition rate columns forward by the length of the
       pause period for all years greater than or equal to ``period.start``,
       within each group of the first two index levels.
    2. ``accumulate_building_condition_rates``:
       Recomputes cumulative totals for the condition rate columns and their
       corresponding accumulator columns.

    Parameters
    ----------
    s_curve_building_code : pandas.DataFrame
        A DataFrame indexed by a MultiIndex with at least three levels,
        where index level 2 represents the year. Must contain the condition
        rate columns referenced in ``conditions`` and the accumulator columns
        required by ``accumulate_building_condition_rates``.
    period : YearRange | tuple[int, int] | int
        The period defining the pause:
        - If a ``tuple[int, int]``: interpreted as (start_year, end_year), inclusive.
        - If an ``int``: treated as the pause start year, with the end year taken
          as the maximum year present in the DataFrame.
        - If a ``YearRange``: used directly.
        The pause length is determined as the number of years in ``period``.
    conditions : list[str] or None, default None
        Column names representing the building condition rates to pause.
        If ``None``, defaults to:
        ``['small_measure', 'renovation', 'demolition']``.

    Returns
    -------
    pandas.DataFrame
        A DataFrame where:
        - Values in the selected condition columns have been shifted forward
          according to the pause period.
        - Accumulator columns have been updated to reflect the new running totals.
        The presence and structure of the columns match the output of
        ``accumulate_building_condition_rates``.

    Notes
    -----
    - This function does not mutate the input DataFrame; it returns a new one.
    - All shifting is done within each group of the first two index levels.
    - Years are expected to be integers.
    - See ``shift_building_condition_rates`` and
      ``accumulate_building_condition_rates`` for detailed behavior of the
      underlying operations.

    Examples
    --------
    Pause condition rates starting from 2028 and recompute accumulations:

    >>> out = pause_building_condition_rates(df, period=2028)

    Pause explicitly from 2026 through 2029:

    >>> out = pause_building_condition_rates(df, period=YearRange(2026, 2029))

    Pause only renovation rates:

    >>> out = pause_building_condition_rates(
    ...     df, period=(2025, 2027), conditions=['renovation']
    ... )
    """
    return (s_curve_building_code
            .pipe(shift_building_condition_rates, period=period, conditions=conditions)
            .pipe(accumulate_building_condition_rates))


def shift_building_condition_rates(s_curve_building_code:pd.DataFrame,
                                   period: YearRange|tuple[int, int]|int,
                                   conditions: list[str]|None=None) -> pd.DataFrame:
    """
    Shift building condition rates over a given period forward in time.

    This function takes a copy of the input DataFrame and, for the specified building conditions,
    shifts values occurring from `period.start` onwards by the length of the period
    (i.e., the number of years in `period`). The shift is done within each group
    defined by the first two levels of the index. Newly created gaps are filled with 0.

    The intended use is to simulate a pause (deferral) in certain building-related
    condition rates (e.g., small measures, renovation, demolition) for a span of years,
    and resume them after the pause by moving the corresponding values forward.

    Parameters
    ----------
    s_curve_building_code : pandas.DataFrame
        A DataFrame indexed by a MultiIndex with **at least three levels** where the
        third level (index level number 2) is an integer year. The DataFrame must contain
        columns whose names match those provided in `conditions`. The function
        operates on a copy of this DataFrame and does not mutate the original.
    period : YearRange | tuple[int, int] | int
        The pause period:
        - If a `tuple[int, int]`, it is interpreted as `(start_year, end_year)` inclusive.
          The start will be clamped up to the minimum year present in the DataFrame.
        - If an `int`, it is treated as the start year; the end year is set to the
          maximum year present in the DataFrame. The start will be clamped up to
          the minimum year present in the DataFrame.
    conditions : list[str] | None, default None
        Column names representing the building condition rates to pause. If `None`, defaults to
        `['small_measure', 'renovation', 'demolition']`.

    Returns
    -------
    pandas.DataFrame
        A new DataFrame (copy of the input) where, for rows with year >= `period.start`
        and columns listed in `conditions`, values are shifted **forward** by the pause length
        within each group of the first two index levels. Any values shifted beyond the
        available years are dropped by the shift operation, and any newly introduced
        gaps in the target slice are filled with 0.

    Raises
    ------
    ValueError
        If `period` is not a `YearRange`, an `int`, or a valid `(start_year, end_year)` tuple
        where `start_year <= end_year`.

    Notes
    -----
    - The function assumes:
      * The DataFrame index has a third level (at position 2) representing the year.
      * Years are integers and sortable.
      * The columns listed in `conditions` exist in the DataFrame.
    - The operation:
      1. Determines the effective `YearRange` for the pause, clamping the start
         to the minimum year in the data if needed.
      2. Computes `pause_length = len(period)`.
      3. For `year >= period.start`, shifts the `conditions` columns by `pause_length`
         **within each group of the first two index levels**.
      4. Fills `NaN` introduced by the shift with 0 in the affected slice.

    Examples
    --------
    Suppose `df` has a MultiIndex `(region, building_code, year)` and includes
    columns `'small_measure'`, `'renovation'`, and `'demolition'`.

    Pause from 2028 through the max available year:
    >>> out = shift_building_condition_rates(df, period=2028)

    Pause explicitly from 2026 to 2029 (inclusive):
    >>> out = shift_building_condition_rates(df, period=(2026, 2029))

    Using a custom set of conditions:
    >>> out = shift_building_condition_rates(df, period=(2025, 2027),
    ...                                      conditions=['renovation'])
    """
    cr = s_curve_building_code.copy()

    year_level_num = 2
    minimum_year = cr.index.get_level_values(year_level_num).min()
    if isinstance(period, int) and not isinstance(period, bool):
        maximum_year = cr.index.get_level_values(year_level_num).max()
        period = YearRange(start=max(period, minimum_year), end=maximum_year)
    elif isinstance(period, tuple) and len(period) == 2 and isinstance(period[0], int) and isinstance(period[1], int) and \
            period[0] <= period[1]:  # noqa: PLR2004
        period = YearRange(max(period[0], minimum_year), period[1])
    elif not isinstance(period, YearRange):
        msg = f'Illegal value in period `{period}`. YearRange or int expected.'
        raise ValueError(msg)

    if conditions is None:
        conditions = ['small_measure', 'renovation', 'demolition']

    # To avoid any indexing issues, period start is set to minimum year when lower
    if period.start < minimum_year:
        period = YearRange(minimum_year, period.end)
    pause_length = len(period)

    shifted_cr = cr.loc[pd.IndexSlice[:, :, period.start:], conditions].groupby(level=[0, 1]).shift(pause_length)
    cr.loc[pd.IndexSlice[:, :, period.start:], conditions] = shifted_cr.fillna(0)

    return cr


def accumulate_building_condition_rates(building_condition_rates: pd.DataFrame) -> pd.DataFrame:
    """
    Accumulate annual building condition rates into running totals per building category and code.

    This function takes a DataFrame indexed by a MultiIndex with at least three levels,
    where the third level (index level 2) represents the year. For three predefined
    condition columns—``small_measure``, ``renovation``, and ``demolition``—it computes
    cumulative sums across years within each group of the first two index levels.

    The accumulation uses temporary columns:
    - For the first year (hard‑coded as 2020), values are taken from the corresponding
      ``*_acc`` accumulator columns (defaulting to 0 where missing).
    - For all later years (from 2021 onward), values are taken from the annual
      condition rate columns.
    These temporary values are cumulatively summed per group, and the resulting
    running totals populate the ``*_acc`` columns.

    Parameters
    ----------
    building_condition_rates : pandas.DataFrame
        Input DataFrame with a MultiIndex where index level 2 is an integer year.
        Must contain the columns:
        ``'small_measure'``, ``'renovation'``, ``'demolition'``,
        and their accumulator counterparts:
        ``'small_measure_acc'``, ``'renovation_acc'``, ``'demolition_acc'``.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing only the six columns:
        ``['small_measure', 'renovation', 'demolition',
           'small_measure_acc', 'renovation_acc', 'demolition_acc']``.
        The accumulator columns contain cumulative sums over years within each
        group of index levels 0 and 1.

    Notes
    -----
    - The function does **not** modify the input DataFrame; it works on a copy.
    - The first year is assumed to be **2020**.
    - Accumulators for 2020 come from the existing ``*_acc`` columns.
    - From 2021 onward, annual values from the condition columns are used for accumulation.

    Examples
    --------
    Given a MultiIndex of (region, building_code, year):

    >>> out = accumulate_building_condition_rates(df)
    >>> out.columns
    Index(['small_measure', 'renovation', 'demolition',
           'small_measure_acc', 'renovation_acc', 'demolition_acc'], dtype='object')

    The returned accumulator columns represent cumulative totals per
    (region, building_code) across increasing years.
    """
    df = building_condition_rates.copy()
    first_year = 2020
    next_year = 2021

    condition_columns = ['small_measure', 'renovation', 'demolition']
    acc_columns = [f'{bc}_acc' for bc in condition_columns]
    temp_columns = [f'{bc}ac' for bc in condition_columns]

    df.loc[(slice(None), slice(None), first_year), temp_columns] = (
        df.loc[(slice(None), slice(None), first_year), acc_columns].fillna(0.0).to_numpy()
    )

    df.loc[pd.IndexSlice[:, :, next_year:], temp_columns] = (
        df.loc[pd.IndexSlice[:, :, next_year:], condition_columns].to_numpy()
    )

    df[acc_columns] = df.groupby(level=[0, 1])[temp_columns].cumsum()

    return df[condition_columns + acc_columns]


def freeze_scurves_from_year(s_curves: pd.DataFrame,
                             years: int | YearRange | tuple[int, int],
                             condition_columns: list[str]|None = None) -> pd.DataFrame:
    """
    Freeze building condition rate columns over a specified year range and resume the original trajectory after the freeze with a forward time shift.

    This function operates on a MultiIndex DataFrame where the year is at index
    level 2. For the specified freeze period (inclusive), the values of the
    condition columns (as defined by ``list(BuildingCondition)``) are set equal to
    their values at the first freeze year (``start``). For the years following
    the freeze period, the original (unfrozen) time series is continued but
    shifted forward by the length of the freeze, preserving the trajectory shape
    while delaying it in time.

    Parameters
    ----------
    condition_columns :
    s_curves : pandas.DataFrame
        Input DataFrame with a MultiIndex row index. The **year must be at level 2**
        of the index. The DataFrame must contain one column for each member of
        ``BuildingCondition`` (e.g., an Enum listing condition rate columns).
    years : int or YearRange or tuple of (int, int)
        Specification of the freeze period.

        - If ``YearRange``: uses ``[years.start, years.end]`` (inclusive).
          ``start`` is clamped to the minimum year present in the DataFrame.
        - If ``int``: interpreted as ``start=years`` (clamped to the minimum year)
          and ``end = max_year`` present in the DataFrame.
        - If ``(start, end)`` tuple: uses the inclusive range after validating
          that ``start <= end`` and clamping ``start`` to the minimum year.

    Returns
    -------
    pandas.DataFrame
        A copy of ``s_curves`` where:
        - For all index keys, the condition columns in ``[start, end]`` are set to
          their values at ``year == start`` (i.e., frozen).
        - For years ``> end``, the original (unfrozen) values are applied but shifted
          forward by ``(end - start)`` years to avoid a discontinuity.

    Raises
    ------
    ValueError
        If ``years`` is not a supported type (``YearRange``, ``int``, or 2-tuple of
        ``int`` with ``start <= end``).

    Notes
    -----
    - The function assumes the year is at index level 2 and uses
      ``pd.IndexSlice[:, :, ...]`` to select by year range.
    - Only columns listed in ``list(BuildingCondition)`` are modified; other
      columns remain unchanged.
    - The freezing is inclusive of both ``start`` and ``end`` years.
    - Post-freeze continuation uses:

      ``post_freeze_rates.shift(end - start).iloc[1:]``

      to align the shifted series; this implicitly drops the first shifted row to
      guard against misalignment. If you require stricter alignment guarantees,
      consider reindexing by explicit year keys instead of relying on
      ``.iloc[1:]``.

    Examples
    --------
    Freeze from a specific year to the end of the dataset:

    >>> df_frozen = freeze_scurves_from_year(s_curves, 2022)

    Freeze across an explicit range:

    >>> df_frozen = freeze_scurves_from_year(s_curves, (2021, 2023))

    Freeze using a YearRange object:

    >>> rng = YearRange(start=2020, end=2022)
    >>> df_frozen = freeze_scurves_from_year(s_curves, rng)
    """

    # Copy the input DataFrame to avoid mutating the caller data
    df = s_curves.copy()

    # Identify year column and first year
    year_level_num = 2
    minimum_year = df.index.get_level_values(year_level_num).min()

    # Convert arguments to YearRange. Raise error when unable to do so.
    if isinstance(years, YearRange):
        freeze_period = YearRange(max(years.start, minimum_year), years.end)
    elif isinstance(years, int) and not isinstance(years, bool):
        maximum_year = df.index.get_level_values(year_level_num).max()
        freeze_period = YearRange(start=max(years, minimum_year), end=maximum_year)
    elif isinstance(years, tuple) and len(years)== 2 and isinstance(years[0], int) and isinstance(years[1], int) and years[0] <= years[1]:  # noqa: PLR2004
        freeze_period = YearRange(max(years[0], minimum_year), years[1])
    else:
        msg = f'Illegal value in years `{years}`. YearRange or int expected.'
        raise ValueError(msg)

    # Save freeze rates and post freeze rates
    condition_columns = list(BuildingCondition) if condition_columns is None else condition_columns
    freeze_rates = df.loc[pd.IndexSlice[:, :, freeze_period.start]][condition_columns]
    post_freeze_rates = df.loc[pd.IndexSlice[:, :, freeze_period.start + 1:]][condition_columns]

    # Apply freeze rate on columns for the freeze perioder
    freeze_index = pd.IndexSlice[:, :, freeze_period.start:freeze_period.end]
    df.loc[freeze_index, condition_columns] = freeze_rates

    # Set post freeze rates
    post_freeze_index = pd.IndexSlice[:, :, freeze_period.end + 1:]
    df.loc[post_freeze_index, condition_columns] = post_freeze_rates.shift(freeze_period.end - freeze_period.start).iloc[1:]

    return df


def main() -> None:
    import pathlib  # noqa: PLC0415
    logger.info('Calculate all scurves from data/s_curve.csv')
    scurve_parameters_csv_path = pathlib.Path(__file__).parent.parent / 'data/original/s_curve.csv'
    scurve_parameters_csv = pd.read_csv(scurve_parameters_csv_path)

    df_scurve_rates = scurve_rates(translate_scurve_parameter_to_shortform(scurve_parameters_csv))
    print(df_scurve_rates)

    rates_with_age = scurve_rates_with_age(df_scurve_rates)
    print(rates_with_age)

    df = scurve_rates_to_long(rates_with_age)
    print(df)

    logger.info('done')


if __name__ == '__main__':
    main()
