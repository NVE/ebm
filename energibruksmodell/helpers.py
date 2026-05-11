import numpy as np
import pandas as pd

from ebm.model import bema

energy_use_index = ['building_category', 'building_group', 'building_code', 'purpose', 'building_condition', 'heating_systems', 'load', 'energy_product']

def filter_house_t69(df):
    return df.query('building_category=="house" and building_code=="TEK69"').copy().pipe(as_gwh).reset_index(drop=True)

def filter_house(df):
    return df.query('building_category=="house"').copy().pipe(as_gwh).reset_index(drop=True)

def filter_electricity(df):
    return df.query('energy_product=="Electricity"')

def filter_dh(df):
    return df.query('energy_product=="DH"')

def diff_year(year=2025, col='GWh'):
    def _compare_to_year(df):
        return df.loc[:, col] - df.loc[year, col]
    return _compare_to_year

def as_gwh(df):
    df['GWh'] = df.kwh / 1_000_000
    return df


def as_type_category(df):
    categories = ('building_category', 'building_code', 'building_condition', 'purpose', 'heating_systems', 'load', 'heating_system', 'energy_product', 'building_group')
    for category in categories:
        if category in df.columns:
            df[category] = df[category].astype('category')
    return df


def bema_sort(df):
    by_columns = [c for c in ['building_category', 'building_code', 'purpose', 'building_condition', 'heating_systems', 'load', 'energy_product'] if c in df.columns]
    return  df.sort_values(by=by_columns, key=bema.map_sort_order)

def group_existing_conditions(df: pd.DataFrame) -> pd.DataFrame:
    df['condition_group'] = 'existing'
    df.loc[df[df.building_condition=='demolition'].index, 'condition_group'] = 'demolished'
    return df

def group_new_conditions(df: pd.DataFrame) -> pd.DataFrame:
    if 'condition_group' not in df.columns:
        df['condition_group'] = 'existing'

    df.loc[df[df.building_code=='TEK17'].index, 'condition_group'] = 'constructed'
    return df

def group_building_categories(df: pd.DataFrame) -> pd.DataFrame:
    #df['building_group'] = df['building_category']
    df.loc[df.query('~building_category.isin(["house", "apartment_block"])').index, 'building_group'] = 'Non residential'
    df.loc[df.query('building_category.isin(["house", "apartment_block"])').index, 'building_group'] = 'Residential'
    return df


building_group_queries = {
    "Non residential": '~building_category.isin(["house", "apartment_block", "holiday_home"])',
    "Residential": 'building_category.isin(["house", "apartment_block"])',
}


def group_building_by_query(
        df: pd.DataFrame, building_group: str = "Non residential", query: str | None = None
) -> pd.DataFrame:
    if query is None:
        query = building_group_queries.get(building_group, building_group_queries.get("Non residential"))

    df.loc[df.query(query).index, "building_group"] = building_group
    return df


def group_non_residential(df: pd.DataFrame, building_group: str = "Non residential") -> pd.DataFrame:
    if "building_category" in df.columns:
        if "building_group" not in df.columns:
            df["building_group"] = df["building_category"]
    elif "building_category" in df.index.names:
        if "building_group" not in df.columns:
            df["building_group"] = df.index.get_level_values("building_category")
    else:
        raise KeyError("building_category column or index level is required for grouping non residential")

    query = '~building_category.isin(["house", "apartment_block", "holiday_home"])'
    return group_building_by_query(df=df, building_group=building_group, query=query)


def group_residential(df: pd.DataFrame, building_group='Residential') -> pd.DataFrame:
    if "building_category" in df.columns:
        if "building_group" not in df.columns:
            df["building_group"] = df["building_category"]
    elif "building_category" in df.index.names:
        if "building_group" not in df.columns:
            df["building_group"] = df.index.get_level_values("building_category")
    else:
        raise KeyError("building_category column or index level is required for grouping residential")

    query = building_group_queries.get(building_group, building_group_queries.get('Residential'))
    return group_building_by_query(df=df, building_group=building_group, query=query)


