import polars as pl

# Function to load Elhub data from Azure Data Lake Storage using Polars
def load_elhub_data(
    dataset="forbruk_per_time_prisomraade_kommune_naeringshovedgruppe",
    year_filter=None,
    month_filter=None,
    columns=None,
    show_schema=False,
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

    print(f"🔍 Loading data from: {abfss_path}")
    # print(f"📌 Selected columns: {columns}")

    # Load data lazily
    df_lazy = pl.scan_parquet(abfss_path, storage_options=storage_options)

    # Optionally preview schema
    if show_schema:
        print("📊 Schema preview:")
        print(df_lazy.collect_schema())

    # Select only needed columns and collect the result
    df = df_lazy.select(columns).collect()
    return df


print("Elhub data extraction module loaded successfully!")