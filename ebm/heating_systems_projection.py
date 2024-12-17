import typing
import pandas as pd

from loguru import logger

from ebm.model.database_manager import DatabaseManager
from ebm.model.heating_systems import HeatingSystems
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory, RESIDENTIAL, NON_RESIDENTIAL

BUILDING_CATEGORY = 'building_category'
TEK = 'TEK'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
TEK_SHARES = 'TEK_shares'

class HeatingSystemsProjection:

    def __init__(self,
                 shares_start_year: pd.DataFrame,
                 efficiencies: pd.DataFrame,
                 projection: pd.DataFrame,
                 tek_list: typing.List[str],
                 period: YearRange):
        
        self.shares_start_year = shares_start_year
        self.efficiencies = efficiencies
        self.projection = projection
        self.tek_list = tek_list
        self.period = period
        
        self._validate_years()
        check_sum_of_shares(shares_start_year)

    def _validate_years(self):
        """
        Ensures that the years in the dataframes provided during initialization 
        align with the specified period.

        This method performs the following validations:
        1. Confirms that `shares_start_year` has exactly one unique start year.
        2. Checks that the minimum year in `projection` for each combination of 
        `BUILDING_CATEGORY` and `TEK` matches the expected start year + 1.
        3. Verifies that all years in the given `period` are present in the 
        `projection` dataframe for each unique combination of 
        `BUILDING_CATEGORY` and `TEK`.

        Raises
        -------
        ValueError 
            If any of the above validations fail.
        """
        start_year = self.shares_start_year[YEAR].unique()
        if len(start_year) != 1:
            raise ValueError(f"More than one start year in dataframe.")
        start_year = start_year[0]

        if start_year != self.period.start:
            raise ValueError(f"Start year in dataframe doesn't match start year for given period.")
        
        projection = self.projection.melt(id_vars = [BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS],
                                          var_name = YEAR, value_name = "Andel_utskiftning")
        projection[YEAR] = projection[YEAR].astype(int) 
        min_df = projection.groupby([BUILDING_CATEGORY, TEK]).agg(min_year=(YEAR, 'min')).reset_index()
        min_mismatch = min_df[min_df['min_year'] != (start_year + 1)]

        if not min_mismatch.empty:
            raise ValueError("Years don't match between dataframes.")
        
        projection_period = self.period.subset(1).range()

        def check_years(group):
            return set(projection_period).issubset(group[YEAR])
        
        period_match = projection.groupby(by=[BUILDING_CATEGORY, TEK]).apply(check_years).reset_index()
        if not period_match[period_match[0] == False].empty:
            raise ValueError("Years in dataframe not present in given period.")

    def calculate_projection(self):
        """
        Project heating system shares across model years. 

        Returns:
        --------
        pd.Dataframe
            TEK shares for heating systems per year, along with different load shares and efficiencies. 

        Raises:
        -------
        ValueError
            If sum of shares for a TEK is not equal to 1.    
        """
        shares_all_heating_systems = add_missing_heating_systems(self.shares_start_year, 
                                                                 HeatingSystems,
                                                                 self.period.start) 
        projected_shares = expand_building_category_tek(self.projection, self.tek_list)
        new_shares = project_heating_systems(shares_all_heating_systems, projected_shares, self.period)
        heating_systems_projection = add_existing_tek_shares_to_projection(new_shares, 
                                                                           self.shares_start_year, 
                                                                           self.period)
        check_sum_of_shares(heating_systems_projection) 
        heating_systems_projection = add_load_shares_and_efficiencies(heating_systems_projection, self.efficiencies)
        return heating_systems_projection
    
    @staticmethod
    def new_instance(period: YearRange,
                     database_manager: DatabaseManager = None) -> 'HeatingSystemsProjection':
        """
        Creates a new instance of the HeatingSystemsProjection class, using the specified YearRange Period and
        an optional database manager.

        If a database manager is not provided, a new DatabaseManager instance will be created.

        Parameters
        ----------
        period: YearRange
        database_manager: DatabaseManager

        Returns 
        -------
        HeatingSystemsProjection
            A new instance of HeatingSystemsProjection initialized with data from the specified
            database manager.
        """
        dm = database_manager if isinstance(database_manager, DatabaseManager) else DatabaseManager()
        shares_start_year = dm.get_heating_systems_shares_start_year()
        efficiencies = dm.get_heating_systems_efficiencies()
        projection = dm.get_heating_systems_projection()
        tek_list = dm.get_tek_list()
        return HeatingSystemsProjection(shares_start_year=shares_start_year,
                                        efficiencies=efficiencies,
                                        projection=projection,
                                        tek_list=tek_list,
                                        period=period)


