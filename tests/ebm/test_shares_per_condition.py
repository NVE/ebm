import typing
import pytest
import re
import pandas as pd

from ebm.model.data_classes import TEKParameters
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange
from unittest.mock import MagicMock


@pytest.fixture
def tek():
    return 'TEK49_RES'


@pytest.fixture 
def tek_list():
    return ['TEK49_RES']


@pytest.fixture
def tek_params():
    return {'TEK49_RES': TEKParameters(tek='TEK49_RES',
                                       building_year=1963,
                                       start_year=1956,
                                       end_year=1970)
    }


def generate_scurve_series(values: typing.List[float],
                           ages: typing.List[int]):
    """
    Generates a 'scurve' pd.Series with the given values and ages (length must match).
    """
    scurve_series = pd.Series(values, index=ages, name='scurve')
    scurve_series.index.name = 'age'
    return scurve_series


@pytest.fixture
def small_measure_scurve():
    return generate_scurve_series(values = [0.1,0.2,0.3,0.4,0.5], 
                                  ages = [47, 48, 49, 50, 51])


@pytest.fixture
def renovation_scurve():
    return generate_scurve_series(values = [0.2,0.3,0.4,0.5,0.6],
                                  ages = [47, 48, 49, 50, 51])


@pytest.fixture
def demolition_scurve():
    return generate_scurve_series(values = [0.3,0.4,0.5,0.6,0.7],
                                  ages = [47, 48, 49, 50, 51])


@pytest.fixture()
def scurves(small_measure_scurve, renovation_scurve, demolition_scurve):
    return {
        'small_measure': small_measure_scurve,
        'renovation': renovation_scurve,
        'demolition': demolition_scurve
    }


@pytest.fixture()
def never_shares():
    return {
        'small_measure': 0.01, 
        'renovation': 0.05, 
        'demolition': 0.05
    }


@pytest.fixture
def period():
    return YearRange(2010,2014)


@pytest.fixture
def default_params(tek_list: typing.List[str],
                   tek_params: typing.Dict[str, TEKParameters],
                   scurves: typing.Dict[str, pd.Series],
                   never_shares: typing.Dict[str, float],
                   period: YearRange):
    """
    Default parameters for creating a SharesPerCondition object.  
    """
    return {
        'tek_list': tek_list,
        'tek_params': tek_params,
        'scurves': scurves,
        'never_shares': never_shares,
        'period': period
    }


def test_control_series_values(default_params):
    """
    Do not raise any error with correct series values.
    """
    series = pd.Series([0.1,0.2])
    s = SharesPerCondition(**default_params)  
    s._control_series_values(series)


def test_control_series_values_negative_values(default_params):
    """
    Raise ValueError with negative values in series.
    """
    series = pd.Series([-1,0.2]) 
    s = SharesPerCondition(**default_params) 
    with pytest.raises(ValueError, match=re.escape('The series contains negative values')):
        s._control_series_values(series)


def test_control_series_values_na_values(default_params):
    """
    Raise ValueError with NA values in series.
    """
    series = pd.Series([None,0.2]) 
    s = SharesPerCondition(**default_params)   
    with pytest.raises(ValueError, match=re.escape('The series contains missing (NA) values')):
        s._control_series_values(series)


def test_scurve_per_year(default_params, tek, renovation_scurve, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)  
    result = s._scurve_per_year(tek=tek, scurve=renovation_scurve)
    expected = pd.Series(renovation_scurve.values, index= period.year_range, name='scurve')
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_scurve_per_year_building_ages_not_present(default_params, tek):
    """
    Raise ValueError if the calculated building ages per modelyear does not match with the 
    building ages in the given S-curve. 
    
    The method calculates building ages per model year according to the construction year of 
    the given TEK and 'period' of the SharesPerCondition object. With the given default_params,
    calculated building ages are = [47, 48, 49, 50, 51], and an ValueError should be raised if 
    they are not in the given scurve.  
    """
    s = SharesPerCondition(**default_params) 
    scurve = generate_scurve_series(values = [0.1,0.2],
                                    ages = [1,2])
    with pytest.raises(ValueError, match=re.escape('Building ages not present in S-curve index')):
        s._scurve_per_year(tek, scurve)


