import pandas as pd
import pytest

from ebm.model.data_classes import YearRange


def test_year_range_basics():
    """
    Test that YearRange sets the correct data and works as an iterator with a length
    """
    years = YearRange(2010, 2012)
    assert years.start == 2010
    assert years.end == 2012

    assert years.year_range == (2010, 2011, 2012,)

    for index, year in enumerate(years):
        assert year == index + 2010

    assert len(years) == 3

    with pytest.raises(ValueError):
        YearRange(start=2050, end=2010)


def test_year_range_subset():
    """
    Test valid year ranges for YearRange including not going beyond last year and raising value error on a
        negative offset.

    """
    assert YearRange(2010, 2050).subset(offset=1, length=4).year_range == (2011, 2012, 2013, 2014)
    assert YearRange(2010, 2050).subset(offset=0, length=1).year_range == (2010, )
    assert YearRange(2010, 2050).subset(offset=1, length=1).year_range == (2011, )
    assert YearRange(2010, 2100).subset(offset=1, length=2).year_range == (2011, 2012, )
    assert YearRange(2010, 2012).subset(offset=0, length=6).year_range == (2010, 2011, 2012, )

    with pytest.raises(ValueError):
        YearRange(2010, 2015).subset(offset=-1, length=6)
    with pytest.raises(ValueError):
        YearRange(2010, 2014).subset(offset=6, length=6)


def test_year_range_to_index():
    year_range = YearRange(2010, 2012)

    result = year_range.to_index()
    assert isinstance(result, pd.Index)
    assert 2010 in result
    assert 2011 in result
    assert 2012 in result

