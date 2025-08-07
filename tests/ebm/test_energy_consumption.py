import numpy as np
import pandas as pd
import pytest

from ebm.energy_consumption import EnergyConsumption


@pytest.fixture
def heating_systems_parameters_house_building_code07():
    heating_systems_parameters_house_building_code07 = pd.DataFrame(
        data=[
            ['house', 'TEK07', np.int64(2020), 'DH', np.float64(0.11371747224812079), 'DH', 'Ingen', 'Ingen', 'DH', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.99), np.float64(1.0), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'DH - Bio', np.float64(0.0033946606308616), 'DH', 'Bio', 'Ingen', 'DH', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.95), np.float64(0.05), np.float64(0.99), np.float64(0.65), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler', np.float64(0.022406810402312557), 'Electric boiler', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.98), np.float64(1.0), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler - Solar', np.float64(0.0003390668680222), 'Electric boiler', 'Solar', 'Ingen', 'Electricity', 'Solar', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(0.98), np.float64(0.7), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electricity', np.float64(0.4578496981974673), 'Electricity', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(1.0), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)], ['house', 'TEK07', np.int64(2020), 'Electricity - Bio', np.float64(0.2040037143152775), 'Electricity', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.7), np.float64(0.3), np.float64(1.0), np.float64(0.65), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP - Electricity', np.float64(0.0073046316982173), 'HP', 'Electricity', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.62), np.float64(0.38), np.float64(2.5), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)], ['house', 'TEK07', np.int64(2020), 'HP Central heating - Bio', np.float64(0.0086647944512573), 'HP Central heating', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.65), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP Central heating - Electric boiler', np.float64(0.18231915118846304), 'HP Central heating', 'Electric boiler', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.99), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)], ['house', 'TEK49', np.int64(2020), 'DH', np.float64(0.0213315113565833), 'DH', 'Ingen', 'Ingen', 'DH', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.99), np.float64(1.0), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)], ['house', 'TEK49', np.int64(2020), 'DH - Bio', np.float64(0.0076580066831269), 'DH', 'Bio', 'Ingen', 'DH', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.95), np.float64(0.05), np.float64(0.99), np.float64(0.65), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'Electric boiler', np.float64(0.0256775930931896), 'Electric boiler', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.98), np.float64(1.0), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'Electric boiler - Solar', np.float64(0.0003008594060781), 'Electric boiler', 'Solar', 'Ingen', 'Electricity', 'Solar', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(0.98), np.float64(0.7), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'Electricity', np.float64(0.12062163535825479), 'Electricity', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(1.0), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'Electricity - Bio', np.float64(0.17753878375790685), 'Electricity', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.7), np.float64(0.3), np.float64(1.0), np.float64(0.65), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'HP - Bio - Electricity', np.float64(0.5197916085732984), 'HP', 'Bio', 'Electricity', 'Electricity', 'Bio', 'Electricity', np.float64(0.28), np.float64(0.62), np.float64(0.1), np.float64(2.5), np.float64(0.65), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'HP - Electricity', np.float64(0.12326471144131464), 'HP', 'Electricity', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.62), np.float64(0.38), np.float64(2.5), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK49', np.int64(2020), 'HP Central heating - Electric boiler', np.float64(0.0038152903302471), 'HP Central heating', 'Electric boiler', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.99), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)]],
        columns=['building_category', 'building_code', 'year', 'heating_systems', 'heating_system_share', 'Grunnlast', 'Spisslast', 'Ekstralast', 'Grunnlast energivare', 'Spisslast energivare', 'Ekstralast energivare', 'Ekstralast andel', 'Grunnlast andel', 'Spisslast andel', 'Grunnlast virkningsgrad', 'Spisslast virkningsgrad', 'Ekstralast virkningsgrad', 'Tappevann', 'Tappevann energivare', 'Tappevann virkningsgrad', 'Spesifikt elforbruk', 'Kjoling virkningsgrad'])
    return heating_systems_parameters_house_building_code07


