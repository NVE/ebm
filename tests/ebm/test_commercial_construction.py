import numpy as np
import pandas as pd
import pytest

from ebm.model import BuildingCategory
from ebm.model.construction import ConstructionCalculator as ConCal
from ebm.model.data_classes import YearRange


@pytest.fixture
def default_input() -> dict:
    return {
        'population': {
            2010: 4858199, 2011: 4920305, 2012: 4985870, 2013: 5051275, 2014: 5109056, 2015: 5165802,
            2016: 5213985, 2017: 5258317, 2018: 5295619, 2019: 5331813, 2020: 5367580, 2021: 5392161, 2022: 5417877,
            2023: 5445398, 2024: 5472086, 2025: 5498632, 2026: 5525306, 2027: 5551674, 2028: 5577823, 2029: 5603715,
            2030: 5629226, 2031: 5654339, 2032: 5678901, 2033: 5703018, 2034: 5726770, 2035: 5750140, 2036: 5773171,
            2037: 5795526, 2038: 5816913, 2039: 5837339, 2040: 5856848, 2041: 5875453, 2042: 5893145, 2043: 5909922,
            2044: 5925797, 2045: 5940757, 2046: 5954781, 2047: 5967882, 2048: 5980064, 2049: 5991350, 2050: 6001759,
            2051: 6012168, 2052: 6022577, 2053: 6032986, 2054: 6043395, 2055: 6053804, 2056: 6064213, 2057: 6074622,
            2058: 6085031, 2059: 6095440, 2060: 6105849, 2061: 6105849
        },
        'household_size': {
            2010: 2.22, 2011: 2.22, 2012: 2.22, 2013: 2.2, 2014: 2.2, 2015: 2.2, 2016: 2.19, 2017: 2.19,
            2018: 2.17, 2019: 2.16, 2020: 2.15, 2021: 2.14, 2022: 2.13, 2023: 2.12, 2024: 2.115,
            2025: 2.11, 2026: 2.105, 2027: 2.1, 2028: 2.095, 2029: 2.09, 2030: 2.085, 2031: 2.081,
            2032: 2.077, 2033: 2.073, 2034: 2.07, 2035: 2.067, 2036: 2.064, 2037: 2.062, 2038: 2.06,
            2039: 2.059, 2040: 2.058, 2041: 2.057, 2042: 2.056, 2043: 2.055, 2044: 2.054, 2045: 2.053,
            2046: 2.052, 2047: 2.051, 2048: 2.05, 2049: 2.05, 2050: 2.05, 2051: 2.05, 2052: 2.05, 2053: 2.05,
            2054: 2.05, 2055: 2.05, 2056: 2.05, 2057: 2.05, 2058: 2.05, 2059: 2.05, 2060: 2.05, 2061: 2.05
        }

    }


