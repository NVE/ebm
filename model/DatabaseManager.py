import pandas as pd

class DatabaseManager():

    #TODO: Add input validtion (loguru)
    
    def __init__(self):
        
        # Test data
        s_curve_input_dict = {
            'building_type': ['Apartment', 'Apartment', 'Apartment', 'House', 'House', 'House'],
            'renovation_state': ['EE', 'Rehabilitation', 'Demolition', 'EE', 'Rehabilitation', 'Demolition'],
            'earliest_renovation_age': [5, 10, 60, 3, 10, 60],
            'average_age': [20, 30, 90, 23, 37, 90],
            'last_renovation_age': [50, 60, 150, 80, 75, 150],
            'rush_period_years': [20, 14, 40, 30, 24, 40],
            'rush_share': [0.8, 0.6, 0.7, 0.8, 0.65, 0.7],
            'never_share': [0.1, 0.15, 0.05, 0.01, 0.05, 0.05]
            }
        
        self.s_curve_input_df = pd.DataFrame(s_curve_input_dict)

    def get_s_curve_input(self, building_type, renovation_state):
        
        df = self.s_curve_input_df
        df = df[df['building_type'] == building_type]
        df = df[df['renovation_state'] == renovation_state]

        return df
        