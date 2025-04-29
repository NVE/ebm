import numpy as np
import pandas as pd

from ebm.energy_consumption import EnergyConsumption


def test_calculate():
    heating_systems_parameters_house_tek07 = pd.DataFrame(
        data=[
            ['house', 'TEK07', np.int64(2020), 'DH', np.float64(0.11371747224812079), 'DH', 'Ingen', 'Ingen', 'DH', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.99), np.float64(1.0), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'DH - Bio', np.float64(0.0033946606308616), 'DH', 'Bio', 'Ingen', 'DH', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.95), np.float64(0.05), np.float64(0.99), np.float64(0.65), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler', np.float64(0.022406810402312557), 'Electric boiler', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.98), np.float64(1.0), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler - Solar', np.float64(0.0003390668680222), 'Electric boiler', 'Solar', 'Ingen', 'Electricity', 'Solar', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(0.98), np.float64(0.7), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electricity', np.float64(0.4578496981974673), 'Electricity', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(1.0), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electricity - Bio', np.float64(0.2040037143152775), 'Electricity', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.7), np.float64(0.3), np.float64(1.0), np.float64(0.65), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP - Electricity', np.float64(0.0073046316982173), 'HP', 'Electricity', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.62), np.float64(0.38), np.float64(2.5), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP Central heating - Bio', np.float64(0.0086647944512573), 'HP Central heating', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.65), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP Central heating - Electric boiler', np.float64(0.18231915118846304), 'HP Central heating', 'Electric boiler', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.99), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)]],
        columns=
            ['building_category', 'TEK', 'year', 'heating_systems', 'TEK_shares', 'Grunnlast', 'Spisslast', 'Ekstralast', 'Grunnlast energivare', 'Spisslast energivare', 'Ekstralast energivare',
            'Ekstralast andel', 'Grunnlast andel', 'Spisslast andel', 'Grunnlast virkningsgrad',
            'Spisslast virkningsgrad', 'Ekstralast virkningsgrad', 'Tappevann',
            'Tappevann energivare', 'Tappevann virkningsgrad', 'Spesifikt elforbruk', 'Kjoling virkningsgrad'])

    ec = EnergyConsumption(heating_systems_parameters_house_tek07)

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
        columns=['building_category', 'TEK', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2', 'm2']
    )
    ec.heating_systems_parameters = ec.grouped_heating_systems()
    result = ec.calculate(energy_need_house_tek07.set_index(['building_category', 'TEK', 'building_condition', 'year', 'purpose']))

    assert len(result) == 108

    expected_kwh = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6651070.530467674, 198545.80687125237,
                    1310522.239040187, 19831.232696061743, 26778564.233474825, 11931702.891071877, 427230.9229484828,
                    506783.6796580713, 10663423.21577154, 3589587.1522666374, 107155.30292705327, 707289.716816096,
                    10702.929366528282, 14452408.77965387, 6439547.920331961, 230576.81091213098, 273511.4861804224,
                    5755056.5430289935, 11415235.66838739, 340764.2673496213, 2272201.502764267, 34383.66430672801,
                    46429043.384822026, 20687350.76139284, 740738.8567948897, 287031.7171043851, 6039540.732445766,
                    15157462.588387938, 464310.11889364396, 3017091.3918848266, 48394.905523822345, 60416760.40623587,
                    31268436.921584405, 605330.3783315744, 587817.5343465661, 10461760.018493421, 3111729.1623366117,
                    92890.4263562946, 613132.9160367926, 9278.119187390348, 12528455.211697856, 5582293.50785034,
                    199881.64550366005, 237100.71149664832, 4988923.939214393, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    assert result.kwh.tolist() == expected_kwh
    assert result.kwh.sum() == sum(expected_kwh)


def test_calculate_supports_non_index_energy_need():
    """ Most functions works with row num indexed dataframes

    Make sure EnergyConsumption.calculate does not surprise by expecting the parameter dataframe to be indexed by
        'building_category', 'TEK', 'building_condition', 'year', 'purpose'
    """
    heating_systems_parameters_house_tek07 = pd.DataFrame(
        data=[
            ['house', 'TEK07', np.int64(2020), 'DH', np.float64(0.11371747224812079), 'DH', 'Ingen', 'Ingen', 'DH', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.99), np.float64(1.0), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'DH - Bio', np.float64(0.0033946606308616), 'DH', 'Bio', 'Ingen', 'DH', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.95), np.float64(0.05), np.float64(0.99), np.float64(0.65), np.int64(1), 'DH', 'DH', np.float64(0.99), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler', np.float64(0.022406810402312557), 'Electric boiler', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(0.98), np.float64(1.0), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electric boiler - Solar', np.float64(0.0003390668680222), 'Electric boiler', 'Solar', 'Ingen', 'Electricity', 'Solar', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(0.98), np.float64(0.7), np.int64(1), 'Electric boiler', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electricity', np.float64(0.4578496981974673), 'Electricity', 'Ingen', 'Ingen', 'Electricity', 'Ingen', 'Ingen', np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(1.0), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'Electricity - Bio', np.float64(0.2040037143152775), 'Electricity', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.7), np.float64(0.3), np.float64(1.0), np.float64(0.65), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP - Electricity', np.float64(0.0073046316982173), 'HP', 'Electricity', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.62), np.float64(0.38), np.float64(2.5), np.float64(1.0), np.int64(1), 'Electricity', 'Electricity', np.float64(0.98), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP Central heating - Bio', np.float64(0.0086647944512573), 'HP Central heating', 'Bio', 'Ingen', 'Electricity', 'Bio', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.65), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)],
            ['house', 'TEK07', np.int64(2020), 'HP Central heating - Electric boiler', np.float64(0.18231915118846304), 'HP Central heating', 'Electric boiler', 'Ingen', 'Electricity', 'Electricity', 'Ingen', np.float64(0.0), np.float64(0.85), np.float64(0.15), np.float64(3.0), np.float64(0.99), np.int64(1), 'HP Central heating', 'Electricity', np.float64(3.0), np.int64(1), np.int64(4)]],
        columns=
            ['building_category', 'TEK', 'year', 'heating_systems', 'TEK_shares', 'Grunnlast', 'Spisslast', 'Ekstralast', 'Grunnlast energivare', 'Spisslast energivare', 'Ekstralast energivare',
            'Ekstralast andel', 'Grunnlast andel', 'Spisslast andel', 'Grunnlast virkningsgrad',
            'Spisslast virkningsgrad', 'Ekstralast virkningsgrad', 'Tappevann',
            'Tappevann energivare', 'Tappevann virkningsgrad', 'Spesifikt elforbruk', 'Kjoling virkningsgrad'])

    ec = EnergyConsumption(heating_systems_parameters_house_tek07)

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
        columns=['building_category', 'TEK', 'building_condition', 'year', 'purpose', 'energy_requirement', 'kwh_m2', 'm2']
    )
    ec.heating_systems_parameters = ec.grouped_heating_systems()
    result = ec.calculate(energy_need_house_tek07)

    assert len(result) == 108
    assert result.kwh.sum() == 327690851.8522136
