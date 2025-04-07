import os
import typing

import pandas as pd
from loguru import logger

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.buildings import Buildings
from ebm.model.construction import ConstructionCalculator
from ebm.model.filter_scurve_params import FilterScurveParams
from ebm.model.scurve_processor import ScurveProcessor
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager


# Possible adjustment: could use modelyears to filter the desired data to compare, but this requires some changes:
# - need to add modelyears to the EBM dictionaries/list that is retrieved, so that they can be filtered
# - need to add a method for retrieving correct BEMA colums according to modelyears when reading excel file
# - add modelyears filtering in the methods 

def get_building_category_sheet(building_category: BuildingCategory, area_sheet: bool = True) -> str:
    """
    Returns the appropriate sheet name based on the building category and area sheet type.
    
    Parameters:
    - building_category: An instance of BuildingCategory.
    - area_sheet (bool): Determines whether to return the area sheet ('A') or rates sheet ('R') name. Defaults to True for the area sheet.

    Returns:
    - sheet (str): The sheet name corresponding to the building category and sheet type.
    """
    building_category_sheets = {
            BuildingCategory.HOUSE: ['A hus', 'R hus'],
            BuildingCategory.APARTMENT_BLOCK: ['A leil', 'R leil'],
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
            BuildingCategory.STORAGE: ['A ind', 'R ind']
    }

    if area_sheet:
        sheet = building_category_sheets[building_category][0]
    else:
        sheet = building_category_sheets[building_category][1]
    
    return sheet

def xlsx_to_df(workbook: str, sheet: str, header: int, usecols = 'E:AS', n_rows: int = 5, skiprows = None, names = None):
    """
    Reads an excel sheet and returns a dataframe based on the input arguments.

    Parameters:
    - workbook (str): excel file path
    - sheet (str): excel file sheet
    - header (int): Row number (0-indexed) to be used as header/columns in the dataframe
    - usecols: columns to use. Datatype: can be str (e.g. 'A:E'), list of int's or str's
    - nrows (int): number of rows to include from header row 
    - skiprows: line numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file
    - names (list): list of column names to use. Must match number of columns (usecols)

    Returns:
    - df (pd.Dataframe): Data loaded from the Excel sheet.
    """
    if workbook is None:
        workbook = os.environ.get('BEMA_SPREADSHEET')

    if header != None:
        # Number of rows to skip before header. E.g. header= 7, then row 8 is used as header 
        header = header - 1

    df = pd.read_excel(
                    workbook,                       
                    sheet_name = sheet,              
                    header = header,  
                    usecols = usecols,
                    nrows = n_rows,
                    skiprows = skiprows,
                    names = names                                
                    )
    return df

