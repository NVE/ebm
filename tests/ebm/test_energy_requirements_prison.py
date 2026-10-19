import pandas as pd
import pytest

from ebm.model.data_classes import YearRange
from ebm.model.energy_requirement import energy_need_improvements


_energy_need_original_condition = pd.DataFrame(
    {
        'building_category': ['prison', 'prison', 'prison', 'prison', 'prison', 'prison', 'prison', 'prison'],
        'purpose': ['heating_rv', 'heating_rv', 'heating_rv', 'heating_rv', 'lighting', 'lighting', 'lighting', 'lighting'],
        'building_code': ['TEK49', 'TEK49', 'TEK49', 'TEK49', 'TEK49', 'TEK49', 'TEK49', 'TEK49'],
        'year': [2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023],
        'kwh_m2': [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        'building_condition': [
            'original_condition',
            'original_condition',
            'original_condition',
            'original_condition',
            'original_condition',
            'original_condition',
            'original_condition',
            'original_condition',
        ],
        'lineno': [5, 5, 5, 5, 5, 5, 5, 5],
        'model_start_year': [2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020],
        'model_end_year': [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023],
        'function': [
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
            'behaviour_factor',
        ],
        'start_year': [2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020],
        'end_year': [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023],
        'behaviour_factor': [1.06, 1.06, 1.06, 1.06, 1.06, 1.06, 1.06, 1.06],
        'heating_rv_factor': [1, 1, 1, 1, 1, 1, 1, 1],
        'uncalibrated_kwh_m2': [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
        'calibrated_kwh_m2': [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
    }
)

_improvement_building_upgrade = pd.DataFrame(
    {
        'building_category': ['prison', 'prison', 'prison', 'prison'],
        'building_code': ['TEK49', 'TEK49', 'TEK49', 'TEK49'],
        'purpose': ['heating_rv', 'heating_rv', 'heating_rv', 'heating_rv'],
        'building_condition': ['original_condition', 'renovation', 'small_measure', 'renovation_and_small_measure'],
        'reduction_share': [0.0, 0.2, 0.07, 0.25],
        'lineno': [2, 4, 3, 5],
    }
)

_energy_need_yearly_reduction = pd.DataFrame(
    {
        'building_category_definition': ['prison', 'prison'],
        'building_code_definition': ['default', 'default'],
        'purpose_definition': ['lighting', 'lighting'],
        'function': ['improvement_at_end_year', 'yearly_reduction'],
        'start_year': [2020, 2020],
        'value': [0.555555556, 0.005],
        'end_year': [2023, 2023],
        'lineno': [6, 7],
        'building_category': ['prison', 'prison'],
        'building_code': ['TEK49', 'TEK49'],
        'building_code_alias': ['default', 'default'],
        'purpose': ['lighting', 'lighting'],
        'purpose_alias': ['lighting', 'lighting'],
        'dupe': [False, False],
    }
)

use_building_category = 'hotel'

@pytest.mark.parametrize('use_category', ['hotel', 'prison'])
def test_energy_need_improvements_with_building_category(use_category):
    years = YearRange(2020, 2023)
    actual = energy_need_improvements(
        energy_need_original_condition=_energy_need_original_condition.assign(building_category=use_building_category),
        improvement_building_upgrade=_improvement_building_upgrade.assign(building_category=use_building_category),
        improvements=_energy_need_yearly_reduction.assign(building_category=use_building_category),
        years=years,
    )
    filter_query = f'building_category=="{use_building_category}" and purpose.isin(["heating_rv", "lighting"]) and building_condition=="original_condition"'
    filtered = actual.query(filter_query)

    assert filtered.building_category.to_list() == [use_building_category] * 8
    assert filtered.building_code.to_list() == ['TEK49'] * 8
    assert filtered.purpose.to_list() == ['heating_rv'] * 4 + ['lighting'] * 4

    assert filtered.kwh_m2.to_list() == pytest.approx([10.6, 10.6, 10.6, 10.6, 10.547, 8.55088, 6.574462, 4.61759])
