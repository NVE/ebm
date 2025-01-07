from loguru import logger
import pandas as pd

from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.filter_tek import FilterTek

ADJUSTED_REQUIREMENT = 'eq_ts'
# there are 3 time-of-use zones: peak, shoulder and offpeak.
HEATING_RV_GRUNNLAST = 'RV_GL'
HEATING_RV_SPISSLAST = 'RV_SL'
HEATIG_RV_EKSTRALAST = 'RV_EL'
HEAT_PUMP = 'RV_HP'
COOLING_KV = 'CL_KV'
DHW_TV = 'DHW_TV'
OTHER_SV = 'O_SV'
HEATING_RV = 'heating_rv'
HEATING_DHW = 'heating_dhw'
COOLING = 'cooling'
DHW_EFFICIENCY = 'Tappevann virkningsgrad'

HEATING_SYSTEMS = 'heating_systems'
TEK_SHARES = 'TEK_shares'
GRUNNLAST_ANDEL = 'Grunnlast andel'
GRUNNLAST_VIRKNINGSGRAD = 'Grunnlast virkningsgrad'
KJOLING_VIRKNINGSGRAD = 'Kjoling virkningsgrad'
SPESIFIKT_ELFORBRUK = 'Spesifikt elforbruk'
EKSTRALAST_ANDEL = 'Ekstralast andel'
EKSTRALAST_VIRKNINGSGRAD = 'Ekstralast virkningsgrad'
SPISSLAST_ANDEL = 'Spisslast andel'
SPISSLAST_VIRKNINGSGRAD = 'Spisslast virkningsgrad'

GRUNNLAST_ENERGIVARE = 'Grunnlast energivare'
SPISSLAST_ENERGIVARE = 'Spisslast energivare'
EKSTRALAST_ENERGIVARE = 'Ekstralast energivare'
TAPPEVANN_ENERGIVARE = 'Tappevann energivare'
HP_ENERGY_SOURCE = 'hp_source'


