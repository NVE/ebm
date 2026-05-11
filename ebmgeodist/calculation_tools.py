import polars as pl
from typing import Union
from ebmgeodist.initialize import NameHandler
from loguru import logger

class NoElhubDataError(Exception):
    """Custom exception for cases where no Elhub data is available.
      Raised when no Elhub data is found for the provided years."""

    pass

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


def df_geography_mean(
        df: pl.DataFrame, 
        years: list[int],
        level: str = "municipal"
)-> pl.DataFrame:
    """
    Sum the values in the 'forbruk_kwh' column and convert it to GWh,
    then calculate the mean yearly forbruk per geography level.

    Args:
        df (pl.DataFrame): DataFrame containing Elhub data with 'forbruk_kwh' column.
        years (list[int]): List of years to filter the DataFrame.
        level (str): The geographical level to group by, either "municipal" or "pricearea".

    Returns:
        pl.DataFrame: DataFrame with the average yearly forbruk per geography level in GWh.
    """

    # Extract year from timestamp
    df = df.with_columns(
        pl.col("lokal_dato_tid_start").dt.year().alias("year")
    )
    
    # Filter the DataFrame for the specified years
    df_filtered = df.filter(pl.col("year").is_in(years))
    if df_filtered.is_empty():
        logger.error(f"No data for the provided Elhub years: {years} in the parquet file under the input folder.")
        logger.error("You should update the parquet file with the desired years.")
        raise NoElhubDataError(f"Missing Elhub data for years: {years}")

    if level == "municipal":
        geography_cols = ["kommune_nr", "kommune_navn"]
    elif level == "pricearea":
        geography_cols = ["prisomraade"]
    else:
        raise ValueError(f"Unknown distribution level: {level}.")

    # Group and aggregate yearly usage per geography level
    df_yearly = (
        df_filtered
        .group_by([*geography_cols, "year"])
        .agg(
            (pl.col("forbruk_kwh").sum() / 1_000_000).alias("yearly_forbruk_gwh")
        )
    )

    return (
        df_yearly
        .with_columns(pl.col("yearly_forbruk_gwh").cast(pl.Float64))
        .group_by(geography_cols)
        .agg(pl.col("yearly_forbruk_gwh").mean().alias("mean_yearly_forbruk_gwh"))
        )


def df_total_consumption_buildingcategory(df: pl.DataFrame)-> float:
    return df.select(pl.col("mean_yearly_forbruk_gwh").sum()).item()


def df_factor_calculation(
        dict_df1: dict[str, pl.DataFrame], 
        dict_df2: dict[str, float], 
        years: list[int],
        level: str = "municipal"
) -> dict[str, pl.DataFrame]:
    """
    Calculate factors for each year based on the mean yearly forbruk per geography level.
    Args:
        dict_df1 (dict[str, pl.DataFrame]): Dictionary of DataFrames with mean forbruk per geography level.
        dict_df2 (dict[str, float]): Dictionary of DataFrames with total forbruk per geography level.
        years (list[int]): List of years to calculate factors for.

    Returns:
        dict[str, pl.DataFrame]: Dictionary with DataFrames containing factors for each year per geography level.
    """
    # Define year columns as strings
    years_column = [str(year) for year in years]
    dfs_factors = {}
    for df_name, df in dict_df1.items():
        unknown_value = 0

        if level == "municipal" and "kommune_nr" in df.columns:
            unknown_row = df.filter(pl.col("kommune_nr") == "0000")
            if unknown_row.height > 0:
                unknown_value = unknown_row["mean_yearly_forbruk_gwh"][0]
                df = df.filter(pl.col("kommune_nr") != "0000")
            
        total_consumption = dict_df2[df_name] - unknown_value
        
        df = df.with_columns(
            (pl.col("mean_yearly_forbruk_gwh")/(total_consumption)).alias(year)
            for year in years_column
        )
        
        dfs_factors[df_name] = df

    return dfs_factors


