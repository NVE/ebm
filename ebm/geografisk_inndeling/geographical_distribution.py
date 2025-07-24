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


def geographical_distribution(elhub_years: list[int], building_category: str = None, step: str = None, output_format: bool = False) -> Path:
    """
    _summary_

    Args:
        step (str, optional): _description_. Defaults to None.
        elhub_years (list[int], optional): _description_. Defaults to [2022, 2023, 2024].
    """
    input_file = get_output_file("ebm/geografisk_inndeling/data/yearly_aggregated_elhub_data.parquet")

    if step == "azure":
        # Load data for different years
        # Note: Adjust the year_filter and columns parameters as needed
        elhub_data = {
            f"df_elhub_{str(year)[-2:]}": load_elhub_data(year_filter=year, columns=True)
            for year in elhub_years
            }
        # Clean up memory
        gc.collect()

        logger.info(f"📍Elhub data loaded successfully for years {elhub_years}")

        # Stack the DataFrames for each year into a single DataFrame
        df_stacked = list(elhub_data.values())[0]
        for df in list(elhub_data.values())[1:]:
            df_stacked = df_stacked.vstack(df)
        # Save the stacked DataFrame to a parquet file
        df_stacked_year = yearly_aggregated_elhub_data(df_stacked)
        df_stacked_year.write_parquet(input_file, compression = "zstd")
        logger.info(f"📍New stacked Elhub data saved in the data directory with filename: {input_file.name}")
    else:
        # Load data from local parquet file
        create_output_directory(filename=input_file)
        df_stacked = pl.read_parquet(input_file)
        logger.info(f"📍Stacked Elhub data loaded successfully from the data directory from file: {input_file.name}")
        
    elhub_dataframes = {}

    # Normalize input (could be string or list)
    normalized = NameHandler.normalize_to_list(building_category)
    
    if isinstance(normalized, str):
        normalized = [normalized]

    if NameHandler.COLUMN_NAME_BOLIG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_BOLIG] = get_household_data(df_stacked)

    if NameHandler.COLUMN_NAME_FRITIDSBOLIG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_FRITIDSBOLIG] = get_holiday_home_data(df_stacked)

    if NameHandler.COLUMN_NAME_YRKESBYGG in normalized:
        elhub_dataframes[NameHandler.COLUMN_NAME_YRKESBYGG] = get_commercial_data(df_stacked)

    if not elhub_dataframes:
        raise ValueError("Ingen gyldig bygningskategori valgt.")

    dfs_elhub_mean = {
        name: df_commune_mean(df, elhub_years)
        for name, df in elhub_dataframes.items()
    }

    # Calculate total consumption for each building category
    dfs_elhub_sum = {
        name: df_total_consumption_buildingcategory(df)
        for name, df in dfs_elhub_mean.items()
    }
        
    logger.info(f"📍Mean total power consumption calculated.")

    # Calculate factors for each year
    if output_format:
        year_cols = (2020, 2050)
    else:
        year_cols = range(2020, 2051)
    
    dfs_elhub_factors = df_factor_calculation(dfs_elhub_mean, dfs_elhub_sum, year_cols)
    logger.info(f"📍Factors calculated for the selected building categories.")

    df_ebm = pl.from_pandas(load_energy_use())
    dfs_ebm_distributed = ebm_energy_use_geographical_distribution(df_ebm, dfs_elhub_factors,\
                        year_cols, building_category= building_category, output_format=output_format)

    # Step 1: Define output file path (relative to project root)
    output_file = get_output_file("ebm/geografisk_inndeling/output/energibruk_kommunefordelt.xlsx")

    # Step 2: Ensure directory exists
    create_output_directory(filename=output_file)
    
    # Step 3: Write the results to Excel file
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, pl_df in dfs_ebm_distributed.items():
            pl_df.sort(by="kommune_nr").to_pandas().to_excel(writer, sheet_name=sheet_name, index=False)

    make_pretty(output_file)
    return output_file