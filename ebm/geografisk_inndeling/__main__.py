"Geographical distribution (GD) starts from where when running as a script or module"
import os
from pathlib import Path
from ebm.geografisk_inndeling.geographical_distribution import geographical_distribution
from ebm.geografisk_inndeling.initialize import make_arguments, create_input_folder
import gc
from loguru import logger


def main():
    
    program_name = 'ebm-geografisk-inndeling (GD)'
    default_path = Path('output/kommunefordelingsnøkler.xlsx')

    arguments = make_arguments(program_name, default_path)

    if arguments.create_input:
        logger.info("📁 Oppretter input-mappe og kopierer data...")
        create_input_folder()

    # Choose source
    if arguments.source == "azure":
        logger.info("☁️ Henter Elhub-data direkte fra Azure-datasjøen. Dette forutsetter at du har tilgang via «az login».")
        step = 'azure'
    else:
        logger.info("📂 Leser data lokalt fra data-mappen...")
        step = 'local'
        

    building_category_choice = arguments.category
    elhub_years = arguments.years

    convert_result_to_long: bool = arguments.long_format


    logger.info(
        f"\n🔍 Lager kommunefordelingsfaktorer for bygningskategori '{building_category_choice}' "
        f"fra Elhub data i tidsperioden: {elhub_years} ..."
    )

    file_to_open = geographical_distribution(elhub_years, building_category=building_category_choice, step=step, output_format = convert_result_to_long)

    logger.info(f"✅ Kommunefordelingsnøkler er generert og lagret i output-mappen med filnavn: {file_to_open.name}")
    os.startfile(file_to_open, 'open')

    # Clean up memory
    gc.collect()


if __name__ == "__main__":
    main()
