import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from ebmgeodist.initialize import NameHandler
from ebmgeodist.data_loader import load_elhub_data, load_energy_use_from_file, load_energy_use
from ebmgeodist.calculation_tools import df_commune_mean, df_total_consumption_buildingcategory,\
      df_factor_calculation, yearly_aggregated_elhub_data, ebm_energy_use_geographical_distribution
from ebmgeodist.initialize import create_output_directory, get_output_file
from ebmgeodist.spreadsheet import make_pretty
import gc
import polars as pl
import pandas as pd
from loguru import logger
from datetime import datetime
from zoneinfo import ZoneInfo



def prepare_elhub_data(elhub_years: list[int], step: str) -> pl.DataFrame:
    input_file = get_output_file("input/yearly_aggregated_elhub_data.parquet")

    if step == "azure":
        elhub_data = {
            f"df_elhub_{str(year)[-2:]}": load_elhub_data(year_filter=year, columns=True)
            for year in elhub_years
        }
        gc.collect()

        df_stacked = list(elhub_data.values())[0]
        for df in list(elhub_data.values())[1:]:
            df_stacked = df_stacked.vstack(df)

        df_stacked_year = yearly_aggregated_elhub_data(df_stacked)
        
        # Save the stacked DataFrame to a Parquet file with a timestamp
        norwegian_time = datetime.now(ZoneInfo("Europe/Oslo"))
        timestamp = norwegian_time.strftime("%Y%m%d_%H%M%S")
        output_file = input_file.parent / f"yearly_aggregated_elhub_data_{timestamp}.parquet"
        df_stacked_year.write_parquet(output_file, compression="zstd")
        logger.info(f"📍New stacked Elhub data with a timestamp of the format YearMonthDay_HourMinutesSeconds:{timestamp} saved in: {output_file.name}")
    else:
        create_output_directory(filename=input_file)
        df_stacked = pl.read_parquet(input_file)
        logger.info(f"📍Loaded Elhub data from: {input_file.name}")

    return df_stacked

def get_household_data(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        (pl.col("naeringshovedomraade_kode").is_in(["XX"])) |
        (pl.col("naeringshovedgruppe_kode").is_in(["68.2"]))
    )


def get_holiday_home_data(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(pl.col("naeringshovedomraade_kode").is_in(["XY"]))


def get_commercial_data(df: pl.DataFrame) -> pl.DataFrame:
    commercial_list = [{"45": "60"}, {"64": "96"}, "99"]
    filter_list = []

    for item in commercial_list:
        if isinstance(item, dict):
            for start, end in item.items():
                filter_list.extend([str(i) for i in range(int(start), int(end) + 1)])
        else:
            filter_list.append(item)

    return df.filter(pl.col("naering_kode").is_in(filter_list))

def calculate_elhub_factors(df_stacked: pl.DataFrame, normalized: list[str], elhub_years: list[int], year_cols) -> dict:
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

    if NameHandler.COLUMN_NAME_BOLIG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_BOLIG] = get_household_data(df_stacked)
    if NameHandler.COLUMN_NAME_FRITIDSBOLIG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_FRITIDSBOLIG] = get_holiday_home_data(df_stacked)
    if NameHandler.COLUMN_NAME_YRKESBYGG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_YRKESBYGG] = get_commercial_data(df_stacked)

    if not elhub_dataframes:
        raise ValueError("Ingen gyldig bygningskategori valgt.")

    dfs_mean = {name: df_commune_mean(df, elhub_years) for name, df in elhub_dataframes.items()}
    dfs_sum = {name: df_total_consumption_buildingcategory(df) for name, df in dfs_mean.items()}
    logger.info("📍Calculated mean and total consumption.")

    return df_factor_calculation(dfs_mean, dfs_sum, year_cols)


