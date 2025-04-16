import pandas as pd
import pytest

from ebm.model.column_operations import explode_column_alias


def test_explode_column_alias():
    df = pd.DataFrame({'category': ['A', 'B', 'default']})

    result = explode_column_alias(df, column='category', values=['A', 'B'], alias='default')
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category', values=['A', 'B'])
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category')
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category', de_dup_by=['category'])
    assert result.category.to_list() == ['A', 'B']



if __name__ == '__main__':
    pytest.main()