@pytest.fixture
def kindergarten() -> dict:
    return {
        'constructed_floor_area':
            {2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0, 2015: 74890.73759432697,
             2016: 65965.10086973036, 2017: 62559.24226308569, 2018: 54202.14005623806, 2019: 53800.03410215887,
             2020: 54326.16297718395, 2021: 35550.479445514284, 2022: 34593.50806467679, 2023: 34109.556961511975,
             2024: 30245.937783479705, 2025: 27125.1847868981},
        'total_floor_area':
            {2010: 1275238.0, 2011: 1364962.8357142857, 2012: 1429890.6714285715, 2013: 1490993.5071428572,
             2014: 1570066.342857143, 2015: 1644037.9161657556, 2016: 1709083.8527497717,
             2017: 1770723.930727143, 2018: 1824006.9064976668, 2019: 1876887.7763141114,
             2020: 1930294.775005581, 2021: 1964926.090165381, 2022: 1998600.4339443436,
             2023: 2031790.8266201413, 2024: 2061117.6001179067, 2025: 2087323.6206190905,
             2026: 2110579.505206357, 2027: 2130447.3028574944, 2028: 2146988.0476022293,
             2029: 2160185.137790355, 2030: 2170019.4143462055, 2031: 2179700.265239823,
             2032: 2189168.7102543195, 2033: 2198465.611500741, 2034: 2207621.80830818,
             2035: 2216630.7473192043, 2036: 2225509.0046732007, 2037: 2234126.669696369,
             2038: 2242371.1788375233, 2039: 2250245.230537959, 2040: 2257765.7864286765,
             2041: 2264937.8579006535, 2042: 2271757.975529367, 2043: 2278225.3683315897,
             2044: 2284345.0476982994, 2045: 2290112.0022385186, 2046: 2295518.13662836,
             2047: 2300568.4622588023, 2048: 2305264.521096299, 2049: 2309615.1794479643,
             2050: 2313627.7616544575},
        'floor_area_over_population_growth':
            {2010: np.nan, 2011: 5.503806636996176, 2012: 3.56968635129183, 2013: 3.2575308223948776,
             2014: 4.636257198422607, 2015: 4.241820252276373, 2016: 4.241820252276373, 2017: 4.241820252276373,
             2018: 4.241820252276373, 2019: 4.241820252276373, 2020: 4.241820252276373, 2021: 3.9176382270487355,
             2022: 3.5934562018210983, 2023: 3.269274176593461, 2024: 2.9450921513658237, 2025: 2.6209101261381864,
             2026: 2.296728100910549, 2027: 1.9725460756829118, 2028: 1.6483640504552746, 2029: 1.3241820252276373,
             2030: 1.0, 2031: 1.0, 2032: 1.0, 2033: 1.0, 2034: 1.0, 2035: 1.0, 2036: 1.0, 2037: 1.0, 2038: 1.0,
             2039: 1.0, 2040: 1.0, 2041: 1.0, 2042: 1.0, 2043: 1.0, 2044: 1.0, 2045: 1.0, 2046: 1.0, 2047: 1.0,
             2048: 1.0, 2049: 1.0, 2050: 1.0},
        'demolition_floor_area':
            {2010: 0.0, 2011: 919.1642857142858, 2012: 919.1642857142851, 2013: 919.1642857142858,
             2014: 919.1642857142856, 2015: 919.164285714287, 2016: 919.1642857142851, 2017: 919.164285714286,
             2018: 919.164285714286, 2019: 919.1642857142851, 2020: 919.164285714287, 2021: 919.164285714287,
             2022: 919.1642857142851, 2023: 919.1642857142851, 2024: 919.164285714287, 2025: 919.164285714287,
             2026: 919.1642857142833, 2027: 919.164285714287, 2028: 2688.4857142857145, 2029: 2688.4857142857145,
             2030: 5282.0776190476245, 2031: 5282.077619047614, 2032: 5282.077619047617, 2033: 5282.077619047617,
             2034: 5282.077619047617, 2035: 5282.077619047617, 2036: 5282.077619047617, 2037: 5282.077619047617,
             2038: 5282.077619047617, 2039: 5282.077619047617, 2040: 5282.077619047617, 2041: 5282.077619047617,
             2042: 6130.231190476188, 2043: 6130.231190476203, 2044: 8622.681666666656, 2045: 8622.681666666656,
             2046: 8622.681666666671, 2047: 8622.681666666671, 2048: 8622.681666666671, 2049: 8622.681666666642,
             2050: 8622.681666666671},
        'accumulated_constructed_floor_area':
            {2010: 97574.0, 2011: 188218.0, 2012: 254065.0, 2013: 316087.0, 2014: 396079.0, 2015: 470969.73759432696,
             2016: 536934.8384640573, 2017: 599494.080727143, 2018: 653696.220783381, 2019: 707496.2548855399,
             2020: 761822.4178627238, 2021: 797372.8973082381, 2022: 831966.4053729149, 2023: 866075.9623344268,
             2024: 896321.9001179065, 2025: 923447.0849048046, 2026: 947622.1337777856, 2027: 968409.0957146371,
             2028: 987638.3261736577, 2029: 1003523.902076069, 2030: 1018640.2562509673, 2031: 1033603.1847636325,
             2032: 1048353.7073971764, 2033: 1062932.6862626455, 2034: 1077370.960689132, 2035: 1091661.977319204,
             2036: 1105822.312292248, 2037: 1119722.0549344642, 2038: 1133248.641694666, 2039: 1146404.771014149,
             2040: 1159207.4045239142, 2041: 1171661.5536149389, 2042: 1184611.9024341286, 2043: 1197209.5264268273,
             2044: 1211951.8874602036, 2045: 1226341.5236670894, 2046: 1240370.3397235975, 2047: 1254043.3470207064,
             2048: 1267362.0875248697, 2049: 1280335.4275432017, 2050: 1292970.6914163616}
    }


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
        index=YearRange(2010, 2050).to_index())
    building_growth = pd.Series(
        data=[np.nan,
              0.07035928643459943, 0.04756747511027215, 0.042732522797172434, 0.05303365530129667] + [0.0] * 36,
        index=YearRange(2010, 2050).to_index())

    years = YearRange(start=2010, end=2050)

    # Start years (2011 - 2014) use building growth over population growth
    calculated_building_growth_over_population_growth = pd.Series(
        data=[np.nan, 5.503806636996176, 3.56968635129183, 3.2575308223948776, 4.636257198422607],
        index=YearRange(2010, 2014).to_index())

    # The next six years (2015-2020) use the mean of the start years
    calculated_mean_build_over_pop = pd.Series(
        data=[4.24182025227637] * 6,
        index=YearRange(2015, 2020).to_index())

    # The next 10 years use the mean of the starting years multiplied by a cut-off calculated from number of years
    #   since the start of the period (2020)
    calculated_years = pd.Series(data=[3.91763822705, 3.59345620182, 3.26927417659, 2.94509215137,
                                       2.62091012614, 2.29672810091, 1.97254607568, 1.64836405046, 1.32418202523],
                                 index=YearRange(2021, 2029).to_index())
    fixed_rate_from_2030 = pd.Series(
        data=[1.0] * 21,
        index=YearRange(2030, 2050).to_index()
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
        + [1.000000] * 21,
        index=YearRange(2010, 2050).to_index()
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


def test_calculate_constructed_floor_area_kindergarten(kindergarten):
    constructed_floor_area = pd.Series({2010: 97574, 2011: 90644, 2012: 65847, 2013: 62022, 2014: 79992})
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

    expected_constructed = pd.Series(kindergarten.get('constructed_floor_area'), name='constructed_floor_area')

    result = ConCal.calculate_constructed_floor_area(
        constructed_floor_area,
        demolition_floor_area,
        total_floor_area,
        period)

    pd.testing.assert_series_equal(result, expected_constructed)


def test_calculate_total_floor_area_as_kindergarten(kindergarten):
    years = YearRange(2010, 2050)
    floor_area_over_population_growth = pd.Series(
        data=kindergarten.get('floor_area_over_population_growth'),
        name='floor_area_over_population_growth')
    population_growth = pd.Series(
        data={2010: np.nan, 2011: 0.012783749698190627, 2012: 0.013325393446137923, 2013: 0.01311807167054102,
              2014: 0.011438894140588296, 2015: 0.011106944218266523, 2016: 0.00932730290475714,
              2017: 0.008502517747941418, 2018: 0.007093904760781866, 2019: 0.006834706197707874,
              2020: 0.0067082247633216685, 2021: 0.004579531185375796, 2022: 0.004769145431673838,
              2023: 0.005079664968399955, 2024: 0.004901019172519616, 2025: 0.004851166447310984,
              2026: 0.004851024763977696, 2027: 0.004772224379971046, 2028: 0.004710110860255856,
              2029: 0.004641954396903625, 2030: 0.004552515607949337, 2031: 0.004461181697092975,
              2032: 0.00434392065986855, 2033: 0.004246772394870035, 2034: 0.004164812385301975,
              2035: 0.004080834397051092, 2036: 0.004005293784151265, 2037: 0.0038722220422711118,
              2038: 0.0036902603836130865, 2039: 0.0035114845279617946, 2040: 0.0033421050242241623,
              2041: 0.0031766233305012825, 2042: 0.0030111720747318937, 2043: 0.002846866995466657,
              2044: 0.002686160663372572, 2045: 0.0025245549248480437, 2046: 0.002360641918193185,
              2047: 0.002200080909776636, 2048: 0.0020412601991794954, 2049: 0.0018872707716841575,
              2050: 0.0017373379956102664},
        name='population_growth')

    total_floor_area = pd.Series(
        data={2010: 1275238.0, 2011: 1364962.8357142857, 2012: 1429890.6714285715, 2013: 1490993.5071428572,
              2014: 1570066.342857143})

    expected = pd.Series(kindergarten.get('total_floor_area'), name='total_floor_area')

    result = ConCal.calculate_total_floor_area(
        floor_area_over_population_growth=floor_area_over_population_growth,
        population_growth=population_growth,
        total_floor_area=total_floor_area,
        period=years)

    pd.testing.assert_series_equal(result, expected)


def test_calculate_commercial_construction_kindergarten(default_input, kindergarten):
    period = YearRange(2010, 2050)
    total_floor_area = np.int64(1275238)
    constructed_floor_area = pd.Series(
        name='constructed_floor_area',
        data={2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0})
    demolition_floor_area = pd.Series(
        name='demolition_floor_area',
        data=kindergarten.get('demolition_floor_area'))

    population = pd.Series(name='population', data=default_input.get('population')).loc[period]

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=period)

    expected_acc_constructed = pd.Series(
        name='accumulated_constructed_floor_area',
        data={2010: 97574.0, 2011: 188218.0, 2012: 254065.0, 2013: 316087.0, 2014: 396079.0, 2015: 470969.73759432696,
              2016: 536934.8384640573, 2017: 599494.080727143, 2018: 653696.220783381, 2019: 707496.2548855399,
              2020: 761822.4178627238, 2021: 797372.8973082381, 2022: 831966.4053729149, 2023: 866075.9623344268,
              2024: 896321.9001179065, 2025: 923447.0849048046, 2026: 947622.1337777856, 2027: 968409.0957146371,
              2028: 987638.3261736577, 2029: 1003523.902076069, 2030: 1018640.2562509673, 2031: 1033603.1847636325,
              2032: 1048353.7073971764, 2033: 1062932.6862626455, 2034: 1077370.960689132, 2035: 1091661.977319204,
              2036: 1105822.312292248, 2037: 1119722.0549344642, 2038: 1133248.641694666, 2039: 1146404.771014149,
              2040: 1159207.4045239142, 2041: 1171661.5536149389, 2042: 1184611.9024341286, 2043: 1197209.5264268273,
              2044: 1211951.8874602036, 2045: 1226341.5236670894, 2046: 1240370.3397235975, 2047: 1254043.3470207064,
              2048: 1267362.0875248697, 2049: 1280335.4275432017, 2050: 1292970.6914163616})
    expected_acc_constructed.index = expected_acc_constructed.index.set_names('year')

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed)

    expected_total_floor_area = pd.Series(
        name='total_floor_area',
        data=kindergarten.get('total_floor_area'), index=YearRange(2010, 2050).to_index())

    pd.testing.assert_series_equal(result.total_floor_area, expected_total_floor_area)


