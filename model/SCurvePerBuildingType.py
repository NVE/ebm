from DatabaseManager import *
from SCurve import *

class SCurvePerBuildingType():
    
    #TODO:
    # 1. get s_curve_acc for the 3 types of renovation (rehab, enok, demolition) across lifetime (1-30)
    #   - need 3 different sets of input parameters for the SCurve class
    # 2. generate accumated s_curves per TEK for for the 3 renovation types. 
    #   - need input data with TEK and corresponding building age
    #   - calculation: match each TEK age with the year values from the s_curve_acc
    # 3. calculate accumulated s_curve per TEK for only rehab, only enok and enok + rehab 
    #   - need values from the s_curves in step 2. 
    #   - need never_share for the 3 renovation types (currently in s_curve)

    def __init__(self, building_type):
        
        self.building_type = building_type
        self.database = DatabaseManager()
        
        input_ee = self.database.get_s_curve_input(building_type, 'EE')
        input_rehab = self.database.get_s_curve_input(building_type, 'Rehabilitation')
        input_demolition = self.database.get_s_curve_input(building_type, 'Demolition')
        
        self._s_curve_ee = SCurve(input_ee)._s_curve_acc
        self._s_curve_rehab = SCurve(input_rehab)._s_curve_acc
        self._s_curve_demolition = SCurve(input_demolition)._s_curve_acc

    def s_curve_demolition_tek(self):
        pass

    def s_curve_rehab_tek(self):
        pass

    def s_curve_enok_tek(self):
        pass    

    def s_curve_only_rehab_tek(self):
        pass

    def s_curve_only_enok_tek(self):
        pass

    def s_curve_rehab_and_enok_tek(self):
        pass
