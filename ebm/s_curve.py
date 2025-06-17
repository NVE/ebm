import pandas as pd

from ebm.model.area import building_condition_accumulated_scurves, building_condition_scurves


def calculate_s_curve_original_condition(s_curve_cumulative_demolition, s_curve_renovation,
                                         s_curve_renovation_and_small_measure, s_curve_small_measure):
    return (1.0 -
            s_curve_cumulative_demolition -
            s_curve_renovation -
            s_curve_renovation_and_small_measure -
            s_curve_small_measure)


def calculate_s_curve_small_measure(s_curve_renovation_and_small_measure, s_curve_small_measure_total):

    # ### SharesPerCondition calc_small_measure
    #  - ❌   sette til 0 før byggeår
    # ```python
    #     construction_year = self.tek_params[tek].building_year
    #     shares.loc[self.period_index <= construction_year] = 0
    # ```

    return s_curve_small_measure_total - s_curve_renovation_and_small_measure


def calculate_s_curve_renovation_and_small_measure(s_curve_renovation, s_curve_renovation_total):
    # ### SharesPerCondition calc_renovation_and_small_measure
    #  - ❌ Sette til 0 før byggeår

    return s_curve_renovation_total - s_curve_renovation


def trim_s_curve_renovation_from_renovation_total(s_curve_renovation, s_curve_renovation_max, s_curve_renovation_total,
                                                  scurve_total):
    s_curve_total_smaller_than_max_renovation = s_curve_renovation_total.loc[scurve_total < s_curve_renovation_max]
    s_curve_renovation = s_curve_total_smaller_than_max_renovation.combine_first(s_curve_renovation)
    return s_curve_renovation


def calculate_s_curve_renovation_from_small_measure(s_curve_renovation_max, s_curve_small_measure_total):
    # ## small_measure and renovation to scurve_small_measure_total, RN
    # ## SharesPerCondition calc_renovation
    #
    #  - ❌ Ser ut som det er edge case for byggeår.
    #  - ❌ Årene før byggeår må settes til 0 for scurve_renovation?

    return (s_curve_renovation_max - s_curve_small_measure_total).clip(lower=0.0)


def calculate_s_curve_total(s_curve_renovation_total, s_curve_small_measure_total):
    return (s_curve_small_measure_total + s_curve_renovation_total).clip(lower=0.0)


def trim_scurve_max_value(s_curve_cumulative_small_measure, s_curve_small_measure_max):
    return s_curve_cumulative_small_measure.combine(s_curve_small_measure_max, min).clip(0)


def calculate_s_curve_small_measure_max(s_curve_cumulative_demolition, s_curve_small_measure_never_share):
    return 1.0 - s_curve_cumulative_demolition - s_curve_small_measure_never_share


def calculate_s_curve_renovation_max(s_curve_cumulative_demolition, s_curve_renovation_never_share):
    return 1.0 - s_curve_cumulative_demolition - s_curve_renovation_never_share


def calculate_s_curve_cumulative_renovation(s_curves_with_tek, years):
    return s_curves_with_tek.renovation_acc.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)


def calculate_s_curve_cumulative_small_measure(s_curves_with_tek, years):
    return s_curves_with_tek.small_measure_acc.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)


def calculate_s_curve_small_measure_never_share(s_curves_with_tek, years):
    return s_curves_with_tek.small_measure_nvr.loc[(slice(None), slice(None), list(years.year_range))]


def calculate_s_curve_renovation_never_share(s_curves_with_tek, years):
    return s_curves_with_tek.renovation_nvr.loc[(slice(None), slice(None), list(years.year_range))]


def calculate_s_curve_demolition(cumulative_demolition, years):
    return cumulative_demolition.demolition.loc[(slice(None), slice(None), list(years.year_range))].fillna(0.0)


def calculate_s_curve_cumulative_demolition(cumulative_demolition, years):
    s_curve_cumulative_demolition = cumulative_demolition.demolition_acc.loc[
        (slice(None), slice(None), list(years.year_range))].fillna(0.0)
    return s_curve_cumulative_demolition


def transform_scurve_parameters_never_share(s_curves, scurve_parameters):
    max_age = s_curves.index.get_level_values(level='age').max()
    df_never_share = pd.DataFrame(
        [(row.building_category, idx, row.condition + '_nvr', row.never_share) for idx in range(-max_age, max_age + 1)
         for row in
         scurve_parameters.itertuples()],
        columns=['building_category', 'age', 'building_condition', 'scurve']).sort_values(
        ['building_category', 'building_condition', 'age']).set_index(
        ['building_category', 'age', 'building_condition'])
    return df_never_share


def transform_scurve_parameters_to_scurve(scurve_parameters):
    scurve_by_year = building_condition_scurves(scurve_parameters)
    scurve_accumulated = building_condition_accumulated_scurves(scurve_parameters)
    s_curves = pd.concat([scurve_by_year, scurve_accumulated])
    return s_curves


def accumulate_demolition(s_curves_long, years):
    demolition_acc = s_curves_long
    demolition_acc.loc[demolition_acc.query(f'year<={years.start}').index, 'demolition'] = 0.0
    demolition_acc['demolition_acc'] = demolition_acc.groupby(by=['building_category', 'TEK'])[['demolition']].cumsum()[
        ['demolition']]

    return demolition_acc


def merge_s_curves_and_tek(s_curves, df_never_share, tek_parameters):
    s_curves = pd.concat([s_curves, df_never_share])

    s_curves_by_tek = s_curves.reset_index().join(tek_parameters, how='cross')
    s_curves_by_tek['year'] = s_curves_by_tek['building_year'] + s_curves_by_tek['age']
    s_curves_long = s_curves_by_tek.pivot(index=['building_category', 'TEK', 'year'],
                                          columns=['building_condition'],
                                          values='scurve').reset_index()
    s_curves_long = (s_curves_long
        .reset_index(drop=True)
        .set_index(['building_category', 'TEK', 'year'], drop=True)
        .rename_axis(None, axis=1))
    return s_curves_long