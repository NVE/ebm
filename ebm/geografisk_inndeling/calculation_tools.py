import polars as pl
from typing import Optional


def df_commune_mean(
        df: pl.DataFrame, 
        years: list[int],
        buildingkategory: Optional[str] = None
)-> pl.DataFrame:
    """
    Sum the values in the 'forbruk_kwh' column and convert it to GWh or MWh,
    then calculate the mean yearly forbruk per kommune.

    Args:
        df (pl.DataFrame): DataFrame containing Elhub data with 'forbruk_kwh' column.
        years (list[int]): List of years to filter the DataFrame.
        buildingkategory (str, optional): Building category to filter by. 
            If 'Fritidsboliger', use MWh instead of GWh. Defaults to None.

    Returns:
        pl.DataFrame: DataFrame with the average yearly forbruk per kommune in GWh or MWh.
    """

    # Extract year from timestamp
    df = df.with_columns(
        pl.col("lokal_dato_tid_start").dt.year().alias("year")
    )

    # Filter the DataFrame for the specified years
    df_filtered = df.filter(
        pl.col("year").is_in(years)
    )

    # Decide units based on building category
    unit_divisor = 1_000 if buildingkategory == "Fritidsboliger" else 1_000_000
    value_col = "yearly_forbruk_mwh" if buildingkategory == "Fritidsboliger" else "yearly_forbruk_gwh"
    mean_col = f"mean_{value_col}"

    # Group and aggregate yearly usage per kommune
    df_yearly = (
        df_filtered
        .group_by(["kommune_nr", "kommune_navn", "year"])
        .agg(
            (pl.col("forbruk_kwh").sum() / unit_divisor).alias(value_col)
        )
    )

     # Calculate mean across years
    df_mean_per_kommune = (
        df_yearly
        .with_columns(
            pl.col(value_col).cast(pl.Float64)
        )
        .group_by(["kommune_nr", "kommune_navn"])
        .agg(
            pl.col(value_col).mean().alias(mean_col)
        )
    )

    return df_mean_per_kommune


def df_total_consumption_buildingcategory(
        df: pl.DataFrame
)-> pl.DataFrame:
    """
    Sum the values in the 'forbruk_kwh' column and convert it to GWh or MWh for total forbruk per kommune,
    for each building category boliger, fritidsboliger, and yrkesbygg.

    Args:
        df (pl.DataFrame): DataFrame containing Elhub data with 'forbruk_kwh' column.

    Returns:
        pl.DataFrame: DataFrame with the total forbruk per kommune in GWh or MWh.
    """


    df_total = (
        df.select(pl.col("mean_yearly_forbruk_gwh").sum()).to_numpy()
    )
    return df_total


def df_factor_calculation(
        dict_df1: dict[str, pl.DataFrame], 
        dict_df2: dict[str, pl.DataFrame], 
        years: list[int]) -> dict[str, pl.DataFrame]:
    """
    Calculate factors for each year based on the mean yearly forbruk per kommune.

    Args:
        dict_df1 (dict[str, pl.DataFrame]): Dictionary of DataFrames with mean forbruk per kommune.
        dict_df2 (dict[str, pl.DataFrame]): Dictionary of DataFrames with total forbruk per kommune.
        years (list[int]): List of years to calculate factors for.

    Returns:
        dict[str, pl.DataFrame]: Dictionary with DataFrames containing factors for each year per kommune.
    """
    # Define year columns as strings
    years_column = [str(year) for year in years]
    dfs_factors = {}
    for df_name, df in dict_df1.items():
        df = df.with_columns(
            [pl.lit(None).alias(year) for year in years_column]
        )
        
        # Remove unknown value row
        unknown_value = df.filter(pl.col("kommune_nr") == "0000")[["mean_yearly_forbruk_gwh"]].to_numpy()[0][0]
        df = df.filter(pl.col("kommune_nr") != "0000")
        
        # Calculate factors
        df = df.with_columns(
                 (pl.col("mean_yearly_forbruk_gwh")/(dict_df2[df_name][0][0] - unknown_value)).alias(year)
                 for year in years_column
                 if year != "mean_yearly_forbruk_gwh" 
                 )
        
        dfs_factors[df_name] = df

    return dfs_factors