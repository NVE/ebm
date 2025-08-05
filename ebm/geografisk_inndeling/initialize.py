"""Module for setting up input, output and managing default data"""
import os
import argparse
from pathlib import Path
from loguru import logger
from typing import Union

class NameHandler:
    """
    Handles column names
    """
    COLUMN_NAME_BOLIG = "bolig"
    COLUMN_NAME_FRITIDSBOLIG = "Fritidsboliger"
    COLUMN_NAME_YRKESBYGG = "yrkesbygg"
    
    @classmethod
    def normalize_category(cls, value: str) -> Union[str, list[str]]:
        """
        Normalizes the category input to a standard format.
        """
        value = value.strip().lower()
        mapping = {
            "bolig": cls.COLUMN_NAME_BOLIG,
            "boliger": cls.COLUMN_NAME_BOLIG,
            "fritid": cls.COLUMN_NAME_FRITIDSBOLIG,
            "fritidsbolig": cls.COLUMN_NAME_FRITIDSBOLIG,
            "fritidsboliger": cls.COLUMN_NAME_FRITIDSBOLIG,
            "yrkesbygg": cls.COLUMN_NAME_YRKESBYGG,
            "yrke": cls.COLUMN_NAME_YRKESBYGG,
            "alle": [cls.COLUMN_NAME_BOLIG, cls.COLUMN_NAME_FRITIDSBOLIG, cls.COLUMN_NAME_YRKESBYGG]
        }
        
        if value in mapping:
            return mapping[value]
        else:
            raise argparse.ArgumentTypeError(
                f"Ugyldig kategori: '{value}'. Gyldige verdier er: boliger, fritidsboliger, yrkesbygg, alle"
            )
    
    @classmethod
    def normalize_to_list(cls, value: Union[str, list[str]]) -> list[str]:
        """
        Always returns a list of normalized categories,
        even if input is a single string or a list of strings.
        """
        if isinstance(value, list):
            result = []
            for v in value:
                normalized = cls.normalize_category(v)
                result.append(normalized)
            return list(result)
        else:
            normalized = cls.normalize_category(value)
            return normalized if isinstance(normalized, list) else [normalized]


def make_arguments(program_name: str, default_path: Path) -> argparse.Namespace:

    arg_parser = argparse.ArgumentParser(prog=program_name,
                                         description="Energibruksmodell - Geographical distribution of energy use",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument('--debug', action='store_true',
                            help='Run in debug mode. (Extra information written to stdout)')
    
    arg_parser.add_argument('--input', '-i', type=Path, default=default_path.parent,
                            help='Path to the input directory containing required files.')
    
    arg_parser.add_argument('--category', '-c', 
        type=NameHandler.normalize_to_list,
        nargs='?',
        default=NameHandler.normalize_to_list("alle"),
        help="Velg bygningskategori: boliger, fritidsboliger, yrkesbygg eller alle"
    )

    arg_parser.add_argument(
        "--years", "-y",
        type=int,
        nargs="+",
        metavar="ÅR",
        help="Årene som skal inkluderes i beregningen av fordelingsnøklene, f.eks: --years 2022 2023 2024"
    )

    arg_parser.add_argument('--source','-s', choices=['azure', 'lokalt'], default='lokalt',
                            help='''
Velg datakilde: 'azure' for å hente dataen direkte fra Elhub datasjøen, eller 'local' for å bruke parquet filen
    som følger med, (standard: local)
                            ''')
    
    arg_parser.add_argument('--create-input', action='store_true',
                            help='''
                            Create input directory and copy necessary data files from data/ directory.
                            ''')
    
    arg_parser.add_argument('--long-format', action='store_true', help='''Use long format for output data. Default is wide format.''')

    arg_parser.add_argument('--energy-type', '-e',
                            choices=['strom', 'fjernvarme'],
                             default='strom',
                             help='''
                             Velg energitype: 'strom' for elektrisitet, 'fjernvarme' for fjernvarme, eller 'alle' for begge typer. (standard: strom)
                            ''')

    arguments = arg_parser.parse_args()
    return arguments
    

def get_project_root(root_name: str = "Energibruksmodell") -> Path:
    """
    Finds the nearest parent folder matching `root_name` from this script's location.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name.lower() == root_name.lower():
            return parent
    raise FileNotFoundError(f"Could not find project root named '{root_name}' starting from {current}")



def get_output_file(relative_path: str, root_folder: str = "Energibruksmodell") -> Path:
    """
    Builds an output path relative to the detected project root.
    """
    if not relative_path:
        raise ValueError("Relative path must be provided.")
    return get_project_root(root_folder) / relative_path



def create_output_directory(filename: Path = None) -> Path:
    """
    Ensures the output directory for the given file exists.
    """
    if filename:
        output_dir = filename.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    raise ValueError("Filename must be provided to determine output directory.")


def create_input_folder():
    input_dir = Path("input")
    data_dir = Path("data")
    parquet_file = data_dir / "yearly_aggregated_elhub_data.parquet"
    destination_file = input_dir / "yearly_aggregated_elhub_data.parquet"

    # Create input/ folder if it doesn't exist
    input_dir.mkdir(parents=True, exist_ok=True)

    # Copy .parquet file from data/ to input/
    if parquet_file.exists():
        shutil.copy(parquet_file, destination_file)
        logger.info(f"✅ Fil kopiert: {parquet_file} → {destination_file}")
    else:
        logger.error(f"❌ Filen {parquet_file} finnes ikke.")
        raise FileNotFoundError(f"{parquet_file} finnes ikke.")