def load_fjernvarme_factors(normalized: list[str], year_cols) -> dict:
    input_file = get_output_file("input/fjernvarme_kommune_fordelingsnøkler.xlsx")
    df = pl.from_pandas(pd.read_excel(input_file))
    years_column = [str(year) for year in year_cols]

    factor_dict = {}
    for category in [NameHandler.COLUMN_NAME_BOLIG, NameHandler.COLUMN_NAME_YRKESBYGG]:
        if category in normalized:
            value_col = "bolig" if category == NameHandler.COLUMN_NAME_BOLIG else "yrkesbygg"
            base_df = df.select("kommune_nr", "kommune_navn", value_col)
            extended = base_df.with_columns([pl.col(value_col).alias(year) for year in years_column])
            factor_dict[category] = extended

    logger.info("📍Loaded fjernvarme distribution factors.")
    return factor_dict

def load_ved_factors(year_cols) -> dict:
    input_file = get_output_file("input/ved_kommune_fordelingsnøkler.xlsx")
    df = pl.from_pandas(pd.read_excel(input_file))
    years_column = [str(year) for year in year_cols]
    factor_dict = {}
    value_col = "bolig"
    base_df = df.select("kommune_nr", "kommune_navn", value_col)
    extended = base_df.with_columns([pl.col(value_col).alias(year) for year in years_column])
    factor_dict[NameHandler.COLUMN_NAME_BOLIG] = extended

    logger.info("📍Loaded ved distribution factors.")
    return factor_dict

def log_distribution_strategy(energitype, category, method):
    logger.warning(f"Bruker {method} fordelingsnøkkel for {energitype} i {category}.")


def get_distribution_factors(energitype, normalized, elhub_years, step, year_cols):
    if energitype == "strom":
        df_stacked = prepare_elhub_data(elhub_years, step)
        return calculate_elhub_factors(df_stacked, normalized, elhub_years, year_cols)
    elif energitype == "fjernvarme":
        return load_fjernvarme_factors(normalized, year_cols)
    elif energitype in ["ved", "fossil"]:
        dfs_factors = {}
        if NameHandler.COLUMN_NAME_FRITIDSBOLIG in normalized:
                 log_distribution_strategy(energitype, NameHandler.COLUMN_NAME_FRITIDSBOLIG, "Elhub")
                 df_stacked = prepare_elhub_data(elhub_years, step)
                 strom_factors = calculate_elhub_factors(df_stacked, normalized, elhub_years, year_cols)
                 dfs_factors.update(strom_factors)
        if NameHandler.COLUMN_NAME_BOLIG in normalized:
            ved_factors = load_ved_factors(year_cols)
            dfs_factors[NameHandler.COLUMN_NAME_BOLIG] = ved_factors[NameHandler.COLUMN_NAME_BOLIG]
        if not dfs_factors:
            raise ValueError(f"Ugyldig kombinasjon av bygningskategorier for energitype '{energitype}': {normalized}")
        return dfs_factors
    else:
        raise ValueError(f"Unknown energitype: {energitype}")



def export_distribution_to_excel(dfs: dict, output_file: Path):
    create_output_directory(filename=output_file)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, pl_df in dfs.items():
            df_export = pl_df.with_columns(
                pl.col("kommune_nr").cast(pl.Utf8).str.zfill(4)
                ).sort("kommune_nr").to_pandas()
            df_export.to_excel(writer, sheet_name=sheet_name, index=False)
    make_pretty(output_file)
    logger.info(f"📁 Wrote results to {output_file}")


def geographical_distribution(
    elhub_years: list[int],
    energitype: str = None,
    building_category: str = None,
    step: str = None,
    output_format: bool = False
) -> Path:
    """
    Calculate and export energy use distribution based on Elhub or fjernvarme data.

    Args:
        elhub_years (list[int]): Years to include in Elhub aggregation.
        energitype (str): 'strom' or 'fjernvarme'.
        building_category (str): e.g. 'bolig', 'yrkesbygg'.
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

    dfs_factors = get_distribution_factors(energitype, normalized, elhub_years, step, year_cols)
    
    dfs_distributed = ebm_energy_use_geographical_distribution(
        df_ebm,
        dfs_factors,
        year_cols,
        energitype=energitype,
        building_category=normalized
    )

    output_file = get_output_file(
        f"output/{energitype}_energibruk_kommunefordelt.xlsx"
    )

    export_distribution_to_excel(dfs_distributed, output_file)
    return output_file


