import pandas as pd
from loguru import logger

from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.filter_tek import FilterTek


class HeatingSystems:
    def __init__(self, heating_systems_parameters: pd.DataFrame = None):
        self.heating_systems_parameters = heating_systems_parameters

    def calculate(self, energy_requirements: pd.DataFrame) -> pd.DataFrame:
        logger.warning('Merge TEK69s and PRE_TEK49s at an improper place')
        energy_requirements = FilterTek.remove_tek_suffix(energy_requirements, suffix='_RES')
        energy_requirements = FilterTek.remove_tek_suffix(energy_requirements, suffix='_COM')
        energy_requirements = FilterTek.merge_tek(energy_requirements, 'TEK69', ['TEK69_1976', 'TEK69_1986'])
        energy_requirements = FilterTek.merge_tek(energy_requirements, 'PRE_TEK49',
                                                  ['PRE_TEK49_1940', 'PRE_TEK49_1950'])
        energy_requirements = energy_requirements.sort_index()

        # If _RES of _COM is in TEK this will not work
        # energy_requirements.index[energy_requirements.index.str.endswith('_RES')]
        if energy_requirements.index.get_level_values('TEK').str.endswith('_RES').any() or energy_requirements.index.get_level_values('TEK').str.endswith('_COM').any():
            raise ValueError('Found _RES or _COM in energy_requirements')

        d2 = \
        energy_requirements.reset_index().merge(self.heating_systems_parameters.reset_index(), left_on=['building_category', 'TEK'],
                                                right_on=['building_category', 'TEK'])[
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'kwh_m2', 'm2', 'energy_requirement',
             'Oppvarmingstyper', 'tek_share', 'Grunnlast andel', 'Grunnlast virkningsgrad', 'Spisslast andel',
             'Spisslast virkningsgrad', 'Ekstralast andel', 'Ekstralast virkningsgrad', 'Tappevann virkningsgrad',
             'Spesifikt elforbruk',
             'Kjoling virkningsgrad']]  # ,'Innfyrt_energi_kWh','Innfyrt_energi_GWh','Energibehov_samlet_GWh']]

        d2 = d2.set_index(['building_category', 'building_condition', 'purpose', 'TEK', 'year']).sort_index()

        # Make column eq_ts for tek_share adjusted energy requirement
        d2['eq_ts'] = d2.energy_requirement * d2.tek_share

        # Zero fill columns before calculating to avoid unnecessary NaN
        d2.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']] = 0.0

        # Adjust energy requirements by efficiency

        # heating rv
        heating_rv_slice = (slice(None), slice(None), 'heating_rv', slice(None), slice(None))
        d2.loc[heating_rv_slice, 'RV_GL'] = (
                d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Grunnlast andel'] / d2.loc[
            heating_rv_slice, 'Grunnlast virkningsgrad'])
        d2.loc[heating_rv_slice, 'RV_SL'] = (
                d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Spisslast andel'] / d2.loc[
            heating_rv_slice, 'Spisslast virkningsgrad'])
        d2.loc[heating_rv_slice, 'RV_EL'] = (
                d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Ekstralast andel'] / d2.loc[
            heating_rv_slice, 'Ekstralast virkningsgrad'])

        # heating dhw
        heating_dhw_slice = (slice(None), slice(None), 'heating_dhw', slice(None), slice(None))
        d2.loc[heating_dhw_slice, 'DHW_TV'] = d2.loc[heating_dhw_slice, 'eq_ts'] / d2.loc[
            heating_dhw_slice, 'Tappevann virkningsgrad']

        # cooling
        cooling_slice = (slice(None), slice(None), 'cooling', slice(None), slice(None))
        d2.loc[cooling_slice, 'CL_KV'] = d2.loc[cooling_slice, 'eq_ts'] / d2.loc[cooling_slice, 'Kjoling virkningsgrad']

        # lighting, electrical equipment, fans and pumps
        other_slice = (
            slice(None), slice(None), [e for e in EnergyPurpose if e not in ('heating_rv', 'heating_dhw', 'cooling')],
            slice(None), slice(None))
        d2.loc[other_slice, 'O_SV'] = d2.loc[other_slice, 'eq_ts'] / d2.loc[other_slice, 'Spesifikt elforbruk']

        d2.loc[:, 'kwh'] = d2.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']].sum(axis=1)

        d2.loc[:, 'gwh'] = d2.loc[:, 'kwh'] / 10 ** 6

        d2 = d2.sort_index(level=['building_category', 'TEK', 'year', 'building_condition', 'purpose'])
        return d2[['Oppvarmingstyper',
                   'tek_share',
                   'eq_ts',
                   'RV_GL',
                   'RV_SL',
                   'RV_EL',
                   'DHW_TV',
                   'CL_KV',
                   'O_SV',
                   'kwh',
                   'gwh']]
