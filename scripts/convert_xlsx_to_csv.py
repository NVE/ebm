import pathlib
import pandas as pd

# Convert a file from xlsx to csv (with same filename) in same directory

folder_path = 'input'
filename = 'area_parameters'

def xlsx_to_csv(folder_path, filename):
    source = pathlib.Path(f'{folder_path}/{filename}.xlsx')
    target = pathlib.Path(f'{folder_path}/{filename}.csv')
    
    df = pd.read_excel(source)
    df.to_csv(target, sep=',', encoding='utf-8', index=False)

    print(df)

def csv_to_xlsx(folder_path, filename):
    source = pathlib.Path(f'{folder_path}/{filename}.csv')
    target = pathlib.Path(f'{folder_path}/{filename}.xlsx')

    df = pd.read_csv(source)
    df.to_excel(target, index=False)

    print(df)

xlsx_to_csv(folder_path, filename)
#csv_to_xlsx(folder_path, filename)