def repeat_m2_from_year(df: pd.DataFrame, start_year=2025):
    df = df.pipe(bema_sort)
    df = df.fillna(0.0)
    df.loc[df.query(f'year>{start_year}').index, ['m2']] = np.nan
    df.loc[df.query(f'year>{start_year}').index, ['construction', 'net_construction', 'rebuilt']] = 0.0
    df.loc[df.m2.isna(), ['demolition', 'original_condition', 'small_measure', 'renovation', 'renovation_and_small_measure']] = np.nan
    df['m2'] = df.m2.ffill()
    df = df.ffill()
    return df

def flatten_column_names(df: pd.DataFrame, delimiter: str='_') -> pd.DataFrame:
    def flatten_name(s):
        return f"{s}" if isinstance(s, str) else delimiter.join(s)
    df.columns = [flatten_name(a) for a in df.columns]
    return  df


def sum_heating_rv_by_heating_systems(df: pd.DataFrame) ->pd.DataFrame:
    # 'building_category', 'building_code', 'building_condition',
    grouping = ['heating_systems', 'load', 'energy_product', 'purpose', 'year']
    df = (
        df.query('purpose=="heating_rv"')
          .groupby(by=grouping, as_index=False)
          .sum(['kwh', 'GWh'])
    )
    df['heating_system_share'] = df['heating_system_share']/4
    return df[[c for c in ['building_category', 'building_code', 'building_condition','heating_systems', 'energy_product','load', 'purpose', 'year', 'kwh', 'GWh', 'heating_system_share'] if c in df.columns]]


def shorten_columns(df: pd.DataFrame, keep=None):
    if keep is None:
        keep = []
    columns = [
        "B",
        "T",
        "C",
        "year",
        "P",
        # 'building_category', 'building_code', 'building_condition', 'year', 'purpose',
        "reduction_yearly",
        "reduction_policy",
        "reduction_condition",
        "original_kwh_m2",
        "reduction_yearly_kwh_m2",
        "reduction_policy_kwh_m2",
        "reduction_condition_kwh_m2",
        "reduced_kwh_m2",
        "m2",
        "reduction_yearly_kwh",
        "reduction_policy_kwh",
        "reduction_condition_kwh",
        "reduced_kwh",
        "energy_requirement",
        "energy_requirement_10",
    ]

    renaming = {
        "original_kwh_m2": "okwh_m2",
        "heating_rv_factor": "cb_f",
        "calibrated_kwh_m2": "cb_kwh_m2",
        "reduction_yearly": "RY",
        "reduction_yearly_kwh_m2": "RY_kwh_m2",
        "reduction_yearly_kwh": "RY_kwh",
        "reduction_policy": "RP",
        "reduction_policy_kwh_m2": "RP_kwh_m2",
        "reduction_policy_kwh": "RP_kwh",
        "reduction_condition": "RC",
        "reduction_condition_kwh_m2": "RC_kwh_m2",
        "reduction_condition_kwh": "RC_kwh",
        #    'year': 'Y',
        "reduced_kwh": "rdc_kwh",
        "reduced_kwh_m2": "rdc_kwh_m2",
        "behaviour_factor": "beh_f",
        "behaviour_factor_kwh_m2": "beh_kwh_m2",
        'heating_systems': 'HS',
        'load': 'L',
        "kwh_m2": "kwh_m2",
        "kwh": "kwh",
        "GWh": "GWh",
        "m2": "m2",
        "energy_requirement": "erq",
    }
    df["B"] = df["building_category"].str.capitalize().str[0:3]

    df["T"] = df["building_code"].str[0] + df["building_code"].str.upper().str[-2:]
    df.loc[df[df["building_condition"] == "original_condition"].index, "C"] = "oc".upper()
    df.loc[df[df["building_condition"] == "small_measure"].index, "C"] = "sm".upper()
    df.loc[df[df["building_condition"] == "renovation"].index, "C"] = "rn".upper()
    df.loc[df[df["building_condition"] == "renovation_and_small_measure"].index, "C"] = "rs".upper()
    df.loc[df[df["building_condition"] == "demolition"].index, "C"] = "dx".upper()
    # %%
    df["P"] = df["purpose"].str.upper().str[0] + df["purpose"].str.upper().str[-1]

    sort_columns = [
        c for c in ["building_category", "building_code", "building_condition", "purpose", "year"] if c in df.columns
    ]
    df = (
        df.reset_index()
        .sort_values(by=sort_columns, key=bema.map_sort_order)
        .rename(columns=renaming, errors="ignore")
        .set_index([c for c in ["B", "T", "C", "P", "year"] if c in df.columns])
    )
    return df[[v for v in renaming.values() if v in df.columns] + keep]


