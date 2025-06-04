import pathlib
import json
from common_lib import process_docs


# TODO: for each folder add a file that summarizes the content so that AI models can decide which to pick
def enumerate_data_sources(folder_path_str: str) -> list[str]:
    """Enumerate the data sources in the local corpus.
    Basically, list the subfolders of given folder_path.

    Arguments:
        folder_path_str: the path to the folder containing the data sources (STRING). Defaults to "etc/data/".
    Returns:
        A list of STRING data sources (subfolders) in the given folder_path.
    """
    folder_path = pathlib.Path(folder_path_str)
    if not folder_path.is_dir():
        raise RuntimeError(f"{folder_path_str} is not a valid folder path.")

    return [p.name for p in folder_path.iterdir() if p.is_dir()]


# TODO: add some sort of error handling and optimize for 1M context window.
# TODO: local cache: local `.cache/buridone.md` - with some expiration heuristic (timestamp or other)
def build_document(folder_path_str: pathlib.Path) -> str:
    try:
        content = process_docs.process_documents(folder_path_str)
        return json.dumps({"status": "ok", "content": content})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
