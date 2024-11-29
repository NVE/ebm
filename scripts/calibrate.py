import pandas as pd
import tkinter as tk

import pyperclip

from ebm.cmd.run_calculation import calculate_building_category_area_forecast
from ebm.cmd.run_calculation import calculate_building_category_energy_requirements, calculate_heating_systems
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory
from ebm.model import DatabaseManager


ELECTRICITY = 'Elektrisitet'
DISTRICT_HEATING = 'Fjernvarme'
BIO = 'Bio'
FOSSIL = 'Fossil'

HEATPUMP_AIR_SOURCE = 'luftluft'
HEATPUMP_WATER_SOUCE = 'vannbåren'

CALIBRATION_YEAR = 2023

model_period = YearRange(2020, 2050)
start_year = model_period.start
end_year = model_period.end


def extract_area_forecast(database_manager) ->pd.DataFrame:
    area_forecasts = []
    for building_category in BuildingCategory:
        area_forecast_result = calculate_building_category_area_forecast(
            building_category=building_category,
            database_manager=database_manager,
            start_year=start_year,
            end_year=end_year)
        area_forecasts.append(area_forecast_result)

    area_forecast = pd.concat(area_forecasts)
    return area_forecast


def extract_energy_requirements(area_forecast: pd.DataFrame, database_manager) -> pd.DataFrame:
    all_requirement = []

    for building_category in BuildingCategory:
        en_req = calculate_building_category_energy_requirements(
            building_category=building_category,
            area_forecast=area_forecast[area_forecast['building_category'] == building_category],
            database_manager=database_manager,
            start_year=start_year,
            end_year=end_year)
        all_requirement.append(en_req)

    energy_requirement = pd.concat(all_requirement)
    return energy_requirement


def extract_heating_systems(energy_requirements, database_manager) -> pd.DataFrame:
    heating_systems = calculate_heating_systems(energy_requirements=energy_requirements,
                                                database_manager=database_manager)

    # heating_systems[heating_systems['purpose']=='heating_rv']
    return heating_systems


def transform_heating_systems(heating_systems, calibration_year) -> pd.DataFrame:
    # Filter heating_rv
    heating_systems = heating_systems.loc[
        (slice(None), slice(None), 'heating_rv', slice(None), slice(None), slice(None))].copy()

    # Group building_categories
    heating_systems['is_residential'] = 'commercial'
    heating_systems.loc[['house', 'apartment_block'], 'is_residential'] = 'residential'
    grouper = ['Oppvarmingstyper', 'is_residential', 'year']
    year_slice = (slice(None), slice(None), calibration_year)
    heating_systems_2023: pd.DataFrame = heating_systems.groupby(by=grouper).sum('gwh').loc[year_slice]

    # Classify energy_source
    if 'energy_source' in heating_systems_2023.columns:
        heating_systems_2023.drop(columns=['energy_source'], inplace=True)
    heating_systems_2023.insert(0, 'energy_source', value=None)

    heating_systems_2023.loc['DH', 'energy_source'] = DISTRICT_HEATING
    heating_systems_2023.loc['HP Central heating - DH', 'energy_source'] = DISTRICT_HEATING
    heating_systems_2023.loc['DH - Bio', 'energy_source'] = DISTRICT_HEATING

    heating_systems_2023.loc['Gas', 'energy_source'] = FOSSIL

    heating_systems_2023.loc['HP Central heating - Gas', 'energy_source'] = HEATPUMP_AIR_SOURCE

    heating_systems_2023.loc['Electricity', 'energy_source'] = ELECTRICITY

    heating_systems_2023.loc['Electric boiler', 'energy_source'] = 'Tappevann'
    heating_systems_2023.loc['Electric boiler - Solar', 'energy_source'] = 'Tappevann'

    heating_systems_2023.loc['Electricity - Bio', 'energy_source'] = BIO

    heating_systems_2023.loc['HP - Bio', 'energy_source'] = HEATPUMP_WATER_SOUCE
    heating_systems_2023.loc['HP - Electricity', 'energy_source'] = HEATPUMP_AIR_SOURCE

    heating_systems_2023.loc['HP Central heating - Bio', 'energy_source'] = HEATPUMP_WATER_SOUCE
    heating_systems_2023.loc['HP Central heating', 'energy_source'] = HEATPUMP_WATER_SOUCE

    # Filter energy_use

    energy_use = heating_systems_2023[heating_systems_2023['energy_source'].isin([ELECTRICITY, BIO, FOSSIL,
                                                                                  DISTRICT_HEATING])].groupby(by=['is_residential', 'energy_source']).sum()[['gwh']].copy()

    # Group and sum energy_usage by energy_source
    df = energy_use.groupby(by=['is_residential', 'energy_source']).sum()[['gwh']].copy()

    df = df.reset_index().copy()[['is_residential', 'energy_source', 'gwh']]
    df = df.pivot(columns=['is_residential'], index=['energy_source'], values=['gwh'])
    df['comOres'] = df.loc[:, ('gwh', 'commercial')] / df.loc[:, ('gwh', 'residential')]

    df.insert(1, ('pct', 'commercial'), df.loc[:, ('gwh', 'commercial')] / df.loc[:, ('gwh', 'commercial')].sum())
    df.insert(2, ('pct', 'residential'), df.loc[:, ('gwh', 'residential')] / df.loc[:, ('gwh', 'residential')].sum())

    # Add total

    df['total'] = df[('gwh', 'commercial')] + df[('gwh', 'residential')]
    return df


def sort_heating_systems_by_energy_source(transformed):
    custom_order = [ELECTRICITY, BIO, FOSSIL, DISTRICT_HEATING]

    unsorted = transformed.reset_index()
    unsorted['energy_source'] = pd.Categorical(unsorted['energy_source'], categories=custom_order, ordered=True)
    df_sorted = unsorted.sort_values(by=['energy_source'])
    df_sorted = df_sorted.set_index([('energy_source', '')])

    return df_sorted


def copy_to_clipboard(text):
    r = tk.Tk()
    r.withdraw()  # Hide the main window
    r.clipboard_clear()  # Clear the clipboard
    r.clipboard_append(text)  # Append the text to the clipboard
    r.update()  # Update the clipboard
    #r.destroy()  # Destroy the main window


def main():
    database_manager = DatabaseManager()
    area_forecast = extract_area_forecast(database_manager)
    energy_requirements = extract_energy_requirements(area_forecast, database_manager)
    heating_systems = extract_heating_systems(energy_requirements, database_manager)
    
    transformed = transform_heating_systems(heating_systems, CALIBRATION_YEAR)
    sorted_df = sort_heating_systems_by_energy_source(transformed)

    print(transformed.to_markdown())
    transposed = sorted_df[[('gwh', 'residential'), ('gwh', 'commercial'), ('total', '')]].transpose()
    print(transposed.to_markdown())
    transposed = transposed.set_index(pd.Index(['Boliger', 'Yrkesbygg', 'Total'], name='gwh'))
    tabbed = transposed.round(1).to_csv(sep='\t', header=False, index_label=None).replace('.', ',')
    print(tabbed)
    pyperclip.copy(tabbed)


if __name__ == '__main__':
    main()
