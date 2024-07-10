import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition

building_list = ['apartment_block', 'house',
                 'kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                 'hospital', 'nursinghome', 'culture', 'sports', 'storage_repairs']

def dict_to_df(dict):
    df = pd.DataFrame(dict)
    return df

# Database method testing
db = DatabaseManager()
#og_tek_list = db.get_tek_list()
buildling_category_list = db.get_building_category_list()
#condition_list = db.get_condition_list()
#s = db.get_scurve_params_per_building_category('House', condition_list)
#print(s) 

# Buildings
b = Buildings('house')
tek_list = b.tek_list
tek_params = b.tek_params
shares = b.shares_per_condition

df = dict_to_df(shares)

print(df)

