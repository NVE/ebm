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


def filter_energy_data(
    df: pl.DataFrame,
    building_categories: list[str],
    energy_types: list[str]
) -> pl.DataFrame:
    """Filter the dataframe by building group and energy source."""
    return df.filter(
        (pl.col("building_group").is_in(building_categories)) &
        (pl.col("energy_source").is_in(energy_types))
    )


def distribute_energy_use_for_category(
    df_category: pl.DataFrame,
    dist_df: pl.DataFrame,
    years_column: list[str],
    category: str,
    energitype: str
) -> tuple[str, pl.DataFrame, str, pl.DataFrame]:
    """
    Multiply the energy use with distribution factors and return two named outputs:
    - Energibruk per kommune
    - Fordelingsnøkler
    """
    multiplied = pl.DataFrame({
        year: df_category[year] * dist_df[year]
        for year in years_column
    })

    kommune_cols = ["kommune_nr", "kommune_navn"]
    if energitype == "strom" and "mean_yearly_forbruk_gwh" in dist_df.columns:
        kommune_cols.append("mean_yearly_forbruk_gwh")

    kommune_info = dist_df.select(kommune_cols)
    energibruk_df = kommune_info.hstack(multiplied)

    return (
        f"{category}_energibruk", energibruk_df,
        f"{category}_fordelingsnøkler", dist_df
    )


def ebm_energy_use_geographical_distribution(
    df_energy_use: pl.DataFrame,
    distribution_factors: dict[str, pl.DataFrame],
    years: list[int],
    energitype: str,
    building_category: Union[str, list[str]],
) -> dict[str, pl.DataFrame]:
    """
    Geographically distribute energy use across municipalities by category and energy source.
    """

    if isinstance(building_category, str):
        building_category = [building_category]

    years_column = [str(year) for year in years]

    # Define mapping from energitype to column values
    energy_type_map = {
        "strom": ['Elektrisitet', 'Electricity'],
        "fjernvarme": ['DH', 'Fjernvarme', 'District Heating'],
        "ved": ['Ved', 'Wood', 'Bio']
    }

    if energitype not in energy_type_map:
        raise ValueError(f"Ukjent energitype: {energitype}")

    # Filter data for selected energy type and categories
    df_filtered = filter_energy_data(df_energy_use, building_category, energy_type_map[energitype])

    result = {}

    for category in building_category:
        if category not in distribution_factors:
            raise KeyError(f"Mangler fordelingsnøkler for kategori: {category}")

        df_cat = df_filtered.filter(pl.col("building_group") == category)
        dist_df = distribution_factors[category]
        energibruk_key, energibruk_df, fordelingsnokkler_key, fordelingsnokkler_df = distribute_energy_use_for_category(
            df_cat, dist_df, years_column, category, energitype
        )

        result[energibruk_key] = energibruk_df.with_columns(pl.lit("GWh").alias("Units"))
        result[fordelingsnokkler_key] = (
            fordelingsnokkler_df.drop(category) if energitype == "fjernvarme"
            else fordelingsnokkler_df
        )

    return result