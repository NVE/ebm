import typing
import pytest
import re
import pandas as pd

from ebm.model.data_classes import TEKParameters
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange


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
    Test that the method returns the expected result when valid input (default_params) is given.
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
    Test that the method returns the expected result when valid input (default_params) is given.
    """
    s = SharesPerCondition(**default_params)
    result = s.calc_demolition(tek)
    expected = pd.Series([0.0,0.1,0.2,0.3,0.4], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)


def test_calc_demolition_tek_construction_year_in_period(default_params, period, scurves):
    """
    Test that the method adjusts the calculation method when the construction year of the given
    TEK is within the given 'period'. 

    The adjustment is that:
    - the share should be set to 0 in model years before and during the construciton year of the TEK.
    - the share should be set to the S-curve rate of the given model year if that year corresponds to 
      the year after the building was constructed.
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


def test_calc_small_measure_or_renovation(default_params, tek, period):
    """
    Test that the method returns the expected result when valid input (default_params) is given.
    """
    s = SharesPerCondition(**default_params)
    result = s._calc_small_measure_or_renovation(tek, BuildingCondition.RENOVATION)
    expected = pd.Series([0.2,0.3,0.4,0.5,0.55], index= period.year_range)
    expected.index.name = 'year'
    pd.testing.assert_series_equal(result,expected)




