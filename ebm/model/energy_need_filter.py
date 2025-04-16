import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.column_operations import replace_column_alias, explode_column_alias
from ebm.model.energy_purpose import EnergyPurpose


def filter_original_condition(df, building_category, tek, purpose):
    de_duped = de_dupe_dataframe(df)
    return de_duped[(de_duped.building_category==building_category) & (de_duped.TEK==tek) & (de_duped.purpose == purpose)]


def de_dupe_dataframe(df):
    de_duped = explode_dataframe(df)
    de_duped = de_duped.drop_duplicates(['building_category', 'TEK', 'purpose'])
    return de_duped


def explode_dataframe(df):
    tek_list = 'TEK49 PRE_TEK49 PRE_TEK49_RES_1950 TEK69 TEK87 TEK97 TEK07 TEK10 TEK17 TEK21 TEK01'.split(' ')
    # expand building_category
    df = replace_column_alias(df,
                              column='building_category',
                              values={'default': [b for b in BuildingCategory],
                                      'residential': [b for b in BuildingCategory if b.is_residential()],
                                      'non_residential': [b for b in BuildingCategory if not b.is_residential()]})
    # expand tek
    df = replace_column_alias(df, 'TEK', values=tek_list, alias='default')

    # expand purpose
    df = replace_column_alias(df, 'purpose', values=[p for p in EnergyPurpose], alias='default')

    # Add priorty column and sort
    df['bc_priority'] = df.building_category.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
    df['t_priority'] = df.TEK.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
    df['p_priority'] = df.purpose.apply(lambda x: 0 if '+' not in x else len(x.split('+')))
    if not 'priority' in df.columns:
        df['priority'] = 0
    df['priority'] = df.bc_priority + df.t_priority + df.p_priority

    # Explode
    df = df.assign(**{'building_category': df['building_category'].str.split('+'), }).explode('building_category')
    df = df.assign(**{'TEK': df['TEK'].str.split('+')}).explode('TEK')
    df = df.assign(**{'purpose': df['purpose'].str.split('+'), }).explode('purpose')
    # dedupe
    deduped = df.sort_values(by=['building_category', 'TEK', 'purpose', 'priority'])
    deduped['dupe'] = deduped.duplicated(['building_category', 'TEK', 'purpose'], keep=False)
    return deduped

