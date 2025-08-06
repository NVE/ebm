"Geographical distribution (GD) starts from where when running as a script or module"
import os
from pathlib import Path
from ebm.geografisk_inndeling.geographical_distribution import geographical_distribution
from ebm.geografisk_inndeling.initialize import NameHandler, make_arguments, create_input_folder
import gc
from loguru import logger


def main():
    
    program_name = 'ebm-geografisk-inndeling (GD)'
    default_path = Path('output/kommunefordelingsnøkler.xlsx')

    arguments = make_arguments(program_name, default_path)

    if arguments.create_input:
        logger.info("📁 Oppretter input-mappe og kopierer data...")
        create_input_folder()
    
    if arguments.energy_type == "strom":
        logger.info("⚡️ Energikilde satt til strøm.")
        energitype = "strom"
    elif arguments.energy_type == "fjernvarme":
        logger.info("🔥 Energikilde satt til fjernvarme.")
        energitype = "fjernvarme"
    else:
        logger.info("🌲 Energikilde satt til ved.")
        energitype = "ved"


    building_category_choice = arguments.category
    elhub_years = arguments.years

    # Choose source
    if arguments.source == "azure":
        logger.info("☁️ Henter Elhub-data direkte fra Azure-datasjøen. Dette forutsetter at du har tilgang via «az login».")
        step = 'azure'
    else:
        logger.info("📂 Leser data lokalt fra data-mappen...")
        step = 'lokalt'

    # Convert result to long format if specified
    convert_result_to_long: bool = arguments.long_format
    

    if energitype == "strom":
        logger.info(
            f"🔍 Kommunefordeler strøm for bygningskategori '{building_category_choice}' "
            f"fra Elhub data i tidsperioden: {elhub_years} ..."
        )
    elif energitype == "fjernvarme":
        filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_FRITIDSBOLIG.lower()]
        logger.info(
            f"🔍 Kommunefordeler fjernvarme for bygningskategori {filtered_categories}."
            )
        if not filtered_categories:
            raise ValueError(
                "Fjernvarme krever minst én bygningskategori som ikke er fritidsboliger."
            )
    elif energitype == "ved":
        filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_FRITIDSBOLIG.lower()\
                                and cat.lower() != NameHandler.COLUMN_NAME_YRKESBYGG.lower()]
        logger.info(
            f"🔍 Kommunefordeler ved for bygningskategori {filtered_categories}."
            )
        if not filtered_categories:
            raise ValueError(
                "Ved krever minst én bygningskategori som hverken er yrkesbygg eller fritidsboliger."
            )

    file_to_open = geographical_distribution(elhub_years, 
                                            energitype=energitype, 
                                            building_category=(building_category_choice if energitype == "strom" else filtered_categories),
                                            step=step, 
                                            output_format = convert_result_to_long)

    logger.info(f"✅ Kommunefordeling for valgt energitype har kjørt ferdig og resultatene er lagret i output-mappen med filnavn: {file_to_open.name}")
    os.startfile(file_to_open, 'open')

    # Clean up memory
    gc.collect()


if __name__ == "__main__":
    main()
