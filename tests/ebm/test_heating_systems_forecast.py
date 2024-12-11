import io
import typing
import pandas as pd
import pytest

from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory
from ebm.model.heating_systems import HeatingSystems
from ebm.heating_systems_projection import (add_missing_heating_systems,
                                          legge_til_ulike_oppvarmingslaster,
                                          aggregere_lik_oppvarming_fjern_0,
                                          expand_building_category_tek,
                                          project_heating_systems,
                                          add_existing_tek_shares_to_projection,
                                          main)

# TODO: 
# add fixtures for the 3 input data files for one building category, 2 TEKS 
# add expected result dataframe and see that it runs ok. Refactor from there

BUILDING_CATEGORY = 'building_category'
TEK = 'TEK'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
TEK_SHARES = 'TEK_shares'


def test_add_missing_heating_systems_ok():
    """
    Test that missing heating systems are added with default value = 0. 
    """
    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5                                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    result = add_missing_heating_systems(shares)

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5
kindergarten,TEK97,Electric boiler,2020,0.0
kindergarten,TEK97,Electricity,2020,0.0
kindergarten,TEK97,Gas,2020,0.0                                       
kindergarten,TEK97,Electricity - Bio,2020,0.0
kindergarten,TEK97,DH - Bio,2020,0.0
kindergarten,TEK97,HP - Bio,2020,0.0
kindergarten,TEK97,HP - Electricity,2020,0.0
kindergarten,TEK97,HP Central heating - DH,2020,0.0
kindergarten,TEK97,HP Central heating,2020,0.0
kindergarten,TEK97,HP Central heating - Gas,2020,0.0
kindergarten,TEK97,Electric boiler - Solar,2020,0.0
kindergarten,TEK97,HP Central heating - Bio,2020,0.0                                                                                                    
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    expected = expected.sort_values(by=[BUILDING_CATEGORY, TEK, HEATING_SYSTEMS])
    result = result.sort_values(by=[BUILDING_CATEGORY, TEK, HEATING_SYSTEMS])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)

    pd.testing.assert_frame_equal(result, expected)


def test_add_missing_heating_systems_require_start_year_match():
    """
    Raise ValueError if given start year doesn't match year in input file.
    """
    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.5                                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    with pytest.raises(ValueError):
        add_missing_heating_systems(shares, start_year=2023)


