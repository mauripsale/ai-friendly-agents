from pathlib import Path
from typing import List
import pathlib


def find_files(folder: Path, extensions: List[str]) -> List[Path]:
    """
    Finds files with given extensions in a folder and its subfolders.
    Returns a sorted list of unique file paths.
    """
    found_files: List[Path] = []
    for ext in extensions:
        # Using rglob for recursive search
        found_files.extend(list(folder.rglob(f"*{ext}")))

    # Sort and unique for deterministic behavior
    return sorted(list(set(found_files)))


# # NOT CALLED BY ANYONE
# def enumerate_data_sources(folder_path_str: str) -> list[str]:
#     """Enumerate the data sources in the local corpus.
#     Basically, list the subfolders of given folder_path.

#     Arguments:
#         folder_path_str: the path to the folder containing the data sources (STRING). Defaults to "etc/data/".
#     Returns:
#         A list of STRING data sources (subfolders) in the given folder_path.
#     """
#     folder_path = pathlib.Path(folder_path_str)
#     if not folder_path.is_dir():
#         return []

#     subfolders = [p.name for p in folder_path.iterdir() if p.is_dir()]
#     print(subfolders)
#     return sorted(subfolders)
