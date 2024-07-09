import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition

def dict_to_df(dict):
    df = pd.DataFrame(dict)
    return df

# Database method testing
db = DatabaseManager()
condition_list = db.get_condition_list()
s = db.get_scurve_params_per_building_category('House', condition_list)
print(s) 

# Buildings
#b = Buildings('House')
#scurve_data = b.scurve_data
#print(scurve_data)

