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

    assert year_range[0] == pd.Index(data=[2010])
    expected_index = pd.Index(data=[2010, 2011], name='year')
    pd.testing.assert_index_equal(year_range[0:2], expected_index)
    assert result.name == 'year'

    pd.testing.assert_index_equal(YearRange(2010, 2011).to_index(name='foo'),
                                  pd.Index(data=[2010, 2011], name='foo'))

def test_year_range_cross_join():
    df = pd.DataFrame(data=[('a', 1), ('b', 2)], columns=['L', 'N'])
    result = YearRange(2010, 2012).cross_join(df)

    expected = pd.DataFrame(
        data=[('a', 1, 2010), ('a', 1, 2011), ('a', 1, 2012),
              ('b', 2, 2010), ('b', 2, 2011), ('b', 2, 2012)], columns=['L', 'N', 'year'])

    pd.testing.assert_frame_equal(result, expected)


def test_year_range_from_series():
    s = pd.Series([1, 2, 3, 4], pd.Index([2001, 2002, 2003, 2004], name='year'))
    assert YearRange(2001, 2004) == YearRange.from_series(s), 'YearRange not loaded correctly from index.level==year'

    s = pd.Series([2010, 2011, 2012, 2013], name='year', index=pd.Index([2004, 2008, 2012, 2016], name='leap years'))
    assert YearRange(2010, 2013) == YearRange.from_series(s), 'YearRange not loaded correctly from index.level==year'


