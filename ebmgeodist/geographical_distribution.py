from pathlib import Path
from ebmgeodist.initialize import NameHandler
from ebmgeodist.data_loader import load_elhub_data, load_energy_use
from ebmgeodist.calculation_tools import df_geography_mean, df_total_consumption_buildingcategory,\
      df_factor_calculation, yearly_aggregated_elhub_data, ebm_energy_use_geographical_distribution
from ebmgeodist.initialize import create_output_directory, get_output_file
from ebmgeodist.spreadsheet import make_pretty
import gc
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from collections.abc import Iterable



def prepare_elhub_data(elhub_years: list[int], step: str) -> pl.DataFrame:
    input_file = get_output_file("input/yearly_aggregated_elhub_data.parquet")

    if step == "azure":
        aggregated_years = []
        for year in elhub_years:
                df_year = load_elhub_data(year_filter=year, columns=True)
                df_year_agg = yearly_aggregated_elhub_data(df_year)
                aggregated_years.append(df_year_agg)

                del df_year
                gc.collect()
                logger.info(f"📍Loaded and aggregated Elhub data for year: {year}"
        )
        
        df_stacked_year = pl.concat(aggregated_years)
        
        # Save the stacked DataFrame to a Parquet file with a timestamp
        norwegian_time = datetime.now(ZoneInfo("Europe/Oslo"))
        timestamp = norwegian_time.strftime("%Y%m%d_%H%M%S")
        output_file = input_file.parent / f"yearly_aggregated_elhub_data_{timestamp}.parquet"
        df_stacked_year.write_parquet(output_file, compression="zstd")
        logger.info(f"📍New stacked Elhub data with a timestamp of the format YearMonthDay_HourMinutesSeconds:{timestamp} saved in: {output_file.name}")
        return df_stacked_year
    else:
        create_output_directory(filename=input_file)
        df_stacked_year = pl.read_parquet(input_file)
        logger.info(f"📍Loaded Elhub data from: {input_file.name}")
    return df_stacked_year

def get_household_data(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        (pl.col("naeringshovedomraade_kode").is_in(["XX"])) |
        (pl.col("naeringshovedgruppe_kode").is_in(["68.2"]))
    )


def get_holiday_home_data(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(pl.col("naeringshovedomraade_kode").is_in(["XY"]))


def get_commercial_data(df: pl.DataFrame) -> pl.DataFrame:
    # single_codes = ["35.1", "35.2"] # NACE overview document in Sharepoint under "Energibruk"
    single_codes = [] # NACE overview document in Sharepoint under "Energibruk"
    # USE THIS! ranges = [{"36" : "39"}, {"45": "61"}, {"64": "99"}] # NACE overview document in Sharepoint under "Energibruk"
    ranges = [{"45": "61"}, {"64": "99"}] # NACE overview document in Sharepoint under "Energibruk"


    filter_set: set[str] = set(single_codes)
    for r in ranges:
        for start, end in r.items():
            filter_set.update({str(i) for i in range(int(start), int(end) + 1)})
        
    return df.filter(
    pl.col("naering_kode").is_in(filter_set)
    | pl.col("naeringshovedgruppe_kode").is_in(filter_set)
)


def calculate_elhub_factors(df_stacked: pl.DataFrame,
                            normalized: list[str],
                            elhub_years: list[int], 
                            year_cols: Iterable[int],
                            level: str
                            ) -> dict[str, pl.DataFrame]:
    """
    Calculate Elhub factors for different building categories.
    Args:
        df_stacked (pl.DataFrame): Stacked Elhub data.
        normalized (list[str]): List of building categories to include.
        elhub_years (list[int]): List of years for Elhub aggregation.
        year_cols: Columns representing the years in the output format.
    Returns:
        dict: Dictionary containing DataFrames for each building category with calculated factors.
    """
    elhub_dataframes = {}

    if NameHandler.COLUMN_NAME_RESIDENTIAL in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_RESIDENTIAL] = get_household_data(df_stacked)
    if NameHandler.COLUMN_NAME_HOLIDAY_HOME in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_HOLIDAY_HOME] = get_holiday_home_data(df_stacked)
    if NameHandler.COLUMN_NAME_NON_RESIDENTIAL in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_NON_RESIDENTIAL] = get_commercial_data(df_stacked)

    if not elhub_dataframes:
        raise ValueError("Ingen gyldig bygningskategori valgt.")

    dfs_mean = {name: df_geography_mean(df, elhub_years, level=level) for name, df in elhub_dataframes.items()}
    dfs_sum = {name: df_total_consumption_buildingcategory(df) for name, df in dfs_mean.items()}
    logger.info("📍Calculated mean and total consumption.")

    return df_factor_calculation(dfs_mean, dfs_sum, year_cols, level=level)


def load_dh_factors(
        normalized: list[str],
        year_cols: Iterable[int],
        ) -> dict[str, pl.DataFrame]:
    input_file = get_output_file("input/dh_distribution_keys.xlsx")
    df = pl.from_pandas(pd.read_excel(input_file))
    years_column = [str(year) for year in year_cols]

    factor_dict = {}
    for category in [NameHandler.COLUMN_NAME_RESIDENTIAL, NameHandler.COLUMN_NAME_NON_RESIDENTIAL]:
        if category in normalized:
            value_col = "bolig" if category == NameHandler.COLUMN_NAME_RESIDENTIAL else "yrkesbygg"
            base_df = df.select("kommune_nr", "kommune_navn", value_col)
            extended = base_df.with_columns([pl.col(value_col).alias(year) for year in years_column])
            factor_dict[category] = extended

    logger.info("📍Loaded district heating distribution factors.")
    return factor_dict