def test_calculate_industrial_construction_storage_repairs(default_input):
    year_range = YearRange(2010, 2050)
    total_floor_area = np.int64(1275238)
    constructed_floor_area = pd.Series(
        name='constructed_floor_area',
        data={2010: 33755, 2011: 33755, 2012: 33755, 2013: 33755, 2014: 33755})
    demolition_floor_area = pd.Series(
        name='demolition_floor_area',
        data={y: 33755.0 for y in year_range})
    population = pd.Series(name='population', data=default_input.get('population')).loc[year_range]

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.STORAGE_REPAIRS,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=year_range)

    expected_constructed = pd.Series(name='constructed_floor_area', data=[33755.0]*41, index=year_range.to_index())
    pd.testing.assert_series_equal(result.constructed_floor_area, expected_constructed, check_names=False)

    expected_accumulated = pd.Series(expected_constructed.cumsum(), name='accumulated_constructed_floor_area')
    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_accumulated, check_names=False)


def test_calculate_commercial_construction_kindergarten_to_2030(default_input, kindergarten):
    """
            Test calculate_industrial_construction from 2010 to 2030
        """
    period = YearRange(2010, 2030)
    constructed_floor_area = pd.Series(name='constructed_floor_area',
                                       data={2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0})
    demolition_floor_area = pd.Series(name='demolition_floor_area', data=kindergarten.get('demolition_floor_area')).loc[
                            2010:2030]

    population = pd.Series(name='population', data=default_input.get('population')).loc[period]

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=np.int64(1275238),
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=period)

    expected_acc_constructed = pd.Series(name='accumulated_constructed_floor_area',
        data={2010: 97574.0, 2011: 188218.0, 2012: 254065.0, 2013: 316087.0, 2014: 396079.0, 2015: 470969.73759432696,
              2016: 536934.8384640573, 2017: 599494.080727143, 2018: 653696.220783381, 2019: 707496.2548855399,
              2020: 761822.4178627238, 2021: 797372.8973082381, 2022: 831966.4053729149, 2023: 866075.9623344268,
              2024: 896321.9001179065, 2025: 923447.0849048046, 2026: 947622.1337777856, 2027: 968409.0957146371,
              2028: 987638.3261736577, 2029: 1003523.902076069, 2030: 1018640.2562509673})
    expected_acc_constructed.index = expected_acc_constructed.index.set_names('year')

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed)

    expected_total_floor_area = pd.Series(name='total_floor_area', data=kindergarten.get('total_floor_area')).loc[
                                2010:2030]

    pd.testing.assert_series_equal(result.total_floor_area, expected_total_floor_area, check_names=False)


