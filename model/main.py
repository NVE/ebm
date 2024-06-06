from DatabaseManager import *
from SCurve import *
from BuildingType import *

import pandas as pd

# TESTING
buildingtype_list = DatabaseManager().get_building_type_list()

for building_type in buildingtype_list:
    s = BuildingType(building_type)
    small_measures = pd.DataFrame(s.acc_s_curve_small_measures)
    rehabilitation = pd.DataFrame(s.acc_s_curve_rehabilitation)
    demolition = pd.DataFrame(s.acc_s_curve_demolition)
    
    print(demolition)
    exit()




