"Geographical distribution (GD) starts from where when running as a script or module"
import os
import sys
from pathlib import Path
from ebmgeodist.geographical_distribution import geographical_distribution
from ebmgeodist.initialize import NameHandler, make_arguments, init, create_output_directory
from ebmgeodist.file_handler import FileHandler
from ebmgeodist.enums import ReturnCode
import gc
from loguru import logger


def main():
    
    program_name = 'ebmgeodist'
    default_path = Path('output/ebm_output.xlsx')

    arguments = make_arguments(program_name, default_path)
    
    input_directory = arguments.input
    logger.info(f'Using data from "{input_directory}"')
    file_handler=FileHandler(directory=input_directory)
    
    # Create input directory if requested
    if arguments.create_input:
        if init(file_handler):
            logger.info(f'Finished creating input files in {file_handler.input_directory}')
            return ReturnCode.OK, None
        # Exit with 0 for success. The assumption is that the user would like to review the input before proceeding.
        return ReturnCode.MISSING_INPUT_FILES, None
    
    # Make sure all required files exists
    file_handler = FileHandler(directory=input_directory)
    missing_files = file_handler.check_for_missing_files()
    if missing_files:
        print(f"""
    Use {program_name} --create-input to create an input directory with default files in the current directory
    """.strip(),
              file=sys.stderr)
        return ReturnCode.MISSING_INPUT_FILES, None
    
    if arguments.energy_type == "strom":
        logger.info("⚡️ Energikilde satt til strøm.")
        energitype = "strom"
    elif arguments.energy_type == "fjernvarme":
        logger.info("🔥 Energikilde satt til fjernvarme.")
        energitype = "fjernvarme"
    elif arguments.energy_type == "ved":
        logger.info("🌲 Energikilde satt til ved.")
        energitype = "ved"
    elif arguments.energy_type == "fossil":
        logger.info("💨 Energikilde satt til fossil energi.")
        energitype = "fossil"


    building_category_choice = arguments.category
    elhub_years = arguments.years

    # Choose source
    if arguments.source == "azure":
        logger.info("☁️ Henter Elhub-data direkte fra Azure-datasjøen. Dette forutsetter at du har tilgang via «az login».")
        step = 'azure'
    else:
        logger.info("📂 Leser data lokalt fra data-mappen...")
        step = 'lokalt'

    # Only include start and end years in the output if specified
    include_start_end_years: bool = arguments.start_end_years
    

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
        filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_YRKESBYGG.lower()]
        logger.info(
            f"🔍 Kommunefordeler ved for bygningskategori {filtered_categories}."
            )
        if not filtered_categories:
            raise ValueError(
                "Ved krever minst én bygningskategori som ikke er yrkesbygg."
            )
    elif energitype == "fossil":
        filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_BOLIG.lower()\
                               and cat.lower() != NameHandler.COLUMN_NAME_YRKESBYGG.lower()]
        logger.info(
            f"🔍 Kommunefordeler fossil energi for bygningskategori {filtered_categories}."
            )
        if not filtered_categories:
            raise ValueError(
                "Fossil energi er kun tilgjengelig for bygningskategorier som ikke er boliger eller yrkesbygg."
            )

    file_to_open = geographical_distribution(elhub_years, 
                                            energitype=energitype, 
                                            building_category=(building_category_choice if energitype == "strom" else filtered_categories),
                                            step=step, 
                                            output_format = include_start_end_years)

    logger.info(f"✅ Kommunefordeling for valgt energitype har kjørt ferdig og resultatene er lagret i output-mappen med filnavn: {file_to_open.name}")
    os.startfile(file_to_open, 'open')

    # Clean up memory
    gc.collect()


if __name__ == "__main__":
    main()
