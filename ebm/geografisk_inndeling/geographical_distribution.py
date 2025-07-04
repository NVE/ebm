from azure.identity import DefaultAzureCredential
from elhub_data_extraction import load_elhub_data
import gc

# Initialize the DefaultAzureCredential
credential = DefaultAzureCredential()

# Define the storage account name and endpoint
storage_account_name = STORAGE_ACCOUNT
endpoint = f"abfss://{storage_account_name}.dfs.core.windows.net"

# Function to load Elhub data from Azure Data Lake Storage using Polars
# Load data for different years
df_elhub_22 = load_elhub_data(year_filter=2022, columns=True, show_schema=True)
df_elhub_23 = load_elhub_data(year_filter=2023, columns=False)
df_elhub_24 = load_elhub_data(year_filter=2024, columns=False)

gc.collect()

