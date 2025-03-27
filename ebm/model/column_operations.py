from typing import List

import pandas as pd

from ebm.model.building_category import BuildingCategory


def explode_building_category_column(df: pd.DataFrame, unique_columns: List[str]) -> pd.DataFrame:
    """
        Explodes the 'building_category' column in the DataFrame into multiple columns based on residential and non-residential categories.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame containing the 'building_category' column.
        unique_columns : List[str]
            List of columns to use for de-duplication.

        Returns
        -------
        pd.DataFrame
            The DataFrame with exploded 'building_category' columns.
    """
    df = explode_column_alias(df=df, column='building_category',
                              values=[bc for bc in BuildingCategory if bc.is_residential()],
                              alias='residential',
                              de_dup_by=unique_columns)
    df = explode_column_alias(df=df, column='building_category',
                              values=[bc for bc in BuildingCategory if not bc.is_residential()],
                              alias='non_residential',
                              de_dup_by=unique_columns)
    df = explode_column_alias(df=df, column='building_category',
                              values=[bc for bc in BuildingCategory],
                              alias='default',
                              de_dup_by=unique_columns)
    return df


def explode_tek_column(df: pd.DataFrame, unique_columns: List[str],
                       default_tek: None | pd.DataFrame = None) -> pd.DataFrame:
    """
        Explodes the 'TEK' column in the DataFrame into multiple columns based on the provided TEK list.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame containing the 'TEK' column.
        unique_columns : List[str]
            List of columns to use for de-duplication.
        default_tek : Optional[pd.DataFrame], optional
            DataFrame containing default TEK values. If not provided, TEK values are read from 'input/TEK_ID.csv'.

        Returns
        -------
        pd.DataFrame
            The DataFrame with exploded 'TEK' columns.
        """
    # Hvor skal tek_list hentes fra?
    tek_list = pd.read_csv('input/TEK_ID.csv')['TEK'].unique() if default_tek is None else default_tek
    df = explode_column_alias(df=df,
                              column='TEK',
                              values=tek_list,
                              de_dup_by=unique_columns)
    return df


def explode_unique_columns(df: pd.DataFrame, unique_columns: List[str], default_tek: List[str]|None = None) -> pd.DataFrame:
    """
    Explodes 'TEK' and 'building_category' columns in df.


    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the columns to be exploded.
    unique_columns : List[str]
        List of columns to use for de-duplication.
    default_tek : List[str], optional
        List of TEKs to replace default

    Returns
    -------
    pd.DataFrame
        The DataFrame with exploded columns.
    """

    df = explode_tek_column(df, unique_columns, default_tek=default_tek)
    df = explode_building_category_column(df, unique_columns)
    return df


def explode_column_alias(df, column, values=None, alias='default', de_dup_by=None):
    """
    Explodes a specified column in the DataFrame into multiple rows based on provided values and alias.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the column to be exploded.
    column : str
        The name of the column to be exploded.
    values : Optional[List[str]], optional
        List of values to explode the column by. If not provided, unique values from the column excluding the alias are used.
    alias : str, optional
        The alias to be used for default values. Default is 'default'.
    de_dup_by : Optional[List[str]], optional
        List of columns to use for de-duplication. If not provided, no de-duplication is performed.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the exploded column.

    Examples
    --------
    >>> d_f = pd.DataFrame({'category': ['A', 'B', 'default']})
    >>> explode_column_alias(d_f, column='category', values=['A', 'B'], alias='default')
       category
    0         A
    1         B
    2         A
    2         B
    """

    values = values if values is not None else [c for c in df[column].unique().tolist() if c != alias]
    df.loc[:, '_explode_column_alias_default'] = df.loc[:, column] == alias
    df.loc[df[df[column] == alias].index, column] = '+'.join(values)
    df = df.assign(**{column: df[column].str.split('+')}).explode(column)
    if de_dup_by:
        df = df.sort_values(by='_explode_column_alias_default', ascending=True)
        df = df.drop_duplicates(de_dup_by)
    return df.drop(columns=['_explode_column_alias_default'], errors='ignore')