def test_calculate_commercial_construction_kindergarten_to_2060(default_input, kindergarten):
    """
        Test calculate_industrial_construction from 2010 to 2060
    """
    period = YearRange(2010, 2060)
    constructed_floor_area = pd.Series(name='constructed_floor_area',
                                       data={2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0})
    demolition_floor_area = pd.Series(name='demolition_floor_area', data=kindergarten.get('demolition_floor_area'))
    demolition_floor_area = pd.concat(
        [demolition_floor_area, pd.Series({y: 8622.68167 for y in period.subset(41, 10)})])

    population = pd.Series(name='population', data=default_input.get('population')).loc[2010:2050]
    population = pd.concat([population, pd.Series({y: 6001759 + (10 * y) for y in period.subset(41, 10)})])

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=np.int64(1275238),
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=period)

    expected_acc_constructed = pd.Series(name='accumulated_constructed_floor_area',
                                         data=kindergarten.get('accumulated_constructed_floor_area'))
    expected_acc_constructed = pd.concat([expected_acc_constructed, pd.Series(
        {2051: 1309499.8060823437, 2052: 1318126.3426684805, 2053: 1326752.8792546168, 2054: 1335379.4158407536,
         2055: 1344005.9524268904, 2056: 1352632.4890130272, 2057: 1361259.025599164, 2058: 1369885.5621853007,
         2059: 1378512.098771437, 2060: 1387138.6353575739})])
    expected_acc_constructed.name = 'accumulated_constructed_floor_area'

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed,
                                   check_names=False)