def add_missing_heating_systems(heating_systems_shares: pd.DataFrame, 
                                heating_systems: HeatingSystems = None,
                                start_year: int = None) -> pd.DataFrame:
    """
    Add missing HeatingSystems per BuildingCategory and TEK with a default TEK_share of 0. 
    """
    df_aggregert_0 = heating_systems_shares.copy()
    input_start_year = df_aggregert_0[YEAR].unique()
    if len(input_start_year) != 1:
        raise ValueError(f"More than one start year in dataframe")
    
    # TODO: drop start year as input param and only use year in dataframe?
    if not start_year:
        start_year =  input_start_year[0]
    elif start_year != input_start_year:
        raise ValueError(f"Given start_year doesn't match year in dataframe.")
    
    if not heating_systems:
        heating_systems = HeatingSystems
    oppvarmingstyper = pd.DataFrame(
        {HEATING_SYSTEMS: [hs for hs in heating_systems]}
    )

    df_aggregert_0_kombinasjoner = df_aggregert_0[[BUILDING_CATEGORY, TEK]].drop_duplicates()
    df_aggregert_0_alle_oppvarmingstyper = df_aggregert_0_kombinasjoner.merge((oppvarmingstyper), how = 'cross')

    df_aggregert_merged = df_aggregert_0_alle_oppvarmingstyper.merge(df_aggregert_0, 
                                                                    on = [BUILDING_CATEGORY, TEK, HEATING_SYSTEMS],
                                                                    how = 'left')
    #TODO: Kan droppe kopi av df og heller ta fillna() for de to kolonnene 
    manglende_rader = df_aggregert_merged[df_aggregert_merged[TEK_SHARES].isna()].copy()
    manglende_rader[YEAR] = start_year
    manglende_rader[TEK_SHARES] = 0
    manglende_rader = manglende_rader[[BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, YEAR, TEK_SHARES]]

    df_aggregert_alle_kombinasjoner = pd.concat([df_aggregert_0, manglende_rader])
    
    return df_aggregert_alle_kombinasjoner


def add_load_shares_and_efficiencies(df: pd.DataFrame, 
                                      heating_systems_efficiencies: pd.DataFrame) -> pd.DataFrame:
    df_hoved_spiss_og_ekstralast = heating_systems_efficiencies.copy()
    df_oppvarmingsteknologier_andeler = df.merge(df_hoved_spiss_og_ekstralast, on = [HEATING_SYSTEMS], 
                                                 how ='left')
    df_oppvarmingsteknologier_andeler[YEAR] = df_oppvarmingsteknologier_andeler[YEAR].astype(int) 
    return df_oppvarmingsteknologier_andeler


def aggregere_lik_oppvarming_fjern_0(df):
    df_fjern_null = df.query(f"{TEK_SHARES} != 0").copy()
    df_aggregert = df_fjern_null.groupby([BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, YEAR], 
                                         as_index = False)[TEK_SHARES].sum()
    return df_aggregert


def expand_building_category_tek(heating_systems_forecast: pd.DataFrame,
                                 tek_list: typing.List[str]) -> pd.DataFrame:
    """
    Adds necessary building categories and TEK's to the heating_systems_forecast dataframe. 
    """
    alle_bygningskategorier = '+'.join(BuildingCategory)
    alle_tek = '+'.join(tek for tek in tek_list)
    husholdning = '+'.join(bc for bc in BuildingCategory if bc.is_residential())
    yrkesbygg = '+'.join(bc for bc in BuildingCategory if bc.is_non_residential())
    
    df = heating_systems_forecast.copy()
    df.loc[df[TEK] == "default", TEK] = alle_tek
    df.loc[df[BUILDING_CATEGORY] == "default", BUILDING_CATEGORY] = alle_bygningskategorier
    df.loc[df[BUILDING_CATEGORY] == RESIDENTIAL, BUILDING_CATEGORY] = husholdning
    df.loc[df[BUILDING_CATEGORY] == NON_RESIDENTIAL, BUILDING_CATEGORY] = yrkesbygg

    df = df.assign(**{BUILDING_CATEGORY: df[BUILDING_CATEGORY].str.split('+')}).explode(BUILDING_CATEGORY)
    df2 = df.assign(**{TEK: df[TEK].str.split('+')}).explode(TEK)
    df2 = df2.reset_index(drop = True)
    return df2


