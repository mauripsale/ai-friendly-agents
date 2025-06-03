from pathlib import Path
from typing import List

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

