import sys

import pandas as pd
import pytest
from loguru import logger

from ebm.geografisk_inndeling.data_loader import load_energy_use2

from tests.integration.test_energy_use_integration import (kalibrert_database_manager,
                                                           expected_building_group_energy_use,
                                                           cwd_ebm_data)


def test_load_energy_use(kalibrert_database_manager):
    result = load_energy_use2(kalibrert_database_manager.file_handler.input_directory)
    expect_columns = ['building_group', 'energy_product', 'year']
    result = result[expect_columns + ['kwh']].groupby(by=expect_columns).sum()

    expected = pd.DataFrame(expected_building_group_energy_use)
    expected.index.names = expect_columns

    df = pd.merge(left=result, right=expected, suffixes=('_result', '_expected'), on=expect_columns, how='outer')

    df_diff = df[df['kwh_result'] != df['kwh_expected']]

    for i, r in df_diff.iterrows():
        logger.error(f'Error in row {i} expected: {r[1]} was: {r[0]}')

    assert df_diff.empty, 'Expected no differences between the dataframes result and expected'


if __name__ == "__main__":
    pytest.main([sys.argv[0]])