def test_expand_building_categoy_tek_all_categories():
    """
    Checks if all categories are added if building_category value == default.
    """
    forecast = pd.read_csv(io.StringIO("""
default,default,gas,DH,0.05,0.075    
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)
    result = expand_building_category_tek(forecast)
    result_categories = result[BUILDING_CATEGORY].unique()
    expected_categories = ['house', 'apartment_block', 'kindergarten', 'school', 'university', 'office', 'retail',
                           'hotel', 'hospital', 'nursing_home', 'culture', 'sports', 'storage_repairs']
    invalid_categories = [bc for bc in result_categories if bc not in expected_categories]
    assert not invalid_categories


def test_expand_building_categoy_tek_residential_categories():
    """
    Checks if correct categories are added if building_category value == residential.
    """
    forecast = pd.read_csv(io.StringIO("""
residential,default,gas,DH,0.05,0.075    
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)
    result = expand_building_category_tek(forecast)
    result_categories = result[BUILDING_CATEGORY].unique()
    residential_categories = ['house', 'apartment_block']
    invalid_categories = [bc for bc in result_categories if bc not in residential_categories]
    assert not invalid_categories


def test_expand_building_categoy_tek_non_residential_categories():
    """
    Checks if correct categories are added if building_category value == non_residential.
    """
    forecast = pd.read_csv(io.StringIO("""
non_residential,default,gas,DH,0.05,0.075    
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)
    result = expand_building_category_tek(forecast)
    result_categories = result[BUILDING_CATEGORY].unique()
    non_residential_categories = ['kindergarten', 'school', 'university', 'office', 'retail', 'hotel',
                                  'hospital', 'nursing_home', 'culture', 'sports', 'storage_repairs']
    invalid_categories = [bc for bc in result_categories if bc not in non_residential_categories]
    assert not invalid_categories


def test_project_heating_systems_ok():

    shares_start_year_all_systems = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,DH,2020,0.0                                                                                                   
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)

    projected_shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)

    result = project_heating_systems(shares_start_year_all_systems, projected_shares)

    expected = pd.read_csv(io.StringIO("""
2021,kindergarten,TEK97,DH,0.25
2022,kindergarten,TEK97,DH,0.5
2021,kindergarten,TEK97,Electricity,0.75
2022,kindergarten,TEK97,Electricity,0.5                                                                                                                   
""".strip()), 
names=[YEAR,BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,TEK_SHARES], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.skip()
def test_project_heating_systems_different_years_in_data():
    """
    """
    shares_start_year_all_systems = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2022,1
kindergarten,TEK97,DH,2022,0.0                                                                                                   
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)

    projected_shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.75                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022,2023] ,skipinitialspace=True)

    result = project_heating_systems(shares_start_year_all_systems, projected_shares)

    expected = pd.read_csv(io.StringIO("""
2023,kindergarten,TEK97,DH,0.75
2023,kindergarten,TEK97,Electricity,0.25                                                                                                                   
""".strip()), 
names=[YEAR,BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,TEK_SHARES], skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    
    pd.testing.assert_frame_equal(result, expected)


def test_add_existing_tek_shares_to_projection_ok():
    """
    Test that function returns expected result with ok input.
    """
    projected_shares = pd.read_csv(io.StringIO("""
2021,kindergarten,TEK97,DH,0.25
2022,kindergarten,TEK97,DH,0.5
2021,kindergarten,TEK97,Electricity,0.75
2022,kindergarten,TEK97,Electricity,0.5                                                                                                                   
""".strip()), 
names=[YEAR,BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,TEK_SHARES], skipinitialspace=True)
    
    shares = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,Gas,2020,1                       
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    result = add_existing_tek_shares_to_projection(projected_shares, 
                                                   shares,
                                                   period=YearRange(2020,2022))
    
    #TODO: should DH = 0 in 2020 also be included in results? 
    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,Electricity,2021,0.75
kindergarten,TEK97,Electricity,2022,0.5
kindergarten,TEK97,DH,2021,0.25
kindergarten,TEK97,DH,2022,0.5
kindergarten,TEK97,Gas,2020,1
kindergarten,TEK97,Gas,2021,1
kindergarten,TEK97,Gas,2022,1                                                                              
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES] ,skipinitialspace=True)

    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    pd.testing.assert_frame_equal(result, expected)


def test_main_ok():
    """
    Test that main function runs ok with input that is correct.
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1
kindergarten,TEK97,Gas,2020,1                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)

    efficiencies = pd.read_csv(io.StringIO("""
Electric boiler,0
DH,0
Electricity,0
Gas,0
Electricity - Bio,0
DH - Bio,0
HP - Bio,0
HP - Electricity,0
HP Central heating - DH,0
HP Central heating,0
HP Central heating - Gas,0
Electric boiler - Solar,0
HP Central heating - Bio,0                                                                                    
""".strip()), 
names=[HEATING_SYSTEMS, 'Value'], skipinitialspace=True)

    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)

    result = main(shares_start_year, efficiencies, projection, period=YearRange(2020,2022))

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,1,0
kindergarten,TEK97,Electricity,2021,0.75,0
kindergarten,TEK97,Electricity,2022,0.5,0
kindergarten,TEK97,DH,2021,0.25,0
kindergarten,TEK97,DH,2022,0.5,0
kindergarten,TEK97,Gas,2020,1,0
kindergarten,TEK97,Gas,2021,1,0
kindergarten,TEK97,Gas,2022,1,0                                                                              
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES,'Value'] ,skipinitialspace=True)
    
    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.skip()
def test_main_different_periods():
    """
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2022,1
kindergarten,TEK97,Gas,2022,1                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)

    efficiencies = pd.read_csv(io.StringIO("""
Electric boiler,0
DH,0
Electricity,0
Gas,0
Electricity - Bio,0
DH - Bio,0
HP - Bio,0
HP - Electricity,0
HP Central heating - DH,0
HP Central heating,0
HP Central heating - Gas,0
Electric boiler - Solar,0
HP Central heating - Bio,0                                                                                    
""".strip()), 
names=[HEATING_SYSTEMS, 'Value'], skipinitialspace=True)

    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.1,0.25,0.5                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022,2023] ,skipinitialspace=True)

    result = main(shares_start_year, efficiencies, projection, period=YearRange(2022,2023))

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2022,1,0
kindergarten,TEK97,Electricity,2023,0.5,0
kindergarten,TEK97,DH,2023,0.5,0
kindergarten,TEK97,Gas,2022,1,0
kindergarten,TEK97,Gas,2023,1,0                                                                              
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES,'Value'] ,skipinitialspace=True)
    
    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    
    pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    pytest.main()
    
