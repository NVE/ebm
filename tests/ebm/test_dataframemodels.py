import io
from typing import cast

import pandas as pd
import pandera as pa
import pytest

from ebm.model.dataframemodels import YearlyReduction, EnergyNeedYearlyImprovements, PolicyImprovement


def test_from_energy_need_yearly_improvements_handle_duplicate_keys():
    """
    Make sure from_energy_need_yearly_improvements does not raise ValueError when unpacking that may result
    result in duplicate keys in the default index.

    default,default,cooling has duplicate primaries as well as start_year and end_year

    """
    energy_need_improvements_csv = io.StringIO("""
building_category,TEK,purpose,value,start_year,function,end_year
default,default,cooling,0.5,2021,yearly_reduction,2029
default,default,cooling,0.5,2021,improvement_at_end_year,2029
default,default,electrical_equipment,0.01,2021,yearly_reduction,
default,default,fans_and_pumps,0.0,2020,yearly_reduction,
default,default,heating_dhw,0.0,2020,yearly_reduction,
house,default,default,0.099,2031,yearly_reduction,2050
default,default,lighting,0.005,2031,yearly_reduction,2050
default,default,lighting,0.5555555555555556,2020,improvement_at_end_year,2030
    """.strip())

    energy_need_yearly_improvements = EnergyNeedYearlyImprovements(pd.read_csv(energy_need_improvements_csv))
    YearlyReduction.from_energy_need_yearly_improvements(energy_need_yearly_improvements)


def test_from_energy_need_yearly_improvements():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 2021, 'yearly_reduction', 2023,0.2],
            # ['house', 'TEK1', 'heating_rv', 1.0, 2021, 'improvement_at_end_year', 2023]
        ],
        columns=['building_category', 'TEK', 'purpose', 'start_year', 'function', 'end_year', 'value']
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


def test_from_energy_need_yearly_improvements_default_start_year_is_2020():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', None, 'yearly_reduction', 2050, 0.1],
            ['house', 'TEK2', 'lighting', 2020, 'yearly_reduction', None, 0.2],
            ['house', 'TEK3', 'lighting', None, 'yearly_reduction', None, 0.3],
        ],
        columns=['building_category', 'TEK', 'purpose', 'start_year', 'function', 'end_year', 'value']
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    df = cast(pd.DataFrame, df)
    assert df['start_year'].dtype == int
    assert (df['start_year'] == 2020).all()

    assert df['end_year'].dtype == int
    assert (df['end_year'] == 2050).all()


def test_from_energy_need_yearly_improvements_fill_optional_columns():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 'yearly_reduction', 0.1],
            ['house', 'TEK2', 'lighting', 'yearly_reduction', 0.2],
            ['house', 'TEK3', 'lighting', 'yearly_reduction', 0.3],
        ],
        columns=['building_category', 'TEK', 'purpose', 'function', 'value']
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    df = cast(pd.DataFrame, df)
    assert df['start_year'].dtype == int
    assert (df['start_year'] == 2020).all()

    assert df['end_year'].dtype == int
    assert (df['end_year'] == 2050).all()


def test_from_energy_need_policy_improvement():
    csv_file="""building_category,TEK,purpose,value,start_year,function,end_year
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
    csv_file="""building_category,TEK,purpose,value,start_year,function,end_year
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


@pytest.fixture
def policy_improvements_df():
    df = pd.DataFrame(
        columns=['building_category', 'TEK', 'purpose', 'start_year', 'end_year',
                 'improvement_at_end_year'],
        data=[['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['house', 'TEK01', 'default', 2020, 2040, 0.9]])
    return df


def test_energy_req_policy_improvements(policy_improvements_df):
    PolicyImprovement.to_schema().validate(policy_improvements_df)


def test_energy_req_policy_improvements_wrong_year_range(policy_improvements_df):
    policy_improvements_df.loc[0, 'start_year'] = 2050
    policy_improvements_df.loc[0, 'end_year'] = 2010

    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


@pytest.mark.parametrize('start_year', [-1, ""])
def test_energy_req_policy_improvements_wrong_start_year(policy_improvements_df, start_year):
    policy_improvements_df['start_year'] = start_year
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


@pytest.mark.parametrize('end_year', [-1, ""])
def test_energy_req_policy_improvements_wrong_end_year(policy_improvements_df, end_year):
    policy_improvements_df['end_year'] = end_year
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


@pytest.mark.parametrize('improvement_at_end_year', [-1, 2])
def test_energy_req_policy_improvements_value_between_zero_and_one(policy_improvements_df,
                                                                   improvement_at_end_year):
    policy_improvements_df.loc[0, 'improvement_at_end_year'] = improvement_at_end_year
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema().validate(policy_improvements_df)


def test_energy_req_policy_improvements_require_unique_rows():
    duplicate_df = pd.DataFrame(
        columns=['building_category', 'TEK', 'purpose', 'start_year', 'end_year', 'improvement_at_period_end'],
        data=[['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['default', 'default', 'lighting', 2018, 2030, 0.6],
              ['default', 'default', 'lighting', 2018, 2030, 0.1]])
    with pytest.raises(pa.errors.SchemaError):
        PolicyImprovement.to_schema()(duplicate_df)


def test_from_policy_improvements__fill_optional_columns():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 'improvement_at_period_end', 0.1],
            ['house', 'TEK2', 'lighting', 'improvement_at_period_end', 0.2],
            ['house', 'TEK3', 'lighting', 'improvement_at_period_end', 0.3],
        ],
        columns=['building_category', 'TEK', 'purpose', 'function', 'value']
    ))
    df = PolicyImprovement.from_energy_need_yearly_improvements(dfm)

    df = cast(pd.DataFrame, df)
    assert df['start_year'].dtype == int
    assert (df['start_year'] == 2020).all()

    assert df['end_year'].dtype == int
    assert (df['end_year'] == 2050).all()


if __name__ == '__main__':
    pytest.main()
