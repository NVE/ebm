import io

import pandas as pd

from ebm.energy_requirements import transform_energy_requirements_by_condition
from ebm.model import BuildingCategory
from ebm.model.building_condition import BuildingCondition


def test_transform_energy_requirements_by_condition():
    test_data = io.StringIO("""building_category,TEK,purpose,kw_h_m
apartment_block,PRE_TEK49,HeatingRV, 100
apartment_block,TEK07,HeatingRV,200
house,TEK07,HeatingRV,400""")
    energy_requirements = pd.read_csv(test_data)
    condition_reduction = pd.DataFrame(data=[[BuildingCondition.ORIGINAL_CONDITION, 0],
                                             [BuildingCondition.SMALL_MEASURE, 0.2],
                                             [BuildingCondition.RENOVATION, 0.4],
                                             [BuildingCondition.RENOVATION_AND_SMALL_MEASURE, 0.8]],
                                       columns=['building_condition', 'reduction'])

    df = transform_energy_requirements_by_condition(energy_requirements, condition_reduction)

    pre_tek49 = df[(df.building_category == 'apartment_block') &
                   (df.TEK == 'PRE_TEK49') &
                   (df.purpose == 'HeatingRV')]

    expected_pre_tek49 = pd.Series([100.0], name='kw_h_m')
    pd.testing.assert_series_equal(pre_tek49[pre_tek49.building_condition == 'original_condition'].kw_h_m,
                                   expected_pre_tek49)
    pd.testing.assert_series_equal(
        pre_tek49.kw_h_m,
        pd.Series([100.0, 80.0, 60.0, 20.0], name='kw_h_m'), check_index=False)


def test_dummy():
    energy_required = pd.Series(data=[100.0, 200.0, 400.0],
                                index=[(BuildingCategory.HOUSE, 'PRETEK_49'),
                                       (BuildingCategory.APARTMENT_BLOCK, 'PRETEK_49'),
                                       (BuildingCategory.APARTMENT_BLOCK, 'TEK07')],
                                name='heating_rv')

    condition_reduction = pd.Series(data=[0, 0.2, 0.4, 0.8],
                                    index=[BuildingCondition.ORIGINAL_CONDITION,
                                           BuildingCondition.SMALL_MEASURE,
                                           BuildingCondition.RENOVATION,
                                           BuildingCondition.RENOVATION_AND_SMALL_MEASURE])



