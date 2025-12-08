import pandas as pd
from loguru import logger


class SCurve:
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
            'building_category': building_category, 'building_condition': condition,
            'earliest_age_for_measure': earliest_age, 'average_age_for_measure': average_age,
            'rush_period_years':rush_years, 'last_age_for_measure':last_age, 'rush_share':rush_share,
            'never_share':never_share}],
        )


    def __repr__(self):
        return (
        f"SCurve(earliest_age={int(self.df.earliest_age_for_measure)}, "
        f"average_age={int(self.df.average_age_for_measure)}, "
        f"rush_years={int(self.df.rush_period_years)}, "
        f"rush_share={float(self.df.rush_share)}, "
        f"last_age={int(self.df.last_age_for_measure)}, "
        f"never_share={float(self.df.never_share)})"
        )

    def calc_scurve(self) -> pd.DataFrame:
        from ebm.areaforecast.s_curve import translate_scurve_parameter_to_shortform, scurve_rates, scurve_rates_with_age  # noqa: PLC0415, I001
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
