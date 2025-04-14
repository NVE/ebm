import io
from typing import cast

import pandas as pd
import pytest

from ebm.model.dataframemodels import YearlyReduction, EnergyNeedYearlyImprovements, PolicyImprovement


def test_from_energy_need_yearly_improvements():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 2021, 'yearly_reduction', 2023,0.2],
            # ['house', 'TEK1', 'heating_rv', 1.0, 2021, 'improvement_at_end_year', 2023]
        ],
        columns=['building_category', 'TEK', 'purpose', 'start_year', 'function', 'end_year', 'yearly_efficiency_improvement']
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    # Casting df to DataFrame so that Pycharm stops warning about DataFrameBase not having the method set_index
    df = cast(pd.DataFrame, df).set_index(['building_category','TEK','purpose','start_year', 'end_year'])

    expected_yearly_reduction_factor = pd.Series(
        data=[0.2],
        name='yearly_efficiency_improvement',
        index=pd.Index(data=[('house', 'TEK1', 'lighting', 2021, 2023)],
                       name=('building_category', 'TEK', 'purpose' ,'start_year',  'end_year')
                       )
    )

    actual_yearly_reduction_factor = df['yearly_efficiency_improvement']
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
    df = cast(pd.DataFrame, df).set_index(['building_category','TEK','purpose','start_year', 'end_year'])

    lighting = df.query('purpose=="lighting"')

    assert (lighting.improvement_at_end_year == 0.5555555555555556).all()

    el_eq = df.query('purpose=="electrical_equipment"')
    expected_policy_improvement_factor = [0.8]
    assert el_eq.improvement_at_end_year.round(8).tolist() == expected_policy_improvement_factor


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