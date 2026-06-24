import pytest

from ebm.cmd.run_calculation import validate_years
from ebm.model.data_classes import YearRange


def test_validate_years_valid():
    result = validate_years(2010, 2050)

    assert isinstance(result, YearRange)
    assert result.start== 2010
    assert result.end== 2050


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (2020, 2020),  # equal
        (2030, 2020),  # start > end
    ],
)
def test_validate_years_start_greater_or_equal(start_year, end_year):
    with pytest.raises(ValueError) as exc:
        validate_years(start_year, end_year)

    assert "greater than end year" in str(exc.value)


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (2009, 2050),
        (1990, 2000),
    ],
)
def test_validate_years_start_too_small(start_year, end_year):
    with pytest.raises(ValueError) as exc:
        validate_years(start_year, end_year)

    assert "minimum start year is 2010" in str(exc.value)


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (2010, 2071),
        (2015, 3000),
    ],
)
def test_validate_years_end_too_large(start_year, end_year):
    with pytest.raises(ValueError) as exc:
        validate_years(start_year, end_year)

    assert "Max end_year year is 2070" in str(exc.value)
