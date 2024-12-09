import io
import typing
import pandas as pd
import pytest

from ebm.model.building_category import BuildingCategory
from ebm.model.heating_systems import HeatingSystems
from ebm.heating_systems_projection import (legge_til_alle_oppvarmingstyper,
                                          legge_til_ulike_oppvarmingslaster,
                                          aggregere_lik_oppvarming_fjern_0,
                                          expand_building_category_tek,
                                          framskrive_oppvarming,
                                          legge_til_resterende_aar_oppvarming,
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

@pytest.fixture
def shares() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
kindergarten,TEK97,DH,2020,0.1832382347789622
kindergarten,TEK97,Electric boiler,2020,0.5487908275136798
kindergarten,TEK97,Electricity,2020,0.1352944639341367
kindergarten,TEK97,Electricity - Bio,2020,0.01932495652066477
kindergarten,TEK97,Gas,2020,0.07299731601863742
kindergarten,TEK97,HP Central heating,2020,0.04035420123391918                                                                                                      
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES], skipinitialspace=True)


@pytest.fixture
def efficiencies() -> pd.DataFrame:
    return pd.read_csv(io.StringIO("""
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


@pytest.fixture
def forecast() -> pd.DataFrame:

    return pd.read_csv(io.StringIO("""
default,default,Gas,HP Central heating,0.05,0.075
default,default,Gas,Electric boiler,0.05,0.075
non_residential,TEK69,HP Central heating - Gas,HP Central heating,0.1,0.15
House,default,Electricity - Bio,HP - Bio,0.05000000000000001,0.05489399966624506
Apartment block,default,Electricity - Bio,HP Central heating - Bio,0.05000000000000001,0.05489399966624506
residential,default,HP - Electricity,HP - Bio,0.05000000000000001,0.055016300447270426
kindergarten+Office,TEK87+TEK97,Electricity,DH,0.05000000000000001,0.055016300447270426        
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,NEW_HEATING_SYSTEMS,2021,2022] ,skipinitialspace=True)

@pytest.mark.skip()
def test_legg_til_alle_oppvarmingstyper_ok(efficiencies):
    """
    """
    shares = pd.read_csv(io.StringIO("""
Bygningskategori,TEK,Oppvarmingstyper,Year,TEK_andeler
Kindergarten,TEK97,DH,2020,0.1832382347789622
Kindergarten,TEK97,Gas,2020,0.07299731601863742                                                                                               
""".strip()), skipinitialspace=True)
    
    expected = pd.read_csv(io.StringIO("""
Bygningskategori,TEK,Oppvarmingstyper,Year,TEK_andeler
Kindergarten,TEK97,DH,2020,0.1832382347789622
Kindergarten,TEK97,Gas,2020,0.07299731601863742
Kindergarten,TEK97,Electric boiler,2020,0.0
Kindergarten,TEK97,Electricity,2020,0.0
Kindergarten,TEK97,Electricity - Bio,2020,0.0
Kindergarten,TEK97,DH - Bio,2020,0.0
Kindergarten,TEK97,HP - Bio,2020,0.0
Kindergarten,TEK97,HP - Electricity,2020,0.0
Kindergarten,TEK97,HP Central heating - DH,2020,0.0
Kindergarten,TEK97,HP Central heating,2020,0.0
Kindergarten,TEK97,HP Central heating - Gas,2020,0.0
Kindergarten,TEK97,Electric boiler - Solar,2020,0.0
Kindergarten,TEK97,HP Central heating - Bio,2020,0.0                                                                                                    
""".strip()), skipinitialspace=True)
    
    result = legge_til_alle_oppvarmingstyper(shares, efficiencies)
    result.reset_index(drop=True, inplace=True)
    pd.testing.assert_frame_equal(result, expected)


# TODO: add tests to check if the different building categories are set properly. TEK??
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


def test_main_ok(shares, efficiencies, forecast):

    expected = pd.read_csv(io.StringIO("""
kindergarten,TEK97,Electricity - Bio,2021,0.01932495652066477,0
kindergarten,TEK97,Electricity - Bio,2022,0.01932495652066477,0
kindergarten,TEK97,DH,2021,0.19000295797566905,0
kindergarten,TEK97,DH,2022,0.19068163565561505,0
kindergarten,TEK97,Electric boiler,2021,0.5524406933146117,0
kindergarten,TEK97,Electric boiler,2022,0.5542656262150776,0
kindergarten,TEK97,Electricity,2021,0.12852974073742984,0
kindergarten,TEK97,Electricity,2022,0.12785106305748384,0
kindergarten,TEK97,Gas,2021,0.06569758441677367,0
kindergarten,TEK97,Gas,2022,0.0620477186158418,0
kindergarten,TEK97,HP Central heating,2021,0.044004067034851053,0
kindergarten,TEK97,HP Central heating,2022,0.045828999935316986,0
kindergarten,TEK97,DH,2020,0.1832382347789622,0
kindergarten,TEK97,Electric boiler,2020,0.5487908275136798,0
kindergarten,TEK97,Electricity,2020,0.1352944639341367,0
kindergarten,TEK97,Electricity - Bio,2020,0.01932495652066477,0
kindergarten,TEK97,Gas,2020,0.07299731601863742,0
kindergarten,TEK97,HP Central heating,2020,0.04035420123391918,0
""".strip()),
names=[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS,YEAR,TEK_SHARES,'Value'] ,skipinitialspace=True)
    
    result = main(shares, efficiencies, forecast)
    result = result[result[YEAR].isin([2020,2021,2022])]
    result.reset_index(drop=True, inplace=True)
    pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    pytest.main()
    
