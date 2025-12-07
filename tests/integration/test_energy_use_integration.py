import os
import pathlib
import sys

import pandas as pd
import pytest
from loguru import logger

from ebm import extractors
from ebm.cmd.pipeline import load_config
from ebm.model.data_classes import YearRange
from ebm.model.database_manager import DatabaseManager
from ebm.model.energy_use import calculate_energy_use
from ebm.model.file_handler import FileHandler

expected_building_group_energy_use = {
    'kwh': {('Residential', 'Bio', 2020): 4788825216.425719, ('Residential', 'Bio', 2021): 4781280230.150457,
            ('Residential', 'Bio', 2022): 4764208461.91, ('Residential', 'Bio', 2023): 4757203300.271702,
            ('Residential', 'Bio', 2024): 4702657720.902674, ('Residential', 'Bio', 2025): 4637666417.66,
            ('Residential', 'Bio', 2026): 4576639450.690714, ('Residential', 'Bio', 2027): 4515036442.927422,
            ('Residential', 'Bio', 2028): 4453495280.110844, ('Residential', 'Bio', 2029): 4392678075.975616,
            ('Residential', 'Bio', 2030): 4331957397.639449, ('Residential', 'Bio', 2031): 4270638998.9928374,
            ('Residential', 'Bio', 2032): 4206703529.1823277, ('Residential', 'Bio', 2033): 4142902138.4826884,
            ('Residential', 'Bio', 2034): 4078480622.5262, ('Residential', 'Bio', 2035): 4013934811.311016,
            ('Residential', 'Bio', 2036): 3949606190.134894, ('Residential', 'Bio', 2037): 3872653761.7300243,
            ('Residential', 'Bio', 2038): 3795917186.048778, ('Residential', 'Bio', 2039): 3719260312.864082,
            ('Residential', 'Bio', 2040): 3645969161.6627994, ('Residential', 'Bio', 2041): 3620731852.3399687,
            ('Residential', 'Bio', 2042): 3598373226.7441354, ('Residential', 'Bio', 2043): 3575299283.2259507,
            ('Residential', 'Bio', 2044): 3551903949.5981746, ('Residential', 'Bio', 2045): 3528169064.9771514,
            ('Residential', 'Bio', 2046): 3504087473.877657, ('Residential', 'Bio', 2047): 3476748690.6934733,
            ('Residential', 'Bio', 2048): 3449057595.4897804, ('Residential', 'Bio', 2049): 3420281067.0114727,
            ('Residential', 'Bio', 2050): 3390632536.13436, ('Residential', 'DH', 2020): 1857082296.4135938,
            ('Residential', 'DH', 2021): 1860856978.739231, ('Residential', 'DH', 2022): 1863752230.1062946,
            ('Residential', 'DH', 2023): 1873218107.0187275, ('Residential', 'DH', 2024): 2058677339.9957652,
            ('Residential', 'DH', 2025): 2098902313.989615, ('Residential', 'DH', 2026): 2101902151.602252,
            ('Residential', 'DH', 2027): 2139031655.4884844, ('Residential', 'DH', 2028): 2176490076.8487096,
            ('Residential', 'DH', 2029): 2214156705.618156, ('Residential', 'DH', 2030): 2215561142.7889395,
            ('Residential', 'DH', 2031): 2252524983.891313, ('Residential', 'DH', 2032): 2288557476.638861,
            ('Residential', 'DH', 2033): 2288170212.7096043, ('Residential', 'DH', 2034): 2323278447.7259874,
            ('Residential', 'DH', 2035): 2321617876.283609, ('Residential', 'DH', 2036): 2356213289.6906114,
            ('Residential', 'DH', 2037): 2385764893.3904543, ('Residential', 'DH', 2038): 2378616590.5865026,
            ('Residential', 'DH', 2039): 2407358834.5643554, ('Residential', 'DH', 2040): 2400247626.7262797,
            ('Residential', 'DH', 2041): 2428531972.0246058, ('Residential', 'DH', 2042): 2421235197.5354657,
            ('Residential', 'DH', 2043): 2449398034.5029106, ('Residential', 'DH', 2044): 2477034349.527523,
            ('Residential', 'DH', 2045): 2468570512.792454, ('Residential', 'DH', 2046): 2495160207.558666,
            ('Residential', 'DH', 2047): 2484466249.320536, ('Residential', 'DH', 2048): 2508337205.5425124,
            ('Residential', 'DH', 2049): 2495685156.8676863, ('Residential', 'DH', 2050): 2482497950.4832416,
            ('Residential', 'Electricity', 2020): 37071496927.11284, ('Residential', 'Electricity', 2021): 37029197525.37465,
            ('Residential', 'Electricity', 2022): 36989418901.482605, ('Residential', 'Electricity', 2023): 37088406609.24847,
            ('Residential', 'Electricity', 2024): 36867007293.05276, ('Residential', 'Electricity', 2025): 36750035439.66159,
            ('Residential', 'Electricity', 2026): 36664834747.2307, ('Residential', 'Electricity', 2027): 36481736708.55,
            ('Residential', 'Electricity', 2028): 36318343183.4606, ('Residential', 'Electricity', 2029): 36154451792.15,
            ('Residential', 'Electricity', 2030): 36001151842.6294, ('Residential', 'Electricity', 2031): 35962804667.080765,
            ('Residential', 'Electricity', 2032): 35915198138.81447, ('Residential', 'Electricity', 2033): 35879856685.60712,
            ('Residential', 'Electricity', 2034): 35816219297.32666, ('Residential', 'Electricity', 2035): 35785005351.70673,
            ('Residential', 'Electricity', 2036): 35694160536.33721, ('Residential', 'Electricity', 2037): 35565639809.882866,
            ('Residential', 'Electricity', 2038): 35468146253.347664, ('Residential', 'Electricity', 2039): 35321223972.89438,
            ('Residential', 'Electricity', 2040): 35198504837.56481, ('Residential', 'Electricity', 2041): 35087715428.0407,
            ('Residential', 'Electricity', 2042): 35023661993.97, ('Residential', 'Electricity', 2043): 34896484726.94015,
            ('Residential', 'Electricity', 2044): 34786775527.04805, ('Residential', 'Electricity', 2045): 34708213183.45203,
            ('Residential', 'Electricity', 2046): 34589761749.040016, ('Residential', 'Electricity', 2047): 34471758702.1105,
            ('Residential', 'Electricity', 2048): 34335149779.404625, ('Residential', 'Electricity', 2049): 34217253629.19904,
            ('Residential', 'Electricity', 2050): 34092268470.39, ('Residential', 'Ingen', 2020): 0.0,
            ('Residential', 'Ingen', 2021): 0.0, ('Residential', 'Ingen', 2022): 0.0, ('Residential', 'Ingen', 2023): 0.0,
            ('Residential', 'Ingen', 2024): 0.0, ('Residential', 'Ingen', 2025): 0.0, ('Residential', 'Ingen', 2026): 0.0,
            ('Residential', 'Ingen', 2027): 0.0, ('Residential', 'Ingen', 2028): 0.0, ('Residential', 'Ingen', 2029): 0.0,
            ('Residential', 'Ingen', 2030): 0.0, ('Residential', 'Ingen', 2031): 0.0, ('Residential', 'Ingen', 2032): 0.0,
            ('Residential', 'Ingen', 2033): 0.0, ('Residential', 'Ingen', 2034): 0.0, ('Residential', 'Ingen', 2035): 0.0,
            ('Residential', 'Ingen', 2036): 0.0, ('Residential', 'Ingen', 2037): 0.0, ('Residential', 'Ingen', 2038): 0.0,
            ('Residential', 'Ingen', 2039): 0.0, ('Residential', 'Ingen', 2040): 0.0, ('Residential', 'Ingen', 2041): 0.0,
            ('Residential', 'Ingen', 2042): 0.0, ('Residential', 'Ingen', 2043): 0.0, ('Residential', 'Ingen', 2044): 0.0,
            ('Residential', 'Ingen', 2045): 0.0, ('Residential', 'Ingen', 2046): 0.0, ('Residential', 'Ingen', 2047): 0.0,
            ('Residential', 'Ingen', 2048): 0.0, ('Residential', 'Ingen', 2049): 0.0, ('Residential', 'Ingen', 2050): 0.0,
            ('Residential', 'Solar', 2020): 2091260.766183585, ('Residential', 'Solar', 2021): 2088301.8014598538,
            ('Residential', 'Solar', 2022): 2081448.643985017, ('Residential', 'Solar', 2023): 2079170.9996649974,
            ('Residential', 'Solar', 2024): 2074582.1317013446, ('Residential', 'Solar', 2025): 2068490.6376518041,
            ('Residential', 'Solar', 2026): 2063688.091091381, ('Residential', 'Solar', 2027): 2058394.9455057923,
            ('Residential', 'Solar', 2028): 2053077.0313689576, ('Residential', 'Solar', 2029): 2047959.1863727896,
            ('Residential', 'Solar', 2030): 2042770.0668798666, ('Residential', 'Solar', 2031): 2037159.4654290455,
            ('Residential', 'Solar', 2032): 2030179.6904434524, ('Residential', 'Solar', 2033): 2023102.6230804604,
            ('Residential', 'Solar', 2034): 2015534.885926151, ('Residential', 'Solar', 2035): 2007691.2296148627,
            ('Residential', 'Solar', 2036): 1999768.3305618546, ('Residential', 'Solar', 2037): 1985361.660853026,
            ('Residential', 'Solar', 2038): 1970693.435959307, ('Residential', 'Solar', 2039): 1955776.780073403,
            ('Residential', 'Solar', 2040): 1942138.4943073988, ('Residential', 'Solar', 2041): 1928725.4754622038,
            ('Residential', 'Solar', 2042): 1916737.2952380048, ('Residential', 'Solar', 2043): 1904394.1817497099,
            ('Residential', 'Solar', 2044): 1891876.4088004471, ('Residential', 'Solar', 2045): 1879173.773981755,
            ('Residential', 'Solar', 2046): 1866282.146654752, ('Residential', 'Solar', 2047): 1851650.0434458097,
            ('Residential', 'Solar', 2048): 1836803.6935016927, ('Residential', 'Solar', 2049): 1821374.6119763046,
            ('Residential', 'Solar', 2050): 1805491.7126416897, ('Non-residential', 'Bio', 2020): 101557132.72809598,
            ('Non-residential', 'Bio', 2021): 101302607.78075051, ('Non-residential', 'Bio', 2022): 101188389.60102122,
            ('Non-residential', 'Bio', 2023): 101346044.63769531, ('Non-residential', 'Bio', 2024): 101503459.92926183,
            ('Non-residential', 'Bio', 2025): 101556799.89033622, ('Non-residential', 'Bio', 2026): 101506765.64682631,
            ('Non-residential', 'Bio', 2027): 101277700.80668746, ('Non-residential', 'Bio', 2028): 101072155.97942267,
            ('Non-residential', 'Bio', 2029): 100871426.30954705, ('Non-residential', 'Bio', 2030): 100305737.5381496,
            ('Non-residential', 'Bio', 2031): 99903987.42877857, ('Non-residential', 'Bio', 2032): 99552412.15487796,
            ('Non-residential', 'Bio', 2033): 99191646.07625379, ('Non-residential', 'Bio', 2034): 98832200.92927141,
            ('Non-residential', 'Bio', 2035): 98474978.72599679, ('Non-residential', 'Bio', 2036): 98130597.74692447,
            ('Non-residential', 'Bio', 2037): 97785805.07775594, ('Non-residential', 'Bio', 2038): 97430782.0635449,
            ('Non-residential', 'Bio', 2039): 97068448.56611995, ('Non-residential', 'Bio', 2040): 96696368.30557051,
            ('Non-residential', 'Bio', 2041): 96275942.15789312, ('Non-residential', 'Bio', 2042): 95893566.53443238,
            ('Non-residential', 'Bio', 2043): 95497780.5120125, ('Non-residential', 'Bio', 2044): 95093005.49909942,
            ('Non-residential', 'Bio', 2045): 94681951.711988, ('Non-residential', 'Bio', 2046): 94260578.26055041,
            ('Non-residential', 'Bio', 2047): 93439123.67882389, ('Non-residential', 'Bio', 2048): 92833428.01497278,
            ('Non-residential', 'Bio', 2049): 92231780.86995913, ('Non-residential', 'Bio', 2050): 91622027.80740257,
            ('Non-residential', 'DH', 2020): 4423747518.8634615, ('Non-residential', 'DH', 2021): 4415568070.12422,
            ('Non-residential', 'DH', 2022): 4414384497.767668, ('Non-residential', 'DH', 2023): 4426506223.131906,
            ('Non-residential', 'DH', 2024): 4527944403.31363, ('Non-residential', 'DH', 2025): 4559790929.9018345,
            ('Non-residential', 'DH', 2026): 4581523665.738846, ('Non-residential', 'DH', 2027): 4589719130.0956955,
            ('Non-residential', 'DH', 2028): 4599192469.8, ('Non-residential', 'DH', 2029): 4608803865.051731,
            ('Non-residential', 'DH', 2030): 4601976683.323316, ('Non-residential', 'DH', 2031): 4613137777.879646,
            ('Non-residential', 'DH', 2032): 4621232411.851534, ('Non-residential', 'DH', 2033): 4633706981.501938,
            ('Non-residential', 'DH', 2034): 4641182344.3524885, ('Non-residential', 'DH', 2035): 4648598631.548968,
            ('Non-residential', 'DH', 2036): 4661270680.361897, ('Non-residential', 'DH', 2037): 4668828796.079716,
            ('Non-residential', 'DH', 2038): 4675752380.170249, ('Non-residential', 'DH', 2039): 4682161357.608822,
            ('Non-residential', 'DH', 2040): 4683142671.717943, ('Non-residential', 'DH', 2041): 4686478543.857488,
            ('Non-residential', 'DH', 2042): 4691426567.982776, ('Non-residential', 'DH', 2043): 4695587785.653626,
            ('Non-residential', 'DH', 2044): 4694392940.027948, ('Non-residential', 'DH', 2045): 4697463359.601239,
            ('Non-residential', 'DH', 2046): 4695131341.303659, ('Non-residential', 'DH', 2047): 4677920868.654059,
            ('Non-residential', 'DH', 2048): 4676418225.704957, ('Non-residential', 'DH', 2049): 4674722677.0622,
            ('Non-residential', 'DH', 2050): 4672303519.084109, ('Non-residential', 'Electricity', 2020): 25060040864.557102,
            ('Non-residential', 'Electricity', 2021): 24781866798.24038,
            ('Non-residential', 'Electricity', 2022): 24554204359.587547,
            ('Non-residential', 'Electricity', 2023): 24414448636.34977,
            ('Non-residential', 'Electricity', 2024): 24134264259.48454,
            ('Non-residential', 'Electricity', 2025): 23907109002.703754,
            ('Non-residential', 'Electricity', 2026): 23650318194.1226,
            ('Non-residential', 'Electricity', 2027): 23346427931.26,
            ('Non-residential', 'Electricity', 2028): 23053576919.774857,
            ('Non-residential', 'Electricity', 2029): 22755174910.569397,
            ('Non-residential', 'Electricity', 2030): 22380307452.650845,
            ('Non-residential', 'Electricity', 2031): 22305918274.07,
            ('Non-residential', 'Electricity', 2032): 22239753792.264534,
            ('Non-residential', 'Electricity', 2033): 22170009239.42864,
            ('Non-residential', 'Electricity', 2034): 22101923090.82,
            ('Non-residential', 'Electricity', 2035): 22036110791.94,
            ('Non-residential', 'Electricity', 2036): 21965872384.988487,
            ('Non-residential', 'Electricity', 2037): 21895577817.117966,
            ('Non-residential', 'Electricity', 2038): 21825511491.981224,
            ('Non-residential', 'Electricity', 2039): 21753171046.01,
            ('Non-residential', 'Electricity', 2040): 21683344801.40307,
            ('Non-residential', 'Electricity', 2041): 21597841256.130234,
            ('Non-residential', 'Electricity', 2042): 21518001413.45979,
            ('Non-residential', 'Electricity', 2043): 21435631525.4,
            ('Non-residential', 'Electricity', 2044): 21355874312.82299,
            ('Non-residential', 'Electricity', 2045): 21269303814.17199,
            ('Non-residential', 'Electricity', 2046): 21185064002.88,
            ('Non-residential', 'Electricity', 2047): 21012590312.611423,
            ('Non-residential', 'Electricity', 2048): 20885462601.59,
            ('Non-residential', 'Electricity', 2049): 20757121513.622425,
            ('Non-residential', 'Electricity', 2050): 20626689875.071304, ('Non-residential', 'Fossil', 2020): 22325995.474820293,
            ('Non-residential', 'Fossil', 2021): 22284594.592829693, ('Non-residential', 'Fossil', 2022): 22278464.234987915,
            ('Non-residential', 'Fossil', 2023): 22339423.1518955, ('Non-residential', 'Fossil', 2024): 17919320.106229,
            ('Non-residential', 'Fossil', 2025): 14955498.53703225, ('Non-residential', 'Fossil', 2026): 11969013.472209465,
            ('Non-residential', 'Fossil', 2027): 8963499.839415869, ('Non-residential', 'Fossil', 2028): 5968539.153594006,
            ('Non-residential', 'Fossil', 2029): 2980818.346081184, ('Non-residential', 'Ingen', 2020): 0.0,
            ('Non-residential', 'Ingen', 2021): 0.0, ('Non-residential', 'Ingen', 2022): 0.0, ('Non-residential', 'Ingen', 2023): 0.0,
            ('Non-residential', 'Ingen', 2024): 0.0, ('Non-residential', 'Ingen', 2025): 0.0, ('Non-residential', 'Ingen', 2026): 0.0,
            ('Non-residential', 'Ingen', 2027): 0.0, ('Non-residential', 'Ingen', 2028): 0.0, ('Non-residential', 'Ingen', 2029): 0.0,
            ('Non-residential', 'Ingen', 2030): 0.0, ('Non-residential', 'Ingen', 2031): 0.0, ('Non-residential', 'Ingen', 2032): 0.0,
            ('Non-residential', 'Ingen', 2033): 0.0, ('Non-residential', 'Ingen', 2034): 0.0, ('Non-residential', 'Ingen', 2035): 0.0,
            ('Non-residential', 'Ingen', 2036): 0.0, ('Non-residential', 'Ingen', 2037): 0.0, ('Non-residential', 'Ingen', 2038): 0.0,
            ('Non-residential', 'Ingen', 2039): 0.0, ('Non-residential', 'Ingen', 2040): 0.0, ('Non-residential', 'Ingen', 2041): 0.0,
            ('Non-residential', 'Ingen', 2042): 0.0, ('Non-residential', 'Ingen', 2043): 0.0, ('Non-residential', 'Ingen', 2044): 0.0,
            ('Non-residential', 'Ingen', 2045): 0.0, ('Non-residential', 'Ingen', 2046): 0.0, ('Non-residential', 'Ingen', 2047): 0.0,
            ('Non-residential', 'Ingen', 2048): 0.0, ('Non-residential', 'Ingen', 2049): 0.0, ('Non-residential', 'Ingen', 2050): 0.0,
            ('Non-residential', 'Solar', 2020): 866616.4581550302, ('Non-residential', 'Solar', 2021): 864444.5229845959,
            ('Non-residential', 'Solar', 2022): 863469.8661415464, ('Non-residential', 'Solar', 2023): 864815.182278608,
            ('Non-residential', 'Solar', 2024): 866158.4526011569, ('Non-residential', 'Solar', 2025): 866613.6179539261,
            ('Non-residential', 'Solar', 2026): 866186.6612475654, ('Non-residential', 'Solar', 2027): 864231.9845536058,
            ('Non-residential', 'Solar', 2028): 862478.0109486872, ('Non-residential', 'Solar', 2029): 860765.1264778348,
            ('Non-residential', 'Solar', 2030): 855937.9401806492, ('Non-residential', 'Solar', 2031): 852509.6900174757,
            ('Non-residential', 'Solar', 2032): 849509.5962726241, ('Non-residential', 'Solar', 2033): 846431.0747263648,
            ('Non-residential', 'Solar', 2034): 843363.8250727843, ('Non-residential', 'Solar', 2035): 840315.544442363,
            ('Non-residential', 'Solar', 2036): 837376.841701132, ('Non-residential', 'Solar', 2037): 834434.6258889482,
            ('Non-residential', 'Solar', 2038): 831405.11157642, ('Non-residential', 'Solar', 2039): 828313.21479109,
            ('Non-residential', 'Solar', 2040): 825138.1460501275, ('Non-residential', 'Solar', 2041): 821550.5278373187,
            ('Non-residential', 'Solar', 2042): 818287.6057796868, ('Non-residential', 'Solar', 2043): 814910.2488996427,
            ('Non-residential', 'Solar', 2044): 811456.1863575309, ('Non-residential', 'Solar', 2045): 807948.5452147719,
            ('Non-residential', 'Solar', 2046): 804352.8433843245, ('Non-residential', 'Solar', 2047): 797343.1332731004,
            ('Non-residential', 'Solar', 2048): 792174.5565633595, ('Non-residential', 'Solar', 2049): 787040.5270386506,
            ('Non-residential', 'Solar', 2050): 781837.3273693894}}


