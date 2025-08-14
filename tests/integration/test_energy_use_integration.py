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
    'kwh': {('bolig', 'Bio', 2020): 4788825216.425719, ('bolig', 'Bio', 2021): 4781280230.150457,
            ('bolig', 'Bio', 2022): 4764208461.9151945, ('bolig', 'Bio', 2023): 4757203300.271702,
            ('bolig', 'Bio', 2024): 4702657720.902674, ('bolig', 'Bio', 2025): 4637666417.665211,
            ('bolig', 'Bio', 2026): 4576639450.690714, ('bolig', 'Bio', 2027): 4515036442.927422,
            ('bolig', 'Bio', 2028): 4453495280.110845, ('bolig', 'Bio', 2029): 4392678075.975616,
            ('bolig', 'Bio', 2030): 4331957397.639449, ('bolig', 'Bio', 2031): 4270638998.9928374,
            ('bolig', 'Bio', 2032): 4206703529.1823277, ('bolig', 'Bio', 2033): 4142902138.4826884,
            ('bolig', 'Bio', 2034): 4078480622.5262, ('bolig', 'Bio', 2035): 4013934811.311016,
            ('bolig', 'Bio', 2036): 3949606190.134894, ('bolig', 'Bio', 2037): 3872653761.7300243,
            ('bolig', 'Bio', 2038): 3795917186.048778, ('bolig', 'Bio', 2039): 3719260312.864082,
            ('bolig', 'Bio', 2040): 3645969161.6627994, ('bolig', 'Bio', 2041): 3620731852.3399687,
            ('bolig', 'Bio', 2042): 3598373226.7441354, ('bolig', 'Bio', 2043): 3575299283.225951,
            ('bolig', 'Bio', 2044): 3551903949.5981746, ('bolig', 'Bio', 2045): 3528169064.9771514,
            ('bolig', 'Bio', 2046): 3504087473.877657, ('bolig', 'Bio', 2047): 3476748690.6934733,
            ('bolig', 'Bio', 2048): 3449057595.4897804, ('bolig', 'Bio', 2049): 3420281067.0114727,
            ('bolig', 'Bio', 2050): 3390632536.1343603, ('bolig', 'DH', 2020): 1857082296.4135938,
            ('bolig', 'DH', 2021): 1860856978.739231, ('bolig', 'DH', 2022): 1863752230.1062946,
            ('bolig', 'DH', 2023): 1873218107.0187275, ('bolig', 'DH', 2024): 2058677339.9957652,
            ('bolig', 'DH', 2025): 2098902313.989615, ('bolig', 'DH', 2026): 2101902151.602252,
            ('bolig', 'DH', 2027): 2139031655.4884844, ('bolig', 'DH', 2028): 2176490076.8487096,
            ('bolig', 'DH', 2029): 2214156705.618156, ('bolig', 'DH', 2030): 2215561142.7889395,
            ('bolig', 'DH', 2031): 2252524983.891313, ('bolig', 'DH', 2032): 2288557476.638861,
            ('bolig', 'DH', 2033): 2288170212.7096043, ('bolig', 'DH', 2034): 2323278447.7259874,
            ('bolig', 'DH', 2035): 2321617876.283609, ('bolig', 'DH', 2036): 2356213289.6906114,
            ('bolig', 'DH', 2037): 2385764893.3904543, ('bolig', 'DH', 2038): 2378616590.5865026,
            ('bolig', 'DH', 2039): 2407358834.5643554, ('bolig', 'DH', 2040): 2400247626.72628,
            ('bolig', 'DH', 2041): 2428531972.0246058, ('bolig', 'DH', 2042): 2421235197.5354657,
            ('bolig', 'DH', 2043): 2449398034.5029106, ('bolig', 'DH', 2044): 2477034349.527523,
            ('bolig', 'DH', 2045): 2468570512.792454, ('bolig', 'DH', 2046): 2495160207.558666,
            ('bolig', 'DH', 2047): 2484466249.320536, ('bolig', 'DH', 2048): 2508337205.5425124,
            ('bolig', 'DH', 2049): 2495685156.8676863, ('bolig', 'DH', 2050): 2482497950.4832416,
            ('bolig', 'Electricity', 2020): 37071496927.11284, ('bolig', 'Electricity', 2021): 37029197525.37465,
            ('bolig', 'Electricity', 2022): 36989418901.482605, ('bolig', 'Electricity', 2023): 37088406609.24847,
            ('bolig', 'Electricity', 2024): 36867007293.05276, ('bolig', 'Electricity', 2025): 36750035439.66159,
            ('bolig', 'Electricity', 2026): 36664834747.2307, ('bolig', 'Electricity', 2027): 36481736708.55523,
            ('bolig', 'Electricity', 2028): 36318343183.4606, ('bolig', 'Electricity', 2029): 36154451792.15,
            ('bolig', 'Electricity', 2030): 36001151842.6294, ('bolig', 'Electricity', 2031): 35962804667.080765,
            ('bolig', 'Electricity', 2032): 35915198138.81447, ('bolig', 'Electricity', 2033): 35879856685.60712,
            ('bolig', 'Electricity', 2034): 35816219297.32666, ('bolig', 'Electricity', 2035): 35785005351.70673,
            ('bolig', 'Electricity', 2036): 35694160536.33721, ('bolig', 'Electricity', 2037): 35565639809.882866,
            ('bolig', 'Electricity', 2038): 35468146253.347664, ('bolig', 'Electricity', 2039): 35321223972.89438,
            ('bolig', 'Electricity', 2040): 35198504837.56481, ('bolig', 'Electricity', 2041): 35087715428.0407,
            ('bolig', 'Electricity', 2042): 35023661993.97515, ('bolig', 'Electricity', 2043): 34896484726.940155,
            ('bolig', 'Electricity', 2044): 34786775527.04805, ('bolig', 'Electricity', 2045): 34708213183.45203,
            ('bolig', 'Electricity', 2046): 34589761749.04002, ('bolig', 'Electricity', 2047): 34471758702.1105,
            ('bolig', 'Electricity', 2048): 34335149779.40463, ('bolig', 'Electricity', 2049): 34217253629.19904,
            ('bolig', 'Electricity', 2050): 34092268470.395252, ('bolig', 'Ingen', 2020): 0.0,
            ('bolig', 'Ingen', 2021): 0.0, ('bolig', 'Ingen', 2022): 0.0, ('bolig', 'Ingen', 2023): 0.0,
            ('bolig', 'Ingen', 2024): 0.0, ('bolig', 'Ingen', 2025): 0.0, ('bolig', 'Ingen', 2026): 0.0,
            ('bolig', 'Ingen', 2027): 0.0, ('bolig', 'Ingen', 2028): 0.0, ('bolig', 'Ingen', 2029): 0.0,
            ('bolig', 'Ingen', 2030): 0.0, ('bolig', 'Ingen', 2031): 0.0, ('bolig', 'Ingen', 2032): 0.0,
            ('bolig', 'Ingen', 2033): 0.0, ('bolig', 'Ingen', 2034): 0.0, ('bolig', 'Ingen', 2035): 0.0,
            ('bolig', 'Ingen', 2036): 0.0, ('bolig', 'Ingen', 2037): 0.0, ('bolig', 'Ingen', 2038): 0.0,
            ('bolig', 'Ingen', 2039): 0.0, ('bolig', 'Ingen', 2040): 0.0, ('bolig', 'Ingen', 2041): 0.0,
            ('bolig', 'Ingen', 2042): 0.0, ('bolig', 'Ingen', 2043): 0.0, ('bolig', 'Ingen', 2044): 0.0,
            ('bolig', 'Ingen', 2045): 0.0, ('bolig', 'Ingen', 2046): 0.0, ('bolig', 'Ingen', 2047): 0.0,
            ('bolig', 'Ingen', 2048): 0.0, ('bolig', 'Ingen', 2049): 0.0, ('bolig', 'Ingen', 2050): 0.0,
            ('bolig', 'Solar', 2020): 2091260.766183585, ('bolig', 'Solar', 2021): 2088301.8014598538,
            ('bolig', 'Solar', 2022): 2081448.643985017, ('bolig', 'Solar', 2023): 2079170.9996649974,
            ('bolig', 'Solar', 2024): 2074582.1317013446, ('bolig', 'Solar', 2025): 2068490.6376518041,
            ('bolig', 'Solar', 2026): 2063688.091091381, ('bolig', 'Solar', 2027): 2058394.9455057923,
            ('bolig', 'Solar', 2028): 2053077.0313689576, ('bolig', 'Solar', 2029): 2047959.1863727896,
            ('bolig', 'Solar', 2030): 2042770.0668798666, ('bolig', 'Solar', 2031): 2037159.4654290455,
            ('bolig', 'Solar', 2032): 2030179.6904434524, ('bolig', 'Solar', 2033): 2023102.6230804604,
            ('bolig', 'Solar', 2034): 2015534.885926151, ('bolig', 'Solar', 2035): 2007691.2296148627,
            ('bolig', 'Solar', 2036): 1999768.3305618546, ('bolig', 'Solar', 2037): 1985361.660853026,
            ('bolig', 'Solar', 2038): 1970693.435959307, ('bolig', 'Solar', 2039): 1955776.780073403,
            ('bolig', 'Solar', 2040): 1942138.4943073988, ('bolig', 'Solar', 2041): 1928725.4754622038,
            ('bolig', 'Solar', 2042): 1916737.2952380048, ('bolig', 'Solar', 2043): 1904394.1817497099,
            ('bolig', 'Solar', 2044): 1891876.4088004471, ('bolig', 'Solar', 2045): 1879173.7739817551,
            ('bolig', 'Solar', 2046): 1866282.1466547523, ('bolig', 'Solar', 2047): 1851650.0434458097,
            ('bolig', 'Solar', 2048): 1836803.6935016927, ('bolig', 'Solar', 2049): 1821374.6119763046,
            ('bolig', 'Solar', 2050): 1805491.7126416897, ('yrkesbygg', 'Bio', 2020): 101557132.72809598,
            ('yrkesbygg', 'Bio', 2021): 101302607.78075051, ('yrkesbygg', 'Bio', 2022): 101188389.60102122,
            ('yrkesbygg', 'Bio', 2023): 101346044.63769531, ('yrkesbygg', 'Bio', 2024): 101503459.92926183,
            ('yrkesbygg', 'Bio', 2025): 101556799.89033622, ('yrkesbygg', 'Bio', 2026): 101506765.64682631,
            ('yrkesbygg', 'Bio', 2027): 101277700.80668746, ('yrkesbygg', 'Bio', 2028): 101072155.97942267,
            ('yrkesbygg', 'Bio', 2029): 100871426.30954705, ('yrkesbygg', 'Bio', 2030): 100305737.5381496,
            ('yrkesbygg', 'Bio', 2031): 99903987.42877857, ('yrkesbygg', 'Bio', 2032): 99552412.15487796,
            ('yrkesbygg', 'Bio', 2033): 99191646.07625379, ('yrkesbygg', 'Bio', 2034): 98832200.92927141,
            ('yrkesbygg', 'Bio', 2035): 98474978.72599679, ('yrkesbygg', 'Bio', 2036): 98130597.74692447,
            ('yrkesbygg', 'Bio', 2037): 97785805.07775594, ('yrkesbygg', 'Bio', 2038): 97430782.0635449,
            ('yrkesbygg', 'Bio', 2039): 97068448.56611995, ('yrkesbygg', 'Bio', 2040): 96696368.30557051,
            ('yrkesbygg', 'Bio', 2041): 96275942.15789312, ('yrkesbygg', 'Bio', 2042): 95893566.53443238,
            ('yrkesbygg', 'Bio', 2043): 95497780.5120125, ('yrkesbygg', 'Bio', 2044): 95093005.49909942,
            ('yrkesbygg', 'Bio', 2045): 94681951.711988, ('yrkesbygg', 'Bio', 2046): 94260578.26055041,
            ('yrkesbygg', 'Bio', 2047): 93439123.67882389, ('yrkesbygg', 'Bio', 2048): 92833428.01497278,
            ('yrkesbygg', 'Bio', 2049): 92231780.86995913, ('yrkesbygg', 'Bio', 2050): 91622027.80740257,
            ('yrkesbygg', 'DH', 2020): 4423747518.8634615, ('yrkesbygg', 'DH', 2021): 4415568070.12422,
            ('yrkesbygg', 'DH', 2022): 4414384497.767668, ('yrkesbygg', 'DH', 2023): 4426506223.131906,
            ('yrkesbygg', 'DH', 2024): 4527944403.31363, ('yrkesbygg', 'DH', 2025): 4559790929.9018345,
            ('yrkesbygg', 'DH', 2026): 4581523665.738846, ('yrkesbygg', 'DH', 2027): 4589719130.0956955,
            ('yrkesbygg', 'DH', 2028): 4599192469.805006, ('yrkesbygg', 'DH', 2029): 4608803865.051731,
            ('yrkesbygg', 'DH', 2030): 4601976683.323316, ('yrkesbygg', 'DH', 2031): 4613137777.879646,
            ('yrkesbygg', 'DH', 2032): 4621232411.851534, ('yrkesbygg', 'DH', 2033): 4633706981.501938,
            ('yrkesbygg', 'DH', 2034): 4641182344.3524885, ('yrkesbygg', 'DH', 2035): 4648598631.548968,
            ('yrkesbygg', 'DH', 2036): 4661270680.361897, ('yrkesbygg', 'DH', 2037): 4668828796.079716,
            ('yrkesbygg', 'DH', 2038): 4675752380.170249, ('yrkesbygg', 'DH', 2039): 4682161357.608822,
            ('yrkesbygg', 'DH', 2040): 4683142671.717943, ('yrkesbygg', 'DH', 2041): 4686478543.857488,
            ('yrkesbygg', 'DH', 2042): 4691426567.982776, ('yrkesbygg', 'DH', 2043): 4695587785.653626,
            ('yrkesbygg', 'DH', 2044): 4694392940.027948, ('yrkesbygg', 'DH', 2045): 4697463359.601239,
            ('yrkesbygg', 'DH', 2046): 4695131341.303659, ('yrkesbygg', 'DH', 2047): 4677920868.654059,
            ('yrkesbygg', 'DH', 2048): 4676418225.704957, ('yrkesbygg', 'DH', 2049): 4674722677.0622,
            ('yrkesbygg', 'DH', 2050): 4672303519.084109, ('yrkesbygg', 'Electricity', 2020): 25060040864.557102,
            ('yrkesbygg', 'Electricity', 2021): 24781866798.24038,
            ('yrkesbygg', 'Electricity', 2022): 24554204359.587547,
            ('yrkesbygg', 'Electricity', 2023): 24414448636.34977,
            ('yrkesbygg', 'Electricity', 2024): 24134264259.48454,
            ('yrkesbygg', 'Electricity', 2025): 23907109002.703754,
            ('yrkesbygg', 'Electricity', 2026): 23650318194.1226,
            ('yrkesbygg', 'Electricity', 2027): 23346427931.265903,
            ('yrkesbygg', 'Electricity', 2028): 23053576919.774857,
            ('yrkesbygg', 'Electricity', 2029): 22755174910.569397,
            ('yrkesbygg', 'Electricity', 2030): 22380307452.650845,
            ('yrkesbygg', 'Electricity', 2031): 22305918274.076366,
            ('yrkesbygg', 'Electricity', 2032): 22239753792.264534,
            ('yrkesbygg', 'Electricity', 2033): 22170009239.42864,
            ('yrkesbygg', 'Electricity', 2034): 22101923090.827156,
            ('yrkesbygg', 'Electricity', 2035): 22036110791.946575,
            ('yrkesbygg', 'Electricity', 2036): 21965872384.988487,
            ('yrkesbygg', 'Electricity', 2037): 21895577817.117966,
            ('yrkesbygg', 'Electricity', 2038): 21825511491.981224,
            ('yrkesbygg', 'Electricity', 2039): 21753171046.01578,
            ('yrkesbygg', 'Electricity', 2040): 21683344801.40307,
            ('yrkesbygg', 'Electricity', 2041): 21597841256.130234,
            ('yrkesbygg', 'Electricity', 2042): 21518001413.45979,
            ('yrkesbygg', 'Electricity', 2043): 21435631525.407852,
            ('yrkesbygg', 'Electricity', 2044): 21355874312.822987,
            ('yrkesbygg', 'Electricity', 2045): 21269303814.17199,
            ('yrkesbygg', 'Electricity', 2046): 21185064002.886875,
            ('yrkesbygg', 'Electricity', 2047): 21012590312.61142,
            ('yrkesbygg', 'Electricity', 2048): 20885462601.59522,
            ('yrkesbygg', 'Electricity', 2049): 20757121513.622425,
            ('yrkesbygg', 'Electricity', 2050): 20626689875.071304, ('yrkesbygg', 'Fossil', 2020): 22325995.474820293,
            ('yrkesbygg', 'Fossil', 2021): 22284594.592829693, ('yrkesbygg', 'Fossil', 2022): 22278464.234987915,
            ('yrkesbygg', 'Fossil', 2023): 22339423.1518955, ('yrkesbygg', 'Fossil', 2024): 17919320.106229,
            ('yrkesbygg', 'Fossil', 2025): 14955498.53703225, ('yrkesbygg', 'Fossil', 2026): 11969013.472209465,
            ('yrkesbygg', 'Fossil', 2027): 8963499.839415869, ('yrkesbygg', 'Fossil', 2028): 5968539.153594006,
            ('yrkesbygg', 'Fossil', 2029): 2980818.346081184, ('yrkesbygg', 'Ingen', 2020): 0.0,
            ('yrkesbygg', 'Ingen', 2021): 0.0, ('yrkesbygg', 'Ingen', 2022): 0.0, ('yrkesbygg', 'Ingen', 2023): 0.0,
            ('yrkesbygg', 'Ingen', 2024): 0.0, ('yrkesbygg', 'Ingen', 2025): 0.0, ('yrkesbygg', 'Ingen', 2026): 0.0,
            ('yrkesbygg', 'Ingen', 2027): 0.0, ('yrkesbygg', 'Ingen', 2028): 0.0, ('yrkesbygg', 'Ingen', 2029): 0.0,
            ('yrkesbygg', 'Ingen', 2030): 0.0, ('yrkesbygg', 'Ingen', 2031): 0.0, ('yrkesbygg', 'Ingen', 2032): 0.0,
            ('yrkesbygg', 'Ingen', 2033): 0.0, ('yrkesbygg', 'Ingen', 2034): 0.0, ('yrkesbygg', 'Ingen', 2035): 0.0,
            ('yrkesbygg', 'Ingen', 2036): 0.0, ('yrkesbygg', 'Ingen', 2037): 0.0, ('yrkesbygg', 'Ingen', 2038): 0.0,
            ('yrkesbygg', 'Ingen', 2039): 0.0, ('yrkesbygg', 'Ingen', 2040): 0.0, ('yrkesbygg', 'Ingen', 2041): 0.0,
            ('yrkesbygg', 'Ingen', 2042): 0.0, ('yrkesbygg', 'Ingen', 2043): 0.0, ('yrkesbygg', 'Ingen', 2044): 0.0,
            ('yrkesbygg', 'Ingen', 2045): 0.0, ('yrkesbygg', 'Ingen', 2046): 0.0, ('yrkesbygg', 'Ingen', 2047): 0.0,
            ('yrkesbygg', 'Ingen', 2048): 0.0, ('yrkesbygg', 'Ingen', 2049): 0.0, ('yrkesbygg', 'Ingen', 2050): 0.0,
            ('yrkesbygg', 'Solar', 2020): 866616.4581550302, ('yrkesbygg', 'Solar', 2021): 864444.5229845959,
            ('yrkesbygg', 'Solar', 2022): 863469.8661415464, ('yrkesbygg', 'Solar', 2023): 864815.182278608,
            ('yrkesbygg', 'Solar', 2024): 866158.4526011569, ('yrkesbygg', 'Solar', 2025): 866613.6179539261,
            ('yrkesbygg', 'Solar', 2026): 866186.6612475654, ('yrkesbygg', 'Solar', 2027): 864231.9845536058,
            ('yrkesbygg', 'Solar', 2028): 862478.0109486872, ('yrkesbygg', 'Solar', 2029): 860765.1264778348,
            ('yrkesbygg', 'Solar', 2030): 855937.9401806492, ('yrkesbygg', 'Solar', 2031): 852509.6900174757,
            ('yrkesbygg', 'Solar', 2032): 849509.5962726241, ('yrkesbygg', 'Solar', 2033): 846431.0747263648,
            ('yrkesbygg', 'Solar', 2034): 843363.8250727843, ('yrkesbygg', 'Solar', 2035): 840315.544442363,
            ('yrkesbygg', 'Solar', 2036): 837376.841701132, ('yrkesbygg', 'Solar', 2037): 834434.6258889482,
            ('yrkesbygg', 'Solar', 2038): 831405.11157642, ('yrkesbygg', 'Solar', 2039): 828313.21479109,
            ('yrkesbygg', 'Solar', 2040): 825138.1460501275, ('yrkesbygg', 'Solar', 2041): 821550.5278373187,
            ('yrkesbygg', 'Solar', 2042): 818287.6057796868, ('yrkesbygg', 'Solar', 2043): 814910.2488996427,
            ('yrkesbygg', 'Solar', 2044): 811456.1863575309, ('yrkesbygg', 'Solar', 2045): 807948.5452147719,
            ('yrkesbygg', 'Solar', 2046): 804352.8433843245, ('yrkesbygg', 'Solar', 2047): 797343.1332731004,
            ('yrkesbygg', 'Solar', 2048): 792174.5565633595, ('yrkesbygg', 'Solar', 2049): 787040.5270386506,
            ('yrkesbygg', 'Solar', 2050): 781837.3273693894}}


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
    result = result[expect_columns + ['kwh']].groupby(by=expect_columns).sum()

    expected = pd.DataFrame(expected_building_group_energy_use)
    expected.index.names = expect_columns

    df = pd.merge(left=result, right=expected, suffixes=('_result', '_expected'), on=expect_columns, how='outer')

    df_diff = df[df['kwh_result'] != df['kwh_expected']]

    for i, r in df_diff.iterrows():
        logger.error(f'Error in row {i} expected: {r[1]} was: {r[0]}')

    assert df_diff.empty, 'Expected no differences between the dataframes result and expected'


