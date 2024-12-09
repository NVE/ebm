import pandas as pd

from ebm.model.building_category import BuildingCategory, RESIDENTIAL, NON_RESIDENTIAL

BUILDING_CATEGORY = 'building_category'
TEK = 'TEK'
HEATING_SYSTEMS = 'heating_systems'
NEW_HEATING_SYSTEMS = 'new_heating_systems'
YEAR = 'year'
TEK_SHARES = 'TEK_shares'


def add_missing_heating_systems(heating_systems_shares: pd.DataFrame, 
                                heating_systems_efficiencies: pd.DataFrame) -> pd.DataFrame:
    df_aggregert_0 = heating_systems_shares.copy()
    oppvarmingstyper = heating_systems_efficiencies[[HEATING_SYSTEMS]].copy()

    df_aggregert_0_kombinasjoner = df_aggregert_0[[BUILDING_CATEGORY, TEK]].drop_duplicates()
    df_aggregert_0_alle_oppvarmingstyper = df_aggregert_0_kombinasjoner.merge((oppvarmingstyper), how = 'cross')

    df_aggregert_merged = df_aggregert_0_alle_oppvarmingstyper.merge(df_aggregert_0, 
                                                                    on = [BUILDING_CATEGORY, TEK, HEATING_SYSTEMS],
                                                                    how = 'left')
    manglende_rader = df_aggregert_merged[df_aggregert_merged[TEK_SHARES].isna()].copy()
    manglende_rader[YEAR] = 2020
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


def framskrive_oppvarming(df: pd.DataFrame, 
                          inputfil: pd.DataFrame) -> pd.DataFrame:
    inputfil_oppvarming = inputfil

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

    return nye_andeler_samlet_uten_0


def legge_til_resterende_aar_oppvarming(df_nye_andeler: pd.DataFrame,
                                        df_eksisterende: pd.DataFrame) -> pd.DataFrame:
    df_nye_andeler_kopi = df_nye_andeler.copy()

    def sortering_oppvarmingstyper(df):
        df_kombinasjoner = df.copy()
        df_kombinasjoner['Sortering'] = df_kombinasjoner[BUILDING_CATEGORY] + df_kombinasjoner[TEK] + df_kombinasjoner[HEATING_SYSTEMS]
        kombinasjonsliste = list(df_kombinasjoner['Sortering'].unique())
        
        return df_kombinasjoner, kombinasjonsliste

    df_nye_andeler, alle_nye_kombinasjonsliste = sortering_oppvarmingstyper(df_nye_andeler)
    df_eksisterende, eksisterende_kombinasjonsliste = sortering_oppvarmingstyper(df_eksisterende)
    df_eksisterende_filtrert = df_eksisterende.query(f"Sortering != {alle_nye_kombinasjonsliste}")
    df_eksisterende_filtrert = df_eksisterende_filtrert.drop(columns = ['Sortering'])

    # TODO: add period to this function, and set lower limit to period equal to last year (max) present in forecast data? 
    year_2021_2050 = list(range(2021, 2051))
    utvidede_aar_uendret = pd.concat([
        df_eksisterende_filtrert.assign(**{YEAR:year}) for year in year_2021_2050
    ])

    samlede_nye_andeler = pd.concat([utvidede_aar_uendret, df_nye_andeler_kopi, 
                                     df_eksisterende], ignore_index = True)
    samlede_nye_andeler = samlede_nye_andeler.drop(columns = ['Sortering'])
    return samlede_nye_andeler


def main(heating_systems_shares: pd.DataFrame,
         heating_systems_efficiencies: pd.DataFrame,
         heating_systems_forecast: pd.DataFrame) -> pd.DataFrame:
    
    # Legger til 0 på oppvarmingstyper som ikke eksisterer enda.
    df_aggregert_alle_kombinasjoner = add_missing_heating_systems(heating_systems_shares, 
                                                                      heating_systems_efficiencies)

    # Gjør klar inputfilen for oppvarmingsandelene som skal framskrives.
    inputfil_oppvarming = expand_building_category_tek(heating_systems_forecast)

    # Framskriver oppvarmingsløsninger basert på andelene i input filen
    nye_andeler = framskrive_oppvarming(df_aggregert_alle_kombinasjoner, inputfil_oppvarming)

    # Legger til andeler det ikke er utført noen form for framskrivning på for 2021-2050
    df_framskrevet_oppvarming = legge_til_resterende_aar_oppvarming(nye_andeler, heating_systems_shares)

    # Legger til virkningsgrader og andeler til grunn,spiss og ekstralast og tappevann
    df_framskrevet_oppvarming_lastfordeling = legge_til_ulike_oppvarmingslaster(df_framskrevet_oppvarming, 
                                                                                heating_systems_efficiencies)

    return df_framskrevet_oppvarming_lastfordeling


#if __name__ == '__main__':
#    main()
    