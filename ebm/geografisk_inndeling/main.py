import os
from ebm.geografisk_inndeling.geographical_distribution import geographical_distribution
import gc
import polars as pl
from loguru import logger



def get_user_input() -> tuple[str, list[int]]:
    print("\n🧱 Velg bygningskategori:")
    print("1. Boliger")
    print("2. Fritidsboliger")
    print("3. Yrkesbygg")
    print("4. Alle kategorier")
    
    category_choice = input("Skriv inn tallet for ønsket kategori (1–4): ").strip()
    
    category_map = {
        "1": "boliger",
        "2": "fritidsboliger",
        "3": "yrkesbygg",
        "4": "alle"  
    }

    building_category = category_map.get(category_choice)
    if building_category is None:
        raise ValueError("Ugyldig valg av kategori.")

    # Ask for years to include
    years_input = input("Hvilke år vil du inkludere?  (2022-2024): ")
    try:
        years = [int(y.strip()) for y in years_input.split(",")]
    except ValueError:
        raise ValueError("Årene må være kommaseparerte heltall.")

    return building_category, years


def main():
    print("📊 Geografisk fordeling av EBM fremskriving\n")
    
    building_category, elhub_years = get_user_input()

    logger.info(f"\n🔍 Lager kommunefordelingsfaktorer for bygningskategori '{building_category}' fra Elhub data i tidsperioden: {elhub_years} ...")

    file_to_open = geographical_distribution(elhub_years, step="alle")

    logger.info("✅ Kommunefordelingsnøkler er generert og lagret i output-mappen med filnavn: kommunefordelingsnøkler.xlsx.")
    os.startfile(file_to_open, 'open')

    # Clean up memory
    gc.collect()


if __name__ == "__main__":
    main()