@pytest.fixture
def cwd_ebm_data(request):
    """
    Change working directory to tests/ebm/data. The working directory
    is reset when the test finishes.
    """
    ebm_data = pathlib.Path(__file__).parent / pathlib.Path(r'../ebm/data')
    os.chdir(ebm_data)
    yield
    os.chdir(request.config.invocation_params.dir)


@pytest.fixture
def kalibrert_database_manager(cwd_ebm_data):
    """
    Provides a DatabaseManager configured to load input from tests/ebm/data/kalibrert
    """
    input_path, output_path, years = load_config()
    input_path = pathlib.Path('kalibrert')
    output_path.mkdir(exist_ok=True)

    file_handler = FileHandler(directory=input_path)
    database_manager = DatabaseManager(file_handler=file_handler)
    return database_manager


def test_energy_use(kalibrert_database_manager):
    scurve_parameters = kalibrert_database_manager.get_scurve_params()  # 📍

    area_parameters = kalibrert_database_manager.get_area_parameters()  # 📍

    building_code_parameters = kalibrert_database_manager.file_handler.get_building_code()  # 📍

    result = calculate_energy_use(database_manager=kalibrert_database_manager, years=YearRange(2020, 2050),
                                  area_parameters=area_parameters, scurve_parameters=scurve_parameters,
                                  building_code_parameters=building_code_parameters)

    expect_columns = ['building_group', 'energy_product', 'year']
    result = result[expect_columns + ['kwh']].groupby(by=expect_columns).sum().round(2)

    expected = pd.DataFrame(expected_building_group_energy_use).round(2)
    # expected = expected.drop(columns=['Grunnlast', 'Ekstralast', 'Spisslast'])
    expected.index.names = expect_columns

    df = pd.merge(left=result, right=expected, suffixes=('_result', '_expected'), on=expect_columns, how='outer')

    df_diff = df[df['kwh_result'] != df['kwh_expected']]

    # Log readable error messages for every different value
    max_difference = 0
    for i, r in df_diff.iterrows():
        difference = abs(r[1] - r[0])
        max_difference = max(max_difference, difference)
        logger.error(f'Error in row {i} expected: {r[1]} was: {r[0]} ({difference}')
    logger.error(f'{max_difference=}')
    assert df_diff.empty, 'Expected no differences between the dataframes result and expected'


