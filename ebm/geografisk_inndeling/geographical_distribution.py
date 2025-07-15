import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from ebm.geografisk_inndeling.data_loader import load_elhub_data, load_energy_use
from ebm.geografisk_inndeling.calculation_tools import df_commune_mean, df_total_consumption_buildingcategory, df_factor_calculation
from ebm.geografisk_inndeling.initialize import create_output_directory, get_output_file
from ebm.geografisk_inndeling.spreadsheet import make_pretty
import gc
import polars as pl
import pandas as pd
from loguru import logger


def geographical_distribution(elhub_years: list[int], step: str = None) -> Path:
    """
    _summary_

    Args:
        step (str, optional): _description_. Defaults to None.
        elhub_years (list[int], optional): _description_. Defaults to [2022, 2023, 2024].
    """
    # Initialize the DefaultAzureCredential
    credential = DefaultAzureCredential()

    # Define the storage account name and endpoint  
    storage_account_name = STORAGE_ACCOUNT
    endpoint = f"abfss://{storage_account_name}.dfs.core.windows.net"

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

        
    if step == "alle":
        # Husholdning
        df_stacked_household = df_stacked.filter(
            (pl.col("naeringshovedomraade_kode").is_in(["XX"]))|
            (pl.col("naeringshovedgruppe_kode").is_in(["68.2"]))
            )

        # Feriehus
        df_stacked_holiday_home = df_stacked.filter(pl.col("naeringshovedomraade_kode").is_in(["XY"]))

        # Yrkesbygg
        commercial_list = [{"45": "60"}, {"64": "96"}, "99"]

        filter_list = []

        for item in commercial_list:
            if isinstance(item, dict):
                for start, end in item.items():
                    filter_list.extend([str(i) for i in range(int(start), int(end)+1)])
            else:
                filter_list.append(item)

        df_stacked_commercial = df_stacked.filter(pl.col("naering_kode").is_in(filter_list))

        elhub_dataframes = {    "Household": df_stacked_household,
                                "Holiday_home": df_stacked_holiday_home,
                                "Commercial": df_stacked_commercial
                                }

        dfs_elhub_mean = {}
        for df_name, stacked_df in elhub_dataframes.items():
            df = df_commune_mean(stacked_df, elhub_years)
            dfs_elhub_mean[df_name] = df

        # Calculate total consumption for each building category
        dfs_elhub_sum = {}
        for df_name, stacked_df in dfs_elhub_mean.items():
            df = df_total_consumption_buildingcategory(stacked_df)
            dfs_elhub_sum[df_name] = df

        logger.info(f"📍Mean total power consumption calculated.")

        # Calculate factors for each year
        exel_fomrat = input("Vil du ha Excel-resultatene i breddeformat? (ja/nei): ").lower()
        if exel_fomrat == "ja":
            year_cols = range(2020, 2051)
        elif exel_fomrat == "nei":
            year_cols = (2020, 2050)
        else:
            raise ValueError("Ugyldig svar. Skriv 'ja' eller 'nei'.")
        
        dfs_elhub_factors = df_factor_calculation(dfs_elhub_mean, dfs_elhub_sum, year_cols)
        logger.info(f"📍Factors calculated for the selected building categories.")

        # Step 1: Define output file path (relative to project root)
        output_file = get_output_file("ebm/geografisk_inndeling/output/kommunefordelingsnøkler.xlsx")

        # Step 2: Ensure directory exists
        create_output_directory(filename=output_file)

        # Step 3: Save to Excel
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name, pl_df in dfs_elhub_factors.items():
                pl_df.sort(by="kommune_nr").to_pandas().to_excel(writer, sheet_name=sheet_name, index=False)
        make_pretty(output_file)

        # Running the code below gives an error, so I comment it out for now
        # This is the error message: FileNotFoundError: [Errno 2] No such file or directory: 'input\\building_code.csv'
        ebm = load_energy_use()
        print(f"EBM data loaded successfully: {ebm}")
        # with pd.ExcelWriter(output_file, engine="openpyxl", mode='a') as writer:
        #     ebm.to_excel(writer, sheet_name="EBM", index=False)
    
    return output_file