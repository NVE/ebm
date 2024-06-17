from DatabaseManager import *
from SCurve import *
from Buildings import *

import pandas as pd

# TESTING

output_folder = 'output'

building_category_list = DatabaseManager().get_building_category_list()


def s_curves_to_dataframe(building_category):
    s = Buildings(building_category)
    small_measures_df = pd.DataFrame(s.s_curve_small_measures)
    rehabilitation_df = pd.DataFrame(s.s_curve_rehabilitation)
    demolition_df = pd.DataFrame(s.s_curve_demolition)

    small_measures_df = small_measures_df.rename(columns={'rate': 'small_measures'})
    rehabilitation_df = rehabilitation_df.rename(columns={'rate': 'rehabilitation'})
    demolition_df = demolition_df.rename(columns={'rate': 'demolition'})

    merged_df = small_measures_df.merge(rehabilitation_df, on='year').merge(demolition_df, on='year')

    return merged_df

def export_all_s_curves(building_category_list, output_folder):
    for building_category in building_category_list:
        
        s_curves_df = s_curves_to_dataframe(building_category)
        s_curves_df.to_excel(os.path.join(output_folder, f'{building_category}_s_curves.xlsx'))


def get_demolition_shares_per_tek(building_category):
    s = Buildings(building_category)
    shares = s.get_demolition_shares_per_tek()
    demolition_shares_df = pd.DataFrame(shares)
    return demolition_shares_df


#export_all_s_curves(building_category_list, output_folder)
#df = s_curves_to_dataframe("Apartment") 
df = get_demolition_shares_per_tek('SmallHouse')
print(df)