expected_holiday_home = {'kwh': {('Holiday homes', 'Bio', 2020): 1450.0, ('Holiday homes', 'Bio', 2021): 1270.0,
                                 ('Holiday homes', 'Bio', 2022): 1390.0, ('Holiday homes', 'Bio', 2023): 1390.0,
                                 ('Holiday homes', 'Bio', 2024): 1363.993311965345,
                                 ('Holiday homes', 'Bio', 2025): 1376.2609385993053,
                                 ('Holiday homes', 'Bio', 2026): 1385.7758570733436,
                                 ('Holiday homes', 'Bio', 2027): 1392.6203955040182,
                                 ('Holiday homes', 'Bio', 2028): 1399.4936873365957,
                                 ('Holiday homes', 'Bio', 2029): 1406.3183195659535,
                                 ('Holiday homes', 'Bio', 2030): 1413.0237603429798,
                                 ('Holiday homes', 'Bio', 2031): 1419.6618640933284,
                                 ('Holiday homes', 'Bio', 2032): 1426.1893778363594,
                                 ('Holiday homes', 'Bio', 2033): 1432.595242571341,
                                 ('Holiday homes', 'Bio', 2034): 1438.9165673896175,
                                 ('Holiday homes', 'Bio', 2035): 1445.120912555709,
                                 ('Holiday homes', 'Bio', 2036): 1451.2318706045103,
                                 ('Holiday homes', 'Bio', 2037): 1457.05185405628,
                                 ('Holiday homes', 'Bio', 2038): 1462.6120738686395,
                                 ('Holiday homes', 'Bio', 2039): 1467.9226060200324,
                                 ('Holiday homes', 'Bio', 2040): 1473.0013906672023,
                                 ('Holiday homes', 'Bio', 2041): 1477.8513768770104,
                                 ('Holiday homes', 'Bio', 2042): 1482.4774797608936,
                                 ('Holiday homes', 'Bio', 2043): 1486.8688860736913,
                                 ('Holiday homes', 'Bio', 2044): 1491.0287906378373,
                                 ('Holiday homes', 'Bio', 2045): 1494.9390075410172,
                                 ('Holiday homes', 'Bio', 2046): 1498.5911810937894,
                                 ('Holiday homes', 'Bio', 2047): 1501.9803961847176,
                                 ('Holiday homes', 'Bio', 2048): 1505.0946107907826,
                                 ('Holiday homes', 'Bio', 2049): 1507.9313673562658,
                                 ('Holiday homes', 'Bio', 2050): 1510.4926319257427,
                                 ('Holiday homes', 'Electricity', 2020): 2467.0,
                                 ('Holiday homes', 'Electricity', 2021): 2819.0,
                                 ('Holiday homes', 'Electricity', 2022): 2318.0,
                                 ('Holiday homes', 'Electricity', 2023): 2427.0,
                                 ('Holiday homes', 'Electricity', 2024): 2510.664757550429,
                                 ('Holiday homes', 'Electricity', 2025): 2569.976712184894,
                                 ('Holiday homes', 'Electricity', 2026): 2624.7297237690896,
                                 ('Holiday homes', 'Electricity', 2027): 2674.8615206420313,
                                 ('Holiday homes', 'Electricity', 2028): 2725.4146629389325,
                                 ('Holiday homes', 'Electricity', 2029): 2763.7274703003145,
                                 ('Holiday homes', 'Electricity', 2030): 2802.04677770458,
                                 ('Holiday homes', 'Electricity', 2031): 2840.469973626825,
                                 ('Holiday homes', 'Electricity', 2032): 2878.906153252153,
                                 ('Holiday homes', 'Electricity', 2033): 2904.581963019164,
                                 ('Holiday homes', 'Electricity', 2034): 2930.199594470989,
                                 ('Holiday homes', 'Electricity', 2035): 2955.69044266053,
                                 ('Holiday homes', 'Electricity', 2036): 2981.099848946306,
                                 ('Holiday homes', 'Electricity', 2037): 3006.0176816990174,
                                 ('Holiday homes', 'Electricity', 2038): 3030.500843480454,
                                 ('Holiday homes', 'Electricity', 2039): 3054.5633682635794,
                                 ('Holiday homes', 'Electricity', 2040): 3078.2360829151885,
                                 ('Holiday homes', 'Electricity', 2041): 3088.371445072525,
                                 ('Holiday homes', 'Electricity', 2042): 3098.038942272916,
                                 ('Holiday homes', 'Electricity', 2043): 3107.215977306584,
                                 ('Holiday homes', 'Electricity', 2044): 3115.909226621874,
                                 ('Holiday homes', 'Electricity', 2045): 3124.080685820525,
                                 ('Holiday homes', 'Electricity', 2046): 3131.7128934222565,
                                 ('Holiday homes', 'Electricity', 2047): 3138.795577968081,
                                 ('Holiday homes', 'Electricity', 2048): 3145.3035743834735,
                                 ('Holiday homes', 'Electricity', 2049): 3151.2317469389395,
                                 ('Holiday homes', 'Electricity', 2050): 3156.5842042180766,
                                 ('Holiday homes', 'Fossil', 2020): 100.0, ('Holiday homes', 'Fossil', 2021): 100.0,
                                 ('Holiday homes', 'Fossil', 2022): 100.0, ('Holiday homes', 'Fossil', 2023): 100.0,
                                 ('Holiday homes', 'Fossil', 2024): 100.0, ('Holiday homes', 'Fossil', 2025): 100.0,
                                 ('Holiday homes', 'Fossil', 2026): 100.0, ('Holiday homes', 'Fossil', 2027): 100.0,
                                 ('Holiday homes', 'Fossil', 2028): 100.0, ('Holiday homes', 'Fossil', 2029): 100.0,
                                 ('Holiday homes', 'Fossil', 2030): 100.0, ('Holiday homes', 'Fossil', 2031): 100.0,
                                 ('Holiday homes', 'Fossil', 2032): 100.0, ('Holiday homes', 'Fossil', 2033): 100.0,
                                 ('Holiday homes', 'Fossil', 2034): 100.0, ('Holiday homes', 'Fossil', 2035): 100.0,
                                 ('Holiday homes', 'Fossil', 2036): 100.0, ('Holiday homes', 'Fossil', 2037): 100.0,
                                 ('Holiday homes', 'Fossil', 2038): 100.0, ('Holiday homes', 'Fossil', 2039): 100.0,
                                 ('Holiday homes', 'Fossil', 2040): 100.0, ('Holiday homes', 'Fossil', 2041): 100.0,
                                 ('Holiday homes', 'Fossil', 2042): 100.0, ('Holiday homes', 'Fossil', 2043): 100.0,
                                 ('Holiday homes', 'Fossil', 2044): 100.0, ('Holiday homes', 'Fossil', 2045): 100.0,
                                 ('Holiday homes', 'Fossil', 2046): 100.0, ('Holiday homes', 'Fossil', 2047): 100.0,
                                 ('Holiday homes', 'Fossil', 2048): 100.0, ('Holiday homes', 'Fossil', 2049): 100.0,
                                 ('Holiday homes', 'Fossil', 2050): 100.0}}