def test_calculate_commercial_construction_kindergarten_from_2011(default_input, kindergarten):
    total_floor_area = np.int64(1275238)
    constructed_floor_area = pd.Series(
        name='constructed_floor_area', data={2021: 97574.0, 2022: 90644.0, 2023: 65847.0, 2024: 62022.0, 2025: 79992.0})
    demolition_floor_area = pd.Series(name='demolition_floor_area', data=kindergarten.get('demolition_floor_area'))
    demolition_floor_area.index = demolition_floor_area.index + 11

    population = pd.Series(name='population', data=default_input.get('population')).loc[2010:2050]
    population.index = population.index + 11

    period = YearRange(2021, 2061)
    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=period)

    expected_acc_constructed = pd.Series(
        name='accumulated_constructed_floor_area', data=kindergarten.get('accumulated_constructed_floor_area').values())
    expected_acc_constructed.index = period.to_index()

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed)

    expected_total_floor_area = pd.Series(
        name='total_floor_area', data=kindergarten.get('total_floor_area').values(), index=period.to_index())

    pd.testing.assert_series_equal(result.total_floor_area, expected_total_floor_area)


def test_calculate_constructed_floor_area_culture(default_input):
    period = YearRange(2010, 2050)
    constructed_floor_area = pd.Series({2010: 43646.0, 2011: 72625.0, 2012: 73971.0, 2013: 50951.0, 2014: 47282.0})
    total_floor_area = 2_899_338

    demolition_floor_area = pd.Series(
        data={
            2010: np.nan, 2011: 6514.803571428638, 2012: 6514.803571428638, 2013: 6514.803571428172,
            2014: 6514.803571428638, 2015: 6514.803571428638, 2016: 6514.803571428638, 2017: 6514.803571428638,
            2018: 6515.8035714285725, 2019: 6515.8035714285725, 2020: 6515.80357142858, 2021: 6515.803571428565,
            2022: 6515.80357142858, 2023: 6515.80357142858, 2024: 6515.803571428565, 2025: 6515.80357142858,
            2026: 6515.803571428565, 2027: 6515.80357142858, 2028: 8499.792857142864, 2029: 8499.792857142835,
            2030: 35005.82309523813, 2031: 35005.82309523807, 2032: 35005.82309523807, 2033: 35005.8230952381,
            2034: 35005.82309523801, 2035: 35005.82309523813, 2036: 35005.82309523801, 2037: 35005.82309523813,
            2038: 35005.82309523801, 2039: 35005.82309523813, 2040: 35005.82309523807, 2041: 35005.82309523807,
            2042: 35969.34095238091, 2043: 35969.34095238091, 2044: 45517.42380952381, 2045: 45517.42380952381,
            2046: 45517.42380952393, 2047: 45517.423809523694, 2048: 45517.42380952381, 2049: 45517.42380952381,
            2050: 45517.42380952381})

    expect_constructed = pd.Series(
        {2010: 43646.0, 2011: 72625.0, 2012: 73971.0, 2013: 50951.0, 2014: 47282.0, 2015: 56435.39139011735,
         2016: 49107.890774816275, 2017: 45863.52521453006, 2018: 39747.97397897526, 2019: 38861.125415409384,
         2020: 38575.31197881227, 2021: 27936.89130081136, 2022: 28257.308141670597, 2023: 29062.02012957906,
         2024: 27675.28187208429, 2025: 26854.406778789067, 2026: 26234.440298789108, 2027: 25292.898523465672,
         2028: 26406.320826615905, 2029: 25518.183834014664, 2030: 51068.16674489324, 2031: 50817.576302630594,
         2032: 50470.65335366898, 2033: 50190.47057274709, 2034: 49960.6577299686, 2035: 49720.14127533493,
         2036: 49506.69866245211, 2037: 49081.07268514234, 2038: 48471.5964336085, 2039: 47866.52755166293,
         2040: 47289.162135695806, 2041: 46719.98183467728, 2042: 47108.6527727599, 2043: 46532.54660524649,
         2044: 55512.708409824525, 2045: 54936.60224231111, 2046: 54347.27396603511, 2047: 53766.13080470776,
         2048: 53187.506140286685, 2049: 52623.36283308279, 2050: 52071.18238618702})

    population = pd.Series(name='population', data=default_input.get('population')).loc[period]
    expected_constructed_floor_area = pd.Series(name='constructed_floor_area', data=expect_constructed)

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.CULTURE,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area,
                                                      population=population, period=period)

    pd.testing.assert_series_equal(result.constructed_floor_area, expected_constructed_floor_area,
                                   check_names=False)


