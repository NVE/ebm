import pytest
import pandas as pd

from unittest.mock import Mock

from ebm.model.building_category import BuildingCategory
from ebm.model.construction import ConstructionCalculator as ConCal
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager


def test_calculate_construction_calls_commercial_construction():
    bc = BuildingCategory.STORAGE_REPAIRS
    demolition_floor_area = pd.Series([35_500, 35_500, 35_500, 35_500, 35_500,
                                       35_500, 35_500, 35_500],
                                      index=YearRange(2020, 2027).to_index())
    database_manager = DatabaseManager()
    database_manager.get_building_category_floor_area = Mock(return_value=pd.Series(
        [35_500, 35_500, 35_500, 35_500, 35_500],
        index=YearRange(2020, 2024).to_index()),
        name='area')
    database_manager.get_construction_population = Mock(return_value=pd.DataFrame(
        [{'household_size': 1, 'population': 100_000}, {'household_size': 1, 'population': 100_000},
         {'household_size': 1, 'population': 100_000}, {'household_size': 1, 'population': 100_000},
         {'household_size': 1, 'population': 100_000}, {'household_size': 1, 'population': 100_000},
         {'household_size': 1, 'population': 100_000}, {'household_size': 1, 'population': 100_000}],
        index=YearRange(2020, 2027).to_index()))

    database_manager.get_area_parameters = Mock(return_value=pd.DataFrame(
        [{'building_category': bc, 'area': 35_500}, {'building_category': bc, 'area': 35_500},
         {'building_category': bc, 'area': 35_500}, {'building_category': bc, 'area': 35_500},
         {'building_category': bc, 'area': 35_500}, {'building_category': bc, 'area': 35_500},
         {'building_category': bc, 'area': 35_500}, {'building_category': bc, 'area': 35_500}],
        index=YearRange(2020, 2027).to_index()
    ))
    period = YearRange(2020, 2027)
    database_manager.get_area_per_person = Mock(return_value=pd.Series([1.0, 1.2, 1.3, 1.4,
                                                                        1.3, 1.2, 1.1, 1.0],
                                                                       index=period.to_index(),
                                                                       name='area_by_person'))

    # Store the original calculate_commercial_construction
    org_calculate_commercial_construction = ConCal.calculate_commercial_construction

    ConCal.calculate_commercial_construction = Mock()
    ConCal.calculate_construction(
        building_category=bc,
        demolition_floor_area=demolition_floor_area,
        database_manager=database_manager,
        period=period)

    database_manager.get_area_per_person.assert_called_with(BuildingCategory.STORAGE_REPAIRS)
    ConCal.calculate_commercial_construction.assert_called_once()

    # Unset mock on ConstructionCalculator so that any following test using
    # calculate_commercial_construction will work as expected

    ConCal.calculate_commercial_construction = org_calculate_commercial_construction


def test_calculate_commercial_construction_return_dataframe():
    period = YearRange(2020, 2027)
    cc = ConCal()
    building_category = BuildingCategory.KINDERGARTEN
    population = pd.Series([1_000_000, 1_000_000, 1_000_000, 1_000_000,
                            1_000_000, 1_000_000, 1_000_000, 1_000_000],
                           index=period.to_index())
    area_by_person = pd.Series([1.0, 1.2, 1.3, 1.4,
                                1.3, 1.2, 1.1, 1.0],
                               index=period.to_index())
    demolition = pd.Series([10_000, 12_000, 14_000, 15_000,
                            16_000, 17_000, 18_000, 19_000],
                           index=period.to_index())

    result = ConCal.calculate_commercial_construction(
        building_category,
        population,
        area_by_person,
        demolition)

    assert isinstance(result, pd.DataFrame), 'Expected calculate_commercial_construction to return pd.DataFrame'


def test_calculate_commercial_construction_with_area_per_person_as_series():
    period = YearRange(2020, 2022)
    cc = ConCal()
    building_category = BuildingCategory.KINDERGARTEN
    population = pd.Series([1_000_000, 1_500_000, 2_000_000],
                           index=period.to_index())
    area_by_person = pd.Series([1.0, 1.2, 1.3],
                               index=period.to_index())
    demolition = pd.Series([10_000, 12_000, 14_000],
                           index=period.to_index())

    expected_yearly_construction = pd.Series([0.0, 810_000, 812_000],
                                             index=period.to_index())
    expected_accumulated_construction = pd.Series([0.0, 810_000, 1622_000],
                                             index=period.to_index())
    expected = pd.DataFrame({
            "constructed_floor_area": expected_yearly_construction,
            "accumulated_constructed_floor_area": expected_accumulated_construction
        })

    result = ConCal.calculate_commercial_construction(
        building_category,
        population,
        area_by_person,
        demolition)
    
    pd.testing.assert_frame_equal(result, expected)
    

def test_calculate_commercial_construction_with_area_per_person_as_float():
    period = YearRange(2020, 2022)
    cc = ConCal()
    building_category = BuildingCategory.KINDERGARTEN
    population = pd.Series([1_000_000, 1_500_000, 2_000_000],
                           index=period.to_index())
    area_by_person = 0.6
    demolition = pd.Series([10_000, 12_000, 14_000],
                           index=period.to_index())

    expected_yearly_construction = pd.Series([0.0, 310_000, 312_000],
                                             index=period.to_index())
    expected_accumulated_construction = pd.Series([0.0, 310_000, 622_000],
                                             index=period.to_index())
    expected = pd.DataFrame({
            "constructed_floor_area": expected_yearly_construction,
            "accumulated_constructed_floor_area": expected_accumulated_construction
        })

    result = ConCal.calculate_commercial_construction(
        building_category,
        population,
        area_by_person,
        demolition)
    
    pd.testing.assert_frame_equal(result, expected)


def test_calculate_commercial_construction_strip_values_outside_demolition_index():
    """
    When population has a longer index than demolition, filter out excess population
    """
    building_category = BuildingCategory.KINDERGARTEN
    population = pd.Series([900_000, 1_000_000, 1_500_000, 2_000_000, 2_300_000],
                           index=YearRange(2019, 2023).to_index())
    demolition = pd.Series([10_000, 12_000, 14_000],
                           index=YearRange(2020, 2022).to_index())
    area_by_person = 0.6

    result = ConCal.calculate_commercial_construction(building_category, population, area_by_person, demolition)
    expected = pd.Series([0.0, 310_000.0, 312_000.0], index=YearRange(2020, 2022).to_index())

    pd.testing.assert_series_equal(result.constructed_floor_area, expected, check_names=False)


def test_calculate_commercial_construction_require_demolition_years_in_population():
    period = YearRange(2020, 2022)
    building_category = BuildingCategory.KINDERGARTEN
    population = pd.Series([1_000_000, 1_500_000, 2_000_000],
                           index=[period.to_index()])
    area_by_person = 0.6
    demolition = pd.Series([10_000, 12_000, 14_000, 16_000],
                           index=[2020, 2021, 2022, 2023])
    
    with pytest.raises(ValueError, match='years in demolition series not present in popolutation series'):
        ConCal.calculate_commercial_construction(
        building_category,
        population,
        area_by_person,
        demolition)