import pandas as pd

from ebm.model.building_category import BuildingCategory
from ebm.model.column_operations import replace_column_alias
from ebm.model.energy_purpose import EnergyPurpose


def filter_original_condition(df, building_category, tek, purpose):
    exploded = explode_dataframe(df)
    de_duped = de_dupe_dataframe(exploded)
    return de_duped[(de_duped.building_category==building_category) & (de_duped.TEK==tek) & (de_duped.purpose == purpose)]


def de_dupe_dataframe(df, unique_columns=None):
    de_dupe_by = unique_columns if unique_columns else ['building_category', 'TEK', 'purpose']

    de_duped = df.drop_duplicates(de_dupe_by)
    return de_duped


def explode_dataframe(df: pd.DataFrame, tek_list=None) -> pd.DataFrame:
    if not tek_list:
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


def _load_file(infile):
    df = pd.read_csv(infile)
    TEKs = 'TEK49 PRE_TEK49 TEK69 TEK87 TEK97 TEK07 TEK10 TEK17'.split(' ')

    return explode_dataframe(df, tek_list=TEKs).sort_values(by=['dupe', 'building_category', 'TEK', 'purpose', 'priority'])


def main():
    import pathlib
    import sys
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    if not sys.argv[1:]:
        files = pathlib.Path('input').glob('*.csv')
    else:
        files = [pathlib.Path(f) for f in sys.argv[1:]]
    for filename in files:
        print(f'# {filename}')
        print(_load_file(filename))


if __name__ == '__main__':
    main()
