import polars as pl
from typing import Optional, Union


def yearly_aggregated_elhub_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregate Elhub data by year, summing the 'forbruk_kwh' column.
    Args:
        df (pl.DataFrame): DataFrame containing Elhub data with 'forbruk_kwh' column.
    Returns:
        pl.DataFrame: DataFrame with yearly aggregated 'forbruk_kwh' values.
    """
    df_stacked_year = df.with_columns(
	pl.col("lokal_dato_tid_start").dt.truncate("1y").alias("lokal_dato_tid_start")
).group_by(
	["lokal_dato_tid_start", "kommune_nr", "kommune_navn", "naeringshovedomraade_kode", "naering_kode", "naeringshovedgruppe_kode", "prisomraade"]
).agg(
	pl.col("forbruk_kwh").sum().alias("forbruk_kwh")
)
    return df_stacked_year


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


def ebm_energy_use_geographical_distribution(
        df1: pl.DataFrame,
        dict_df2: dict[str, pl.DataFrame],
        years: list[int],
        building_category: Union[str, list[str]],
        output_format: bool = False) -> dict[str, pl.DataFrame]:
    """ Function to geographically distribute energy use data based on building category and energy source.

    Args:
        df1 (pl.DataFrame): DataFrame containing energy use data with columns for building group and energy source.
        dict_df2 (dict[str, pl.DataFrame]): Dictionary of DataFrames with mean yearly forbruk and distribution keys per kommune.
        years (list[int]): List of years pertaingning to the projected energy use data.
        building_category (Union[str, list[str]]): Building category or categories to filter the DataFrame.
        output_format (bool, optional): _description_. Defaults to False.

    Returns:
        dict[str, pl.DataFrame]: _description_
    """
    if isinstance(building_category, str):
        building_category = [building_category]
    # Define year columns as strings
    years_column = [str(year) for year in years]

    df = df1.filter(
        (pl.col('building_group').is_in(building_category)) &
        (pl.col('energy_source').is_in(['Elektrisitet', 'Electricity'])))
    
    for category in building_category:
        df_category = df.filter(pl.col('building_group') == category)
        multiplied = pl.DataFrame({
            year: df_category[year] * dict_df2[category][year]
            for year in years_column
            })

        # Combine back with kommune_nr or relevant index
        kommune = dict_df2[category].select(["kommune_nr", "kommune_navn", "mean_yearly_forbruk_gwh"])
        dict_df2[category + "_energibruk"] = kommune.hstack(multiplied)
        dict_df2[category + "_fordelingsnøkler"] = dict_df2.pop(category)

    return dict_df2