def test_calc_demolition(default_params, tek, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_demolition(tek)
    expected = pd.Series([0.0,0.1,0.2,0.3,0.4], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_demolition_with_tek_construction_year_in_period(default_params, period, scurves):
    """
    Test that the method adjusts the calculation method when the construction year of the given
    TEK is within the given 'period'. 

    The adjustment is that:
    - the share should be set to 0 in model years before and during the construciton year of the TEK.
    - the share should be set to the S-curve rate of the given model year if that year corresponds to 
      the year after the building was constructed.

    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    demolition_scurve = generate_scurve_series([0.6,0.8,0.9,0.9,0.9],
                                               [1,2,3,4,5])
    scurves['demolition'] = demolition_scurve
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves
                              })
    result = s.calc_demolition(tek)
    expected = pd.Series([0.0,0.0,0.0,0.6,0.2], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


#TODO: can this value be negative or above 1? 
def test_calc_max_measure_share(default_params):
    s = SharesPerCondition(**default_params)
    demolition_shares = pd.Series([0.0,0.1,0.2])
    never_share = 0.2
    result = s._calc_max_measure_share(demolition_shares, never_share)
    expected = pd.Series([0.8,0.7,0.6])
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure_or_renovation_with_renovation(default_params, tek, period):
    """
    Test that the method runs for the building_condition 'renovation' and returns the 
    expected result when ran with valid input (default_params).

    The method should return the scurve_per_model year for the given building condition, 
    or the scurve rate should be replaced by the 'measure_limit' if the scurve rate exceeds
    the measure_limit for a given year. In this test, the measure_limit is 0,55 in 2014, 
    while the given scurve_rate is 0,6. Thus this is the only value that should be changed.
    """
    s = SharesPerCondition(**default_params)
    result = s._calc_small_measure_or_renovation(tek, BuildingCondition.RENOVATION)
    expected = pd.Series([0.2,0.3,0.4,0.5,0.55], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure_or_renovation_with_small_measure(default_params, 
                                                             tek, 
                                                             small_measure_scurve, 
                                                             period):
    """
    Test that the method runs for the building_condition 'small_measure' and returns the 
    expected result when ran with valid input (default_params).

    The method should return the scurve_per_model year for the given building condition, 
    or the scurve rate should be replaced by the 'measure_limit' if the scurve rate exceeds
    the measure_limit for a given year. In this test, the scurve rates should not exceed the
    measure_limit for any years, and no values should be changed.
    """
    s = SharesPerCondition(**default_params)
    result = s._calc_small_measure_or_renovation(tek, BuildingCondition.SMALL_MEASURE)
    expected = pd.Series(small_measure_scurve.values, index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure_or_renovation_invalid_building_condition(default_params, tek):
    """
    Test that the method raises a ValueError if the given building_condition isn't
    'small_measure' or 'renovation'.
    """
    s = SharesPerCondition(**default_params)

    with pytest.raises(ValueError, match=re.escape('Invalid building_condition')):
        s._calc_small_measure_or_renovation(tek, 'not a building_condition')


def test_calc_small_measure_or_renovation_with_tek_construction_year_in_period(default_params,
                                                                               scurves,
                                                                               period):
    """
    Test that the share is 0 in years before and including the year the building was constructed, 
    when ran with a TEK that has construction year within in the model period.

    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    small_measure_scurve = generate_scurve_series([0.1,0.2,0.3,0.4,0.5],
                                                  [1,2,3,4,5])
    demolition_scurve = generate_scurve_series([0.6,0.8,0.9,0.9,0.9],
                                               [1,2,3,4,5])
    scurves['small_measure'] = small_measure_scurve
    scurves['demolition'] = demolition_scurve
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves
                              })
    result = s._calc_small_measure_or_renovation(tek, BuildingCondition.SMALL_MEASURE)
    expected = pd.Series([0,0,0,0.1,0.2], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_renovation(default_params, tek, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_renovation(tek)
    expected = pd.Series([0.2,0.3,0.4,0.25,0.05], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_renovation_set_shares_to_zero(default_params, tek, never_shares, period):
    """
    Test that the share value is set to 0 in years where the total share for doing 
    a small measure exceeds the measure limit. In other words, when the calculated
    share for doing a renovation is a negative value. 

    To produce this scenario the measure_limit is reduced below the calculated total 
    share for small measures. This can is done by increasing the never_share, which is
    used in the measure_limit calculation. In this test, this results in a negative share
    value for 2014, which then is set to 0. 
    """
    never_shares['renovation'] = 0.2
    s = SharesPerCondition(**{**default_params,
                              'never_shares':never_shares})
    result = s.calc_renovation(tek)
    expected = pd.Series([0.2,0.3,0.3,0.1,0.0], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_renovation_with_tek_construction_year_in_period(default_params,
                                                              scurves,
                                                              period):
    """
    Test that the share is 0 in years before and including the year the building was constructed, 
    when ran with a TEK that has construction year within in the model period.
    
    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    scurves = {
        'small_measure': generate_scurve_series(values = [0.1,0.2,0.3,0.4,0.5], 
                                                ages = [1, 2, 3, 4, 5]),
        'renovation': generate_scurve_series(values = [0.2,0.3,0.4,0.5,0.6],
                                             ages = [1, 2, 3, 4, 5]),
        'demolition': generate_scurve_series(values = [0.3,0.4,0.5,0.6,0.7],
                                             ages = [1, 2, 3, 4, 5])
    }
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves
                              })
    result = s.calc_renovation(tek)
    expected = pd.Series([0,0,0,0.2,0.3], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_renovation_and_small_measure(default_params, tek, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_renovation_and_small_measure(tek)
    expected = pd.Series([0.0,0.0,0.0,0.25,0.5], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_renovation_and_small_measure_with_tek_construction_year_in_period(default_params,
                                                                                scurves,
                                                                                never_shares,
                                                                                period):
    """
    Test that the share is 0 in years before and including the year the building was constructed, 
    when ran with a TEK that has construction year within in the model period.
    
    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    scurves = {
        'small_measure': generate_scurve_series(values = [0.1,0.2,0.3,0.4,0.5], 
                                                ages = [1, 2, 3, 4, 5]),
        'renovation': generate_scurve_series(values = [0.2,0.3,0.4,0.5,0.6],
                                             ages = [1, 2, 3, 4, 5]),
        'demolition': generate_scurve_series(values = [0.3,0.4,0.5,0.6,0.7],
                                             ages = [1, 2, 3, 4, 5])
    }
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves,
                              'never_shares': never_shares
                              })
    result = s.calc_renovation_and_small_measure(tek)
    expected = pd.Series([0.0,0,0,0,0], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure(default_params, tek, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_small_measure(tek)
    expected = pd.Series([0.1,0.2,0.3,0.15,0.0], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure_with_tek_construction_year_in_period(default_params,scurves,period):
    """
    Test that the share is 0 in years before and including the year the building was constructed, 
    when ran with a TEK that has construction year within in the model period.
    
    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    scurves = {
        'small_measure': generate_scurve_series(values = [0.1,0.2,0.3,0.4,0.5], 
                                                ages = [1, 2, 3, 4, 5]),
        'renovation': generate_scurve_series(values = [0.2,0.3,0.4,0.5,0.6],
                                             ages = [1, 2, 3, 4, 5]),
        'demolition': generate_scurve_series(values = [0.3,0.4,0.5,0.6,0.7],
                                             ages = [1, 2, 3, 4, 5])
    }
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves
                              })
    result = s.calc_small_measure(tek)
    expected = pd.Series([0.0,0,0,0.1,0.2], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_original_condition(default_params, tek, period):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_original_condition(tek)
    expected = pd.Series([0.7,0.4,0.1,0.05,0.05], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_small_measure_with_tek_start_year_in_period(default_params,scurves,period):
    """
    Test that the share is 0 in years before the start year of the TEK, when ran with a TEK that has
    start year after the model start year.
    
    When changing the construction_year of the given TEK, the ages included in the scurves used in 
    the method must also be adjusted to match with the specified construction_year and model period. 
    If not, the ValueError in _scurve_per_year will be raised. 
    """
    tek = 'TEK07'
    tek_list = [tek]
    tek_params = {tek: TEKParameters(tek, 2012, 2011, 2013)}
    scurves = {
        'small_measure': generate_scurve_series(values = [0.1,0.2,0.3,0.4,0.5], 
                                                ages = [1, 2, 3, 4, 5]),
        'renovation': generate_scurve_series(values = [0.2,0.3,0.4,0.5,0.6],
                                             ages = [1, 2, 3, 4, 5]),
        'demolition': generate_scurve_series(values = [0.3,0.4,0.5,0.6,0.7],
                                             ages = [1, 2, 3, 4, 5])
    }
    s = SharesPerCondition(**{**default_params,
                              'tek_list': tek_list,
                              'tek_params': tek_params,
                              'scurves': scurves
                              })
    result = s.calc_original_condition(tek)
    expected = pd.Series([0.0,1.0,1.0,0.4,0.4], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


@pytest.mark.parametrize('building_condition, expected',
                        [(BuildingCondition.SMALL_MEASURE, 
                          pd.Series([0.1,0.2,0.3,0.15,0.0], index= [2010,2011,2012,2013,2014])),
                         (BuildingCondition.RENOVATION, 
                          pd.Series([0.2,0.3,0.4,0.25,0.05], index= [2010,2011,2012,2013,2014])),
                         (BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 
                          pd.Series([0.0,0.0,0.0,0.25,0.5], index= [2010,2011,2012,2013,2014])),
                         (BuildingCondition.DEMOLITION, 
                          pd.Series([0.0,0.1,0.2,0.3,0.4], index= [2010,2011,2012,2013,2014])),
                         (BuildingCondition.ORIGINAL_CONDITION, 
                          pd.Series([0.7,0.4,0.1,0.05,0.05], index= [2010,2011,2012,2013,2014]))                                                                            
                          ])
def test_calc_shares(default_params, tek, building_condition, expected):
    """
    Test that the method returns the expected result when ran with valid input (default_params).
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_shares(building_condition, tek)
    pd.testing.assert_series_equal(result,expected, check_names=False)


def test_calc_shares_require_valid_building_condition(default_params):
    """
    Raise ValueError when an invalid BuildingCondition is given.
    """
    s = SharesPerCondition(**default_params)
    with pytest.raises(ValueError, match=re.escape('Invalid building condition')):
        s.calc_shares('not a condition', 'TEK01')


def test_calc_shares_all_teks(default_params):
    """
    Test that the method calls the correct methods according to the given params.
    """
    shares = SharesPerCondition(**default_params)
    shares.calc_shares = MagicMock(side_effect=[1, 2])
    shares_all_teks = shares.calc_shares_all_teks(BuildingCondition.DEMOLITION, ['TEK01', 'TEK02'])

    shares.calc_shares.assert_any_call(BuildingCondition.DEMOLITION, 'TEK01')
    shares.calc_shares.assert_any_call(BuildingCondition.DEMOLITION, 'TEK02')

    assert shares_all_teks == {'TEK01':1, 'TEK02':2}


def test_calc_shares_all_conditions_teks(default_params):
    """
    Test that the method calls the correct methods according to the given params.
    """
    shares = SharesPerCondition(**default_params)
    shares.calc_shares_all_teks = MagicMock(side_effect=lambda x,y: x + ','.join(y))
    shares_condition = shares.calc_shares_all_conditions_teks(['TEK01', 'TEK02'])

    shares.calc_shares_all_teks.assert_called_with(BuildingCondition.DEMOLITION, ['TEK01', 'TEK02'])

    assert shares_condition == {BuildingCondition.ORIGINAL_CONDITION:'original_conditionTEK01,TEK02',
                                BuildingCondition.SMALL_MEASURE:'small_measureTEK01,TEK02',
                                BuildingCondition.RENOVATION:'renovationTEK01,TEK02',
                                BuildingCondition.RENOVATION_AND_SMALL_MEASURE:'renovation_and_small_measureTEK01,TEK02',
                                BuildingCondition.DEMOLITION:'demolitionTEK01,TEK02'} 


def test_control_shares(default_params):
    """
    Test that the defined criterias in _control_shares are passed, when ran with valid input data (default_params).
    """
    s = SharesPerCondition(**default_params)
    s._control_shares()