def test_calculate_commercial_construction_kindergarten_to_2020(default_input, kindergarten):
    period = YearRange(2010, 2020)
    total_floor_area = np.int64(1275238)
    constructed_floor_area = pd.Series(
        name='constructed_floor_area',
        data={2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0})
    demolition_floor_area = pd.Series(
        name='demolition_floor_area',
        data=kindergarten.get('demolition_floor_area'))

    population = pd.Series(name='population', data=default_input.get('population')).loc[period]

    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area.loc[2010:2020],
                                                      population=population, period=period)

    expected_acc_constructed = pd.Series(
        name='accumulated_constructed_floor_area',
        data={2010: 97574.0, 2011: 188218.0, 2012: 254065.0, 2013: 316087.0, 2014: 396079.0, 2015: 470969.73759432696,
              2016: 536934.8384640573, 2017: 599494.080727143, 2018: 653696.220783381, 2019: 707496.2548855399,
              2020: 761822.4178627238})
    expected_acc_constructed.index = expected_acc_constructed.index.set_names('year')

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed)

    expected_total_floor_area = pd.Series(
        name='total_floor_area',
        data=dict(filter(lambda x: x[0] <= 2020, kindergarten.get('total_floor_area').items())), index=YearRange(2010, 2020).to_index())

    pd.testing.assert_series_equal(result.total_floor_area, expected_total_floor_area)