def add_column_ch_m2(df: pd.DataFrame) -> pd.DataFrame:
    df["ch_m2"] = (
    df.groupby(level=["building_category", "building_code", "building_condition"])["m2"]
      .diff()
      .fillna(df.groupby(level=[0,1,2])["m2"].transform("first")).round(2))
    return df


def cross_on_building_conditions(df: pd.DataFrame) -> pd.DataFrame:
    building_conditions = pd.DataFrame(
        ['original_condition', 'small_measure', 'renovation', 'renovation_and_small_measure', 'demolition'],
        columns=['building_condition'])


    return df.merge(building_conditions, how='cross')


def heating_systems_m2(heating_systems: pd.DataFrame, m2: pd.DataFrame) -> pd.DataFrame:
    if 'building_condition' not in heating_systems.columns:
        hs_building_condition = heating_systems.pipe(cross_on_building_conditions)
    else:
        hs_building_condition = heating_systems

    hs_m2 = hs_building_condition.merge(m2, on=['building_category', 'building_code', 'year', 'building_condition'], how='left')

    hs_m2['m2'] = hs_m2.m2 * hs_m2.heating_system_share
    hs_m2['net_construction'] = hs_m2.net_construction * hs_m2.heating_system_share
    hs_m2['rebuilt'] = hs_m2.rebuilt * hs_m2.heating_system_share
    hs_m2['construction'] = hs_m2.construction * hs_m2.heating_system_share
    hs_m2['net_construction_acc'] = hs_m2.net_construction_acc * hs_m2.heating_system_share

    return hs_m2[['building_category', 'building_code', 'year', 'building_condition', 'heating_systems',
                  'heating_system_share', 'm2', 'construction', 'rebuilt', 'net_construction', 'net_construction_acc']]

# columns dropped:
# 'base_load_energy_product', 'peak_load_energy_product','tertiary_load_energy_product',
# 'domestic_hot_water_energy_product','heating_system_share', 'tertiary_load_coverage', 'base_load_coverage','peak_load_coverage', 'base_load_efficiency', 'peak_load_efficiency','tertiary_load_efficiency', 'domestic_hot_water_efficiency',
# 'Spesifikt elforbruk', 'cooling_efficiency',



def demolition_to_negative(df: pd.DataFrame, column='m2') -> pd.DataFrame:
    if column not in df.columns:
        msg = f'A column named `{column}` {"(default)" if column=="m2" else ""} was not found in DataFrame'
        raise KeyError(msg)
    df.loc[(df.query("building_condition=='demolition'")).index, column] = -df.loc[(df.query("building_condition=='demolition'")).index, column]
    df.reset_index()
    df[column]
    df[column] = df[column].where(~df[column].eq(0), 0.0)
    return df


def duplicate_building_condition(energy_need_kwh_m2: pd.DataFrame, target: str = 'demolition', source: str = 'renovation_and_small_measure'):
    demolition_kwh_m2 = energy_need_kwh_m2.query(f'building_condition=="{source}"').copy().reset_index()
    demolition_kwh_m2['building_condition'] = target
    demolition_kwh_m2['kwh_m2'] = demolition_kwh_m2['kwh_m2']
    demolition_kwh_m2 = demolition_kwh_m2.set_index(['building_category', 'building_code', 'purpose', 'building_condition', 'year'])
    return demolition_kwh_m2
