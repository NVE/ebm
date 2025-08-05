import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from ebm.geografisk_inndeling.initialize import NameHandler
from ebm.geografisk_inndeling.data_loader import load_elhub_data, load_energy_use
from ebm.geografisk_inndeling.calculation_tools import df_commune_mean, df_total_consumption_buildingcategory,\
      df_factor_calculation, yearly_aggregated_elhub_data, ebm_energy_use_geographical_distribution
from ebm.geografisk_inndeling.initialize import create_output_directory, get_output_file
from ebm.geografisk_inndeling.spreadsheet import make_pretty
import gc
import polars as pl
import pandas as pd
from loguru import logger



def prepare_elhub_data(elhub_years: list[int], step: str) -> pl.DataFrame:
    input_file = get_output_file("ebm/geografisk_inndeling/data/yearly_aggregated_elhub_data.parquet")

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
        df_stacked_year.write_parquet(input_file, compression="zstd")
        logger.info(f"📍New stacked Elhub data saved: {input_file.name}")
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
    input_file = get_output_file("ebm/geografisk_inndeling/data/fjernvarme_kommune_fordelingsnøkler.xlsx")
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
    normalized_input = NameHandler.normalize_to_list(building_category)

    if isinstance(normalized_input, str):
        normalized_input = [normalized_input]

    # Split into separate categories per energy type
    normalized_strom = normalized_input.copy()

    year_cols = (2020, 2050) if output_format else range(2020, 2051)

    df_ebm = pl.from_pandas(load_energy_use())

    if energitype == "strom":
        df_stacked = prepare_elhub_data(elhub_years, step)
        dfs_factors = calculate_elhub_factors(df_stacked, normalized_strom, elhub_years, year_cols)
        building_cats = normalized_strom

    elif energitype == "fjernvarme":
        normalized_fjernvarme = [
        cat for cat in normalized_input
        if cat.lower() != NameHandler.COLUMN_NAME_FRITIDSBOLIG.lower()
        ]
        if not normalized_fjernvarme:
            raise ValueError(
                "Fjernvarme krever minst én bygningskategori som ikke er fritidsboliger."
                )
        dfs_factors = load_fjernvarme_factors(normalized_fjernvarme, year_cols)
        building_cats = normalized_fjernvarme
    else:
        raise ValueError(f"Unknown energitype: {energitype}")
    
    dfs_distributed = ebm_energy_use_geographical_distribution(
        df_ebm,
        dfs_factors,
        year_cols,
        energitype=energitype,
        building_category=building_cats
    )

    output_file = get_output_file(
        f"ebm/geografisk_inndeling/output/{energitype}_energibruk_kommunefordelt.xlsx"
    )

    export_distribution_to_excel(dfs_distributed, output_file)
    return output_file