def validate_data(building_category: BuildingCategory, data_name: str, df1: pd.DataFrame, df2: pd.DataFrame, join_cols: typing.List[str], precision=5):
    """
    Compare values between two dataframes. 

    Parameters:
    - building_category (BuildingCategory): Building category being analyzed.
    - data_name (str): Name of the dataset being validated.
    - df1 (pd.DataFrame): First dataframe to compare, e.g. EBM data.
    - df2 (pd.DataFrame): Second dataframe to compare, e.g. BEMA data.
    - join_cols (List[str]): List of column names to join on.
    - precision (int): Decimal precision for comparing values.

    Raises:
    - ValueError: If there are issues with the join columns, data types, or row counts.

    Logs:
    - Warnings if rows are missing during the join.
    - Errors if significant differences are found.
    """
    logger.info(f'{building_category} - Validating {data_name} data. Decimal precision {precision}')

    # Check that all join columns are present in both dataframes
    missing_in_df1 = [col for col in join_cols if col not in df1.columns]
    missing_in_df2 = [col for col in join_cols if col not in df2.columns]
    
    if missing_in_df1:
        raise ValueError(f"The following join columns are missing in df1: {missing_in_df1}")
    
    if missing_in_df2:
        raise ValueError(f"The following join columns are missing in df2: {missing_in_df2}")
    
    # Ensure the data types of the join columns match between the two dataframes
    for col in join_cols:
        if df1[col].dtype != df2[col].dtype:
            raise ValueError(f"Data type mismatch for column '{col}': df1 is {df1[col].dtype}, df2 is {df2[col].dtype}")
    
    # Verify that the number of rows in both dataframes is the same
    if len(df1) != len(df2):
        raise ValueError(f"Row count mismatch: df1 has {len(df1)} rows, df2 has {len(df2)} rows")
    
    # Perform anti-join checks to identify any left-out data before merging
    df1_not_in_df2 = df1.merge(df2, on=join_cols, how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only']
    df2_not_in_df1 = df2.merge(df1, on=join_cols, how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only']

    if not df1_not_in_df2.empty:
        logger.warning(f"Rows in df1 but not in df2: {len(df1_not_in_df2)}")
        logger.debug(f"Missing rows from df2: \n{df1_not_in_df2}")

    if not df2_not_in_df1.empty:
        logger.warning(f"Rows in df2 but not in df1: {len(df2_not_in_df1)}")
        logger.debug(f"Missing rows from df1: \n{df2_not_in_df1}")

    # Check row count differences and raise error if they differ
    if len(df1) != len(df2):
        raise ValueError(f"Row count mismatch: df1 has {len(df1)} rows, df2 has {len(df2)} rows. See logs for details.")

    # Perform inner join for value comparison
    df = pd.merge(df2, df1, on = join_cols, how='inner')

    # Compare values between EBM and BEMA data
    df['IDENTICAL'] = df['ebm_value'] == df['bema_value']
    df['DIFFERENCE'] = round(df['ebm_value'], precision) - round(df['bema_value'], precision)

    if precision is None:
        diff = df[df['IDENTICAL'] == False]
    else:
        diff = df[df['DIFFERENCE'] != 0]

    n_diff = len(diff)
    if n_diff > 0:
        logger.error(f'{building_category} - Number of different {data_name} values (decimal precision: {precision}): {n_diff}')
        diff.to_excel(f'output/validate_{data_name}_{building_category}.xlsx',
                      index=False,
                      float_format=f'%.{12}f',
                      freeze_panes=(1, 0))
    #else:
    #    logger.info(f'No difference between data (decimal precision: {precision})')


def load_bema_area(building_category: BuildingCategory, database_manager: DatabaseManager, start_row: int = 551, n_rows = 5, usecols: str = "E:AS"):
    """
    Retrieves area forecast data per building category from the BEMA model and formats it to a dataframe that are compatible for validation.

    Parameters:
    - building_category (BuildingCategory): The building category to load data for.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - start_row (int, optional): The starting row for reading the area data. Defaults to 551.
    - n_rows (int, optional): Number of rows to read per TEK condition. Defaults to 5.
    - usecols (str, optional): Columns to read from the Excel sheet. Defaults to "E:AS".

    Returns:
    - pd.DataFrame: Formatted BEMA area data.  
    """
    # Retrieve workbook and sheet names 
    workbook = os.environ.get('BEMA_SPREADSHEET')
    sheet = get_building_category_sheet(building_category, area_sheet=True)

    # Get tek_list from buildings class
    building = Buildings.build_buildings(building_category, database_manager)
    tek_list = building.tek_list

    # define row number for first header in sheet
    if building_category == BuildingCategory.STORAGE:
        header = 552
    else:
        header = start_row  
    
    # Number of rows between headers/tables in sheet
    skip_rows = 9

    # The order in which conditions are listed in bema   
    bema_sorted_condition_list = ['original_condition','small_measure','renovation','renovation_and_small_measure','demolition']       
  
    df_list = []
    for tek in tek_list:
        # read data from excel
        df = xlsx_to_df(workbook, sheet=sheet, header=header, usecols=usecols, n_rows=n_rows)
    
        # format dataframe
        df['building_condition'] = bema_sorted_condition_list
        df['tek'] = tek
        df = pd.melt(df, id_vars=['tek','building_condition'], var_name='year')
        df.rename(columns={'value':'bema_value'}, inplace=True)
        df['year'] = df['year'].astype(int)

        # append dataframes to list
        df_list.append(df)

        # increase header number for next iteration
        header = header + skip_rows
    
    # concat all tables into one dataframe ordered by tek
    bema_area = pd.concat(df_list)
    return bema_area

def get_ebm_area(building_category: BuildingCategory, database_manager: DatabaseManager, start_year: int = 2010, end_year: int = 2050):
    """
    Retrieves area forecast data per building category from the EBM model and formats it to a dataframe that are compatible for validation.  
    
    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - start_year (int, optional): The starting year for the forecast. Defaults to 2010.
    - end_year (int, optional): The ending year for the forecast. Defaults to 2050.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the EBM area data.
    """
    modelyears = YearRange(start_year, end_year)

    # Retrieve area data
    building = Buildings.build_buildings(building_category, database_manager)
    area_forecast = building.build_area_forecast(database_manager)

    demolition_floor_area = area_forecast.calc_total_demolition_area_per_year()

    constructed_floor_area = ConstructionCalculator.calculate_construction(building_category, 
                                                                          demolition_floor_area,
                                                                          database_manager,
                                                                          modelyears).accumulated_constructed_floor_area
    area = area_forecast.calc_area_dict(constructed_floor_area)

    df_list = []  
    for tek in building.tek_list:
        # Filter data and transform to df
        df = pd.DataFrame(area[tek])

        # Control that length of dataframe matches number of modelyears
        if len(df) != len(modelyears.year_range): 
            raise ValueError(f'Length of dataframe does not match number of modelyears. Length of df: {len(df)}. Number of modelyears {len(modelyears)}')
       
        # Format dataframe for validation/merge with BEMA data
        df.reset_index(inplace=True) # index to column
        df['tek'] = tek
        df = pd.melt(df, id_vars=['tek', 'year'], var_name='building_condition', value_name='ebm_value')
        df = df[['tek', 'building_condition', 'year', 'ebm_value']]
        df_list.append(df)

    ebm_area = pd.concat(df_list)
    return ebm_area  

def validate_area(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    Validates area data by comparing EBM and BEMA model results for a given building category. 

    Parameters:
    - building_category (BuildingCategory): The building category being validated.
    - database_manager (DatabaseManager): The database manager instance.
    - precision (int, optional): Decimal precision for comparing values. Defaults to 5.   
    """    
    bema_area = load_bema_area(building_category, database_manager)
    ebm_area = get_ebm_area(building_category, database_manager)

    data_name = 'area'
    join_cols = ['tek', 'building_condition', 'year']
    
    validate_data(building_category, data_name, ebm_area, bema_area, join_cols, precision)

def get_ebm_shares(building_category: BuildingCategory, database_manager: DatabaseManager, start_year: int = 2010, end_year: int = 2050):
    """
    Retrieves and formats shares data from the EBM model for a given building category and returns it as a DataFrame.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - start_year (int, optional): The starting year for the forecast. Defaults to 2010.
    - end_year (int, optional): The ending year for the forecast. Defaults to 2050.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the EBM shares data.
    """
    modelyears = [*range(start_year, end_year + 1)]
    
    building = Buildings.build_buildings(building_category, database_manager)
    shares = building.get_shares()

    df_list = []
    for condition in shares:
        shares_condition = shares[condition]
        df = pd.DataFrame(shares_condition)
        df.reset_index(inplace=True) # index to column
        df['building_condition'] = condition
        df = pd.melt(df, id_vars=['year', 'building_condition'], var_name='tek', value_name='ebm_value')
        df = df[['building_condition', 'tek', 'year', 'ebm_value']]
        df_list.append(df)
    
    ebm_shares = pd.concat(df_list)
    return ebm_shares  

def load_bema_shares(building_category: BuildingCategory, database_manager: DatabaseManager, start_row: int = 20, usecols: str = "E:AS"):
    """
    Loads shares data from the BEMA model for a given building category, formats it, and returns it as a DataFrame for validation.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (Buildings): The database manager instance for accessing building data.
    - start_row (int, optional): The row number in the sheet where data begins. Defaults to 20.
    - usecols (str, optional): Columns to be read from the sheet. Defaults to "E:AS".

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the BEMA shares data.
    """
    # Retrieve workbook and sheet names 
    workbook = os.environ.get('BEMA_SPREADSHEET')
    sheet = get_building_category_sheet(building_category, area_sheet=False)
    
    # Create building object to get length of TEK's for given building category
    building = Buildings.build_buildings(building_category, database_manager)
    tek_list = building.tek_list
    
    # Number of TEK's define the number of rows with data per condition in BEMA sheet
    n_tek = len(tek_list)

    # Number of rows between headers/tables in sheet
    skip_rows = n_tek + 3 

    # Define row number for first header in sheet
    header = start_row
    
    # Define building condition order according to BEMA order
    bema_building_condition_order = [BuildingCondition.SMALL_MEASURE, 
                                    BuildingCondition.RENOVATION, 
                                    BuildingCondition.RENOVATION_AND_SMALL_MEASURE,
                                    BuildingCondition.DEMOLITION,
                                    BuildingCondition.ORIGINAL_CONDITION]

    df_list = []
    for condition in bema_building_condition_order:
        # Read data from excel
        df = xlsx_to_df(workbook, sheet=sheet, header=header, usecols=usecols, n_rows=n_tek)
        
        # Format dataframe for validation/merge with EBM data
        df['building_condition'] = condition
        df['tek'] = tek_list
        df = pd.melt(df, id_vars=['building_condition', 'tek'], var_name='year')
        df['year'] = df['year'].astype(int)
        df.rename(columns={'value':'bema_value'}, inplace=True)
        df.sort_values(by=['building_condition', 'tek', 'year'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df_list.append(df)
        
        # Increase header number for next iteration
        header = header + skip_rows
    
    bema_shares = pd.concat(df_list)
    return bema_shares

def validate_shares(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    Validates shares data by comparing EBM and BEMA model results for a given building category.

    Parameters:
    - building_category (BuildingCategory): The building category being validated.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - precision (int, optional): Decimal precision for comparing values. Defaults to 5.
    """    
    ebm_shares = get_ebm_shares(building_category, database_manager)
    bema_shares = load_bema_shares(building_category, database_manager)

    data_name = 'shares'
    join_cols = ['building_condition', 'tek', 'year']
    
    validate_data(building_category, data_name, ebm_shares, bema_shares, join_cols, precision)

def get_ebm_scurves(building_category: BuildingCategory, database_manager: DatabaseManager):
    """
    Retrieves and formats S-curve data from the EBM model for a given building category and returns it as a DataFrame.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing data.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the EBM S-curve data.
    """    
    scurve_condition_list = BuildingCondition.get_scruve_condition_list()
    scurve_data_params = database_manager.get_scurve_params()

    scurve_params = FilterScurveParams.filter(building_category, scurve_condition_list, scurve_data_params)
    scurve_processor = ScurveProcessor(scurve_condition_list, scurve_params)

    scurves = scurve_processor.get_scurves()

    # Format dataframe for validation/merge with EBM data
    df = pd.DataFrame(scurves)
    df.reset_index(inplace=True) # index to column 
    df = pd.melt(df, id_vars=['age'], var_name='building_condition', value_name='ebm_value')
    
    return df


def load_bema_scurves(building_category: BuildingCategory, start_row: int = 11, n_rows: int = 6, usecols: str = 'E:ED'):
    """
    Loads S-curve data from the BEMA model for a given building category, formats it, and returns it as a DataFrame for validation.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - start_row (int, optional): The row number in the sheet where data begins. Defaults to 11.
    - n_rows (int, optional): Number of rows to read. Defaults to 6.
    - usecols (str, optional): Columns to be read from the sheet. Defaults to 'E:ED'.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the BEMA S-curve data.
    """
    # Retrieve workbook and sheet names 
    workbook = os.environ.get('BEMA_SPREADSHEET')
    sheet = get_building_category_sheet(building_category, area_sheet=False) 

    # Read data from excel
    df = xlsx_to_df(workbook, sheet=sheet, header=start_row, usecols=usecols, n_rows=n_rows)

    # Drop unwanted rows
    df = df.drop([0, 2, 4])

    # Add building_condition col
    bema_sorted_condition_list = ['demolition', 'small_measure', 'renovation']
    df['building_condition'] = bema_sorted_condition_list

    # Format dataframe for validation/merge with EBM data
    df = pd.melt(df, id_vars=['building_condition'], var_name='age', value_name='bema_value')
    df.sort_values(by=['building_condition', 'age'], inplace=True)
    df['age'] = df['age'].astype(int)

    return df


def validate_scurves(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    Validates S-curve data by comparing EBM and BEMA model results for a given building category.

    Parameters:
    - building_category (BuildingCategory): The building category being validated.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - precision (int, optional): Decimal precision for comparing values. Defaults to 5.
    """    
    ebm_scurves = get_ebm_scurves(building_category, database_manager)
    bema_scurves = load_bema_scurves(building_category)

    data_name = 'scurves'
    join_cols = ['building_condition', 'age']
    
    validate_data(building_category, data_name, ebm_scurves, bema_scurves, join_cols, precision)


def get_ebm_rush_rates(building_category: BuildingCategory, database_manager: DatabaseManager):
    """
    Retrieves and formats yearly rush rates from the EBM model for a given building category and returns it as a DataFrame.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the EBM rush rate data.
    """
    scurve_condition_list = BuildingCondition.get_scruve_condition_list()
    building = Buildings.build_buildings(building_category, database_manager)

    rate_dict = {}
    for condition in scurve_condition_list:
        scurve = building.build_scurve(condition)
        pre_rush_rate = scurve._pre_rush_rate
        rush_rate = scurve._rush_rate
        post_rush_rate = scurve._post_rush_rate
        r_dict = {
            'pre_rush_rate':pre_rush_rate,
            'rush_rate':rush_rate,
            'post_rush_rate':post_rush_rate
        } 
        rate_dict[condition] = r_dict

    # Format df for validation/merge with BEMA data
    rush_rates = pd.DataFrame(rate_dict)
    rush_rates.reset_index(inplace=True, names='rate_type')
    rush_rates = pd.melt(rush_rates, id_vars='rate_type', var_name='building_condition', value_name='ebm_value')
    rush_rates = rush_rates[['building_condition', 'rate_type', 'ebm_value']]

    return rush_rates

def load_bema_rush_rates(building_category: BuildingCategory, database_manager: DatabaseManager, start_row: int = 4, n_rows: int = 3, usecols: str = 'L:N'):
    """
    Loads rush rate data from the BEMA model for a given building category, formats it, and returns it as a DataFrame for validation.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - start_row (int, optional): The row number in the sheet where data begins. Defaults to 4.
    - n_rows (int, optional): Number of rows to read. Defaults to 3.
    - usecols (str, optional): Columns to be read from the sheet. Defaults to 'L:N'.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the BEMA rush rate data.
    """
    # Retrieve workbook and sheet names 
    workbook = os.environ.get('BEMA_SPREADSHEET')
    sheet = get_building_category_sheet(building_category, area_sheet=False) 

    # Fromat df for validation/merge with EBM data
    df = xlsx_to_df(workbook, sheet=sheet, header=start_row, usecols=usecols, n_rows=n_rows)
    bema_sorted_condition_list = ['small_measure', 'renovation', 'demolition']
    df['building_condition'] = bema_sorted_condition_list
    df.rename(columns={'Før rushet':'pre_rush_rate', 'I rushet':'rush_rate', 'Etter rushet':'post_rush_rate'}, inplace=True)
    df = pd.melt(df, id_vars='building_condition', var_name='rate_type', value_name='bema_value')
    
    return df

def validate_rush_rates(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    Validates yearly rush rates by comparing EBM and BEMA model results for a given building category.

    Parameters:
    - building_category (BuildingCategory): The building category being validated.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - precision (int, optional): Decimal precision for comparing values. Defaults to 5
    """    
    ebm_rush_rates = get_ebm_rush_rates(building_category, database_manager)
    bema_rush_rates = load_bema_rush_rates(building_category, database_manager)

    data_name = 'rush_rates'
    join_cols = ['building_condition', 'rate_type']
    
    validate_data(building_category, data_name, ebm_rush_rates, bema_rush_rates, join_cols, precision)


def get_ebm_construction(building_category: BuildingCategory, database_manager, start_year: int = 2010, end_year: int = 2050):
    """
    Retrieve accumulated construction data per building category from the EBM model and format it to a DataFrame that is compatible for validation.

    Parameters:
    - building_category (BuildingCategory): The building category being analyzed.
    - database_manager (DatabaseManager): The database manager instance for accessing building data.
    - start_year (int, optional): The starting year of the data to be retrieved. Defaults to 2010.
    - end_year (int, optional): The ending year of the data to be retrieved. Defaults to 2050.

    Returns:
    - pd.DataFrame: The formatted DataFrame containing the accumulated construction data from the EBM model.  
    """
    modelyears = YearRange(start_year, end_year)

    # Retrieve construction data
    building = Buildings.build_buildings(building_category, database_manager)
    area_forecast = building.build_area_forecast(database_manager)
    demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=modelyears.range())
    yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area,
                                                                       database_manager, modelyears)
    constructed_floor_area = yearly_constructed.accumulated_constructed_floor_area

    # Convert series to df and format for validation/merge with BEMA data
    df = constructed_floor_area.to_frame().reset_index(names='year')
    df.rename(columns={'accumulated_constructed_floor_area':'ebm_value'}, inplace=True)

    return df  


def load_bema_construction(building_category: BuildingCategory, start_year: int = 2010, end_year: int = 2050, sheet: str = 'Nybygging', usecols: str = 'E:AS'):
    """
    Retrieve accumulated construction data per building category from the BEMA model and format it to a DataFrame that is compatible for validation.

    Parameters
    ----------
    building_category : BuildingCategory
        The building category being analyzed.
    start_year : int, optional
        The starting year of the data to be retrieved. Defaults to 2010.
    end_year : int, optional
        The ending year of the data to be retrieved. Defaults to 2050.
    - sheet : str, optional
        The sheet name in the workbook containing the data. Defaults to 'Nybygging'.
    - usecols : str, optional
        The range of columns to be read from the sheet. Defaults to 'E:AS'.

    Returns
    -------
    pd.DataFrame
        The formatted DataFrame containing the accumulated construction data from the BEMA model.

    """
    # Dict with row nr for data to be read per building category
    data_row_construction_building_category = {
        BuildingCategory.HOUSE: 18,
        BuildingCategory.APARTMENT_BLOCK: 30,
        BuildingCategory.KINDERGARTEN: 48,
        BuildingCategory.SCHOOL: 62,
        BuildingCategory.UNIVERSITY: 76,
        BuildingCategory.OFFICE: 90,
        BuildingCategory.RETAIL: 104,
        BuildingCategory.HOTEL: 118,
        BuildingCategory.HOSPITAL: 132,
        BuildingCategory.NURSING_HOME: 146,
        BuildingCategory.CULTURE: 160,
        BuildingCategory.SPORTS: 174,
        BuildingCategory.STORAGE: 189
    }
    
    # Retrieve workbook
    workbook = os.environ.get('BEMA_SPREADSHEET') 

    # List with all row numbers in excel sheet (0-indexed) 
    skiprows = [*range(0, 303)]

    # Index of row with data to be read
    data_row_idx = data_row_construction_building_category[building_category] - 1

    # Alter skiprows so that the desired row is read / don't skip the data row
    del skiprows[data_row_idx]

    # Modelyears list to be used as columns
    modelyears = [*range(start_year, end_year + 1)]

    # Format df for validation/merge with EBM data
    df = xlsx_to_df(workbook, sheet, header=None, usecols=usecols, n_rows=None, skiprows=skiprows, names=modelyears)
    df = pd.melt(df, var_name='year', value_name='bema_value')

    return df


def validate_construction(building_category: BuildingCategory, database_manager: DatabaseManager, precision: int = 5):
    """
    Validate accumulated constructed floor area from EBM and BEMA models for a given building category.

    Parameters
    ----------
    building_category : BuildingCategory
        The building category being validated.
    database_manager : DatabaseManager
        The database manager instance for accessing building data.
    precision : int, optional
        Decimal precision for comparing values. Defaults to 5.
    """    
    ebm_construction = get_ebm_construction(building_category, database_manager)
    bema_construction = load_bema_construction(building_category)

    data_name = 'construction'
    join_cols = ['year']
    
    validate_data(building_category, data_name, ebm_construction, bema_construction, join_cols, precision)


if __name__ == '__main__':
    database_manager = DatabaseManager()
    building_category = BuildingCategory.HOUSE
        
    for building_category in BuildingCategory:
        logger.info(building_category)
        validate_shares(building_category, database_manager)