def test_energy_use_holiday_home(kalibrert_database_manager):
    energy_use_holiday_homes = extractors.extract_energy_use_holiday_homes(kalibrert_database_manager)

    result = pd.melt(energy_use_holiday_homes, id_vars=['building_group', 'energy_source'], var_name='year',
                     value_name='kwh')
    result = result.set_index(['building_group', 'energy_source', 'year'])
    result = result.sort_index(level=['building_group', 'energy_source', 'year'])

    expected = pd.DataFrame(expected_holiday_home)
    expected.index.names = ['building_group', 'energy_source', 'year']
    pd.testing.assert_frame_equal(result.round(2), expected.round(2))


@pytest.mark.explicit
def test_load_energy_use(kalibrert_database_manager):
    """ Make sure load_energy_use works as expected """
    def expected_energy_use_wide(expected_energy_use_long):
        expected = pd.DataFrame(expected_energy_use_long)
        expected.index.names = ['building_group', 'energy_source', 'year']
        expected['GWh'] = expected.kwh / 1_000_000
        expected = expected.drop(columns=['kwh'])
        expected = expected.reset_index().pivot(columns=['year'], index=['building_group', 'energy_source'],
                                                values=['GWh'])
        expected.columns = [c for c in expected.columns.get_level_values(1)]
        return expected
    from ebmgeodist.data_loader import load_energy_use
    result = load_energy_use(kalibrert_database_manager.file_handler.input_directory)
    result = result.drop(columns='U')
    result = result.set_index(['building_group', 'energy_source'])

    expected = expected_energy_use_wide(expected_building_group_energy_use)

    res = result.query('building_group!="Holiday homes"').sort_index()
    exp = expected.sort_index()
    assert res.compare(exp).empty, res.compare(exp)
    # pd.testing.assert_frame_equal(res, exp, check_dtype=False, check_index_type=False)


if __name__ == "__main__":
    pytest.main([sys.argv[0]])