def load_wood_factors(
        year_cols: Iterable[int],
        ) -> dict[str, pl.DataFrame]:
    input_file = get_output_file("input/fuelwood_distribution_keys.xlsx")
    df = pl.from_pandas(pd.read_excel(input_file))
    years_column = [str(year) for year in year_cols]
    factor_dict = {}
    value_col = "bolig"
    base_df = df.select("kommune_nr", "kommune_navn", value_col)
    extended = base_df.with_columns([pl.col(value_col).alias(year) for year in years_column])
    factor_dict[NameHandler.COLUMN_NAME_RESIDENTIAL] = extended

    logger.info("📍Loaded fuelwood distribution factors.")
    return factor_dict

def log_distribution_strategy(
        energy_product: str,
        category: str,
        method: str,
        )-> None:
    logger.warning(f"Using {method} distribution key for {energy_product} in {category}.")


def get_distribution_factors(
        energy_product: str,
        normalized: list[str],
        elhub_years: list[int],
        step: str,
        year_cols: Iterable[int],
        level: str,
        ) -> dict[str, pl.DataFrame]:
    if level == "pricearea" and energy_product in ["dh", "fuelwood", "fossilfuel"]:
        unsupported_categories = [
            category for category in normalized
            if not (
                energy_product in ["fuelwood", "fossilfuel"] 
                and category == NameHandler.COLUMN_NAME_HOLIDAY_HOME
            )
        ]
    
        if unsupported_categories:
            logger.error(
                f"Price area level is currently only calculated directly from Elhub. "
                f"{energy_product} with categories {unsupported_categories} still uses municipal input keys."
            )
    if energy_product == "electricity":
        df_stacked = prepare_elhub_data(elhub_years, step)
        return calculate_elhub_factors(df_stacked, normalized, elhub_years, year_cols, level)
    elif energy_product == "dh":
        return load_dh_factors(normalized, year_cols)
    elif energy_product in ["fuelwood", "fossilfuel"]:
        dfs_factors = {}
        if NameHandler.COLUMN_NAME_HOLIDAY_HOME in normalized:
                 log_distribution_strategy(energy_product, NameHandler.COLUMN_NAME_HOLIDAY_HOME, "Elhub")
                 df_stacked = prepare_elhub_data(elhub_years, step)
                 electricity_factors = calculate_elhub_factors(
                    df_stacked, 
                    NameHandler.COLUMN_NAME_HOLIDAY_HOME, 
                    elhub_years, 
                    year_cols, 
                    level=level,
                    )   
                 dfs_factors.update(electricity_factors)
        if NameHandler.COLUMN_NAME_RESIDENTIAL in normalized:
            wood_factors = load_wood_factors(year_cols)
            dfs_factors[NameHandler.COLUMN_NAME_RESIDENTIAL] = wood_factors[NameHandler.COLUMN_NAME_RESIDENTIAL]
        if not dfs_factors:
            raise ValueError(f"Invalid combination of building categories for energy product '{energy_product}': {normalized}")
        return dfs_factors
    else:
        raise ValueError(f"Unknown energy product: {energy_product}")



def export_distribution_to_excel(
        dfs: dict[str, pl.DataFrame],
          output_file: Path,
          ) -> None:
    create_output_directory(filename=output_file)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, pl_df in dfs.items():
            if "kommune_nr" in pl_df.columns:
                pl_df = pl_df.with_columns(pl.col("kommune_nr").cast(pl.Utf8).str.zfill(4)).sort("kommune_nr")
            elif "prisomraade" in pl_df.columns:
                pl_df = pl_df.sort("prisomraade")
            
            df_export = pl_df.to_pandas()
            df_export.to_excel(writer, sheet_name=sheet_name, index=False)
    make_pretty(output_file)
    logger.info(f"📁 Wrote results to {output_file}")


def geographical_distribution(
    elhub_years: list[int],
    energy_product: str = None,
    building_category: str | list[str] = None,
    step: str  = None,
    output_format: bool = False,
    level: str = "municipal"
) -> Path:
    """
    Calculate and export energy use distribution based on Elhub or district heating data.

    Args:
        elhub_years (list[int]): Years to include in Elhub aggregation.
        energy_product (str): 'electricity' or 'district heating'.
        building_category (str): e.g. 'residential', 'non-residential'.
        step (str): Optional step for Elhub ('azure' or 'local').
        output_format (bool): Whether to use narrow (2020, 2050) or wide (2020–2050) format.

    Returns:
        Path: Path to the generated Excel file.
    """
    # Normalize building category into a list
    normalized = NameHandler.normalize_to_list(building_category)

    if isinstance(normalized, str):
        normalized = [normalized]

    year_cols = (2020, 2050) if output_format else range(2020, 2051)

    df_ebm = pl.from_pandas(load_energy_use())
    

    dfs_factors = get_distribution_factors(energy_product, normalized, elhub_years, step, year_cols, level=level)
    
    dfs_distributed = ebm_energy_use_geographical_distribution(
        df_ebm,
        dfs_factors,
        year_cols,
        energy_product=energy_product,
        building_category=normalized
    )
    category_filename = "_".join(
        building_category
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        for building_category in normalized
    )
    output_file = get_output_file(
        f"output/{energy_product}_use_{category_filename}_{level}.xlsx"
    )

    export_distribution_to_excel(dfs_distributed, output_file)
    return output_file

if __name__ == "__main__":
    pass
