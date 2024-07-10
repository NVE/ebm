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


"""
# get db data
db = DatabaseManager()
buildling_category_list = db.get_building_category_list()
condition_list = db.get_condition_list()
tek_list = db.get_tek_list()
tek_params = db.get_tek_params(tek_list)

# Scurve params
scurve_params = db.get_scurve_params_per_building_category('house', condition_list)

scurve_data = {}
for condition in condition_list:
    scurve_params_condition = scurve_params[condition_list[0]]

    # Calculate the S-curve 
    scurve = SCurve(scurve_params_condition.earliest_age, scurve_params_condition.average_age, scurve_params_condition.last_age, 
                scurve_params_condition.rush_years, scurve_params_condition.rush_share, scurve_params_condition.never_share).scurve

    # Store the parameters in the dictionary
    scurve_data[condition] = [scurve, scurve_params_condition.never_share]

shares_condition = SharesPerCondition(tek_list, tek_params, scurve_data)
shares = shares_condition.shares_per_condition
print(shares)
"""



# Buildings
b = Buildings('house')
#tek_list = b.tek_list
#tek_params = b.tek_params

s = b.get_scurve('renovation')
s = dict_to_df(s)

shares = b.shares_per_condition
df = dict_to_df(shares)

print(s)

