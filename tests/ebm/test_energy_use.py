import numpy as np
import pandas as pd
import pytest

from ebm.energy_consumption import GRUNNLAST_ENERGIVARE, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ANDEL, \
    TEK_SHARES, KJOLING_VIRKNINGSGRAD, DHW_EFFICIENCY, TAPPEVANN_ENERGIVARE, SPISSLAST_VIRKNINGSGRAD, \
    SPISSLAST_ENERGIVARE, EKSTRALAST_VIRKNINGSGRAD, EKSTRALAST_ENERGIVARE, SPISSLAST_ANDEL, EKSTRALAST_ANDEL
from ebm.model import energy_use


@pytest.fixture
def heating_systems_parameters_house_tek07():
    heating_systems_parameters_house_tek07 = pd.DataFrame(
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
        columns=['building_category', 'TEK', 'year', 'heating_systems', 'TEK_shares', 'Grunnlast', 'Spisslast', 'Ekstralast', 'Grunnlast energivare', 'Spisslast energivare', 'Ekstralast energivare', 'Ekstralast andel', 'Grunnlast andel', 'Spisslast andel', 'Grunnlast virkningsgrad', 'Spisslast virkningsgrad', 'Ekstralast virkningsgrad', 'Tappevann', 'Tappevann energivare', 'Tappevann virkningsgrad', 'Spesifikt elforbruk', 'Kjoling virkningsgrad'])
    return heating_systems_parameters_house_tek07


def test_heating_rv():
    heating_systems_projection = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1977, 'Electric boiler', 0.4,
                1.0, 0.97, 'Electricity',
                0.0, 1.0, 'Ingen',
                0.0, 1.0, 'Ingen',
             ],
            ['house', 'TEK99', 1977, 'HP - Bio - Electricity', 0.5,
                0.6, 4.2, 'Electricity',
                0.3, 0.68, 'Bio',
                0.1,0.99, 'Electricity'],
        ],
        columns=['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES,
                 GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE,
                 SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD, SPISSLAST_ENERGIVARE,
                 EKSTRALAST_ANDEL, EKSTRALAST_VIRKNINGSGRAD, EKSTRALAST_ENERGIVARE]
    )

    result = energy_use.heating_rv(heating_systems_projection)
    result = result.reset_index().drop(columns=['index'], errors='ignore')[['building_category','TEK','year','heating_systems','heating_system',
                 'TEK_shares', 'load_share','load_efficiency','energy_product','load','purpose']]

    expected = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1977, 'Electric boiler', 'Electric boiler',
             0.4, 1.0, 0.97, 'Electricity', 'base', 'heating_rv'],
            ['house', 'TEK99', 1977, 'HP - Bio - Electricity', 'HP',
             0.5, 0.6, 4.2, 'Electricity', 'base', 'heating_rv'],
            ['house', 'TEK99', 1977, 'Electric boiler', np.nan,
             0.4, 0.0, 1.0, 'Ingen', 'peak', 'heating_rv'],
            ['house', 'TEK99', 1977, 'HP - Bio - Electricity', 'Bio',
             0.5, 0.3, 0.68, 'Bio', 'peak', 'heating_rv'],
            ['house', 'TEK99', 1977, 'Electric boiler', np.nan,
             0.4, 0.0, 1.0, 'Ingen', 'tertiary', 'heating_rv'],
            ['house', 'TEK99', 1977, 'HP - Bio - Electricity', 'Electricity',
             0.5, 0.1, 0.99, 'Electricity', 'tertiary', 'heating_rv'],],
        columns=['building_category','TEK','year','heating_systems','heating_system',
                 'TEK_shares', 'load_share','load_efficiency','energy_product','load','purpose'])

    assert len(result) == 6

    pd.testing.assert_frame_equal(result , expected)



def test_heating_dhw():
    heating_systems_projection = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1977, 'DH - Bio', 0.5, 99.0, 1.0, 'DH'],
            ['house', 'TEK99', 1977, 'Electric boiler', 1.0, 52.0, 0.98, 'Electricity'],
        ],
        columns=['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, DHW_EFFICIENCY, TAPPEVANN_ENERGIVARE]
    )

    result = energy_use.heating_dhw(heating_systems_projection)

    expected = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1977, 'DH - Bio', 0.5, 1.0, 1.0, 'DH', 'dhw', 'heating_dhw'],
            ['house', 'TEK99', 1977, 'Electric boiler', 1.0, 1.0, 0.98, 'Electricity', 'dhw', 'heating_dhw'],
        ],
        columns=['building_category','TEK','year','heating_systems','TEK_shares', 'load_share','load_efficiency','energy_product','load','purpose'])

    assert len(result) == 2

    pd.testing.assert_frame_equal(result , expected)


