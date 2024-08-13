import typing
import os

from openpyxl import load_workbook
from loguru import logger
from dotenv import load_dotenv
import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.database_manager import DatabaseManager
from ebm.model.buildings import Buildings
from ebm.model.area_forecast import AreaForecast

from ebm.services.spreadsheet import iter_cells

def get_building_category_sheet(building_category: BuildingCategory, area_sheet: bool = True) -> str:
    """
    Returns the sheet name of the A or R sheet of a building category.

    Parameters:
    - building_category: An instance of BuildingCategory.
    - area_sheet (bool): True or False. 
        - True: return A sheet name. 
        - False: return R sheet name 

    Returns:
    - sheet (str): name of the A or R sheet
    """
    building_category_sheets = {
            BuildingCategory.HOUSE: ['A hus', 'R hus'],
            BuildingCategory.APARTMENT_BLOCK: ['A leil', 'R hus'],
            BuildingCategory.KINDERGARTEN: ['A bhg', 'R bhg'],
            BuildingCategory.SCHOOL: ['A skole', 'R skole'],
            BuildingCategory.UNIVERSITY: ['A uni', 'R uni'],
            BuildingCategory.OFFICE: ['A kont', 'R kont'],
            BuildingCategory.RETAIL: ['A forr', 'R forr'],
            BuildingCategory.HOTEL: ['A hotell', 'R hotell'],
            BuildingCategory.HOSPITAL: ['A shus', 'R shus'],
            BuildingCategory.NURSING_HOME: ['A shjem', 'R shjem'],
            BuildingCategory.CULTURE: ['A kult', 'R kult'],
            BuildingCategory.SPORTS: ['A idr', 'R idr'],
            BuildingCategory.STORAGE_REPAIRS: ['A ind', 'R ind']
    }

    if area_sheet:
        sheet = building_category_sheets[building_category][0]
    else:
        sheet = building_category_sheets[building_category][1]
    
    return sheet

def xlsx_to_df(workbook: str, sheet: str, header: int, usecols: str = 'E:AS', nrows: int = 5):
    """
    Reads an excel sheet and returns a dataframe based on the input arguments.

    Parameters:
    - workbook: excel file path
    - sheet: excel file sheet
    - header: row number to be used as header/columns in the dataframe
    - usecols: columns to use, can be str (e.g. 'A:E'), list of int or str
    - nrows: number of rows to include from header row 

    Returns:
    - df: pandas dataframe
    """
    if workbook is None:
        workbook = os.environ.get('BEMA_SPREADSHEET')

    df = pd.read_excel(
                    workbook,                       
                    sheet_name = sheet,              
                    header = header - 1,  # number of rows to skip before header, e.g. header= 7, then row 8 is used as header 
                    usecols = usecols,                
                    nrows = nrows                  
                    )
    return df
   
def load_bema_area(building_category: BuildingCategory, database_manger: Buildings, start_row: int = 551):
    """
    """
    # Retrieve workbook and sheet names 
    workbook = os.environ.get('BEMA_SPREADSHEET')
    sheet = get_building_category_sheet(building_category, area_sheet=True)

    # Get tek_list from buildings class
    building = Buildings.build_buildings(building_category, database_manager)
    tek_list = building.tek_list

    df_list = []
    # row number for first header in sheet
    header = start_row  
    # number of rows between headers/tables in sheet
    skip_rows = 9
    # the order in which conditions are listed in bema   
    bema_sorted_condition_list = ['original_condition','small_measure','renovation','renovation_and_small_measure','demolition']       
    
    for tek in tek_list:
        # read data from excel
        df = xlsx_to_df(workbook, sheet=sheet, header=header, usecols="E:AS", nrows=5)
    
        # format dataframe
        df['building_condition'] = bema_sorted_condition_list
        df['tek'] = tek
        df = pd.melt(df, id_vars=['tek','building_condition'], var_name='year')
        df.rename(columns={'value':'bema_value'}, inplace=True)
        
        # append dataframes to list
        df_list.append(df)

        # increase header number for next iteration
        header = header + skip_rows
    
    # concat all tables into one dataframe ordered by tek
    bema_area = pd.concat(df_list)
    return bema_area

def get_ebm_area(building_category: BuildingCategory, database_manager, start_year: int = 2010, end_year: int = 2050):
    """
    """
    building = Buildings.build_buildings(building_category, database_manager)
    tek_list = building.tek_list
    area_forecast = building.build_area_forecast(database_manager, start_year, end_year) #TODO: get constructed area first 
    area = area_forecast.calc_area()
     
    df_list = []  
    for tek in tek_list:
        df = pd.DataFrame(area[tek])
        df['year'] = range(start_year, end_year + 1)
        df['tek'] = tek
        df = pd.melt(df, id_vars=['tek','year'], var_name='building_condition')
        df = df[['tek', 'building_condition', 'year', 'value']]
        df.rename(columns={'value':'ebm_value'}, inplace=True)
        df_list.append(df)

    ebm_area = pd.concat(df_list)
    return ebm_area  

def control_area(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    """
    logger.debug(f'Controlling area data for building category {building_category}')

    bema_area = load_bema_area(building_category, database_manager)
    ebm_area = get_ebm_area(building_category, database_manager)

    df = pd.merge(ebm_area, bema_area, on = ['tek', 'building_condition', 'year'], how='inner')
    df['IDENTICAL'] = df['ebm_value'] == df['bema_value']
    df['DIFFERENCE'] = round(df['ebm_value'], precision) - round(df['bema_value'], precision)

    diff = df[df['IDENTICAL'] == False]

    n_diff = len(diff)
    if n_diff > 0:
        logger.info(f'Number of different values: {n_diff}')
        n_dec = len(diff[diff['DIFFERENCE'] > 0])
        logger.info(f'Number of values with {precision} decimals difference: {n_dec}')
    else:
        logger.debug(f'No difference between data')


database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE

control_area(building_category, database_manager)


