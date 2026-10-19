import itertools
import os
import sys

import pandas as pd
from loguru import logger

from ebm.definition_expansion import add_lineno, collapse_years, explode_on_plus, explode_years, mark_duplicates, select_groups_with_lowest_lineno_count
from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition
from ebm.model.column_operations import explode_unique_columns
from ebm.model.data_classes import YearRange
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.file_handler import FileHandler


class DatabaseManager:
    """
    Manages database operations.
    """

    # Column names
    COL_TEK = 'building_code'
    COL_TEK_BUILDING_YEAR = 'building_year'
    COL_TEK_START_YEAR = 'period_start_year'
    COL_TEK_END_YEAR = 'period_end_year'
    COL_BUILDING_CATEGORY = 'building_category'
    COL_BUILDING_CONDITION = 'building_condition'
    COL_AREA = 'area'
    COL_ENERGY_REQUIREMENT_PURPOSE = 'purpose'
    COL_ENERGY_REQUIREMENT_VALUE = 'kwh_m2'
    COL_HEATING_REDUCTION = 'reduction_share'

    DEFAULT_VALUE = 'default'

    def __init__(self, file_handler: FileHandler = None, years: YearRange|None=None):
        # Create default FileHandler if file_handler is None

        self.file_handler = file_handler if file_handler is not None else FileHandler()
        if years:
            self.years = years
        else:
            import os  # noqa: PLC0415
            logger.warning('YearRange was not provided for DatabaseManager.')
            try:
                _years = YearRange(int(os.environ.get('EBM_START_YEAR', 2020)), int(os.environ.get('EBM_END_YEAR', 2050)))
                self.years = _years
                logger.warning('Using {default_years} from EBM_START_YEAR and EBM_END_YEAR (default 2020 and 2050).', default_years=_years)
            except ValueError as e:
                logger.error(f"Invalid year range in environment variables: {e}. Using default YearRange(2020, 2050).")
                self.years = YearRange(2020, 2050)


    def __repr__(self):
        return f'DatabaseManager(file_handler={self.file_handler}, years={self.years})'

    def get_building_code_list(self):
        """
        Get a list of building_code.

        Returns:
        - building_code_list (list): List of building_code.
        """
        building_code_id = self.file_handler.get_building_code()
        building_code_list = building_code_id[self.COL_TEK].unique()
        return building_code_list

    def make_building_purpose(self, years: YearRange | None = None) -> pd.DataFrame:
        """
        Returns a dataframe of all combinations building_categories, teks, original_condition, purposes
        and optionally years.

        Parameters
        ----------
        years : YearRange, optional

        Returns
        -------
        pd.DataFrame
        """
        data = []
        columns = [list(BuildingCategory), self.get_building_code_list().tolist(), EnergyPurpose]
        column_headers = ['building_category', 'building_code', 'building_condition', 'purpose']
        if years:
            columns.append(years)
            column_headers.append('year')

        for bc, tek, purpose, *year in itertools.product(*columns):
            row = [bc, tek, 'original_condition', purpose]
            if years:
                row.append(year[0])
            data.append(row)

        return pd.DataFrame(data=data, columns=column_headers)

    def get_building_category(self) -> pd.DataFrame:
        """
        Retrieve building_category

        Returns
        -------
        pd.DataFrame
            Pandas Dataframe containing building_category with parameters
        """
        building_category = self.file_handler.get_building_category()
        return building_category

    def get_building_codes(self) -> pd.DataFrame:
        """
        Retrieve building_code_parameters

        Returns
        -------
        pd.DataFrame
            Pandas Dataframe containing building_code with parameters
        """
        building_code_params_df = self.file_handler.get_building_code()
        return building_code_params_df


    def get_scurve_params(self):
        """
        Get input dataframe with S-curve parameters/assumptions.

        Returns:
        - scurve_params (pd.DataFrame): DataFrame with S-curve parameters.
        """
        scurve_params = self.file_handler.get_s_curve()
        return scurve_params

    def get_construction_population(self) -> pd.DataFrame:
        """
        Get construction population DataFrame.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          year population household_size
        """
        new_buildings_population = self.file_handler.get_construction_population()
        new_buildings_population["household_size"] = new_buildings_population['household_size'].astype('float64')
        new_buildings_population = new_buildings_population.set_index('year')
        return new_buildings_population


    def get_population_forecast_end_year(self) -> int:
        """Retrieve the maximum year from the population forecast data

        This method extracts the highest value from the 'year' level
        of the MultiIndex in the construction population dataset.

        Returns
        -------
        int
            The maximum year available in the population forecast data.

        Raises
        ------
        ValueError
            If the population forecast index does not contain a 'year' level.
        """

        construction_population = self.get_construction_population()
        return construction_population.index.get_level_values(level='year').max()


    def get_new_buildings_category_share(self) -> pd.DataFrame:
        """
        Get building category share by year as a DataFrame.

        The number can be used in conjunction with number of households to calculate total number
        of buildings of category house and apartment block

        Returns:
        - new_buildings_category_share (pd.DataFrame): Dataframe containing population numbers
          "year", "Andel nye småhus", "Andel nye leiligheter", "Areal nye småhus", "Areal nye leiligheter"
        """
        df = self.file_handler.get_construction_building_category_share()
        df['year'] = df['year'].astype(int)
        df = df.set_index('year')
        return df

    def get_area_new_residential_buildings(self) -> pd.Series:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """
        df = self.file_handler.get_building_category_area()

        return df


    def get_building_category_floor_area(self, building_category: BuildingCategory) -> pd.Series:
        """
        Get population and household size DataFrame from a file.

        Returns:
        - construction_population (pd.DataFrame): Dataframe containing population numbers
          "area","type of building","2010","2011"
        """
        df = self.file_handler.get_building_category_area()

        building_category_floor_area = df[building_category].dropna()

        return building_category_floor_area

    #TODO: remove after refactoring
    def get_area_parameters(self) -> pd.DataFrame:
        """
        Get total area (m^2) per building category and TEK.

        Parameters:
        - building_category (str): Optional parameter that filter the returned dataframe by building_category

        Returns:
        - area_parameters (pd.DataFrame): Dataframe containing total area (m^2) per
                                          building category and TEK.
        """
        area_params = self.file_handler.get_area_parameters()
        return area_params


    def get_behaviour_factor(self) -> pd.DataFrame:
        f = self.file_handler.get_file(self.file_handler.BEHAVIOUR_FACTOR)
        building_category_code_purpose = self.get_building_category_code_purpose()
        building_category_code_purpose['model_start_year'] = self.years.start
        building_category_code_purpose['model_end_year'] = self.years.end

        behaviour_factor = f.pipe(add_lineno).pipe(explode_on_plus, 'building_category').pipe(explode_on_plus, 'building_code').pipe(explode_on_plus, 'purpose').assign(
            function='behaviour_factor',

        ).merge(building_category_code_purpose, how='right',
                left_on=['building_category', 'building_code', 'purpose'],
                right_on=['building_category_alias', 'building_code_alias', 'purpose_alias'], suffixes=['_definition', ''])
        behaviour_factor = behaviour_factor.assign(start_year = behaviour_factor['model_start_year'].astype(int),
                                                   end_year = behaviour_factor['model_end_year'].astype(int))
        yearly_behaviour_factor = explode_years(behaviour_factor, start_column='model_start_year', end_column='model_end_year')

        scored = select_groups_with_lowest_lineno_count(
            yearly_behaviour_factor, grouping_columns=['building_category', 'building_code', 'purpose'], filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'building_code', 'purpose', 'year'], keep='first'))
        deduped = marked.drop_duplicates(subset=['building_category', 'building_code', 'purpose', 'year'], keep='first')
        deduped['behaviour_factor'] = deduped['behaviour_factor'].fillna(1.0)

        return deduped.reset_index(drop=True).assign(function='behaviour_factor').drop(
            columns=['building_category_alias', 'building_code_alias', 'purpose_alias', 'building_category_definition',
                     'building_code_definition', 'purpose_definition', 'dupe', 'lineno'], errors='ignore')


    def get_energy_req_original_condition(self, year_range: YearRange|None=None) -> pd.DataFrame:
        """
        Get dataframe with energy requirement (kWh/m^2) for floor area in original condition. The result will be
            calibrated using the dataframe from DatabaseManger.get_calibrate_heating_rv

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement (kWh/m^2) for floor area in original condition,
            per building category and purpose.
        """
        start_year = os.environ.get('EBM_START_YEAR', '2020')
        end_year = os.environ.get('EBM_END_YEAR', '2050')

        if not year_range and (start_year!='2020' or '--start-year') in sys.argv:
            logger.warning('year_range is undefined while, EBM_START_YEAR ({start_year}) is not set to default values. ', start_year=start_year)
        if not year_range and (end_year != '2050' or '--end-year' in sys.argv):
            logger.warning('year_range is undefined while,  EBM_END_YEAR ({end_year}) is not set to default values.', end_year=end_year)
        if not year_range:
            logger.warning('Using default year 2020 -> 2050')

        years = YearRange(2020, 2050) if year_range is None else year_range
        bp2 = self.make_building_purpose(years=years)

        building_code_purpose = self.get_building_category_code_purpose()
        building_code_purpose = building_code_purpose[
            (building_code_purpose.building_category == building_code_purpose.building_category_alias)
            & (building_code_purpose.building_code == building_code_purpose.building_code_alias)
            & (building_code_purpose.purpose == building_code_purpose.purpose_alias)
        ]
        building_purpose = years.cross_join(building_code_purpose)

        ff = self.file_handler.get_energy_req_original_condition()[['building_category', 'building_code', 'purpose', 'kwh_m2']]
        df = explode_unique_columns(ff, ['building_category', 'building_code', 'purpose'], default_building_code=self.get_building_code_list())
        if len(df[df.building_code=='TEK21']) > 0:
            logger.warning('Detected TEK21 in {filename}', filename=self.file_handler.ENERGY_NEED_ORIGINAL_CONDITION)
        df = df.set_index(['building_category', 'purpose', 'building_code']).sort_index()

        #df = building_purpose.set_index(['building_category', 'building_code', 'purpose', 'year']).join(df, how='left')
        df = df.join(building_purpose.set_index(['building_category', 'building_code', 'purpose', 'year']), how='left')

        behaviour_factor = self.get_behaviour_factor().set_index(['building_category', 'building_code', 'purpose', 'year'])

        df = df.join(behaviour_factor)

        heating_rv_factor = self.get_calibrate_heating_rv().set_index(['building_category', 'purpose']).heating_rv_factor
        df = df.join(heating_rv_factor, how='left')

        df['heating_rv_factor'] = df['heating_rv_factor'].astype(float).fillna(1.0)
        df['uncalibrated_kwh_m2'] = df['kwh_m2']
        df['calibrated_kwh_m2'] = df.heating_rv_factor * df.kwh_m2
        df.loc[df.calibrated_kwh_m2.isna(), 'calibrated_kwh_m2'] = df.loc[df.calibrated_kwh_m2.isna(), 'kwh_m2']
        df['kwh_m2'] = df['calibrated_kwh_m2']
        return df.reset_index()


    def get_energy_req_reduction_per_condition(self) -> pd.DataFrame:
        """
        Get dataframe with shares for reducing the energy requirement of the different building conditions. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        Returns
        -------
        pd.DataFrame
            Dataframe containing energy requirement reduction shares for the different building conditions, 
            per building category, TEK and purpose.        
        """
        improvement_building_upgrade = self.file_handler.get_energy_req_reduction_per_condition()
        improvement_building_upgrade = (improvement_building_upgrade
                                        .pipe(add_lineno)
                                        .pipe(explode_on_plus, column_name='building_category')
                                        .pipe(explode_on_plus, column_name='building_code')
                                        .pipe(explode_on_plus, column_name='building_condition')
                                        .pipe(explode_on_plus, column_name='purpose')
        )
        
        if len(improvement_building_upgrade[improvement_building_upgrade.building_code=='TEK21']) > 0:
            logger.warning('Detected TEK21 in {filename}', filename=self.file_handler.IMPROVEMENT_BUILDING_UPGRADE)

        building_categories = self.get_building_category_alias()
        building_codes = self.get_building_code_alias()
        purposes = self.get_purpose_alias()
        building_conditions = self.get_building_condition_alias()
        existing_building_conditions = building_conditions[building_conditions.building_condition!='demolition'].reset_index()
        building_category_code_condition = (building_categories
                                            .merge(building_codes, how='cross')
                                            .merge(purposes, how='cross')
                                            .merge(existing_building_conditions, how='cross')
        )

        all_improvement_building_upgrade = improvement_building_upgrade.merge(
            building_category_code_condition,
            how='right',
            left_on=['building_category', 'building_code', 'purpose', 'building_condition'],
            right_on=['building_category_alias', 'building_code_alias', 'purpose_alias', 'building_condition_alias'],
            suffixes=['_definition', ''],
        )
        all_definitions = all_improvement_building_upgrade.dropna()
        scored = select_groups_with_lowest_lineno_count(
            all_definitions, grouping_columns=['building_category', 'building_code', 'purpose', 'building_condition'], filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'building_code', 'purpose', 'building_condition'], keep='first'))
        deduped = marked.drop_duplicates(subset=['building_category', 'building_code', 'purpose', 'building_condition'], keep='first')

        return deduped[['building_category', 'building_code', 'purpose', 'building_condition', 'reduction_share',]]

    
    def get_energy_need_yearly_improvements(self) -> pd.DataFrame:
        """
        Get dataframe with yearly efficiency rates for energy need improvements. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        The column yearly_efficiency_improvement is expected to contain the yearly reduction as
        a float between 0.1 and 1.0.

        Returns
        -------
        pd.DataFrame
            Dataframe containing yearly efficiency rates (%) for energy need improvements,
            per building category, tek and purpose.
        """


        yearly_improvements = self.file_handler.get_energy_need_yearly_improvements()
        split_yearly_improvements = (yearly_improvements
                                     .pipe(add_lineno)
                                     .pipe(explode_on_plus, column_name='building_category')
                                     .pipe(explode_on_plus, column_name='building_code')
                                     .pipe(explode_on_plus, column_name='purpose')
        )
        building_category_code_purpose = self.get_building_category_code_purpose()
        all_energy_need_improvements = split_yearly_improvements.merge(
            building_category_code_purpose.drop(columns=['lineno'], errors='ignore'),
            how='right',
            left_on=['building_category', 'building_code', 'purpose'],
            right_on=['building_category_alias', 'building_code_alias', 'purpose_alias'],
            suffixes=['_definition', ''],
        ).drop(columns=['building_category_alias'])

        all_definitions = all_energy_need_improvements.dropna()
        all_definitions = all_definitions.assign(
            start_year=all_definitions.start_year.astype('int'),
            end_year=all_definitions.end_year.astype('int'),
            lineno=all_definitions.lineno.astype('int'),
        )
        scored_energy_need_improvements = select_groups_with_lowest_lineno_count(
            all_definitions, grouping_columns=['building_category', 'building_code', 'purpose', 'function'], filter_columns=True)
        scored_yearly = explode_years(scored_energy_need_improvements)
        marked_energy_need_improvements = mark_duplicates(scored_yearly,
                                                          grouping_columns=['building_category', 'building_code', 'purpose', 'function'])


        return marked_energy_need_improvements.reset_index(drop=True).pipe(collapse_years)


    def get_energy_need_policy_improvement(self) -> pd.DataFrame:
        """
        Get dataframe with total energy need improvement in a period related to a policy. This
        function calls explode_unique_columns to expand building_category and TEK as necessary.

        Deprecated: Use get_energy_need_yearly_improvements instead.

        Returns
        -------
        pd.DataFrame
            Dataframe containing total energy need improvement (%) in a policy period,
            per building category, tek and purpose.
        """
        import warnings  # noqa: PLC0415
        warning_msg = 'get_energy_need_policy_improvement is deprecated. Use get_energy_need_yearly_improvements instead.'
        warnings.warn(warning_msg, DeprecationWarning)
        logger.warning(warning_msg)
        improvements = self.get_energy_need_yearly_improvements()
        if 'value' not in improvements.columns:
            improvements = improvements.rename(columns={'yearly_efficiency_improvement': 'value'}, errors='ignore')
        enp = improvements[improvements['function']=='improvement_at_end_year'].copy()
        return enp

    def get_holiday_home_fuelwood_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["fuelwood"]
        return df
    
    def get_holiday_home_fossilfuel_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["fossilfuel"]
        return df

    def get_holiday_home_electricity_consumption(self) -> pd.Series:
        df = self.file_handler.get_holiday_home_energy_consumption().set_index('year')["electricity"]
        return df

    def get_holiday_home_by_year(self) -> pd.DataFrame:
        return self.file_handler.get_holiday_home_by_year().set_index('year')

    def get_calibrate_heating_rv(self) -> pd.Series:
        df = self.file_handler.get_calibrate_heating_rv()

        split_df = (
            df.pipe(add_lineno)
            .pipe(explode_on_plus, column_name='building_category')
            .pipe(explode_on_plus, column_name='purpose')
        )
        building_categories = self.get_building_category_alias()
        purposes = self.get_purpose_alias()
        heating_rv = purposes[purposes.purpose == 'heating_rv'].copy()
        building_category_purpose = building_categories.merge(heating_rv, how='cross')
        all_calibrate_heating_rv = split_df.merge(
            building_category_purpose.drop(columns=['lineno'], errors='ignore'),
            how='right',
            left_on=['building_category', 'purpose'],
            right_on=['building_category_alias', 'purpose_alias'],
            suffixes=['_definition', ''],
        )
        scored = select_groups_with_lowest_lineno_count(
            all_calibrate_heating_rv, grouping_columns=['building_category', 'purpose', ], filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'purpose',], keep='first'))
        deduped = marked.drop_duplicates(subset=['building_category', 'purpose',], keep='first')[['building_category', 'purpose', 'heating_rv_factor']]
        return deduped.dropna().reset_index(drop=True)


    def get_calibrate_heating_systems(self) -> pd.DataFrame:
        df = self.file_handler.get_calibrate_heating_systems()
        split_df = explode_on_plus(add_lineno(df), 'building_category')

        building_categories = self.get_building_category_alias()
        merged = building_categories.merge(split_df,
                                           left_on='building_category_alias',
                                           right_on='building_category', suffixes=['', '_definition'])

        scored = select_groups_with_lowest_lineno_count(
            merged, grouping_columns=['building_category', 'to', 'from'], filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'to', 'from'], keep='last'))
        deduped = marked.drop_duplicates(subset=['building_category', 'to', 'from'], keep='last')

        return deduped[['building_category', 'to', 'from', 'factor', 'lineno']].reset_index(drop=True)

    def get_area_per_person(self,
                            building_category: BuildingCategory = None) -> pd.Series:
        """
        Return area_per_person as a pd.Series

        Parameters
        ----------
        building_category: BuildingCategory, optional
            filter for building category
        Returns
        -------
        pd.Series
            float values indexed by building_category, (year)
        """
        df = self.file_handler.get_area_per_person()
        df = df.set_index('building_category')

        if building_category:
            return df.area_per_person.loc[building_category]
        return df.area_per_person

    def get_heating_system_initial_shares(self) -> pd.DataFrame:
        """
        Get initial heating-system shares resolved for each building combination.

        Expands building-category, building-code, and heating-system aliases in
        the source definitions. For each resolved
        ``(building_category, building_code, heating_systems)`` combination,
        keeps definitions associated with the lowest source line number and
        marks remaining duplicate definitions.

        Returns
        -------
        pd.DataFrame
            Resolved initial shares with the source columns, ``lineno`` for
            source-line provenance, and ``dupe`` indicating duplicate resolved
            heating-system definitions.
        """
        shares_start_year = self.file_handler.get_heating_systems_shares_start_year().pipe(add_lineno)
        definitions = (
            shares_start_year
            .pipe(explode_on_plus, 'building_category')
            .pipe(explode_on_plus, 'building_code')
            .pipe(explode_on_plus, 'heating_systems')
        )
        aliases = self.get_building_category_alias().merge(
            self.get_building_code_alias(),
            how='cross',
        )
        expanded = aliases.merge(
            definitions,
            how='inner',
            left_on=['building_category_alias', 'building_code_alias'],
            right_on=['building_category', 'building_code'],
            suffixes=['', '_definition'],
        )
        deduped_on_lineno = expanded.drop_duplicates(subset=['building_category', 'building_code', 'heating_systems', 'lineno'], keep='last')
        df = deduped_on_lineno[shares_start_year.columns].sort_values(
            by=['building_category', 'building_code', 'heating_systems', 'lineno'],
            ascending=True,
        )

        scored = select_groups_with_lowest_lineno_count(
            df, grouping_columns=['building_category', 'building_code', 'heating_systems'], filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'building_code', 'heating_systems', ], keep=False))
        return marked


    def get_heating_system_efficiencies(self) -> pd.DataFrame:
        return self.file_handler.get_heating_system_efficiencies()


    def get_heating_system_forecast(self) -> pd.DataFrame:
        heating_system_forecast_csv = self.file_handler.get_heating_system_forecast().pipe(add_lineno)
        exploded_heating_system_forecast = explode_on_plus(heating_system_forecast_csv, 'building_category').pipe(explode_on_plus, 'building_code')
        building_category_codes = self.get_building_category_alias().merge(self.get_building_code_alias(), how='cross')
        df = building_category_codes.merge(exploded_heating_system_forecast,
                                       how='inner',
                                       left_on=['building_category_alias', 'building_code_alias'],
                                       right_on=['building_category', 'building_code'],
                                       suffixes=['', '_definition'])

        scored = select_groups_with_lowest_lineno_count(
            df,
            grouping_columns=['building_category', 'building_code', 'heating_systems', 'new_heating_systems'],
            filter_columns=True
        )
        marked = scored.assign(dupe=scored.duplicated(subset=['building_category', 'building_code', 'heating_systems', 'new_heating_systems'], keep='last'))
        deduped = marked.drop_duplicates(subset=['building_category', 'building_code', 'heating_systems', 'new_heating_systems'], keep='last')

        return deduped.dropna().drop(columns=[
            'building_category_alias',
            'building_category_definition',
            'building_code_alias',
            'building_code_definition',
            'dupe',
        ], errors='ignore').reset_index(drop=True)

    
    def get_building_category_alias(self) -> pd.DataFrame:
        """Return every building category with category, group, and default aliases."""
        building_categories = self.get_building_category()
        categories = building_categories[[self.COL_BUILDING_CATEGORY]].assign(
            building_category_alias=building_categories[self.COL_BUILDING_CATEGORY],
        )
        groups = building_categories[
            [self.COL_BUILDING_CATEGORY, 'building_group']
        ].rename(columns={'building_group': 'building_category_alias'})
        defaults = building_categories[[self.COL_BUILDING_CATEGORY]].assign(
            building_category_alias=self.DEFAULT_VALUE,
        )

        return pd.concat([categories, groups, defaults], ignore_index=True)

    def get_building_code_alias(self) -> pd.DataFrame:
        building_codes = self.get_building_code_list()
        codes = pd.DataFrame({'building_code': building_codes, 'building_code_alias': building_codes})
        defaults = pd.DataFrame({'building_code': building_codes, 'building_code_alias': [self.DEFAULT_VALUE] * len(building_codes)})
        return pd.concat([codes, defaults], ignore_index=True)

    def get_building_condition_alias(self) -> pd.DataFrame:
        building_conditions = [c for c in BuildingCondition]
        conditions = pd.DataFrame({'building_condition': building_conditions, 'building_condition_alias': building_conditions})
        defaults = pd.DataFrame({'building_condition': building_conditions, 'building_condition_alias': [self.DEFAULT_VALUE] * len(building_conditions)})
        return pd.concat([conditions, defaults], ignore_index=True)

    def get_purpose_alias(self) -> pd.DataFrame:
        purposes = pd.DataFrame({'purpose': list(EnergyPurpose), 'purpose_alias': list(EnergyPurpose)})
        defaults = pd.DataFrame({'purpose': list(EnergyPurpose), 'purpose_alias': [self.DEFAULT_VALUE] * len(EnergyPurpose)})
        return pd.concat([purposes, defaults], ignore_index=True)

    def get_building_category_code_purpose(self) -> pd.DataFrame:
        building_category_alias = self.get_building_category_alias()
        building_code_alias = self.get_building_code_alias()
        purpose_alias = self.get_purpose_alias()

        return (
            building_category_alias
            .merge(building_code_alias, how='cross')
            .merge(purpose_alias, how='cross')
        )


if __name__ == '__main__':
    logger.info('Running DatabaseManager.__main__ {cwd}', cwd=os.getcwd())
    db = DatabaseManager()
    building_category = BuildingCategory.HOUSE

    a = db.get_energy_need_policy_improvement()
    print(a)
