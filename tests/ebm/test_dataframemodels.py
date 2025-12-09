import io
from typing import cast

import pandas as pd
import pandera as pa
import pytest
from ebm.model.dataframemodels import EnergyNeedYearlyImprovements, PolicyImprovement, YearlyReduction


def test_from_energy_need_yearly_improvements_handle_duplicate_keys():
    """Make sure from_energy_need_yearly_improvements does not raise ValueError when unpacking."""
    energy_need_improvements_csv = io.StringIO("""
building_category,building_code,purpose,value,start_year,function,end_year
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
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'function', 'end_year', 'value'],
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    # Casting df to DataFrame so that Pycharm stops warning about DataFrameBase not having the method set_index
    df = cast(pd.DataFrame, df).set_index(['building_category','building_code','purpose','start_year', 'end_year'])

    expected_yearly_reduction_factor = pd.Series(
        data=[0.2],
        name='yearly_efficiency_improvement',
        index=pd.Index(data=[('house', 'TEK1', 'lighting', 2021, 2023)],
                       name=('building_category', 'building_code', 'purpose' ,'start_year',  'end_year'),
                       ),
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
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'function', 'end_year', 'value'],
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
        columns=['building_category', 'building_code', 'purpose', 'function', 'value'],
    ))
    df = YearlyReduction.from_energy_need_yearly_improvements(dfm)

    df = cast(pd.DataFrame, df)
    assert df['start_year'].dtype == int
    assert (df['start_year'] == 2020).all()

    assert df['end_year'].dtype == int
    assert (df['end_year'] == 2050).all()


@pytest.mark.parametrize(('building_category', 'building_code', 'expected'), [
    ('house', 'TEK69', 0.2),
    ('house', 'TEK97', 0.3),
    ('culture', 'TEK69', 0.4),
    ('house', 'TEK07', 0.7),
    ('school', 'TEK17', 1.0),
])
def test_from_energy_need_yearly_improvement_prefer_specific_over_default(building_category: str, building_code: str, expected: float) -> None:
    energy_need_yearly_improvements = pd.DataFrame(
        data=[
            ['default', 'default', 'default', 2020, 'yearly_reduction', 2050, 0.1],
            ['house', 'TEK69', 'lighting', 2020, 'yearly_reduction', 2050, 0.2],
            ['house', 'TEK97', 'lighting', 2020, 'yearly_reduction', 2050, 0.3],
            ['default', 'TEK69', 'lighting', 2020, 'yearly_reduction', 2050, 0.4],
            ['default', 'TEK97', 'lighting', 2020, 'yearly_reduction', 2050, 0.5],
            ['default', 'TEK07', 'lighting', 2020, 'yearly_reduction', 2050, 0.7],
            ['default', 'default', 'lighting', None, 'yearly_reduction', None, 1.0],
        ],
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'function', 'end_year', 'value'],
    )
    yearly_improvements = EnergyNeedYearlyImprovements(energy_need_yearly_improvements)

    df = YearlyReduction.from_energy_need_yearly_improvements(yearly_improvements)

    row = df.query(f'building_category=="{building_category}" and building_code=="{building_code}" and purpose=="lighting"')

    assert len(row) == 1, 'Expected single selection for policy improvement'
    assert row.iloc[0].yearly_efficiency_improvement == expected


@pytest.mark.parametrize(('building_category', 'building_code', 'expected'), [
    ('culture', 'default', 0.2),
    ('default', 'TEK69', 0.2),
    ('culture', 'TEK69', 0.2),
    ('apartment_block', 'TEK97', 1.0),
])
def test_from_energy_need_policy_prefer_specific_over_default(building_category: str, building_code: str, expected: float) -> None:
    policy_improvements = pd.DataFrame([
        {'building_category': 'default', 'building_code': 'default', 'purpose': 'lighting',
            'function': 'improvement_at_end_year', 'start_year': 2020, 'value': 0.1, 'end_year': 2025},
        {'building_category': building_category, 'building_code': building_code, 'purpose': 'lighting',
         'function': 'improvement_at_end_year', 'start_year': 2021, 'value': 0.2, 'end_year': 2026},
        {'building_category': 'default', 'building_code': 'default', 'purpose': 'lighting',
         'function': 'improvement_at_end_year', 'start_year': 2030, 'value': 0.3, 'end_year': 2050},
        {'building_category': 'default', 'building_code': 'default', 'purpose': 'lighting',
         'function': 'improvement_at_end_year', 'start_year': 2021, 'value': 1.0, 'end_year': 2026},
    ])

    df = PolicyImprovement.from_energy_need_yearly_improvements(policy_improvements)

    culture_tek69 = df.query('building_category=="culture" and building_code=="TEK69"')
    assert len(culture_tek69) == 1, 'Expected single selection for policy improvement'
    assert culture_tek69.iloc[0].value == expected


@pytest.mark.parametrize(('building_category', 'building_code', 'expected'), [
    ('house', 'TEK69', 0.2),
    ('culture', 'TEK69', 0.4),
    ('culture', 'TEK97', 0.5),
    ('apartment_block', 'TEK17', 1.0),
])


def test_from_energy_need_policy_improvement():
    csv_file="""building_category,building_code,purpose,value,start_year,function,end_year
default,default,lighting,0.005,2031,yearly_reduction,2050
house,TEK01,lighting,0.5555555555555556,2020,improvement_at_end_year,2030
house,TEK01,electrical_equipment,0.8,2025,improvement_at_end_year,2029
    """.strip()
    df_input = pd.read_csv(io.StringIO(csv_file))
    df = PolicyImprovement.from_energy_need_yearly_improvements(EnergyNeedYearlyImprovements(df_input))

    assert isinstance(df, pd.DataFrame), f'Expected df to be a DataFrame. Was: {type(df)}'
    df = cast(pd.DataFrame, df).set_index(['building_category','building_code','purpose','start_year', 'end_year'])

    lighting = df.query('purpose=="lighting"')

    assert (lighting.improvement_at_end_year == 0.5555555555555556).all()

    el_eq = df.query('purpose=="electrical_equipment"')
    expected_policy_improvement_factor = [0.8]
    assert el_eq.improvement_at_end_year.round(8).tolist() == expected_policy_improvement_factor


@pytest.mark.parametrize(('building_category', 'building_code', 'purpose', 'function', 'expected_start_year', 'expected_value', 'expected_end_year'),
                         [
                             ('house', 'TEK17', 'lighting', 'improvement_at_end_year', 2020, 0.555555556, 2030),
                             ('house', 'TEK69', 'lighting', 'improvement_at_end_year', 2020, 0.555555556, 2030),
                             ('apartment_block', 'TEK17', 'lighting', 'improvement_at_end_year', 2020, 0.555555556, 2030),
                             ('culture', 'TEK17', 'lighting', 'improvement_at_end_year', 2021, 0.555555556, 2025),
                             ('house', 'TEK17', 'lighting', 'yearly_reduction', 2031, 0.005, 2050),
                             ('kindergarten', 'TEK17', 'lighting', 'yearly_reduction', 2027, 0.005, 2050),
                             ('school', 'TEK69', 'cooling', 'yearly_reduction', 2020, 0, 2050),
                             ('university', 'TEK49', 'fans_and_pumps', 'yearly_reduction', 2020, 0, 2050),
                             ('university', 'TEK49', 'electrical_equipment', 'yearly_reduction', 2020, 0.01, 2050),
                             ('house', 'TEK69', 'electrical_equipment', 'yearly_reduction', 2020, 0.01, 2050),
                          ])
def test_energy_need_policy_improvement_bugfix_3520_use_correct_alias_unpacking(building_category: str, building_code: str, purpose: str,
                                                                                function: str,
                                                                                expected_start_year: int, expected_value: float,
                                                                                expected_end_year: int) -> None:
    """
    Test case bug/#3520 for energy_need_improvements building category default overstyrer spesifik building category.

    Test different categories and code for expected values.
    """
    energy_need_improvements = pd.DataFrame(data=[
                ['default', 'default', 'cooling', 'yearly_reduction', 2020, 0, 2050],
                ['default', 'default', 'electrical_equipment', 'yearly_reduction', 2020, 0.01, 2050],
                ['default', 'default', 'fans_and_pumps', 'yearly_reduction', 2020, 0, 2050],
                ['default', 'default', 'heating_dhw', 'yearly_reduction', 2020, 0, 2050],
                ['default', 'default', 'lighting', 'improvement_at_end_year', 2021, 0.555555556, 2025],
                ['default', 'default', 'lighting', 'yearly_reduction', 2027, 0.005, 2050],
                ['house', 'default', 'lighting', 'improvement_at_end_year', 2020, 0.555555556, 2030],
                ['house', 'default', 'lighting', 'yearly_reduction', 2031, 0.005, 2050],
                ['apartment_block', 'default', 'lighting', 'improvement_at_end_year', 2020, 0.555555556, 2030],
                ['apartment_block', 'default', 'lighting', 'yearly_reduction', 2031, 0.005, 2050],
        ],
        columns=['building_category', 'building_code', 'purpose', 'function', 'start_year', 'value', 'end_year'])

    # There should be a common entry point for energy need yearly improvements here, but there isn't so...

    if function == 'yearly_reduction':
        df = YearlyReduction.from_energy_need_yearly_improvements(energy_need_improvements)
    else:
        df = PolicyImprovement.from_energy_need_yearly_improvements(energy_need_improvements)

    result_set = df.query(f'building_category=="{building_category}" and building_code=="{building_code}" and purpose=="{purpose}"')
    assert len(result_set) == 1, 'Expected single selection for policy improvement'
    result = result_set.iloc[0]
    assert result.purpose == purpose
    assert result.function == function
    assert result.start_year == expected_start_year
    assert result.end_year == expected_end_year

    # the values have different names for some reason.
    # Should probably have matched function name in both cases.
    assert result['yearly_efficiency_improvement' if function == 'yearly_reduction' else function] == expected_value


def test_from_energy_need_policy_improvement_explode_groups():
    csv_file="""building_category,building_code,purpose,value,start_year,function,end_year
residential,TEK01+TEK02,lighting,0.1,2020,improvement_at_end_year,2021
non_residential,TEK02,default,0.2,2020,improvement_at_end_year,2021
non_residential,TEK02,default,0.2,2020,yearly_reduction,2021
    """.strip()
    df_input = pd.read_csv(io.StringIO(csv_file))
    df = PolicyImprovement.from_energy_need_yearly_improvements(EnergyNeedYearlyImprovements(df_input))

    assert isinstance(df, pd.DataFrame), f'Expected df to be a DataFrame. Was: {type(df)}'
    df = cast(pd.DataFrame, df).set_index(['building_category','building_code','purpose','start_year', 'end_year'])

    house_light = df.query('building_category=="house" and purpose=="lighting"')

    expected_house_lighting = pd.Series(
        data=[0.1, 0.1],
        name='improvement_at_end_year',
        index=pd.Index(data=[('house', 'TEK01', 'lighting', 2020, 2021),
                            ('house', 'TEK02', 'lighting', 2020, 2021)],
                       name=('building_category', 'building_code', 'purpose', 'start_year', 'end_year')))

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
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year',
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
        columns=['building_category', 'building_code', 'purpose', 'start_year', 'end_year', 'improvement_at_period_end'],
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
        columns=['building_category', 'building_code', 'purpose', 'function', 'value'],
    ))
    df = PolicyImprovement.from_energy_need_yearly_improvements(dfm)

    df = cast(pd.DataFrame, df)
    assert df['start_year'].dtype == int
    assert (df['start_year'] == 2020).all()

    assert df['end_year'].dtype == int
    assert (df['end_year'] == 2050).all()


if __name__ == '__main__':
    pytest.main()
