import pandas as pd
from loguru import logger

from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.filter_tek import FilterTek


class HeatingSystems:
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

        aggregates = {'tek_share': 'sum', 'Ekstralast andel': 'sum', 'Grunnlast andel': 'sum', 'Spisslast andel': 'sum',
        'Grunnlast virkningsgrad': 'sum', 'Spisslast virkningsgrad': 'sum',
        'Ekstralast virkningsgrad': 'sum', 'Tappevann virkningsgrad': 'sum',
        'Spesifikt elforbruk': 'sum', 'Kjoling virkningsgrad': 'sum'}
        grouped = df.groupby(by=['building_category', 'TEK', 'Oppvarmingstyper']).agg(aggregates)
        return grouped.reset_index()

    def calculate(self, energy_requirements: pd.DataFrame) -> pd.DataFrame:
        """

        Parameters
        ----------
        energy_requirements : pd.DataFrame

        Returns
        -------

        """
        # TODO: Remove warning
        logger.warning('Merge TEK69s and PRE_TEK49s at an improper place')

        energy_requirements = self._remove_tek_suffix(energy_requirements)
        energy_requirements = self._group_and_sum_same_tek(energy_requirements)

        # If _RES of _COM is in TEK this will not work
        # energy_requirements.index[energy_requirements.index.str.endswith('_RES')]
        if energy_requirements.index.get_level_values('TEK').str.endswith('_RES').any() or energy_requirements.index.get_level_values('TEK').str.endswith('_COM').any():
            raise ValueError('Found _RES or _COM in energy_requirements')

        # Merge energy_requirements and heating_systems into df
        df = self._merge_energy_requirement_and_heating_systems(energy_requirements)

        # Make column eq_ts for tek_share adjusted energy requirement
        df['eq_ts'] = df.energy_requirement * df.tek_share

        # Zero fill columns before calculating to prevent NaN from messing up sums
        df.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']] = 0.0

        # Adjust energy requirements by efficiency
        # heating rv
        heating_rv_slice = (slice(None), slice(None), 'heating_rv', slice(None), slice(None))
        df.loc[heating_rv_slice, 'RV_GL'] = (
                df.loc[heating_rv_slice, 'eq_ts'] * df.loc[heating_rv_slice, 'Grunnlast andel'] / df.loc[
            heating_rv_slice, 'Grunnlast virkningsgrad'])
        df.loc[heating_rv_slice, 'RV_SL'] = (
                df.loc[heating_rv_slice, 'eq_ts'] * df.loc[heating_rv_slice, 'Spisslast andel'] / df.loc[
            heating_rv_slice, 'Spisslast virkningsgrad'])
        df.loc[heating_rv_slice, 'RV_EL'] = (
                df.loc[heating_rv_slice, 'eq_ts'] * df.loc[heating_rv_slice, 'Ekstralast andel'] / df.loc[
            heating_rv_slice, 'Ekstralast virkningsgrad'])

        # heating dhw energy use is calculated by dividing heating_dhw with 'Tappevann virkningsgrad'
        heating_dhw_slice = (slice(None), slice(None), 'heating_dhw', slice(None), slice(None))
        df.loc[heating_dhw_slice, 'DHW_TV'] = df.loc[heating_dhw_slice, 'eq_ts'] / df.loc[
            heating_dhw_slice, 'Tappevann virkningsgrad']

        # cooling energy use is calculated by dividing cooling with 'Kjoling virkningsgrad'
        cooling_slice = (slice(None), slice(None), 'cooling', slice(None), slice(None))
        df.loc[cooling_slice, 'CL_KV'] = df.loc[cooling_slice, 'eq_ts'] / df.loc[cooling_slice, 'Kjoling virkningsgrad']

        # lighting, electrical equipment, fans and pumps energy use is calculated by dividing with spesific electricity
        # useage
        other_slice = (slice(None), slice(None), EnergyPurpose.other(), slice(None), slice(None))
        df.loc[other_slice, 'O_SV'] = df.loc[other_slice, 'eq_ts'] / df.loc[other_slice, 'Spesifikt elforbruk']

        df.loc[:, 'kwh'] = df.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']].sum(axis=1)

        df.loc[:, 'gwh'] = df.loc[:, 'kwh'] / 10 ** 6

        df = df.sort_index(level=['building_category', 'TEK', 'year', 'building_condition', 'purpose', 'Oppvarmingstyper'])
        return df[['tek_share',
                   'eq_ts',
                   'RV_GL',
                   'RV_SL',
                   'RV_EL',
                   'DHW_TV',
                   'CL_KV',
                   'O_SV',
                   'kwh',
                   'gwh']]

    def _merge_energy_requirement_and_heating_systems(self, energy_requirements):
        df = energy_requirements.reset_index().merge(
            self.heating_systems_parameters.reset_index(),
            left_on=['building_category', 'TEK'],
            right_on=['building_category', 'TEK'])[
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'kwh_m2', 'm2', 'energy_requirement',
             'Oppvarmingstyper', 'tek_share', 'Grunnlast andel', 'Grunnlast virkningsgrad', 'Spisslast andel',
             'Spisslast virkningsgrad', 'Ekstralast andel', 'Ekstralast virkningsgrad', 'Tappevann virkningsgrad',
             'Spesifikt elforbruk',
             'Kjoling virkningsgrad']]
        # Unused columns
        # ,'Innfyrt_energi_kWh','Innfyrt_energi_GWh','Energibehov_samlet_GWh']]
        df = df.set_index(
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'Oppvarmingstyper']).sort_index()
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
