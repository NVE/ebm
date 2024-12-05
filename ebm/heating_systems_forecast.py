import pandas as pd

def legge_til_alle_oppvarmingstyper(heating_systems_shares, heating_systems_efficiencies):
    df_aggregert_0 = heating_systems_shares.copy()
    oppvarmingstyper = heating_systems_efficiencies[["Oppvarmingstyper"]].copy()

    df_aggregert_0_kombinasjoner = df_aggregert_0[['Bygningskategori', 'TEK']].drop_duplicates()
    df_aggregert_0_alle_oppvarmingstyper = df_aggregert_0_kombinasjoner.merge((oppvarmingstyper), how = 'cross')

    df_aggregert_merged = df_aggregert_0_alle_oppvarmingstyper.merge(df_aggregert_0, 
                                                                    on = ['Bygningskategori', 'TEK', 'Oppvarmingstyper'],
                                                                    how = 'left')
    manglende_rader = df_aggregert_merged[df_aggregert_merged['TEK_andeler'].isna()].copy()
    manglende_rader['Year'] = 2020
    manglende_rader['TEK_andeler'] = 0
    manglende_rader = manglende_rader[['Bygningskategori', 'TEK', 'Oppvarmingstyper', 'Year', 'TEK_andeler']]

    df_aggregert_alle_kombinasjoner = pd.concat([df_aggregert_0, manglende_rader])
    
    return df_aggregert_alle_kombinasjoner

def legge_til_ulike_oppvarmingslaster(df, heating_systems_efficiencies):
    df_hoved_spiss_og_ekstralast = heating_systems_efficiencies.copy()
    df_oppvarmingsteknologier_andeler = df.merge(df_hoved_spiss_og_ekstralast, on = ['Oppvarmingstyper'], 
                                                 how ='left')
    return df_oppvarmingsteknologier_andeler

def aggregere_lik_oppvarming_fjern_0(df):
    df_fjern_null = df.query("TEK_andeler != 0").copy()
    df_aggregert = df_fjern_null.groupby(["Bygningskategori", "TEK", "Oppvarmingstyper", "Year"], 
                                         as_index = False)['TEK_andeler'].sum()
    return df_aggregert

def ekspandere_input_oppvarming(heating_systems_forecast):
    alle_bygningskategorier = "House+Apartment block+Kindergarten+Office+Retail+Hotel+Sports+University+School+Nursinghome+Hospital+Storage repairs+Culture"
    alle_tek = "pre_TEK49+TEK49+TEK69+TEK87+TEK97+TEK07+TEK10+TEK17"
    husholdning = "House+Apartment block"
    yrkesbygg = "Kindergarten+Office+Retail+Hotel+Sports+University+School+Nursinghome+Hospital+Storage repairs+Culture"
    
    df = heating_systems_forecast.copy()
    df.loc[df['TEK'] == "default", 'TEK'] = alle_tek
    df.loc[df['Bygningskategori'] == "default", 'Bygningskategori'] = alle_bygningskategorier
    df.loc[df['Bygningskategori'] == "Household", 'Bygningskategori'] = husholdning
    df.loc[df['Bygningskategori'] == "Non-residential", 'Bygningskategori'] = yrkesbygg

    df = df.assign(Bygningskategori = df['Bygningskategori'].str.split('+')).explode('Bygningskategori')
    df2 = df.assign(TEK = df['TEK'].str.split('+')).explode('TEK')
    df2 = df2.reset_index(drop = True)
    return df2

