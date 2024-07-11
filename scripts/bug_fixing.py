import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.shares_per_condition import SharesPerCondition
from ebm.model.scurve import SCurve

building_list = ['apartment_block', 'house',
                 'kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                 'hospital', 'nursinghome', 'culture', 'sports', 'storage_repairs']

def dict_to_df(dict):
    df = pd.DataFrame(dict)
    return df

# get db data
db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
condition_list = db.get_condition_list()
tek_list_original = db.get_tek_list()

b = Buildings('house')
tek_list = b.tek_list

# scurves
s = b.get_scurve('renovation')
s = dict_to_df(s)

# shares
shares = b.shares_per_condition
df = dict_to_df(shares)

# See area input data
#construction_population = db.get_construction_population()
#construction_building_category_share = db.get_construction_building_category_share()
#area = db.get_building_category_area()
#area_by_tek = db.get_building_category_area_by_tek()

print(df)