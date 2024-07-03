import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition

def dict_to_df(dict):
    df = pd.DataFrame(dict)
    return df

database_manager = DatabaseManager()

# SharesPerCondition
"""
tek_list = database_manager.get_tek_list()

tek_params = database_manager.get_tek_params(tek_list)

scurve_data = Buildings('House').scurve_data

shares = SharesPerCondition(tek_list, tek_params, scurve_data)

shares_demolition = shares.get_shares_demolition()
shares_small_measure_total = shares.get_shares_small_measure_total()
shares_renovation_total = shares.get_shares_renovation_total()
shares_renovation = shares.get_shares_renovation()
shares_renovation_and_small_measure = shares.get_shares_renovation_and_small_measure()
shares_small_measures = shares.get_shares_small_measure()
shares_og = shares.get_shares_original_condition()

shares_df = dict_to_df(shares_og)
print(shares_df)
"""

# Buildings
b = Buildings('House')
shares = b.get_shares()
shares_condition = b.get_shares_per_condition('Small measure')
scurve = b.get_scurve('Small measure')
print(scurve)