def framskrive_oppvarming(df, inputfil):
    inputfil_oppvarming = inputfil

    df_framskrive_oppvarming_long = inputfil_oppvarming.melt(id_vars = ["Bygningskategori", "TEK", "Oppvarmingstyper", "Nye_oppvarmingstyper"],
                                                                var_name = "Year", value_name = "Andel_utskiftning")
    liste_eksisterende_oppvarming = list(df_framskrive_oppvarming_long['Oppvarmingstyper'].unique())
    liste_ny_oppvarming = list(df_framskrive_oppvarming_long['Nye_oppvarmingstyper'].unique())

    oppvarming_og_TEK = df.query(f"Oppvarmingstyper == {liste_eksisterende_oppvarming}")[['Bygningskategori','TEK', 'Oppvarmingstyper', 'Year', 'TEK_andeler']].copy()
    oppvarming_og_TEK_foer_endring = df.query(f"Oppvarmingstyper == {liste_ny_oppvarming}")[['Bygningskategori','TEK','Oppvarmingstyper', 'TEK_andeler']].copy()

    df_merge = oppvarming_og_TEK.merge(df_framskrive_oppvarming_long, on = ['Bygningskategori','TEK','Oppvarmingstyper'], how = 'inner')
    df_merge['Ny_andel'] = (df_merge['TEK_andeler']*
                            df_merge['Andel_utskiftning'])

    df_ny_andel_sum = df_merge.groupby(['Bygningskategori', 'TEK','Oppvarmingstyper', 'Year_y'], as_index = False)[['Ny_andel']].sum()
    df_ny_andel_sum = df_ny_andel_sum.rename(columns = {"Ny_andel": "Sum_ny_andel"})

    df_merge_sum_ny_andel = pd.merge(df_merge, df_ny_andel_sum, on = ['Bygningskategori','TEK','Oppvarmingstyper', 'Year_y'])

    df_merge_sum_ny_andel['Eksisterende_andel'] = ((df_merge_sum_ny_andel['TEK_andeler'] -
                                                    df_merge_sum_ny_andel['Sum_ny_andel']))

    kolonner_eksisterende = ['Year_y', 'Bygningskategori', 'TEK', 'Eksisterende_andel', 'Oppvarmingstyper']
    navn_eksisterende_kolonner = {"Eksisterende_andel" : "TEK_andeler",
                                    "Nye_oppvarmingstyper" : "Oppvarmingstyper", 
                                    "Year_y" : "Year"}


    kolonner_nye = ['Year_y', 'Bygningskategori', 'TEK', 'Ny_andel', 'Nye_oppvarmingstyper']
    navn_nye_kolonner = {"Ny_andel" : "TEK_andeler", 
                        "Nye_oppvarmingstyper" : "Oppvarmingstyper", 
                        "Year_y" : "Year"}

    rekkefolge_kolonner = ['Year', 'Bygningskategori', 'TEK', 'Oppvarmingstyper', 'TEK_andeler']

    nye_andeler_eksisterende = df_merge_sum_ny_andel[kolonner_eksisterende].rename(columns = navn_eksisterende_kolonner)
    
    nye_andeler_nye = df_merge_sum_ny_andel[kolonner_nye].rename(columns = navn_nye_kolonner)
    nye_andeler_nye = aggregere_lik_oppvarming_fjern_0(nye_andeler_nye)

    nye_andeler_pluss_eksisterende = nye_andeler_nye.merge(oppvarming_og_TEK_foer_endring, on = ['Bygningskategori','TEK','Oppvarmingstyper'], how = 'inner')
    nye_andeler_pluss_eksisterende['TEK_andeler'] = nye_andeler_pluss_eksisterende['TEK_andeler_x'] + nye_andeler_pluss_eksisterende['TEK_andeler_y']
    nye_andeler_pluss_eksisterende = nye_andeler_pluss_eksisterende.drop(columns = ['TEK_andeler_x', 'TEK_andeler_y'])

    nye_andeler_samlet = pd.concat([nye_andeler_eksisterende, nye_andeler_pluss_eksisterende])
    nye_andeler_drop_dupe = nye_andeler_samlet.drop_duplicates(subset = ['Year', 'Bygningskategori', 'TEK', 'Oppvarmingstyper', 'TEK_andeler'], keep = 'first')
    nye_andeler_samlet_uten_0 = aggregere_lik_oppvarming_fjern_0(nye_andeler_drop_dupe)
    nye_andeler_samlet_uten_0 = nye_andeler_samlet_uten_0[rekkefolge_kolonner]

    return nye_andeler_samlet_uten_0

def legge_til_resterende_aar_oppvarming(df_nye_andeler, df_eksisterende):
    df_nye_andeler_kopi = df_nye_andeler.copy()

    def sortering_oppvarmingstyper(df):
        df_kombinasjoner = df.copy()
        df_kombinasjoner['Sortering'] = df_kombinasjoner['Bygningskategori'] + df_kombinasjoner['TEK'] + df_kombinasjoner['Oppvarmingstyper']
        kombinasjonsliste = list(df_kombinasjoner['Sortering'].unique())
        
        return df_kombinasjoner, kombinasjonsliste

    df_nye_andeler, alle_nye_kombinasjonsliste = sortering_oppvarmingstyper(df_nye_andeler)
    df_eksisterende, eksisterende_kombinasjonsliste = sortering_oppvarmingstyper(df_eksisterende)
    df_eksisterende_filtrert = df_eksisterende.query(f"Sortering != {alle_nye_kombinasjonsliste}")
    df_eksisterende_filtrert = df_eksisterende_filtrert.drop(columns = ['Sortering'])

    year_2021_2050 = list(range(2021, 2051))
    utvidede_aar_uendret = pd.concat([
        df_eksisterende_filtrert.assign(Year=year) for year in year_2021_2050
    ])

    samlede_nye_andeler = pd.concat([utvidede_aar_uendret, df_nye_andeler_kopi, 
                                     df_eksisterende], ignore_index = True)
    samlede_nye_andeler = samlede_nye_andeler.drop(columns = ['Sortering'])
    return samlede_nye_andeler

def main(heating_systems_shares,
         heating_systems_efficiencies,
         heating_systems_forecast):
    
    # Legger til 0 på oppvarmingstyper som ikke eksisterer enda.
    df_aggregert_alle_kombinasjoner = legge_til_alle_oppvarmingstyper(heating_systems_shares, 
                                                                      heating_systems_efficiencies)

    # Gjør klar inputfilen for oppvarmingsandelene som skal framskrives.
    inputfil_oppvarming = ekspandere_input_oppvarming(heating_systems_forecast)

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
    