from rich import print
from rich.table import Table

from ebm.model import DatabaseManager
from ebm.services.console import rich_display_dataframe, df_to_table

data_manager = DatabaseManager()

building_category_share = data_manager.get_new_buildings_category_share()


rich_display_dataframe(building_category_share)

print(df_to_table(building_category_share, rich_table=Table(show_header=True, header_style="bold magenta")))