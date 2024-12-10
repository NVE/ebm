import pandas as pd

from ebm.model.heating_systems import HeatingSystems
from ebm.model.data_classes import YearRange
from ebm.model.building_category import BuildingCategory, RESIDENTIAL, NON_RESIDENTIAL

BUILDING_CATEGORY = 'building_category'
TEK = 'TEK'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
TEK_SHARES = 'TEK_shares'

def add_missing_heating_systems(heating_systems_shares: pd.DataFrame, 
                                heating_systems: HeatingSystems = None,
                                start_year: int = None) -> pd.DataFrame:
    """
    Add missing HeatingSystems per BuildingCategory and TEK with a default TEK_share of 0. 
    """
    df_aggregert_0 = heating_systems_shares.copy()
    input_start_year = df_aggregert_0['year'].unique()
    if len(input_start_year) != 1:
        raise ValueError(f"More than one year in 'heating_systems_share' df")
    
    # TODO: drop start year as input param and only use year in dataframe?
    if not start_year:
        start_year =  input_start_year[0]
    elif start_year != input_start_year:
        raise ValueError(f"Given start_year doesn't match year in 'heating_systems_share' dataframe.")
    
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


def legge_til_ulike_oppvarmingslaster(df: pd.DataFrame, 
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


def expand_building_category_tek(heating_systems_forecast: pd.DataFrame) -> pd.DataFrame:
    """
    Adds necessary building categories and TEK's to the heating_systems_forecast dataframe. 
    """
    alle_bygningskategorier = '+'.join(BuildingCategory)
    alle_tek = "PRE_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17"
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
                            projected_shares: pd.DataFrame) -> pd.DataFrame:
    df = shares_start_year_all_systems.copy()
    inputfil_oppvarming = projected_shares.copy()

    df_framskrive_oppvarming_long = inputfil_oppvarming.melt(id_vars = [BUILDING_CATEGORY, TEK, HEATING_SYSTEMS, NEW_HEATING_SYSTEMS],
                                                                var_name = YEAR, value_name = "Andel_utskiftning")
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

#TODO: existing share in start year = 0 is not added, when not in existing shares (example: test_ok on this function) 
def add_existing_tek_shares_to_projection(new_shares: pd.DataFrame,
                                          existing_shares: pd.DataFrame,
                                          period: YearRange) -> pd.DataFrame:
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


def main(heating_systems_shares: pd.DataFrame,
         heating_systems_efficiencies: pd.DataFrame,
         heating_systems_forecast: pd.DataFrame,
         period: YearRange) -> pd.DataFrame:
    
    start_year = period.start
    df_aggregert_alle_kombinasjoner = add_missing_heating_systems(heating_systems_shares,
                                                                  start_year=start_year)

    # Gjør klar inputfilen for oppvarmingsandelene som skal framskrives.
    inputfil_oppvarming = expand_building_category_tek(heating_systems_forecast)

    # Framskriver oppvarmingsløsninger basert på andelene i input filen
    nye_andeler = project_heating_systems(df_aggregert_alle_kombinasjoner, inputfil_oppvarming)

    # Legger til andeler det ikke er utført noen form for framskrivning på i projection perioden
    df_framskrevet_oppvarming = add_existing_tek_shares_to_projection(nye_andeler, 
                                                                      heating_systems_shares,
                                                                      period)

    # Legger til virkningsgrader og andeler til grunn,spiss og ekstralast og tappevann
    df_framskrevet_oppvarming_lastfordeling = legge_til_ulike_oppvarmingslaster(df_framskrevet_oppvarming, 
                                                                                heating_systems_efficiencies)

    return df_framskrevet_oppvarming_lastfordeling


#if __name__ == '__main__':
#    main()
    