def test_calculate_commercial_construction_kindergarten_from_2011(default_input, kindergarten):
    period = YearRange(2011, 2020)
    total_floor_area = np.int64(1364963)
    constructed_floor_area = pd.Series(
        name='constructed_floor_area',
        data={2010: 97574.0, 2011: 90644.0, 2012: 65847.0, 2013: 62022.0, 2014: 79992.0})
    demolition_floor_area = pd.Series(
        name='demolition_floor_area',
        data=kindergarten.get('demolition_floor_area'))

    population = pd.Series(name='population', data=default_input.get('population')).loc[period]
    demolition_floor_area.loc[2011] = 0
    result = ConCal.calculate_industrial_construction(building_category=BuildingCategory.KINDERGARTEN,
                                                      total_floor_area=total_floor_area,
                                                      constructed_floor_area=constructed_floor_area,
                                                      demolition_floor_area=demolition_floor_area.loc[period],
                                                      population=population, period=period)
    expected_acc_constructed = pd.Series(
        name='accumulated_constructed_floor_area',
        data=[90644.0, 156491.0, 218513.0, 298505.0,
              366059.96180732665, 425312.9887184028, 481302.9645244456, 529662.1539001607,
              577526.936748859, 625726.3209422368], index=period.to_index())

    expected_acc_constructed.index = expected_acc_constructed.index.set_names('year')

    pd.testing.assert_series_equal(result.accumulated_constructed_floor_area, expected_acc_constructed)

    kindergarten_tfa = dict(
        filter(
            lambda x: period.start <= x[0] <= period.end,
            kindergarten.get('total_floor_area').items()))

    expected_total_floor_area = pd.Series(
        name='total_floor_area',
        data=[1364963.0, 1429890.8357142857, 1490993.6714285715, 1570066.5071428572,
              1636702.3046644696, 1695036.1672898314, 1750106.97881016, 1797547.0039001608,
              1844492.6224631448, 1891772.8423708084], index=period.to_index())

    pd.testing.assert_series_equal(result.total_floor_area, expected_total_floor_area)


def test_construction_works_when_total_floor_area_has_fewer_than_4_rows():
    years = YearRange(2011, 2018)
    building_category = BuildingCategory.KINDERGARTEN
    demolition = pd.Series(index=years.to_index(),
                           data=[0.0, 919.164285706933, 2688.485714264203, 2688.4857142642068,
                                 5282.077619025484, 5282.077619025484, 5282.077619025484, 8622.68166663713])
    total_floor_area = np.int64(1_275_238)
    population = {'population': {2011: 4_920_305, 2012: 4985870, 2013: 5051275, 2014: 5109056,
                                 2015: 5165802, 2016: 5213985, 2017: 5258317, 2018: 5295619},
                  'household_size': {2011: 2.22, 2012: 2.22, 2013: 2.2, 2014: 2.2,
                                     2015: 2.2, 2016: 2.19, 2017: 2.19, 2018: 2.17}}
    yearly_construction_floor_area = [97574.0, 90644.0, 65847.0, 62022.0,
                                      79992.0]

    result = ConCal.calculate_industrial_construction(
        building_category=building_category,
        total_floor_area=total_floor_area,
        constructed_floor_area=pd.Series(yearly_construction_floor_area, index=YearRange(2010, 2014)).loc[2011:2014],
        demolition_floor_area=demolition,
        population=pd.Series(population['population'], index=years.to_index()), period=years)

    expected_constructed_floor_area = pd.Series(data=[90644.0, 65847.0, 62022.0, 79992.0,
                                                      71028.00886455, 62951.653328721, 59817.48524542, 55673.859496936],
                                                index=years.to_index(),
                                                name='constructed_floor_area')

    pd.testing.assert_series_equal(result.constructed_floor_area, expected_constructed_floor_area)


if __name__ == "__main__":
    pytest.main()