def test_cooling():
    heating_systems_projection = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1971, 'HP - BIO', 0.5, 99.0, 0.99, 'Nuclear waste'],
            ['house', 'TEK99', 1972, 'HP - BIO', 1.0, 52.0, 3.0, 'Nuclear waste'],
        ],
        columns=['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, KJOLING_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE]
    )

    result = energy_use.cooling(heating_systems_projection)

    expected = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1971, 'HP - BIO', 0.5, 1.0, 0.99, 'Electricity', 'base', 'cooling'],
            ['house', 'TEK99', 1972, 'HP - BIO', 1.0, 1.0, 3.0, 'Electricity', 'base', 'cooling'],
        ],
        columns=['building_category','TEK','year','heating_systems','TEK_shares', 'load_share','load_efficiency','energy_product','load','purpose'])

    assert len(result) == 2

    pd.testing.assert_frame_equal(result , expected)


def test_other():
    heating_systems_projection = pd.DataFrame(
        data=[
            ['house', 'TEK99', 1971, 'HP - BIO', 0.5, 0.2, 1.0, 'Electricity'],
        ],
        columns=['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE]
    )

    result = energy_use.other(heating_systems_projection)

    expected = pd.DataFrame(
        data=[['house', 'TEK99', 1971, 'HP - BIO', 0.5, 1.0, 1.0, 'Electricity', 'base', purpose] for purpose in ['electrical_equipment', 'fans_and_pumps', 'lighting']],
        columns=['building_category','TEK','year','heating_systems','TEK_shares', 'load_share','load_efficiency','energy_product','load','purpose'])

    assert len(result) == 3
    assert result.purpose.to_list() == ['electrical_equipment', 'fans_and_pumps', 'lighting']
    assert result.load.tolist() == ['base'] * 3

    pd.testing.assert_frame_equal(result , expected)

def test_energy_use_kwh():
    energy_need = pd.DataFrame(
        data=[
            ['house', 'TEK07', 'original_condition', 'heating_rv', 1977, 200],
            ['house', 'TEK07', 'original_condition', 'heating_rv', 1978, 240],
            ['shack', 'TEK07', 'original_condition', 'heating_rv', 1978, 240],
        ],
        columns='building_category,TEK,building_condition,purpose,year,energy_requirement'.split(','))
    efficiency_factor = pd.DataFrame(
        data=[
            ['house', 'TEK07', 'heating_rv', 1977, 0.5, 0.2, 4],
            ['house', 'TEK07', 'heating_rv', 1978, 1.0, 0.2, 4],
            ['house', 'TEKXX', 'heating_rv', 1977, 2, 2, 2]],
        columns='building_category,TEK,purpose,year,TEK_shares,load_share,load_efficiency'.split(','))

    result = energy_use.energy_use_kwh(energy_need, efficiency_factor)
    result = result.drop(columns=['index'], errors='ignore')
    expected = pd.DataFrame(
        data = [
            ['house', 'TEK07', 'original_condition', 'heating_rv', 1977, 200, 0.5, 0.2, 4, 5.0],
            ['house', 'TEK07', 'original_condition', 'heating_rv', 1978, 240, 1.0, 0.2, 4, 12.0],
        ],
        columns=['building_category', 'TEK', 'building_condition', 'purpose', 'year', 'energy_requirement', 'TEK_shares', 'load_share',
       'load_efficiency', 'kwh'],
    )

    assert len(result) == 2
    assert result.building_category.to_list() == ['house']*2
    assert result.TEK.to_list() == ['TEK07']*2
    assert result.building_condition.to_list() == ['original_condition']*2
    assert result.year.to_list() == [1977, 1978]
    assert result.kwh.to_list() == [5.0, 12.0]

    pd.testing.assert_frame_equal(result, expected)


def test_efficiency_factor():
    heating_systems = pd.DataFrame(
        data=[
            ['house', 'TEK07', 'heating_rv', 1977, 0.5, 0.2, 4],
            ['house', 'TEK07', 'lighting', 1977, 0.5, 0.2, 1],
        ],
        columns='building_category,TEK,purpose,year,TEK_shares,load_share,load_efficiency'.split(','))

    result = energy_use.efficiency_factor(heating_systems)
    assert 'efficiency_factor' in result.columns
    assert len(result) == 2
    assert result.efficiency_factor.to_list() == [0.025, 0.1]


@pytest.mark.skip
def test_calculate(heating_systems_parameters_house_tek07):
    energy_need_house_tek07 = pd.DataFrame(
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
        columns=['building_category', 'TEK', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2',
                 'm2']
    )

    energy_need_house_tek49 = pd.DataFrame(
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
        columns=['building_category', 'TEK', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2',
                 'm2'])

    energy_need = pd.concat([energy_need_house_tek07, energy_need_house_tek49])

    result = energy_use.energy_use_kwh(energy_need, energy_use.efficiency_factor(energy_use.all_purposes(heating_systems_parameters_house_tek07)))






