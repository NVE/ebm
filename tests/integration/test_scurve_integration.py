import pathlib

import pandas as pd

import ebm.s_curve


def test_scurves():
    p = pathlib.Path(__file__).parent
    parameters_csv = p / 'test_scurve_integration_parameter.csv'
    expected_csv = p / 'test_scurve_integration_expected.csv'
    expected = pd.read_csv(expected_csv, index_col=['building_category', 'building_condition', 'age'])

    s_curve_parameters = ebm.s_curve.translate_scurve_parameter_to_shortform(pd.read_csv(parameters_csv))
    scurve_rates = ebm.s_curve.scurve_rates(s_curve_parameters)
    actual = ebm.s_curve.scurve_rates_with_age(scurve_rates)[['rate', 'rate_acc']].query('age<=130')

    pd.testing.assert_series_equal(actual.rate, expected.share, check_names=False)

