from pathlib import Path


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
