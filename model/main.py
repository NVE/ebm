from DatabaseManager import *
from SCurve import *
from BuildingType import *

import pandas as pd

# TESTING

output_folder = 'output'

buildingtype_list = DatabaseManager().get_building_type_list()

for building_type in buildingtype_list:
    if building_type == 'SmallHouse':
        
        s = BuildingType(building_type)
        small_measures_df = pd.DataFrame(s.acc_s_curve_small_measures)
        rehabilitation_df = pd.DataFrame(s.acc_s_curve_rehabilitation)
        demolition_df = pd.DataFrame(s.acc_s_curve_demolition)
    
        small_measures_df = small_measures_df.rename(columns={'Accumulated Rate': 'small_measures'})
        rehabilitation_df = rehabilitation_df.rename(columns={'Accumulated Rate': 'rehabilitation'})
        demolition_df = demolition_df.rename(columns={'Accumulated Rate': 'demolition'})
        
        merged_df = small_measures_df.merge(rehabilitation_df, on='Year').merge(demolition_df, on='Year')
        
        merged_df.to_excel(os.path.join(output_folder, f'{building_type}_acc_s_curves.xlsx'))
        print(merged_df)

        #exit()




