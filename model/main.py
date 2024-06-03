from DatabaseManager import *
from SCurve import *
from SCurvePerBuildingType import *

import pandas as pd

#input = DatabaseManager().s_curve_input_df
#print(input)

s = SCurvePerBuildingType('House')

ee = pd.DataFrame(s._s_curve_ee)
rehab = pd.DataFrame(s._s_curve_rehab)
demo = pd.DataFrame(s._s_curve_demolition)

print(ee)

