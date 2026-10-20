import pathlib

import pandas as pd
import pytest
from energibruksmodell.controllers import calculate_energy_use
from energibruksmodell.helpers import as_gwh
from tests.integration.test_energy_use_integration import cwd_ebm_data


# From https://stackoverflow.com/questions/71412691/how-to-output-all-differences-if-pandas-testing-assert-frame-equal-fails
def assert_frame_equal_extended_diff(df1, df2):
    try:
        pd.testing.assert_frame_equal(df1, df2)

    except AssertionError as e:
        # if this was a shape or index/col error, then re-raise
        try:
            pd.testing.assert_index_equal(df1.index, df2.index)
            pd.testing.assert_index_equal(df1.columns, df2.columns)
        except AssertionError:
            raise e

        # if not, we have a value error
        diff = df1 != df2
        diffcols = diff.any(axis=0)
        diffrows = diff.any(axis=1)
        cmp = pd.concat(
            {'left': df1.loc[diffrows, diffcols], 'right': df2.loc[diffrows, diffcols]},
            names=['dataframe'],
            axis=1,
        )

        raise AssertionError(e.args[0] + f'\n\nDifferences:\n{cmp}') from None


def test_custom_building_category_same_as_hotel(cwd_ebm_data):
    """Test that energy use for hotel and the custom building_category motel is equal for the same building code, condition, and purpose."""
    input_directory = pathlib.Path('custom-building_category')
    energy_use = calculate_energy_use(input_directory=input_directory, years=(2020, 2030)).pipe(as_gwh)

    gwh = energy_use[['building_category', 'building_code', 'building_condition', 'year', 'purpose', 'heating_systems', 'heating_system', 'load', 'm2', 'kwh_m2', 'kwh']].pipe(as_gwh)
    grouped = gwh.groupby(by=['building_category', 'year', 'building_code', 'building_condition', 'heating_systems', 'load', 'purpose'])[['GWh']].sum()

    assert_frame_equal_extended_diff(grouped.loc['hotel'], grouped.loc['motel'])


if __name__ == "__main__":
    import sys
    pytest.main([sys.argv[0]])
