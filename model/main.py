from DatabaseManager import *
from SCurve import *
from Buildings import *

import pandas as pd

# TESTING

output_folder = 'output'

buildingtype_list = DatabaseManager().get_building_type_list()


def s_curves_to_dataframe(building_type):
    s = Buildings(building_type)
    small_measures_df = pd.DataFrame(s.acc_s_curve_small_measures)
    rehabilitation_df = pd.DataFrame(s.acc_s_curve_rehabilitation)
    demolition_df = pd.DataFrame(s.acc_s_curve_demolition)

    small_measures_df = small_measures_df.rename(columns={'Accumulated Rate': 'small_measures'})
    rehabilitation_df = rehabilitation_df.rename(columns={'Accumulated Rate': 'rehabilitation'})
    demolition_df = demolition_df.rename(columns={'Accumulated Rate': 'demolition'})

    merged_df = small_measures_df.merge(rehabilitation_df, on='Year').merge(demolition_df, on='Year')

    return merged_df

def export_all_s_curves(buildingtype_list, output_folder):
    for building_type in buildingtype_list:
        
        s_curves_df = s_curves_to_dataframe(building_type)
        s_curves_df.to_excel(os.path.join(output_folder, f'{building_type}_acc_s_curves.xlsx'))

#export_all_s_curves(buildingtype_list, output_folder)

df = s_curves_to_dataframe("SmallHouse") 
print(df)





