from pathlib import Path
from typing import List
import pathlib


def find_files(folder: Path, extensions: List[str]) -> List[Path]:
    """Finds files with given extensions in a folder and its subfolders.

    Performs a recursive search within the specified folder for files ending with any
    of the provided extensions. Returns a sorted list of unique file paths.

    Args:
        folder: The path to the directory to search within.
        extensions: A list of file extensions (e.g., ['.txt', '.md']) to search for.

    Returns:
        A sorted list of unique Path objects representing the found files.

    Example:
        >>> find_files(Path("etc/data/sample_docs"), [".txt", ".md"])
        [Path('etc/data/sample_docs/doc1.txt'), Path('etc/data/sample_docs/doc2.md')]
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
