import numpy as np
import pandas as pd
import pytest

from ebm.model.construction import ConstructionCalculator as ConCal
from ebm.model.data_classes import YearRange


def test_calculate_floor_area_over_building_growth_kindergarten():
    """ Test calculate_floor_area_over_building_growth using values for kindergarten """

    population_growth = pd.Series(
        data=[np.nan, 0.012783749698190627, 0.013325393446137923, 0.01311807167054102, 0.011438894140588296,
              0.011106944218266523, 0.00932730290475714, 0.008502517747941418, 0.007093904760781866,
              0.006834706197707874, 0.0067082247633216685, 0.004579531185375796, 0.004769145431673838,
              0.005079664968399955, 0.004901019172519616, 0.004851166447310984, 0.004851024763977696,
              0.004772224379971046, 0.004710110860255856, 0.004641954396903625, 0.004552515607949337,
              0.004461181697092975, 0.00434392065986855, 0.004246772394870035, 0.004164812385301975,
              0.004080834397051092, 0.004005293784151265, 0.0038722220422711118, 0.0036902603836130865,
              0.0035114845279617946, 0.0033421050242241623, 0.0031766233305012825, 0.0030111720747318937,
              0.002846866995466657, 0.002686160663372572, 0.0025245549248480437, 0.002360641918193185,
              0.002200080909776636, 0.0020412601991794954, 0.0018872707716841575, 0.0017373379956102664],
        index=[y for y in range(2010, 2051)])
    building_growth = pd.Series(
        data=[np.nan,
              0.07035928643459943, 0.04756747511027215, 0.042732522797172434, 0.05303365530129667] + [0.0] * 36,
        index=[y for y in range(2010, 2051)])

    years = YearRange(start=2010, end=2050)

    # Start years (2011 - 2014) use building growth over population growth
    calculated_building_growth_over_population_growth = pd.Series(
        data=[np.nan, 5.503806636996176, 3.56968635129183, 3.2575308223948776, 4.636257198422607],
        index=[2010, 2011, 2012, 2013, 2014])

    # The next six years (2015-2020) use the mean of the start years
    calculated_mean_build_over_pop = pd.Series(
        data=[4.24182025227637] * 6,
        index=[y for y in range(2015, 2021)])

    # The next 10 years use the mean of the starting years multiplied by a cut-off calculated from number of years
    #   since the start of the period (2020)
    calculated_years = pd.Series(data=[3.91763822705, 3.59345620182, 3.26927417659, 2.94509215137,
                                       2.62091012614, 2.29672810091, 1.97254607568, 1.64836405046, 1.32418202523],
                                 index=[y for y in range(2021, 2030)]
                                 )
    fixed_rate_from_2030 = pd.Series(
        data=[1.0] * 21,
        index=[y for y in range(2030, 2051)]
    )

    expected = pd.concat([calculated_building_growth_over_population_growth,
                          calculated_mean_build_over_pop,
                          calculated_years,
                          fixed_rate_from_2030])

    result = ConCal.calculate_floor_area_over_building_growth(
        building_growth=building_growth,
        population_growth=population_growth,
        years=years)

    pd.testing.assert_series_equal(result, expected)


def test_calculate_floor_area_over_building_growth():
    # Sample data
    building_growth = pd.Series([1.2, 1.3, 1.4, 1.5, 1.6], index=[2010, 2011, 2012, 2013, 2014])
    population_growth = pd.Series([1.1, 1.2, 1.3, 1.4, 1.5], index=[2010, 2011, 2012, 2013, 2014])
    years = YearRange(start=2010, end=2050)

    # Expected result
    expected_result = pd.Series(
        [np.nan, 1.083333, 1.076923, 1.071429, 1.066667, 1.074588, 1.074588, 1.074588, 1.074588, 1.074588, 1.074588] +
        [1.067129, 1.05967, 1.05221, 1.044752, 1.037293, 1.029835, 1.022376, 1.014918, 1.007459]
        +[1.000000] * 21,
        index=range(2010, 2051)
    )

    # Calculate result
    result = ConCal.calculate_floor_area_over_building_growth(building_growth, population_growth, years)

    # Assert the result is as expected
    pd.testing.assert_series_equal(result, expected_result)


def test_calculate_floor_area_growth():
    """ Test calculate_floor_area returning growth based on total_floor_area """
    total_floor_area = pd.Series({2010: 1000, 2011: 1100, 2012: 1210, 2013: 1331, 2014: 1464.1})
    period = YearRange(2010, 2014)
    expected_growth = pd.Series({2010: np.nan, 2011: 0.1, 2012: 0.1, 2013: 0.1, 2014: 0.1})

    result = ConCal.calculate_floor_area_growth(total_floor_area, period)

    pd.testing.assert_series_equal(result, expected_growth)


def test_calculate_constructed_floor_area_kindergarten():
    constructed_floor_area = pd.Series({2010: 97574, 2011: 90644, 2012: 65847, 2013: 62022, 2014: 79992, 2015: np.nan})
    demolition_floor_area = pd.Series(
        {2010: 0.0, 2011: 919.1642857142858, 2012: 919.1642857142851, 2013: 919.1642857142858, 2014: 919.1642857142856,
         2015: 919.164285714287, 2016: 919.1642857142851, 2017: 919.164285714286, 2018: 919.164285714286,
         2019: 919.1642857142851, 2020: 919.164285714287, 2021: 919.164285714287, 2022: 919.1642857142851,
         2023: 919.1642857142851, 2024: 919.164285714287, 2025: 919.164285714287})
    total_floor_area = pd.Series(
        {2010: 1275238.0, 2011: 1364962.8357142857, 2012: 1429890.6714285715, 2013: 1490993.5071428572,
         2014: 1570066.342857143, 2015: 1644037.9161657556, 2016: 1709083.8527497717, 2017: 1770723.930727143,
         2018: 1824006.9064976668, 2019: 1876887.7763141114, 2020: 1930294.775005581, 2021: 1964926.090165381,
         2022: 1998600.4339443436, 2023: 2031790.8266201413, 2024: 2061117.6001179067, 2025: 2087323.6206190905})
    period = YearRange(2010, 2025)
    expected_constructed = pd.Series(
        {2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0, 2015: 74890.73759432697,
         2016: 65965.10086973036, 2017: 62559.24226308569, 2018: 54202.14005623806, 2019: 53800.03410215887,
         2020: 54326.16297718395, 2021: 35550.479445514284, 2022: 34593.50806467679, 2023: 34109.556961511975,
         2024: 30245.937783479705, 2025: 27125.1847868981})

    result = ConCal.calculate_constructed_floor_area(
        constructed_floor_area,
        demolition_floor_area,
        total_floor_area,
        period)

    pd.testing.assert_series_equal(result, expected_constructed)


if __name__ == "__main__":
    pytest.main()
