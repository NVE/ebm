from pathlib import Path

def make_unique_path(path):
    path = Path(path)
    counter = 1
    new_path = path

    while new_path.exists():
        new_path = path.with_stem(f"{path.stem}_{counter}")
        counter += 1

    return new_path