expected_holiday_home = {'kwh': {('Fritidsboliger', 'Bio', 2020): 1450.0, ('Fritidsboliger', 'Bio', 2021): 1270.0,
                                 ('Fritidsboliger', 'Bio', 2022): 1390.0, ('Fritidsboliger', 'Bio', 2023): 1390.0,
                                 ('Fritidsboliger', 'Bio', 2024): 1363.993311965345,
                                 ('Fritidsboliger', 'Bio', 2025): 1376.2609385993053,
                                 ('Fritidsboliger', 'Bio', 2026): 1385.7758570733436,
                                 ('Fritidsboliger', 'Bio', 2027): 1392.6203955040182,
                                 ('Fritidsboliger', 'Bio', 2028): 1399.4936873365957,
                                 ('Fritidsboliger', 'Bio', 2029): 1406.3183195659535,
                                 ('Fritidsboliger', 'Bio', 2030): 1413.0237603429798,
                                 ('Fritidsboliger', 'Bio', 2031): 1419.6618640933284,
                                 ('Fritidsboliger', 'Bio', 2032): 1426.1893778363594,
                                 ('Fritidsboliger', 'Bio', 2033): 1432.595242571341,
                                 ('Fritidsboliger', 'Bio', 2034): 1438.9165673896175,
                                 ('Fritidsboliger', 'Bio', 2035): 1445.120912555709,
                                 ('Fritidsboliger', 'Bio', 2036): 1451.2318706045103,
                                 ('Fritidsboliger', 'Bio', 2037): 1457.05185405628,
                                 ('Fritidsboliger', 'Bio', 2038): 1462.6120738686395,
                                 ('Fritidsboliger', 'Bio', 2039): 1467.9226060200324,
                                 ('Fritidsboliger', 'Bio', 2040): 1473.0013906672023,
                                 ('Fritidsboliger', 'Bio', 2041): 1477.8513768770104,
                                 ('Fritidsboliger', 'Bio', 2042): 1482.4774797608936,
                                 ('Fritidsboliger', 'Bio', 2043): 1486.8688860736913,
                                 ('Fritidsboliger', 'Bio', 2044): 1491.0287906378373,
                                 ('Fritidsboliger', 'Bio', 2045): 1494.9390075410172,
                                 ('Fritidsboliger', 'Bio', 2046): 1498.5911810937894,
                                 ('Fritidsboliger', 'Bio', 2047): 1501.9803961847176,
                                 ('Fritidsboliger', 'Bio', 2048): 1505.0946107907826,
                                 ('Fritidsboliger', 'Bio', 2049): 1507.9313673562658,
                                 ('Fritidsboliger', 'Bio', 2050): 1510.4926319257427,
                                 ('Fritidsboliger', 'Electricity', 2020): 2467.0,
                                 ('Fritidsboliger', 'Electricity', 2021): 2819.0,
                                 ('Fritidsboliger', 'Electricity', 2022): 2318.0,
                                 ('Fritidsboliger', 'Electricity', 2023): 2427.0,
                                 ('Fritidsboliger', 'Electricity', 2024): 2510.664757550429,
                                 ('Fritidsboliger', 'Electricity', 2025): 2569.976712184894,
                                 ('Fritidsboliger', 'Electricity', 2026): 2624.7297237690896,
                                 ('Fritidsboliger', 'Electricity', 2027): 2674.8615206420313,
                                 ('Fritidsboliger', 'Electricity', 2028): 2725.4146629389325,
                                 ('Fritidsboliger', 'Electricity', 2029): 2763.7274703003145,
                                 ('Fritidsboliger', 'Electricity', 2030): 2802.04677770458,
                                 ('Fritidsboliger', 'Electricity', 2031): 2840.469973626825,
                                 ('Fritidsboliger', 'Electricity', 2032): 2878.906153252153,
                                 ('Fritidsboliger', 'Electricity', 2033): 2904.581963019164,
                                 ('Fritidsboliger', 'Electricity', 2034): 2930.199594470989,
                                 ('Fritidsboliger', 'Electricity', 2035): 2955.69044266053,
                                 ('Fritidsboliger', 'Electricity', 2036): 2981.099848946306,
                                 ('Fritidsboliger', 'Electricity', 2037): 3006.0176816990174,
                                 ('Fritidsboliger', 'Electricity', 2038): 3030.500843480454,
                                 ('Fritidsboliger', 'Electricity', 2039): 3054.5633682635794,
                                 ('Fritidsboliger', 'Electricity', 2040): 3078.2360829151885,
                                 ('Fritidsboliger', 'Electricity', 2041): 3088.371445072525,
                                 ('Fritidsboliger', 'Electricity', 2042): 3098.038942272916,
                                 ('Fritidsboliger', 'Electricity', 2043): 3107.215977306584,
                                 ('Fritidsboliger', 'Electricity', 2044): 3115.909226621874,
                                 ('Fritidsboliger', 'Electricity', 2045): 3124.080685820525,
                                 ('Fritidsboliger', 'Electricity', 2046): 3131.7128934222565,
                                 ('Fritidsboliger', 'Electricity', 2047): 3138.795577968081,
                                 ('Fritidsboliger', 'Electricity', 2048): 3145.3035743834735,
                                 ('Fritidsboliger', 'Electricity', 2049): 3151.2317469389395,
                                 ('Fritidsboliger', 'Electricity', 2050): 3156.5842042180766,
                                 ('Fritidsboliger', 'Fossil', 2020): 100.0, ('Fritidsboliger', 'Fossil', 2021): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2022): 100.0, ('Fritidsboliger', 'Fossil', 2023): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2024): 100.0, ('Fritidsboliger', 'Fossil', 2025): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2026): 100.0, ('Fritidsboliger', 'Fossil', 2027): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2028): 100.0, ('Fritidsboliger', 'Fossil', 2029): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2030): 100.0, ('Fritidsboliger', 'Fossil', 2031): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2032): 100.0, ('Fritidsboliger', 'Fossil', 2033): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2034): 100.0, ('Fritidsboliger', 'Fossil', 2035): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2036): 100.0, ('Fritidsboliger', 'Fossil', 2037): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2038): 100.0, ('Fritidsboliger', 'Fossil', 2039): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2040): 100.0, ('Fritidsboliger', 'Fossil', 2041): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2042): 100.0, ('Fritidsboliger', 'Fossil', 2043): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2044): 100.0, ('Fritidsboliger', 'Fossil', 2045): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2046): 100.0, ('Fritidsboliger', 'Fossil', 2047): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2048): 100.0, ('Fritidsboliger', 'Fossil', 2049): 100.0,
                                 ('Fritidsboliger', 'Fossil', 2050): 100.0}}

def test_energy_use_holiday_home(kalibrert_database_manager):
    energy_use_holiday_homes = extractors.extract_energy_use_holiday_homes(kalibrert_database_manager)

    result = pd.melt(energy_use_holiday_homes, id_vars=['building_group', 'energy_source'], var_name='year',
                     value_name='kwh')
    result = result.set_index(['building_group', 'energy_source', 'year'])
    result = result.sort_index(level=['building_group', 'energy_source', 'year'])

    expected = pd.DataFrame(expected_holiday_home)
    expected.index.names = ['building_group', 'energy_source', 'year']
    pd.testing.assert_frame_equal(result, expected)


if __name__ == "__main__":
    pytest.main([sys.argv[0]])
