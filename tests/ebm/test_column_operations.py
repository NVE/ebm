import pandas as pd
import pytest

from ebm.model.column_operations import explode_column_alias


def test_explode_column_alias():
    df = pd.DataFrame({'category': ['A', 'B', 'default'], 'extra': [0, 1, 2]})

    result = explode_column_alias(df, column='category', values=['A', 'B'], alias='default')
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category', values=['A', 'B'])
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category')
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df, column='category', de_dup_by=['category'])
    assert result.category.to_list() == ['A', 'B']
    assert result.extra.to_list() == [0, 1]

    result = explode_column_alias(df, column='category', values={'default': ['A', 'B']})
    assert result.category.to_list() == ['A', 'B', 'A', 'B']

    result = explode_column_alias(df=pd.DataFrame({'category': ['A', 'B', 'beta', 'alpha', 'default']}),
                                  column='category',
                                  values={'default': ['A', 'B'], 'alpha': ['a'], 'beta': ['b']})

    assert result.category.to_list() == ['A', 'B', 'b', 'a', 'A', 'B']


def test_explode_column_alias_checks_parameter():
    with pytest.raises(ValueError):
        explode_column_alias(df=pd.DataFrame({'not category': ['A', 'B', 'default']}),
                             column='category',
                             values=['A', 'B', 'default'])


def test_explode_column_alias_remove_explode_column_alias_default():
    result = explode_column_alias(df=pd.DataFrame(data={'category': ['A', 'B', 'default'], 'extra': [0, 1, 2]}),
                                  column='category',
                                  values={'default': ['A', 'B']},
                                  de_dup_by=['category'])

    assert result.columns.tolist() == ['category', 'extra']



if __name__ == '__main__':
    pytest.main()
