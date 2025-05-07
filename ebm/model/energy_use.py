import pandas as pd

from ebm.energy_consumption import TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE, \
    SPISSLAST_ENERGIVARE, SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD, EKSTRALAST_ANDEL, EKSTRALAST_VIRKNINGSGRAD, \
    EKSTRALAST_ENERGIVARE, KJOLING_VIRKNINGSGRAD, DHW_EFFICIENCY, TAPPEVANN_ENERGIVARE


def base_load(heating_systems_parameters):
    heating_systems_parameters['heating_system'] = '-'
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD,
         GRUNNLAST_ENERGIVARE, 'heating_system']].copy()
    df = df.rename(columns={GRUNNLAST_ANDEL: 'load_share', GRUNNLAST_VIRKNINGSGRAD: 'load_efficiency',
                            GRUNNLAST_ENERGIVARE: 'energy_product'})
    df.loc[:, 'load'] = 'base'
    df.loc[:, 'purpose'] = 'heating_rv'
    df['heating_system'] = df.heating_systems.apply(lambda s: s.split('-')[0])

    return df


def peak_load(heating_systems_parameters):
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD,
         SPISSLAST_ENERGIVARE, 'heating_system']].copy()
    df = df.rename(columns={SPISSLAST_ANDEL: 'load_share', SPISSLAST_VIRKNINGSGRAD: 'load_efficiency',
                            SPISSLAST_ENERGIVARE: 'energy_product'})
    df.loc[:, 'load'] = 'peak'
    df.loc[:, 'purpose'] = 'heating_rv'
    df['heating_system'] = df.heating_systems.apply(lambda s: s.split('-')[1:2]).explode('heating_system')
    return df


def tertiary_load(heating_systems_parameters):
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, EKSTRALAST_ANDEL, EKSTRALAST_VIRKNINGSGRAD,
         EKSTRALAST_ENERGIVARE, 'heating_system']].copy()
    df = df.rename(columns={EKSTRALAST_ANDEL: 'load_share', EKSTRALAST_VIRKNINGSGRAD: 'load_efficiency',
                            EKSTRALAST_ENERGIVARE: 'energy_product'})
    df.loc[:, 'load'] = 'tertiary'
    df.loc[:, 'purpose'] = 'heating_rv'
    df['heating_system'] = df.heating_systems.apply(lambda s: s.split('-')[2:3]).explode('heating_system')
    return df


def heating_rv(heating_systems_parameters):
    df = heating_systems_parameters.copy()
    # df['_num_loads'] = df.heating_systems.apply(lambda s: len(s.split('-')))
    # df[['heating_systems']]

    base = base_load(df)
    peak = peak_load(df)
    tertiary = tertiary_load(df)

    return pd.concat([base, peak, tertiary])


def heating_dhw(heating_systems_parameters):
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, DHW_EFFICIENCY,
         TAPPEVANN_ENERGIVARE]].copy()
    df.loc[:, GRUNNLAST_ANDEL] = 1.0
    df = df.rename(columns={GRUNNLAST_ANDEL: 'load_share', DHW_EFFICIENCY: 'load_efficiency',
                            TAPPEVANN_ENERGIVARE: 'energy_product'})

    df.loc[:, 'load'] = 'dhw'
    df['purpose'] = 'heating_dhw'
    return df


def cooling(heating_systems_parameters):
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, KJOLING_VIRKNINGSGRAD,
         GRUNNLAST_ENERGIVARE]].copy()
    df.loc[:, GRUNNLAST_ANDEL] = 1.0
    # df_c.loc[:, KJOLING_VIRKNINGSGRAD] = 4.0
    df.loc[:, GRUNNLAST_ENERGIVARE] = 'Electricity'
    df = df.rename(columns={GRUNNLAST_ANDEL: 'load_share', KJOLING_VIRKNINGSGRAD: 'load_efficiency',
        GRUNNLAST_ENERGIVARE: 'energy_product'})

    df.loc[:, 'load'] = 'base'
    df.loc[:, 'purpose'] = 'cooling'
    return df


def other(heating_systems_parameters):
    df = heating_systems_parameters[
        ['building_category', 'TEK', 'year', 'heating_systems', TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD,
         GRUNNLAST_ENERGIVARE]].copy()
    df.loc[:, GRUNNLAST_ANDEL] = 1.0
    df.loc[:, GRUNNLAST_VIRKNINGSGRAD] = 1.0
    df.loc[:, GRUNNLAST_ENERGIVARE] = 'Electricity'
    df = df.rename(columns={GRUNNLAST_ANDEL: 'load_share', GRUNNLAST_VIRKNINGSGRAD: 'load_efficiency',
                            GRUNNLAST_ENERGIVARE: 'energy_product'})
    df.loc[:, 'load'] = 'base'
    df.loc[:, '_purposes'] = 'electrical_equipment,fans_and_pumps,lighting'
    df = df.assign(**{'purpose': df['_purposes'].str.split(',')}).explode('purpose')
    df = df.drop(columns=['_purposes'], errors='ignore')

    return df


def all_purposes(heating_systems_parameters: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([heating_rv(heating_systems_parameters), heating_dhw(heating_systems_parameters),
               cooling(heating_systems_parameters), other(heating_systems_parameters)])


def efficiency_factor(all_purposes):
    df = all_purposes
    df.loc[:, 'efficiency_factor'] = df.loc[:, 'TEK_shares'] * df.loc[:, 'load_share'] / df.loc[:, 'load_efficiency']

    return df
