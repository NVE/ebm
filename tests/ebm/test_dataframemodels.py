from typing import cast

import pandas as pd
import pytest

from ebm.model.dataframemodels import YearlyReduction, EnergyNeedYearlyImprovements



def test_from_energy_need_yearly_improvements():
    dfm = EnergyNeedYearlyImprovements(pd.DataFrame(
        data=[
            ['house', 'TEK1', 'lighting', 0.2, 2021, 'yearly_reduction', 2023]
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


if __name__ == '__main__':
    pytest.main()