def project_heating_systems(shares_start_year_all_systems: pd.DataFrame, 
                            projected_shares: pd.DataFrame,
                            period: YearRange) -> pd.DataFrame:
    df = shares_start_year_all_systems.copy()
    inputfil_oppvarming = projected_shares.copy()

    df_framskrive_oppvarming_long = inputfil_oppvarming.melt(id_vars = [BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS],
                                                            var_name = YEAR, value_name = "Andel_utskiftning")
    df_framskrive_oppvarming_long = df_framskrive_oppvarming_long[df_framskrive_oppvarming_long[YEAR].isin(period.subset(1).range())]

    liste_eksisterende_oppvarming = list(df_framskrive_oppvarming_long[HEATING_SYSTEMS].unique())
    liste_ny_oppvarming = list(df_framskrive_oppvarming_long[NEW_HEATING_SYSTEMS].unique())

    oppvarming_og_TEK = df.query(f"{HEATING_SYSTEMS} == {liste_eksisterende_oppvarming}")[[BUILDING_CATEGORY,TEK, HEATING_SYSTEMS, YEAR, TEK_SHARES]].copy()
    oppvarming_og_TEK_foer_endring = df.query(f"{HEATING_SYSTEMS} == {liste_ny_oppvarming}")[[BUILDING_CATEGORY,TEK,HEATING_SYSTEMS, TEK_SHARES]].copy()

    df_merge = oppvarming_og_TEK.merge(df_framskrive_oppvarming_long, on = [BUILDING_CATEGORY,TEK,HEATING_SYSTEMS], how = 'inner')
    df_merge['Ny_andel'] = (df_merge[TEK_SHARES]*
                            df_merge['Andel_utskiftning'])

    df_ny_andel_sum = df_merge.groupby([BUILDING_CATEGORY, TEK,HEATING_SYSTEMS, f'{YEAR}_y'], as_index = False)[['Ny_andel']].sum()
    df_ny_andel_sum = df_ny_andel_sum.rename(columns = {"Ny_andel": "Sum_ny_andel"})

    df_merge_sum_ny_andel = pd.merge(df_merge, df_ny_andel_sum, on = [BUILDING_CATEGORY,TEK,HEATING_SYSTEMS, f'{YEAR}_y'])

    df_merge_sum_ny_andel['Eksisterende_andel'] = ((df_merge_sum_ny_andel[TEK_SHARES] -
                                                    df_merge_sum_ny_andel['Sum_ny_andel']))

    kolonner_eksisterende = [f'{YEAR}_y', BUILDING_CATEGORY, TEK, 'Eksisterende_andel', HEATING_SYSTEMS]
    navn_eksisterende_kolonner = {"Eksisterende_andel" : TEK_SHARES,
                                    NEW_HEATING_SYSTEMS : HEATING_SYSTEMS, 
                                    f'{YEAR}_y' : YEAR}


    kolonner_nye = [f'{YEAR}_y', BUILDING_CATEGORY, TEK, 'Ny_andel', NEW_HEATING_SYSTEMS]
    navn_nye_kolonner = {"Ny_andel" : TEK_SHARES, 
                        NEW_HEATING_SYSTEMS : HEATING_SYSTEMS, 
                        f'{YEAR}_y' : YEAR}

    rekkefolge_kolonner = [YEAR, BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, TEK_SHARES]

    nye_andeler_eksisterende = df_merge_sum_ny_andel[kolonner_eksisterende].rename(columns = navn_eksisterende_kolonner)
    
    nye_andeler_nye = df_merge_sum_ny_andel[kolonner_nye].rename(columns = navn_nye_kolonner)
    nye_andeler_nye = aggregere_lik_oppvarming_fjern_0(nye_andeler_nye)

    nye_andeler_pluss_eksisterende = nye_andeler_nye.merge(oppvarming_og_TEK_foer_endring, on = [BUILDING_CATEGORY,TEK,HEATING_SYSTEMS], how = 'inner')
    nye_andeler_pluss_eksisterende[TEK_SHARES] = nye_andeler_pluss_eksisterende[f'{TEK_SHARES}_x'] + nye_andeler_pluss_eksisterende[f'{TEK_SHARES}_y']
    nye_andeler_pluss_eksisterende = nye_andeler_pluss_eksisterende.drop(columns = [f'{TEK_SHARES}_x', f'{TEK_SHARES}_y'])

    nye_andeler_samlet = pd.concat([nye_andeler_eksisterende, nye_andeler_pluss_eksisterende])
    nye_andeler_drop_dupe = nye_andeler_samlet.drop_duplicates(subset = [YEAR, BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, TEK_SHARES], keep = 'first')
    nye_andeler_samlet_uten_0 = aggregere_lik_oppvarming_fjern_0(nye_andeler_drop_dupe)
    nye_andeler_samlet_uten_0 = nye_andeler_samlet_uten_0[rekkefolge_kolonner]

    #TODO: check dtype changes in function
    nye_andeler_samlet_uten_0[YEAR] = nye_andeler_samlet_uten_0[YEAR].astype(int) 

    return nye_andeler_samlet_uten_0


