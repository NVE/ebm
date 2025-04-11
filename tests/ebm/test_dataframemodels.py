import io
from typing import cast

import pandas as pd
import pytest

from ebm.model.dataframemodels import YearlyReduction, EnergyNeedYearlyImprovements, PolicyImprovement


def test_from_energy_need_yearly_improvements():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 0.2, 2021, 'yearly_reduction', 2023],
            ['house', 'TEK1', 'heating_rv', 1.0, 2021, 'improvement_at_end_year', 2023]
        ],
        columns='building_category,TEK,purpose,yearly_efficiency_improvement,start_year,function,end_year'.split(',')
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    # Casting df to DataFrame so that Pycharm stops warning about DataFrameBase not having the method set_index
    df = cast(pd.DataFrame, df).set_index(['building_category','TEK','purpose','year'])

    expected_yearly_reduction_factor = pd.Series(
        data=[0.8**(y-2020) for y in range(2021, 2024)],
        name='yearly_reduction_factor',
        index=pd.Index(data=[('house', 'TEK1', 'lighting', y) for y in range(2021, 2024)],
                       name=('building_category', 'TEK', 'purpose' ,'year')
                       )
    )

    actual_yearly_reduction_factor = df['yearly_reduction_factor']
    pd.testing.assert_series_equal(actual_yearly_reduction_factor, expected_yearly_reduction_factor)


def test_from_energy_need_policy_improvement():
    csv_file="""building_category,TEK,purpose,yearly_efficiency_improvement,start_year,function,end_year
default,default,lighting,0.005,2031,yearly_reduction,2050
house,TEK01,lighting,0.5555555555555556,2020,improvement_at_end_year,2030
house,TEK01,electrical_equipment,0.8,2025,improvement_at_end_year,2029
    """.strip()
    df_input = pd.read_csv(io.StringIO(csv_file))
    df = PolicyImprovement.from_energy_need_yearly_improvements(EnergyNeedYearlyImprovements(df_input))

    assert isinstance(df, pd.DataFrame), f'Expected df to be a DataFrame. Was: {type(df)}'
    df = cast(pd.DataFrame, df).set_index(['building_category','TEK','purpose','year'])

    actual_years = set(df.loc[('house', 'TEK01', 'lighting', slice(None))].index.get_level_values(level='year'))
    expected_years = {2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030}

    assert actual_years == expected_years

    lighting = df.query('purpose=="lighting"')

    assert (lighting.improvement_at_end_year == 0.5555555555555556).all()

    expected_policy_improvement_factor = [1., 0.94444444, 0.88888889, 0.83333333, 0.77777778,
                                          0.72222222, 0.66666667, 0.61111111, 0.55555556, 0.5,
                                          0.44444444]
    assert lighting.policy_improvement_factor.round(8).tolist() == expected_policy_improvement_factor

    el_eq = df.query('purpose=="electrical_equipment"')
    expected_policy_improvement_factor = [1., 0.8, 0.6, 0.4, 0.2]
    assert el_eq.policy_improvement_factor.round(8).tolist() == expected_policy_improvement_factor


def test_from_energy_need_policy_improvement_explode_groups():
    csv_file="""building_category,TEK,purpose,yearly_efficiency_improvement,start_year,function,end_year
residential,TEK01+TEK02,lighting,0.1,2020,improvement_at_end_year,2021
non_residential,TEK02,default,0.2,2020,improvement_at_end_year,2021
non_residential,TEK02,default,0.2,2020,yearly_reduction,2021
    """.strip()
    #
    df_input = pd.read_csv(io.StringIO(csv_file))
    df = PolicyImprovement.from_energy_need_yearly_improvements(EnergyNeedYearlyImprovements(df_input))

    assert isinstance(df, pd.DataFrame), f'Expected df to be a DataFrame. Was: {type(df)}'
    df = cast(pd.DataFrame, df).set_index(['building_category','TEK','purpose','start_year', 'end_year'])

    house_light = df.query('building_category=="house" and purpose=="lighting"')

    expected_house_lighting = pd.Series(
        data=[0.1, 0.1],
        name='improvement_at_end_year',
        index=pd.Index(data=[('house', 'TEK01', 'lighting', 2020, 2021),
                            ('house', 'TEK02', 'lighting', 2020, 2021)],
                       name=('building_category', 'TEK', 'purpose', 'start_year', 'end_year')))

    pd.testing.assert_series_equal(house_light.improvement_at_end_year, expected_house_lighting)

    non_residential = df.query('improvement_at_end_year==0.2')
    assert 'hotel' in non_residential.index.get_level_values(level='building_category')
    assert 'school' in non_residential.index.get_level_values(level='building_category')
    assert 'house' not in non_residential.index.get_level_values(level='building_category')
    assert 'apartment_block' not in non_residential.index.get_level_values(level='building_category')

    assert 'heating_rv' in non_residential.index.get_level_values(level='purpose')
    assert 'heating_dhw' in non_residential.index.get_level_values(level='purpose')
    assert 'fans_and_pumps' in non_residential.index.get_level_values(level='purpose')
    assert 'electrical_equipment' in non_residential.index.get_level_values(level='purpose')
    assert 'lighting' in non_residential.index.get_level_values(level='purpose')


if __name__ == '__main__':
    pytest.main()