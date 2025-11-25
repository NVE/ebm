import numpy as np
import pandas as pd
from loguru import logger


class AltCurve:
    def __init__(self,
                 earliest_age: int|None=None,
                 average_age: int|None=None,
                 last_age: int|None=None,
                 rush_years: int|None=None,
                 rush_share: float|None=None,
                 never_share: float|None=None,
                 building_lifetime: int = 130,
                 building_category: str|None = 'unknown',
                 condition: str|None = 'unknown',
                 s:pd.Series|None = None,
                 df:pd.Series|None = None):

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

        self.df = pd.DataFrame([{
            'building_category': building_category, 'condition': condition,
            'earliest_age_for_measure': earliest_age, 'average_age_for_measure': average_age,
            'rush_period_years':rush_years, 'last_age_for_measure':last_age, 'rush_share':rush_share,
            'never_share':never_share}],
        )


    def calc_scurve(self) -> pd.DataFrame:
        df = translate_scurve_parameter_to_shortform(self.df)

        df = scurve_rates(df)
        df = scurve_rates_with_age(df)

        return df



    def get_rates_per_year_over_building_lifetime(self) -> pd.Series:
        """
        Create a series that holds the yearly measure rates over the building lifetime.

        This method defines the periods in the S-curve, adds the yearly measure rates to
        the corresponding periods, and stores them in a pandas Series.

        Returns
        -------
        pd.Series
            A Series containing the yearly measure rates over the building lifetime
            with an index representing the age from 1 to the building lifetime.

        """
        return self.calc_scurve().rate



def translate_scurve_parameter_to_shortform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        'earliest_age_for_measure': 'earliest_age',
        'average_age_for_measure': 'average_age',
        'rush_period_years': 'rush_period',
        'last_age_for_measure': 'last_age',
        'rush_share': 'rush_share',
        'never_share': 'never_share',
    })
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
    df['rate_acc'] = df.groupby(by=['building_category', 'condition'])[['rate']].cumsum()

    # Reset index and set multi-index
    df = df.reset_index().set_index(['building_category', 'condition', 'age'])

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


def main() -> None:
    import pathlib  # noqa: PLC0415
    logger.info('Calculate all scurves from data/s_curve.csv')
    area_parameters_path = pathlib.Path(__file__).parent.parent / 'data/original/s_curve.csv'
    df = pd.read_csv(area_parameters_path)
    for r, v in df.iterrows():
        scurve = AltCurve(
            building_category=v.building_category,
            condition=v.condition,
            earliest_age=v.earliest_age_for_measure,
            average_age=v.average_age_for_measure,
            last_age=v.last_age_for_measure,
            rush_years=v.rush_period_years,
            never_share=v.never_share,
            rush_share=v.rush_share)
        df = scurve.calc_scurve()
        print(v.building_category, v.condition, len(df))
        print(df.iloc[[0, 1, 5, 10, 50, 100]])
    logger.info('done')

if __name__ == '__main__':
    main()


