from DatabaseManager import *

class TEK():

    def __init__(self, tek_id):
        
        self.id = tek_id
        self.database = DatabaseManager()
        self.tek_id_params = self.database.get_tek_params_per_id(tek_id)
        self.building_year = self._get_input_value(self.tek_id_params, 'building_year')
 
        pass

    def _get_input_value(self, df, col):
        """
        Filters input dataframe by column name and returns column value

        Parameters: 
            - df: Pandas dataframe
            - col: str 

        Returns:
            - value: filtered column value
        """
        value = df.loc[df.index[0], col]
        return value
    
    def get_demolition_s_curve(self):
        pass
    
#TEST

d = DatabaseManager()
l = d.get_tek_id_list()
tek_id = l[0]

t = TEK(tek_id)
print(t.tek_id_params)

    