class EnergyConsumption:
    def __init__(self, heating_systems_parameters: pd.DataFrame = None):
        self.heating_systems_parameters = heating_systems_parameters

    def grouped_heating_systems(self) -> pd.DataFrame:
        """
        Groups and sums heating_system_parameters over building_category, TEK, Oppvarmingstyper. All excess values will
            be summed.

        Returns
        -------
        pd.DataFrame
            heating_systems_parameters grouped and summed
        """
        df = self.heating_systems_parameters
        df = df.rename(columns={'tek_share': TEK_SHARES})

        aggregates = {'Grunnlast energivare': 'first', 'Spisslast energivare': 'first',
                      'Ekstralast energivare': 'first', 'Tappevann energivare': 'first', TEK_SHARES: 'sum',
                      EKSTRALAST_ANDEL: 'sum', GRUNNLAST_ANDEL: 'sum', SPISSLAST_ANDEL: 'sum',
                      GRUNNLAST_VIRKNINGSGRAD: 'sum', SPISSLAST_VIRKNINGSGRAD: 'sum', EKSTRALAST_VIRKNINGSGRAD: 'sum',
                      DHW_EFFICIENCY: 'sum', SPESIFIKT_ELFORBRUK: 'sum', KJOLING_VIRKNINGSGRAD: 'sum'}
        grouped = df.groupby(by=['building_category', 'TEK', 'year', HEATING_SYSTEMS]).agg(aggregates)
        return grouped.reset_index()

    def calculate(self, energy_requirements: pd.DataFrame) -> pd.DataFrame:
        """
        calculate energy usage by from energy_requirements and heating_systems_parameters

        Parameters
        ----------
        energy_requirements : pd.DataFrame

        Returns
        -------
        pd.DataFrame

        """
        logger.debug('Calculate heating systems')
        energy_requirements = self._remove_tek_suffix(energy_requirements)
        energy_requirements = self._group_and_sum_same_tek(energy_requirements)

        # If _RES of _COM is in TEK this will not work
        # energy_requirements.index[energy_requirements.index.str.endswith('_RES')]
        if energy_requirements.index.get_level_values('TEK').str.endswith(
                '_RES').any() or energy_requirements.index.get_level_values('TEK').str.endswith('_COM').any():
            raise ValueError('Found _RES or _COM in energy_requirements')
        self.heating_systems_parameters = self.heating_systems_parameters.rename(columns={'tek_share': TEK_SHARES})
        # Merge energy_requirements and heating_systems into df
        df = self._merge_energy_requirement_and_heating_systems(energy_requirements)

        # Make column eq_ts for tek_share adjusted energy requirement
        df[ADJUSTED_REQUIREMENT] = df.energy_requirement * df[TEK_SHARES]

        # Zero fill columns before calculating to prevent NaN from messing up sums
        df.loc[:, [HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, HEATIG_RV_EKSTRALAST, DHW_TV, COOLING_KV, OTHER_SV,
                   HEAT_PUMP]] = 0.0

        # Adjust energy requirements by efficiency
        # heating rv

        df = self.adjust_heat_pump(df)
        df = self.adjust_heating_rv(df)
        df = self.adjust_heating_dhw(df)
        df = self.adjust_cooling(df)
        df = self.adjust_other(df)

        # sum energy use
        df.loc[:, 'kwh'] = df.loc[:,
                           [HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, HEATIG_RV_EKSTRALAST, DHW_TV, COOLING_KV,
                            OTHER_SV]].sum(axis=1)

        df.loc[:, 'gwh'] = df.loc[:, 'kwh'] / 10 ** 6

        df = df.sort_index(level=['building_category', 'TEK', 'year', 'building_condition', 'purpose', HEATING_SYSTEMS])
        return df[[TEK_SHARES, ADJUSTED_REQUIREMENT, HEATING_RV_GRUNNLAST, GRUNNLAST_ENERGIVARE, HEATING_RV_SPISSLAST,
                   SPISSLAST_ENERGIVARE, HEATIG_RV_EKSTRALAST, EKSTRALAST_ENERGIVARE, DHW_TV, TAPPEVANN_ENERGIVARE,
                   COOLING_KV, OTHER_SV, HEAT_PUMP, HP_ENERGY_SOURCE, 'kwh', 'gwh']]

    def adjust_heat_pump(self, df):
        df[HP_ENERGY_SOURCE] = None
        gass = ['HP Central heating - Gas']
        vannbasert = [n for n in df.index.get_level_values('heating_systems').unique() if
                      n.startswith('HP Central heating')]
        elektrisk = [n for n in df.index.get_level_values('heating_systems').unique() if
                     n.startswith('HP') and n not in vannbasert]

        gass_slice = (slice(None), slice(None), slice(None), slice(None), gass)
        vann_slice = (slice(None), slice(None), ['heating_rv', 'heating_dhw'], slice(None), slice(None),
                      vannbasert)  # , 'heating_dhw'
        el_slice = (slice(None), slice(None), ['heating_rv'], slice(None), slice(None), elektrisk)  # 'heating_dhw'

        df.loc[vann_slice, HEAT_PUMP] = df.loc[vann_slice, ADJUSTED_REQUIREMENT] * df.loc[vann_slice, GRUNNLAST_ANDEL]
        df.loc[vann_slice, HP_ENERGY_SOURCE] = 'Vannbåren varme'

        df.loc[el_slice, HEAT_PUMP] = df.loc[el_slice, ADJUSTED_REQUIREMENT] * df.loc[el_slice, GRUNNLAST_ANDEL]
        df.loc[el_slice, HP_ENERGY_SOURCE] = 'Luft/luft'
        return df

    def adjust_other(self, df):
        # lighting, electrical equipment, fans and pumps energy use is calculated by dividing with spesific electricity
        # useage
        other_slice = (slice(None), slice(None), EnergyPurpose.other(), slice(None), slice(None))
        df.loc[other_slice, OTHER_SV] = df.loc[other_slice, ADJUSTED_REQUIREMENT] / df.loc[
            other_slice, SPESIFIKT_ELFORBRUK]
        return df

    def adjust_cooling(self, df):
        # cooling energy use is calculated by dividing cooling with 'Kjoling virkningsgrad'
        cooling_slice = (slice(None), slice(None), COOLING, slice(None), slice(None))
        df.loc[cooling_slice, COOLING_KV] = df.loc[cooling_slice, ADJUSTED_REQUIREMENT] / df.loc[
            cooling_slice, KJOLING_VIRKNINGSGRAD]
        return df

    def adjust_heating_dhw(self, df):
        # heating dhw energy use is calculated by dividing heating_dhw with 'Tappevann virkningsgrad'
        heating_dhw_slice = (slice(None), slice(None), HEATING_DHW, slice(None), slice(None))
        df.loc[heating_dhw_slice, DHW_TV] = df.loc[heating_dhw_slice, ADJUSTED_REQUIREMENT] / df.loc[
            heating_dhw_slice, DHW_EFFICIENCY]
        return df

    def adjust_heating_rv(self, df):
        heating_rv_slice = (slice(None), slice(None), HEATING_RV, slice(None), slice(None))
        df.loc[heating_rv_slice, HEATING_RV_GRUNNLAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] * df.loc[heating_rv_slice, GRUNNLAST_ANDEL] / df.loc[
            heating_rv_slice, GRUNNLAST_VIRKNINGSGRAD])
        df.loc[heating_rv_slice, HEATING_RV_SPISSLAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] * df.loc[heating_rv_slice, SPISSLAST_ANDEL] / df.loc[
            heating_rv_slice, SPISSLAST_VIRKNINGSGRAD])
        df.loc[heating_rv_slice, HEATIG_RV_EKSTRALAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] * df.loc[heating_rv_slice, EKSTRALAST_ANDEL] / df.loc[
            heating_rv_slice, EKSTRALAST_VIRKNINGSGRAD])
        return df

    def _merge_energy_requirement_and_heating_systems(self, energy_requirements):
        df = energy_requirements.reset_index().merge(self.heating_systems_parameters.reset_index(),
            left_on=['building_category', 'TEK', 'year'], right_on=['building_category', 'TEK', 'year'])[
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'kwh_m2', 'm2', 'energy_requirement',
             HEATING_SYSTEMS, TEK_SHARES, GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD, GRUNNLAST_ENERGIVARE,
             SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD, SPISSLAST_ENERGIVARE, EKSTRALAST_VIRKNINGSGRAD, EKSTRALAST_ANDEL,
             EKSTRALAST_ENERGIVARE, TAPPEVANN_ENERGIVARE, DHW_EFFICIENCY, SPESIFIKT_ELFORBRUK, KJOLING_VIRKNINGSGRAD]]
        # Unused columns
        # ,'Innfyrt_energi_kWh','Innfyrt_energi_GWh','Energibehov_samlet_GWh']]
        df = df.set_index(
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', HEATING_SYSTEMS]).sort_index()
        return df

    @staticmethod
    def _group_and_sum_same_tek(energy_requirements):
        energy_requirements = FilterTek.merge_tek(energy_requirements, 'TEK69', ['TEK69_1976', 'TEK69_1986'])
        energy_requirements = FilterTek.merge_tek(energy_requirements, 'PRE_TEK49',
                                                  ['PRE_TEK49_1940', 'PRE_TEK49_1950'])
        energy_requirements = energy_requirements.sort_index()
        return energy_requirements

    @staticmethod
    def _remove_tek_suffix(energy_requirements):
        energy_requirements = FilterTek.remove_tek_suffix(energy_requirements, suffix='_RES')
        energy_requirements = FilterTek.remove_tek_suffix(energy_requirements, suffix='_COM')
        return energy_requirements


def calibrate_heating_systems(df: pd.DataFrame, factor: pd.DataFrame, multiply=False) -> pd.DataFrame:
    # When factor is empty or all factors are 1.0, there is no need to change anything.
    if len(factor) == 0 or (factor.factor == 1.0).all():
        return df
    original = df.copy()
    factor = factor.copy()

    if multiply:
        factor['factor'] = factor['factor'] * 100

    # Add action and value
    df_to = original.merge(factor,
                           left_on=['building_category', 'heating_systems'],
                           right_on=['building_category', 'to'])

    df_from = original.merge(factor,
                             left_on=['building_category', 'heating_systems'],
                             right_on=['building_category', 'from'])

    # Calculate value to add
    df_to_add = df_to.set_index(['building_category', 'TEK', 'year', 'to'])

    if multiply:
        df_to_add['v'] = (df_to_add.TEK_shares * df_to_add.factor)/100 - df_to_add.TEK_shares
    else:
        df_to_add['v'] = df_to_add.TEK_shares * df_to_add.factor - df_to_add.TEK_shares

    # Calculate value to subtract
    df_to_subtract = df_from.set_index(['building_category', 'TEK', 'year', 'from', 'to'])
    df_to_subtract.loc[:, 'v'] = -df_to_add.reset_index().groupby(by=['building_category', 'TEK', 'year', 'from', 'to']).agg(
        {'v': 'sum'})

    # Join add and substract rows
    addition_grouped = df_to_add.groupby(by=['building_category', 'TEK', 'year', 'to']).agg(
        {'v': 'sum', 'heating_systems': 'first', 'TEK_shares': 'first', 'factor': 'first', 'from': 'first'})
    subtraction_grouped = df_to_subtract.groupby(by=['building_category', 'TEK', 'year', 'from']).agg(
        {'v': 'sum', 'heating_systems': 'first', 'TEK_shares': 'first', 'factor': 'first'})

    df_to_sum = original.set_index(['building_category', 'TEK', 'year', 'heating_systems'])
    df_to_sum.loc[:, 'add'] = addition_grouped.loc[:, 'v']
    df_to_sum.loc[:, 'sub'] = subtraction_grouped.loc[:, 'v'].fillna(0)
    df_to_sum.loc[:, 'sub'] = df_to_sum.loc[:, 'sub'].fillna(0)

    df_to_sum.TEK_shares = df_to_sum.TEK_shares + df_to_sum['add'].fillna(0) + df_to_sum['sub'].fillna(0)

    calibrated_and_original = pd.concat([df_to_sum.reset_index(), original.reset_index()]).drop_duplicates(
        ['building_category', 'TEK', 'year', 'heating_systems'],
        keep='first').drop(columns='index',
                           errors='ignore')

    columns_to_keep = ['building_category', 'TEK', 'year', 'heating_systems', 'TEK_shares']
    return calibrated_and_original[columns_to_keep].reset_index(drop=True)


def calibrate_heating_systems_adder(df: pd.DataFrame, factor: pd.DataFrame) -> pd.DataFrame:
    # When factor is empty or all factors are 1.0, there is no need to change anything.
    if len(factor) == 0 or (factor.factor == 0.0).all():
        return df
    original = df.copy()
    factor = factor.copy()

    # Add action and value
    df_to = original.merge(factor,
                           left_on=['building_category', 'heating_systems'],
                           right_on=['building_category', 'to'])

    df_from = original.merge(factor,
                             left_on=['building_category', 'heating_systems'],
                             right_on=['building_category', 'from'])

    # Calculate value to add
    df_to_add = df_to.set_index(['building_category', 'TEK', 'year', 'to'])

    df_to_add['v'] = df_to_add.factor

    # Calculate value to subtract
    df_to_subtract = df_from.set_index(['building_category', 'TEK', 'year', 'from', 'to'])
    df_to_subtract.loc[:, 'v'] = -df_to_add.reset_index().groupby(by=['building_category', 'TEK', 'year', 'from', 'to']).agg(
        {'v': 'sum'})

    # Join add and substract rows
    addition_grouped = df_to_add.groupby(by=['building_category', 'TEK', 'year', 'to']).agg(
        {'v': 'sum', 'heating_systems': 'first', 'TEK_shares': 'first', 'factor': 'first', 'from': 'first'})
    subtraction_grouped = df_to_subtract.groupby(by=['building_category', 'TEK', 'year', 'from']).agg(
        {'v': 'sum', 'heating_systems': 'first', 'TEK_shares': 'first', 'factor': 'first'})

    df_to_sum = original.set_index(['building_category', 'TEK', 'year', 'heating_systems'])
    df_to_sum.loc[:, 'add'] = addition_grouped.loc[:, 'v']
    df_to_sum.loc[:, 'sub'] = subtraction_grouped.loc[:, 'v'].fillna(0)
    df_to_sum.loc[:, 'sub'] = df_to_sum.loc[:, 'sub'].fillna(0)

    df_to_sum.TEK_shares = df_to_sum.TEK_shares + df_to_sum['add'].fillna(0) + df_to_sum['sub'].fillna(0)

    calibrated_and_original = pd.concat([df_to_sum.reset_index(), original.reset_index()]).drop_duplicates(
        ['building_category', 'TEK', 'year', 'heating_systems'],
        keep='first').drop(columns='index',
                           errors='ignore')

    columns_to_keep = ['building_category', 'TEK', 'year', 'heating_systems', 'TEK_shares']
    return calibrated_and_original[columns_to_keep].reset_index(drop=True)
