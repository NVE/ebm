import pandera as pa
from pandera.typing import Index, DataFrame, Series
from pandera.typing.common import DataFrameBase

from ebm.model.column_operations import explode_unique_columns, explode_column_alias
from ebm.model.energy_purpose import EnergyPurpose


class EnergyNeedYearlyImprovements(pa.DataFrameModel):
    building_category: Series[str]
    TEK: Series[str]
    purpose: Series[str]
    yearly_efficiency_improvement: Series[float] = pa.Field(ge=0.0, coerce=True)
    start_year: Series[int] = pa.Field(coerce=True, default=2020)
    function: Series[str]
    end_year: Series[int] = pa.Field(coerce=True, default=2050)
    _filename = 'energy_need_yearly_improvements'

    class Config:
        unique = ['building_category', 'TEK', 'purpose', 'start_year', 'end_year']


class YearlyReduction(pa.DataFrameModel):
    building_category: Series[str]
    TEK: Series[str]
    purpose: Series[str]
    year: Series[int]
    yearly_efficiency_improvement: Series[float] = pa.Field(ge=0.0, coerce=True)
    yearly_reduction_factor: Series[float] = pa.Field(ge=0.0, coerce=True)

    class Config:
        unique = ['building_category', 'TEK', 'purpose', 'year']


    @staticmethod
    def from_energy_need_yearly_improvements(
            en_yearly_improvement: DataFrameBase[EnergyNeedYearlyImprovements]|EnergyNeedYearlyImprovements) -> 'DataFrameBase[YearlyReduction]':
        """
        Transforms a EnergyNeedYearlyImprovement DataFrame into a EnergyNeedYearlyReduction DataFrame.

        Parameters
        ----------
        en_yearly_improvement : DataFrame[EnergyNeedYearlyImprovements]

        Returns
        -------
        DataFrameBase[YearlyReduction]

        Raises
        ------
        pa.errors.SchemaError
            When the resulting dataframe fails to validate
        pa.errors.SchemaErrors
            When the resulting dataframe fails to validate

        """
        unique_columns = ['building_category', 'TEK', 'purpose', 'start_year', 'end_year']
        en_yearly_improvement = explode_unique_columns(en_yearly_improvement,
                                                       unique_columns=unique_columns)

        en_yearly_improvement = explode_column_alias(en_yearly_improvement,
                                                     column='purpose',
                                                     values=[p for p in EnergyPurpose],
                                                     alias='default',
                                                     de_dup_by=unique_columns)

        en_yearly_improvement['year']: pa.typing.DataFrame = en_yearly_improvement.apply(
            lambda row: range(row.start_year, row.end_year + 1), axis=1)

        en_yearly_improvement = en_yearly_improvement.explode(['year'])
        en_yearly_improvement['year'] = en_yearly_improvement['year'].astype(int)
        en_yearly_improvement.loc[:, 'yearly_reduction_factor'] = (1.0-en_yearly_improvement.loc[:, 'yearly_efficiency_improvement'])**(1.0+en_yearly_improvement.loc[:, 'year']-en_yearly_improvement.loc[:, 'start_year']).astype(float)

        en_yearly_improvement = en_yearly_improvement[['building_category', 'TEK', 'purpose',
                                                       'year', 'start_year', 'end_year',
                                                       'yearly_efficiency_improvement',
                                                       'yearly_reduction_factor']]

        return YearlyReduction.validate(en_yearly_improvement, lazy=True)

