import io
import pandas as pd
import pytest

from ebm.heating_systems import HeatingSystems
from ebm.model.data_classes import YearRange
from ebm.heating_systems_projection import (add_missing_heating_systems,
                                            expand_building_category_tek,
                                            project_heating_systems,
                                            add_existing_tek_shares_to_projection,
                                            check_sum_of_shares,
                                            HeatingSystemsProjection)

# TODO: 
# add fixtures for the 3 input data files for one building category, 2 TEKS 
# add expected result dataframe and see that it runs ok. Refactor from there

BUILDING_CATEGORY = 'building_category'
TEK = 'TEK'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
TEK_SHARES = 'TEK_shares'


def test_validate_years_require_one_start_year():
    """
    ValueError if there is more than one start year in the 'shares_start_year' dataframe.
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2021,1
kindergarten,TEK97,Gas,2020,1                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    with pytest.raises(ValueError, match='More than one start year in dataframe.'):
        hsp = HeatingSystemsProjection(shares_start_year=shares_start_year,
                                efficiencies=pd.DataFrame(),
                                projection=pd.DataFrame(),
                                period=YearRange(2020,2022))


def test_validate_years_require_match_on_start_year():
    """
    ValueError if the start_year of the period is not equal to the start year in the 'shares_start_year' dataframe.
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
    
    with pytest.raises(ValueError, match="Start year in dataframe doesn't match start year for given period."):
        hsp = HeatingSystemsProjection(shares_start_year=shares_start_year,
                                    efficiencies=pd.DataFrame(),
                                    projection=pd.DataFrame(),
                                    period=YearRange(2021,2023))


def test_validate_years_require_matching_years_between_dataframes():
    """
    ValueError if the start_year in 'projection' is not equal to one year after the start year in 'shares_start_year'
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
        
    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.55
house,TEK97,Electricity,DH,0.25,0.5,0.55
apartment_block,TEK07,Electricity,DH,0.25,0.5,0.55                                                                                                                                                                                                         
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2020,2021,2022] ,skipinitialspace=True)
    

    with pytest.raises(ValueError, match="Years don't match between dataframes."):
        hsp = HeatingSystemsProjection(shares_start_year=shares_start_year,
                                    efficiencies=pd.DataFrame(),
                                    projection=projection,
                                    period=YearRange(2020,2022))


def test_validate_years_require_period_years_present_in_projection():
    """
    ValueError if the years in the given 'period' is not present in the years col of the 'projection' dataframe.   
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5                                                
""".strip()), 
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)
        
    projection = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.55
house,TEK97,Electricity,DH,0.25,0.5,0.55
apartment_block,TEK07,Electricity,DH,0.25,0.5,0.55                                                                                                                                                                                                         
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022,2023] ,skipinitialspace=True)
    
    with pytest.raises(ValueError, match="Years in dataframe not present in given period."):
        hsp = HeatingSystemsProjection(shares_start_year=shares_start_year,
                                    efficiencies=pd.DataFrame(),
                                    projection=projection,
                                    period=YearRange(2020,2030))


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

    result = project_heating_systems(shares_start_year_all_systems, projected_shares, YearRange(2020,2022))

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

    result = project_heating_systems(shares_start_year_all_systems, projected_shares, YearRange(2022,2023))

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


def test_check_sum_of_shares_ok():
    """
    """
    projected_shares = pd.read_csv(io.StringIO("""
house,TEK97,DH,2020,0.5
house,TEK97,Electricity,2020,0.5
house,TEK97,DH,2021,0.5
house,TEK97,Electricity,2021,0.5                                               
house,TEK07,Gas,2020,0.5
house,TEK07,DH,2020,0.5
house,TEK07,Gas,2021,0.4
house,TEK07,DH,2021,0.5                                               
kindergarten,TEK97,DH,2020,0.4
kindergarten,TEK97,Gas,2020,0.5
kindergarten,TEK97,DH,2021,0.5
kindergarten,TEK97,Gas,2021,0.5                                                                                                                                                                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES] ,skipinitialspace=True)
    
    with pytest.raises(ValueError):
        check_sum_of_shares(projected_shares, precision=1)


def test_calculate_projection_ok():
    """
    Test that calculate_projection method runs ok with input that is correct.
    """
    shares_start_year = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5
kindergarten,TEK97,Gas,2020,0.5                                                
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
kindergarten,TEK97,Electricity,DH,0.25,0.5,0.5,0.5                                                                                                                     
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022,2023,2024] ,skipinitialspace=True)
    
    hsp = HeatingSystemsProjection(shares_start_year=shares_start_year,
                                   efficiencies=efficiencies,
                                   projection=projection,
                                   period=YearRange(2020,2022))
    
    result = hsp.calculate_projection()
    
    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity,2020,0.5,0
kindergarten,TEK97,Electricity,2021,0.375,0
kindergarten,TEK97,Electricity,2022,0.25,0
kindergarten,TEK97,DH,2021,0.125,0
kindergarten,TEK97,DH,2022,0.25,0
kindergarten,TEK97,Gas,2020,0.5,0
kindergarten,TEK97,Gas,2021,0.5,0
kindergarten,TEK97,Gas,2022,0.5,0                                                                              
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES,'Value'] ,skipinitialspace=True)
    
    # dataframe formatting
    expected = expected.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    result = result.sort_values(by=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR])
    expected.reset_index(drop=True, inplace=True)
    result.reset_index(drop=True, inplace=True)
    
    pd.testing.assert_frame_equal(result, expected)

if __name__ == "__main__":
    pytest.main()
    
