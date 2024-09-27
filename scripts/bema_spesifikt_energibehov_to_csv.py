"""
Writes the table from BEMA_SPREADSHEET 'Bygg Behov' row 39 to 78 to csv

"""
import os
import sys

import dotenv
import pandas as pd

from ebm.model import building_category


def main():
    dotenv.load_dotenv()

    spreadsheet = os.environ.get(
        'BEMA_SPREADSHEET',
        'C:/Users/kenord/OneDrive - Norges vassdrags- og energidirektorat/Dokumenter/regneark/BEMA_redigert.xlsm')

    df = pd.read_excel(spreadsheet, sheet_name='Bygg Behov', header=38, nrows=117-39)

    df = df.drop(columns=[df.columns[0]])
    df = df.rename(columns={df.columns[0]: 'building_category_no',
                            df.columns[1]: 'purpose',
                            'TEK17': 'TEK21L',
                            'TEK17.1': 'TEK21',
                            'TEK17.2': 'TEK21H',
                            'TEK17.3': 'TEK17',
                            'Før 49': 'PRE_TEK49'})
    df['building_category'] = df['building_category_no'].apply(building_category.from_norsk)

    columns = df.columns.tolist()
    columns.insert(0, columns.pop(columns.index('building_category')))
    columns.append(columns.pop(columns.index('building_category_no')))
    df = df[columns]

    melted = pd.melt(df,
                     id_vars=['building_category', 'purpose'],
                     value_vars=[c for c in df.columns if 'TEK' in c],
                     var_name='TEK',
                     value_name='kw_h_m')
    melted = melted[['building_category', 'TEK', 'purpose', 'kw_h_m']]

    melted = melted[~melted['TEK'].isin(['TEK17.3', 'TEK21H', 'TEK21L'])]

    sorted_df = melted.sort_values(by=['building_category', 'TEK'])

    return sorted_df


df_energy_use = None

if __name__ == '__main__':
    df_energy_use = main()

    # Write csv to filename in argument 1. If there is no argument 1, write to the screen instead.
    target = sys.stdout if len(sys.argv) < 2 or not sys.argv[1] else sys.argv[1]
    df_energy_use.to_csv(target, encoding='utf-8', sep=',', index=False)
