import pandas as pd

from ebm.model import BuildingCategory
from ebm.model.construction import ConstructionCalculator as ConCal
from ebm.model.data_classes import YearRange


def test_calculate_construction_calls_commercial_construction():
    #cc = ConCal()
    building_category = BuildingCategory.KINDERGARTEN
    demolition_floor_area = None
    database_manager = None
    period = YearRange(2020, 2027)

    result = ConCal.calculate_construction(
        building_category,
        demolition_floor_area,
        database_manager,
        period)


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

    result = cc.calculate_commercial_construction(building_category,
                                                      population,
                                                      area_by_person,
                                                      demolition)

    assert isinstance(result, pd.Series), 'Expected calculate_commercial_construction to return pd.Series'

