import os
from typing import Optional

import polars as pl
import pandas as pd
from loguru import logger

from ebm.temp_calc import calculate_energy_use_wide
from ebmgeodist.initialize import get_output_file


# Function to load Elhub data from Azure Data Lake Storage using Polars
def load_elhub_data(
    dataset="forbruk_per_time_prisomraade_kommune_naeringshovedgruppe",
    year_filter=None,
    month_filter=None,
    columns=None,
):
    # Azure storage configuration
    storage_options = {'use_azure_cli': "True"}
    storage_account = STORAGE_ACCOUNT
    container = STORAGE_CONTAINE

    # Define default column selection if none is provided
    if columns is None:
        columns = [
            "lokal_dato_tid_start",
            "prisomraade",
            "kommune_nr",
            "kommune_navn",
            "forbruk_kwh",
        ]
    else:
        columns = ["uke",
            "naeringshovedomraade_navn",
            "naeringshovedomraade_kode",
            "prisomraade",
            "kommune_navn",
            "naeringshovedgruppe_kode",
            "naeringshovedgruppe_navn",
            "naering_kode",
            "lokal_dato_tid_start",
            "lokal_dato_tid_slutt",
            "antall_maalepunkter",
            "forbruk_kwh",
            "kommune_nr"
        ]

    # Build path based on year and month filters
    year_path = "*" if not year_filter else f"aar={year_filter}"
    month_path = "*" if not month_filter else f"maaned={month_filter}"
    full_path = f"{dataset}/{year_path}/{month_path}/*.snappy.parquet"

    # Compose full Azure ABFSS path
    abfss_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/{full_path}"

    logger.info(f"🔍 Loading Elhub data for year: {year_filter}")
    # print(f"📌 Selected columns: {columns}")

    # Load data lazily
    df_lazy = pl.scan_parquet(abfss_path, storage_options=storage_options)

    # Select only needed columns and collect the result
    df = df_lazy.select(columns).collect()
    return df

def load_energy_use(ebm_input = Optional[str]):
    ebm_input = ebm_input if ebm_input else os.environ.get('EBM_INPUT', 'input')

    energy_use_wide = calculate_energy_use_wide(ebm_input)

    return energy_use_wide

def load_energy_use_from_file() -> pd.DataFrame:
    """
    Load energy use data from the output file.
    This function reads the energy use data from an Excel file located in the output directory.
    Returns:
        pd.DataFrame: DataFrame containing the energy use data.
    """
    energy_use_file_path = get_output_file('output/energy_use.xlsx')
    df = pd.read_excel(energy_use_file_path, sheet_name='wide')
    return df

energy_use = None

if __name__ == '__main__':
    energy_use = load_energy_use_from_file()
