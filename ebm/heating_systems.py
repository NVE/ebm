import pandas as pd
from loguru import logger

from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.filter_tek import FilterTek

ADJUSTED_REQUIREMENT = 'eq_ts'
# there are 3 time-of-use zones: peak, shoulder and offpeak.
HEATING_RV_GRUNNLAST = 'RV_GL'
HEATING_RV_SPISSLAST = 'RV_SL'
HEATIG_RV_EKSTRALAST = 'RV_EL'
COOLING_KV = 'CL_KV'
DHW_TV = 'DHW_TV'
OTHER_SV = 'O_SV'
HEATING_RV = 'heating_rv'
HEATING_DHW = 'heating_dhw'
COOLING = 'cooling'
DHW_EFFICIENCY = 'Tappevann virkningsgrad'

TEK_SHARE = 'tek_share'
GRUNNLAST_ANDEL = 'Grunnlast andel'
GRUNNLAST_VIRKNINGSGRAD = 'Grunnlast virkningsgrad'
KJOLING_VIRKNINGSGRAD = 'Kjoling virkningsgrad'
SPESIFIKT_ELFORBRUK = 'Spesifikt elforbruk'
EKSTRALAST_ANDEL = 'Ekstralast andel'
EKSTRALAST_VIRKNINGSGRAD = 'Ekstralast virkningsgrad'
SPISSLAST_ANDEL = 'Spisslast andel'
SPISSLAST_VIRKNINGSGRAD = 'Spisslast virkningsgrad'


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

        aggregates = {TEK_SHARE: 'sum', EKSTRALAST_ANDEL: 'sum', GRUNNLAST_ANDEL: 'sum', SPISSLAST_ANDEL: 'sum',
                      GRUNNLAST_VIRKNINGSGRAD: 'sum', SPISSLAST_VIRKNINGSGRAD: 'sum',
                      EKSTRALAST_VIRKNINGSGRAD: 'sum', DHW_EFFICIENCY: 'sum',
                      SPESIFIKT_ELFORBRUK: 'sum', KJOLING_VIRKNINGSGRAD: 'sum'}
        grouped = df.groupby(by=['building_category', 'TEK', 'Oppvarmingstyper']).agg(aggregates)
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

        # Merge energy_requirements and heating_systems into df
        df = self._merge_energy_requirement_and_heating_systems(energy_requirements)

        # Make column eq_ts for tek_share adjusted energy requirement
        df[ADJUSTED_REQUIREMENT] = df.energy_requirement * df[TEK_SHARE]

        # Zero fill columns before calculating to prevent NaN from messing up sums
        df.loc[:,
        [HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, HEATIG_RV_EKSTRALAST, DHW_TV, COOLING_KV, OTHER_SV]] = 0.0

        # Adjust energy requirements by efficiency
        # heating rv

        heating_rv_slice = (slice(None), slice(None), HEATING_RV, slice(None), slice(None))

        df.loc[heating_rv_slice, HEATING_RV_GRUNNLAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] * df.loc[
            heating_rv_slice, GRUNNLAST_ANDEL] / df.loc[
                    heating_rv_slice, GRUNNLAST_VIRKNINGSGRAD])

        df.loc[heating_rv_slice, HEATING_RV_SPISSLAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] *
                df.loc[heating_rv_slice, SPISSLAST_ANDEL] / df.loc[heating_rv_slice, SPISSLAST_VIRKNINGSGRAD])

        df.loc[heating_rv_slice, HEATIG_RV_EKSTRALAST] = (
                df.loc[heating_rv_slice, ADJUSTED_REQUIREMENT] *
                df.loc[heating_rv_slice, EKSTRALAST_ANDEL] / df.loc[heating_rv_slice, EKSTRALAST_VIRKNINGSGRAD])

        # heating dhw energy use is calculated by dividing heating_dhw with 'Tappevann virkningsgrad'
        heating_dhw_slice = (slice(None), slice(None), HEATING_DHW, slice(None), slice(None))
        df.loc[heating_dhw_slice, DHW_TV] = df.loc[heating_dhw_slice, ADJUSTED_REQUIREMENT] / df.loc[
            heating_dhw_slice, DHW_EFFICIENCY]

        # cooling energy use is calculated by dividing cooling with 'Kjoling virkningsgrad'
        cooling_slice = (slice(None), slice(None), COOLING, slice(None), slice(None))
        df.loc[cooling_slice, COOLING_KV] = df.loc[cooling_slice, ADJUSTED_REQUIREMENT] / df.loc[
            cooling_slice, KJOLING_VIRKNINGSGRAD]

        # lighting, electrical equipment, fans and pumps energy use is calculated by dividing with spesific electricity
        # useage
        other_slice = (slice(None), slice(None), EnergyPurpose.other(), slice(None), slice(None))
        df.loc[other_slice, OTHER_SV] = df.loc[other_slice, ADJUSTED_REQUIREMENT] / df.loc[
            other_slice, SPESIFIKT_ELFORBRUK]

        df.loc[:, 'kwh'] = df.loc[:,
                           [HEATING_RV_GRUNNLAST, HEATING_RV_SPISSLAST, HEATIG_RV_EKSTRALAST, DHW_TV, COOLING_KV,
                            ('%s' % OTHER_SV)]].sum(axis=1)

        df.loc[:, 'gwh'] = df.loc[:, 'kwh'] / 10 ** 6

        df = df.sort_index(
            level=['building_category', 'TEK', 'year', 'building_condition', 'purpose', 'Oppvarmingstyper'])
        return df[[TEK_SHARE,
                   ADJUSTED_REQUIREMENT,
                   HEATING_RV_GRUNNLAST,
                   HEATING_RV_SPISSLAST,
                   HEATIG_RV_EKSTRALAST,
                   DHW_TV,
                   COOLING_KV,
                   OTHER_SV,
                   'kwh',
                   'gwh']]

    def _merge_energy_requirement_and_heating_systems(self, energy_requirements):
        df = energy_requirements.reset_index().merge(
            self.heating_systems_parameters.reset_index(),
            left_on=['building_category', 'TEK'],
            right_on=['building_category', 'TEK'])[
            ['building_category', 'building_condition', 'purpose', 'TEK', 'year', 'kwh_m2', 'm2', 'energy_requirement',
             'Oppvarmingstyper', 'tek_share', GRUNNLAST_ANDEL, GRUNNLAST_VIRKNINGSGRAD,
             SPISSLAST_ANDEL, SPISSLAST_VIRKNINGSGRAD,
             EKSTRALAST_VIRKNINGSGRAD, EKSTRALAST_ANDEL,
             DHW_EFFICIENCY, SPESIFIKT_ELFORBRUK, KJOLING_VIRKNINGSGRAD]]
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
