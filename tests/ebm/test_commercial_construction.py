from unittest.mock import Mock

import pandas as pd

from ebm.model import BuildingCategory, DatabaseManager
from ebm.model.construction import ConstructionCalculator as ConCal
from ebm.model.data_classes import YearRange


def test_calculate_construction_calls_commercial_construction():
    bc = BuildingCategory.KINDERGARTEN
    demolition_floor_area = pd.Series([35_500, 35_500, 35_500, 35_500, 35_500,
                                       35_500, 35_500, 35_500],
                                      index=YearRange(2020, 2027).to_index())
    database_manager = DatabaseManager()
    database_manager.get_building_category_floor_area = Mock(return_value=pd.Series(
        [35_500, 35_500, 35_500, 35_500, 35_500],
        index=YearRange(2020, 2024).to_index()),
        name='area')
    database_manager.get_construction_population = Mock(return_value=pd.DataFrame(
        [{'household_size': 1, 'population': 100_000},{'household_size': 1, 'population': 100_000},
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

    ConCal.calculate_commercial_construction.assert_called_once()

    # Unset mock on ConstructionCalculator so that any following test using
    # calculate_commercial_construction will work as expected

    ConCal.calculate_commercial_construction = org_calculate_commercial_construction


def test_calculate_commercial_construction_return_series():
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

    assert isinstance(result, pd.Series), 'Expected calculate_commercial_construction to return pd.Series'