def test_calculate(heating_systems_parameters_house_building_code07):
    ec = EnergyConsumption(heating_systems_parameters_house_building_code07)

    energy_need_house_building_code07 = pd.DataFrame(
        data=[
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'heating_rv', np.float64(131957628.54948647), np.float64(39.52794605), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'heating_dhw', np.float64(99378601.09170927), np.float64(29.76888889), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'fans_and_pumps', np.float64(31565836.641483705), np.float64(9.455555556), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'lighting', np.float64(27363685.63968), np.float64(8.1968), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'electrical_equipment', np.float64(58487674.752), np.float64(17.52), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'cooling', np.float64(0.0), np.float64(0.0), np.float64(3338337.6)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'heating_rv', np.float64(0.0), np.float64(29.645959537499998), np.float64(0.0)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'heating_dhw', np.float64(0.0), np.float64(29.76888889), np.float64(0.0)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'fans_and_pumps', np.float64(0.0), np.float64(9.455555556), np.float64(0.0)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'lighting', np.float64(0.0), np.float64(8.1968), np.float64(0.0)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'electrical_equipment', np.float64(0.0), np.float64(17.52), np.float64(0.0)],
            ['house', 'TEK07', 'renovation_and_small_measure', np.int64(2020), 'cooling', np.float64(0.0), np.float64(0.0), np.float64(0.0)]],
        columns=['building_category', 'building_code', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2',
                 'm2']
    )

    energy_need_house_building_code49 = pd.DataFrame(
        data=[['house', 'TEK49', 'original_condition', np.int64(2020), 'cooling', np.float64(0.0), np.float64(0.0), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'original_condition', np.int64(2020), 'electrical_equipment', np.float64(53005673.910250045), np.float64(14.8909375), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'original_condition', np.int64(2020), 'fans_and_pumps', np.float64(1758661.3177500016), np.float64(0.4940625), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'original_condition', np.int64(2020), 'heating_dhw', np.float64(90107754.61375007), np.float64(25.3140625), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'original_condition', np.int64(2020), 'heating_rv', np.float64(469855945.290763), np.float64(131.99710520000002), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'original_condition', np.int64(2020), 'lighting', np.float64(24807336.162120022), np.float64(6.96915), np.float64(3559592.800000003)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'cooling', np.float64(0.0), np.float64(0.0), np.float64(60526768.34152376)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'electrical_equipment', np.float64(901300324.450609), np.float64(14.8909375), np.float64(60526768.34152376)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'fans_and_pumps', np.float64(29904006.483734082), np.float64(0.4940625), np.float64(60526768.34152376)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'heating_dhw', np.float64(1532178396.7203536), np.float64(25.3140625), np.float64(60526768.34152376)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'heating_rv', np.float64(5992018656.144107), np.float64(98.99782890000002), np.float64(60526768.34152376)],
              ['house', 'TEK49', 'renovation_and_small_measure', np.int64(2020), 'lighting', np.float64(421820127.5873303), np.float64(6.96915), np.float64(60526768.34152376)]
        ],
        columns=['building_category', 'building_code', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2',
                 'm2'])

    ec.heating_systems_parameters = ec.grouped_heating_systems()

    df = pd.concat([energy_need_house_building_code07, energy_need_house_building_code49])
    result = ec.calculate(df.set_index(['building_category', 'building_code', 'building_condition', 'year', 'purpose']))

    assert len(result) == 216

    expected_building_code07_kwh = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6651070.530467674, 198545.80687125237,
                          1310522.239040187, 19831.232696061743, 26778564.233474825, 11931702.891071877,
                          427230.9229484828,
                          506783.6796580713, 10663423.21577154, 3589587.1522666374, 107155.30292705327,
                          707289.716816096,
                          10702.929366528282, 14452408.77965387, 6439547.920331961, 230576.81091213098,
                          273511.4861804224,
                          5755056.5430289935, 11415235.66838739, 340764.2673496213, 2272201.502764267,
                          34383.66430672801,
                          46429043.384822026, 20687350.76139284, 740738.8567948897, 287031.7171043851,
                          6039540.732445766,
                          15157462.588387938, 464310.11889364396, 3017091.3918848266, 48394.905523822345,
                          60416760.40623587,
                          31268436.921584405, 605330.3783315744, 587817.5343465661, 10461760.018493421,
                          3111729.1623366117,
                          92890.4263562946, 613132.9160367926, 9278.119187390348, 12528455.211697856, 5582293.50785034,
                          199881.64550366005, 237100.71149664832, 4988923.939214393, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    expected_building_code49_kwh = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1130691.13497985, 405917.80504834,
                          1361058.1262976967, 15947.25557140727, 6393631.07032074, 9410562.878294008,
                          27551904.505320586, 6533729.099299392, 202232.03511800797, 37514.90387196791,
                          13467.840124686272, 45158.18970591716, 529.1097995507943, 212132.60418830856,
                          312230.59139541304, 914137.39528891, 216780.8798554561, 6709.803519791203, 1941550.091777203,
                          697015.9464986431, 2360969.6505233184, 27663.02605726941, 11090759.918337613,
                          16324103.225797048, 47793117.056744084, 11333782.01131499, 114595.74828603973,
                          10123977.204977872, 3729561.30445806, 12310989.566930782, 152900.21987856104,
                          56674792.50377053, 96892812.41015305, 166525361.71154344, 36371660.91957827, 779525.415791344,
                          529177.9730688428, 189974.74612009074, 636992.6836968857, 7463.520424115203,
                          2992301.4567568894, 4404264.29049633, 12894645.168126922, 3057869.1336514144,
                          94647.18977852572, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 19226098.106710378,
                          6902163.9081472065, 23143222.9860025, 271164.68031220906, 108716319.0841581,
                          160015763.40356794, 468488345.4538178, 111098524.41536757, 3438722.4125249824,
                          637897.6539151141, 229005.08150470574, 767862.9103454273, 8996.901630051889,
                          3607070.1658318597, 5309120.94061071, 15543851.632966485, 3686108.730156684,
                          114092.46677303722, 33013819.060557388, 11851951.921037503, 40145564.71138864,
                          470377.83922753175, 188585575.38061014, 277572539.8508891, 812666809.6454388,
                          192717885.66158214, 1948568.473740223, 129109913.14383537, 47562664.98174538,
                          157000629.4482338, 1949918.8617777508, 722767089.4012743, 1235662856.7264872,
                          2123678723.441983, 463843594.9771625, 9941197.682344304, 8998060.842064552, 3230301.356141217,
                          10831325.594704788, 126908.55305771256, 50880633.616611466, 74889432.41645971,
                          219258562.6472124, 51995536.30719079, 1609366.2538875393]

    assert result.query('building_code=="TEK07"').kwh.tolist() == expected_building_code07_kwh
    assert result.query('building_code=="TEK49"').kwh.tolist() == expected_building_code49_kwh
    assert result.kwh.sum() == 8686021800.905739