def filter_energy_data(
    df: pl.DataFrame,
    building_categories: list[str],
    energy_product: list[str]
) -> pl.DataFrame:
    """Filter the dataframe by building group and energy source."""
    return df.filter(
        (pl.col("building_group").is_in(building_categories)) &
        (pl.col("energy_source").is_in(energy_product))
    )


def distribute_energy_use_for_category(
    df_category: pl.DataFrame,
    dist_df: pl.DataFrame,
    years_column: list[str],
    category: str,
    energy_product: str
) -> tuple[str, pl.DataFrame, str, pl.DataFrame]:
    """
    Multiply the energy use with distribution factors and return two named outputs:
    - Energibruk per geography level
    - Fordelingsnøkler
    """
    if df_category.height != 1:
        raise ValueError(
            f"Expected exactly one EBM energy use value for {category}/{energy_product}, "
            f"found {df_category.height} rows."
        )
    multiplied = pl.DataFrame({
        year: dist_df[year] * df_category[year][0]
        for year in years_column
    })
    if "kommune_nr" in dist_df.columns:
        geography_cols = ["kommune_nr", "kommune_navn"]
    elif "prisomraade" in dist_df.columns:
        geography_cols = ["prisomraade"]
    else:
        raise ValueError("Distribution factors must contain either 'kommune_nr' or 'prisomraade'.")
    
    if energy_product == "electricity" and "mean_yearly_forbruk_gwh" in dist_df.columns:
        geography_cols.append("mean_yearly_forbruk_gwh")

    geography_info = dist_df.select(geography_cols)
    energibruk_df = geography_info.hstack(multiplied)

    category_map = {
        NameHandler.COLUMN_NAME_RESIDENTIAL: "residential",
        NameHandler.COLUMN_NAME_HOLIDAY_HOME: "holiday_home",
        NameHandler.COLUMN_NAME_NON_RESIDENTIAL: "non_residential"
}

    category = category_map.get(category, category) 


    return (
        f"{category}_{energy_product}", energibruk_df,
        f"{category}_distrb_keys", dist_df
    )


def ebm_energy_use_geographical_distribution(
    df_energy_use: pl.DataFrame,
    distribution_factors: dict[str, pl.DataFrame],
    years: list[int],
    energy_product: str,
    building_category: Union[str, list[str]],
) -> dict[str, pl.DataFrame]:
    """
    Geographically distribute energy use across the geography level by category and energy source.
    """

    if isinstance(building_category, str):
        building_category = [building_category]

    years_column = [str(year) for year in years]

    # Define mapping from energy_product to column values
    energy_product_map = {
        "electricity": ['Elektrisitet', 'Electricity'],
        "dh": ['DH', 'Fjernvarme', 'District Heating'],
        "fuelwood": ['Ved', 'Wood', 'Bio'],
        "fossilfuel": ['Fossil', 'Fossil Fuel']
    }

    if energy_product not in energy_product_map:
        raise ValueError(f"Unknown energy_product: {energy_product}")

    # Filter data for selected energy product and categories
    df_filtered = filter_energy_data(df_energy_use, building_category, energy_product_map[energy_product])

    result = {}
    
    for category in building_category:
        if category not in distribution_factors:
            raise KeyError(f"Missing distribution factors for category: {category}")

        df_cat = df_filtered.filter(pl.col("building_group") == category)
        dist_df = distribution_factors[category]
        energibruk_key, energibruk_df, fordelingsnokler_key, fordelingsnokler_df = distribute_energy_use_for_category(
            df_cat, dist_df, years_column, category, energy_product
        )
        
        result[energibruk_key] = energibruk_df.with_columns(pl.lit("GWh").alias("Units"))
        result[fordelingsnokler_key] = fordelingsnokler_df
        # result[fordelingsnokler_key] = (
        #     fordelingsnokler_df.drop(category) if energy_product == "dh" or (energy_product == "fuelwood" \
        #     and category == NameHandler.COLUMN_NAME_RESIDENTIAL) 
        #     else fordelingsnokler_df
        # )

    return result

if __name__ == "__main__":
    pass