import io

import pandas as pd

from ebm.model.energy_need_filter import de_dupe_dataframe

def test_de_dupe_dataframe():
    settings = pd.read_csv(io.StringIO(
"""building_category,TEK,purpose,value,start_year,function,end_year
default,default,cooling,0.0,2020,yearly_reduction,
default,default,electrical_equipment,0.01,2021,yearly_reduction,
default,default,lighting,0.005,2031,yearly_reduction,2050
default,default,lighting,0.5555555555555556,2020,improvement_at_end_year,2030
""".strip()))

    df = de_dupe_dataframe(df=settings,
                           unique_columns=['building_category', 'TEK', 'purpose', 'start_year', 'end_year', 'function'])

    others = df.query('purpose not in ["lighting", "electrical_equipment"]')

    assert (others.value == 0.0).all()
    el_eq = df.query('purpose in ["electrical_equipment"]')
    assert len(el_eq) == 143
    assert (el_eq.value == 0.01).all()
    lighting_yearly_reduction = df.query('purpose in ["lighting"] and function=="yearly_reduction"')
    assert len(lighting_yearly_reduction) == 143
    assert (lighting_yearly_reduction.value == 0.005).all()
    lighting_improvement_at_end_year = df.query('function=="improvement_at_end_year"')
    assert len(lighting_improvement_at_end_year) == 143
    assert (lighting_improvement_at_end_year.value == 0.5555555555555556).all()