def test_calculate_supports_non_index_energy_need(heating_systems_parameters_house_building_code07):
    """ Most functions works with row num indexed dataframes

    Make sure EnergyConsumption.calculate does not surprise by expecting the parameter dataframe to be indexed by
        'building_category', 'building_code', 'building_condition', 'year', 'purpose'
    """

    ec = EnergyConsumption(heating_systems_parameters_house_building_code07)

    energy_need_house_building_code07 = pd.DataFrame(
        data=[
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'heating_rv', np.float64(131957628.54948647),
             np.float64(39.52794605), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'heating_dhw', np.float64(99378601.09170927),
             np.float64(29.76888889), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'fans_and_pumps', np.float64(31565836.641483705),
             np.float64(9.455555556), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'lighting', np.float64(27363685.63968),
             np.float64(8.1968), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'electrical_equipment', np.float64(58487674.752),
             np.float64(17.52), np.float64(3338337.6)],
            ['house', 'TEK07', 'original_condition', np.int64(2020), 'cooling', np.float64(0.0), np.float64(0.0),
             np.float64(3338337.6)]],
        columns=['building_category', 'building_code', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2',
                 'm2']
    )
    ec.heating_systems_parameters = ec.grouped_heating_systems()
    result = ec.calculate(energy_need_house_building_code07)

    assert len(result) == 54
    assert round(result.kwh.sum(), 0) == 327690852
