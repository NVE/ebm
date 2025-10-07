"Geographical distribution (GD) starts from where when running as a script or module"
import os
import sys
from pathlib import Path
from ebmgeodist.geographical_distribution import geographical_distribution
from ebmgeodist.initialize import NameHandler, make_arguments, init, create_output_directory
from ebmgeodist.file_handler import FileHandler
from ebmgeodist.enums import ReturnCode
from ebmgeodist.calculation_tools import NoElhubDataError
import gc
from loguru import logger

def run_ebmgeodist():
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
    
    energy_map = {
        "electricity": "⚡️",
        "dh": "🔥",
        "fuelwood": "🌲",
        "fossilfuel": "💨"
    }
    energy_products = arguments.energy_product
    if isinstance(energy_products, str):
        energy_products = [energy_products]

    for category in energy_products:
        energy_product = category.lower()  
        
        if energy_product in energy_map:
            logger.info(f"{energy_map[energy_product]} Energy product is chosen to be {energy_product}.")

        building_category_choice = arguments.building_category
        elhub_years = arguments.years

        # Choose source
        if arguments.source == "azure":
            logger.info("☁️ Loading Elhub data directly from the Azure Data Lake. This assumes you have access via 'az login'.")

            step = 'azure'
        else:
            logger.info("📂 Reading data locally from the data folder...")
            step = 'local'

        # Only include start and end years in the output if specified
        include_start_end_years: bool = arguments.start_end_years
        

        if energy_product == "electricity":
            logger.info(
                f"🔍 Municipal electricity distribution for building category '{building_category_choice}' "
                f"from Elhub data in the time period: {elhub_years} ..."
            )

        elif energy_product == "dh":
            filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_HOLIDAY_HOME.lower()]
            logger.info(
                f"🔍 Municipal district heating distribution for building category {filtered_categories}."
                )
            try:
                if not filtered_categories:
                    raise ValueError(
                        "District heating requires at least one building category that is not holiday homes."
                    )
            except ValueError as e:
                logger.warning(f"⚠️ {e} Skipping district heating calculation.")
                continue
        
        elif energy_product == "fuelwood":
            filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_NON_RESIDENTIAL.lower()]
            logger.info(
                f"🔍 Municipal fuelwood distribution for building category  {filtered_categories}."
                )
            try:
                if not filtered_categories:
                    raise ValueError(
                        "Fuelwood requires at least one building category that is not non-residential buildings."
                    )
            except ValueError as e:
                logger.warning(f"⚠️ {e} Skipping fuelwood calculation.")
                continue    
        elif energy_product == "fossilfuel":
            filtered_categories = [cat for cat in building_category_choice if cat.lower() != NameHandler.COLUMN_NAME_RESIDENTIAL.lower()\
                                and cat.lower() != NameHandler.COLUMN_NAME_NON_RESIDENTIAL.lower()]
            logger.info(
                f"🔍 Municipal fossilfuel distribution for building category {filtered_categories}."
                )
            try:
                if not filtered_categories:
                    raise ValueError(
                        "Fossilfuel requires at least one building category that is not residential or non-residential buildings."
                    )
            except ValueError as e:
                logger.warning(f"⚠️ {e} Skipping fossilfuel calculation.")
                continue

        file_to_open = geographical_distribution(elhub_years, 
                                                energy_product=energy_product, 
                                                building_category=(building_category_choice if energy_product == "electricity" else filtered_categories),
                                                step=step, 
                                                output_format = include_start_end_years)

        logger.info(f"✅ Municipal distribution for selected energy product has finished running and the results are saved in the output folder with filename: {file_to_open.name}")
        os.startfile(file_to_open, 'open')

        # Clean up memory
        gc.collect()

def main():
    try:
        run_ebmgeodist()
    except NoElhubDataError as e:
        logger.critical(f"❌ Program stopped: {e}")
        sys.exit(1)   


if __name__ == "__main__": 
    main()