def check_sum_of_shares(projected_shares: pd.DataFrame, precision: int = 5):
    """
    Control that the sum of TEK_shares equals 1 per TEK, building category and year. 

    Parameters
    ----------
    projected_shares: pd.Dataframe
        Dataframe must contain columns: 'building_category', 'TEK', 'year' and 'TEK_shares'

    Raises
    ------
    ValueError
        If sum of shares for a TEK is not equal to 1.  
    """
    df = projected_shares.copy()
    df = df.groupby(by=[BUILDING_CATEGORY, TEK, YEAR])[['TEK_shares']].sum()
    df['check'] = round(df[TEK_SHARES] * 100, precision) == 100.0
    invalid_shares = df[df['check'] == False].copy()
    invalid_shares.drop(columns=['check'], inplace=True)
    if len(invalid_shares) > 0:
        n = len(invalid_shares)
        logger.error(f"Sum of TEK shares not equal to 1 for:")
        for idx, row in invalid_shares.iterrows():
            logger.error(f"{idx}: {row.to_dict()}")
        raise ValueError(f"Sum of shares for {n} number of TEK's is not equal to 1.")


def add_existing_tek_shares_to_projection(new_shares: pd.DataFrame,
                                          existing_shares: pd.DataFrame,
                                          period: YearRange) -> pd.DataFrame:
    """
    Keeps the TEK_share of a heating system constant for all years in the projection period, if the heating system have
    an existing TEK share that have not been projected.    
    """
    df_nye_andeler_kopi = new_shares.copy()

    def sortering_oppvarmingstyper(df):
        df_kombinasjoner = df.copy()
        df_kombinasjoner['Sortering'] = df_kombinasjoner[BUILDING_CATEGORY] + df_kombinasjoner[TEK] + df_kombinasjoner[HEATING_SYSTEMS]
        kombinasjonsliste = list(df_kombinasjoner['Sortering'].unique())
        
        return df_kombinasjoner, kombinasjonsliste

    new_shares, alle_nye_kombinasjonsliste = sortering_oppvarmingstyper(new_shares)
    existing_shares, eksisterende_kombinasjonsliste = sortering_oppvarmingstyper(existing_shares)
    df_eksisterende_filtrert = existing_shares.query(f"Sortering != {alle_nye_kombinasjonsliste}")
    df_eksisterende_filtrert = df_eksisterende_filtrert.drop(columns = ['Sortering'])

    # TODO: set lower limit to period equal to last year (max) present in forecast data? 
    projection_period = YearRange(period.start + 1, period.end).year_range
    utvidede_aar_uendret = pd.concat([
        df_eksisterende_filtrert.assign(**{YEAR:year}) for year in projection_period
    ])

    samlede_nye_andeler = pd.concat([utvidede_aar_uendret, df_nye_andeler_kopi, 
                                     existing_shares], ignore_index = True)
    samlede_nye_andeler = samlede_nye_andeler.drop(columns = ['Sortering'])
    return samlede_nye_andeler


    