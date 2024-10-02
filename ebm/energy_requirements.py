import pandas as pd


def transform_energy_requirements_by_condition(
        energy_requirements: pd.DataFrame,
        condition_reduction: pd.DataFrame
) -> pd.DataFrame:
    condition_reduction['key'] = 1
    energy_requirements['key'] = 1
    df = pd.merge(energy_requirements, condition_reduction, on='key')

    df.kw_h_m = df.kw_h_m * (1.0 - df['reduction'])

    return df[['building_category',
               'TEK',
               'purpose',
               'building_condition',
               'kw_h_m']]
