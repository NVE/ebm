import pathlib
import pandas as pd
import pytest

import ebm
from ebm.model import FileHandler, DatabaseManager, Buildings, BuildingCategory
from ebm.model.area_forecast import AreaForecast
from ebm.model.area_forecast_new import AreaForecastNew
from ebm.model.building_condition import BuildingCondition
from ebm.model.data_classes import YearRange

@pytest.fixture
def area_forecast() -> AreaForecast:
    input_location = pathlib.Path(ebm.__file__).parent / 'data'
    file_handler = FileHandler(directory=input_location)
    dm = DatabaseManager(file_handler=file_handler)
    building_category =BuildingCategory.KINDERGARTEN
    buildings = Buildings.build_buildings(building_category=building_category,
                                          database_manager=dm)
    tek_list = buildings.tek_list
    tek_params = buildings.tek_params
    shares_per_condition = buildings.shares_per_condition
    
    area_start_year = dm.get_area_start_year()[building_category]

    area_forecast = AreaForecastNew(building_category, 
                                    area_start_year, 
                                    tek_list, 
                                    tek_params, 
                                    shares_per_condition)
    return area_forecast


@pytest.fixture
def accumulated_constructed_floor_area():
    acc_construction =  [97574.0, 188218.0, 254065.0, 316087.0, 396079.0, 470969.737594328, 536934.8384640587, 599494.0807271443,
            653696.2207833815, 707496.2548855395, 761822.4178627231, 797372.8973082342, 831966.4053729081,
            866075.9623344169, 896321.9001178928, 923447.084904787, 947622.1337777632, 968409.0957146097,
            987638.3261736097, 1003523.9020760005, 1018640.256250877, 1033603.1847635206, 1048353.7073970429,
            1062932.6862624898, 1077370.9606889542, 1091661.9773190045, 1105822.3122920264, 1119722.0549342209,
            1133248.6416944005, 1146404.7710138615, 1159207.4045236045, 1171661.553614607, 1184611.902433768,
            1197209.5264264382, 1211951.8874597854, 1226341.5236666417, 1240370.3397231207, 1254043.3470202,
            1267362.0875243337, 1280335.4275426366, 1292970.691415767]
    return pd.Series(acc_construction, index=YearRange(2010,2050).year_range)


def test_area_forecast_calc_area_with_construction_tek_for_kindergarten_tek07(area_forecast,
                                                                              accumulated_constructed_floor_area):
    """ Given accumulated_constructed_floor_area test that AreaForecast::_calc_area_with_construction_tek
            returns expected floor area for TEK07

        Parameters
        ----------
        area_forecast : fixture[AreaForecast]
            give access to a premade AreaForecast Object
        accumulated_constructed_floor_area: fixture[List[float]]
            constructed_floor_area common with TEK10 test
    """
    result = area_forecast.calc_area_with_construction("TEK07", BuildingCondition.ORIGINAL_CONDITION,accumulated_constructed_floor_area)

    expected_tek07 = [0.0, 157116.0, 222963.0, 284985.0, 284985.0, 282728.86875, 280472.7375, 278216.60625, 275960.475,
                      273704.34375, 271448.2125, 269192.08125, 265154.79375, 261117.50625, 257080.21875, 253042.93125,
                      249005.64375, 235825.0875, 222644.53125, 209463.975, 196283.41875, 183102.8625, 169922.30625,
                      156741.75, 143561.19375, 130380.6375, 117200.08125, 104019.525, 90838.96875, 77658.4125,
                      64477.85625, 51297.3, 34910.6625, 18524.025, 14249.25, 14249.25, 14249.25, 14249.25, 14249.25,
                      14249.25, 14249.25]
    expected_tek07 = pd.Series(expected_tek07, index=YearRange(2010,2050).year_range, name='area')
    expected_tek07.index.name = 'year'

    pd.testing.assert_series_equal(result, expected_tek07)


def test_area_forecast_calc_area_with_construction_tek_for_kindergarten_tek10(area_forecast,
                                                                              accumulated_constructed_floor_area):
    """ Given accumulated_constructed_floor_area test that AreaForecast::_calc_area_with_construction_tek
                returns expected floor area for TEK10
    """
    result = area_forecast.calc_area_with_construction("TEK10", BuildingCondition.ORIGINAL_CONDITION, accumulated_constructed_floor_area)
   
    expected_tek10 = [0.0, 0.0, 0.0, 0.0, 79992.0, 154882.73759, 220847.83846, 283407.08073, 337609.22078, 391409.25489,
                      445735.41786, 442206.67914, 438677.94041, 435149.20169, 431620.46296, 428091.72424, 424562.98551,
                      421034.24679, 414719.6617, 408405.07662, 402090.49153, 395775.90644, 389461.32136, 368846.05828,
                      348230.79521, 327615.53213, 307000.26905, 286385.00598, 265769.7429, 245154.47982, 224539.21675,
                      203923.95367, 183308.6906, 162693.42752, 142078.16444, 121462.90137, 100847.63829, 80232.37522,
                      54602.58869, 28972.80216, 22286.77089]
    expected_tek10 = pd.Series(expected_tek10, index=YearRange(2010,2050).year_range, name='area')
    expected_tek10.index.name = 'year'

    pd.testing.assert_series_equal(result, expected_tek10)


if __name__ == "__main__":
    pytest.main()
    
