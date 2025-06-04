import pathlib
import json
from lib import process_docs
import logging

WARNING_SIZE_BYTES = 500_000

# TODO: for each folder add a file that summarizes the content so that AI models can decide which to pick
def enumerate_data_sources(folder_path_str: str) -> list[str]:
    """Enumerate the data sources in the local corpus.

    Lists the subfolders of the given folder_path.

    Args:
        folder_path_str: The path to the folder containing the data sources.

    Returns:
        A list of strings, where each string is the name of a subfolder (data source).

    Raises:
        RuntimeError: If the provided folder_path_str is not a valid folder path.

    Example:
        >>> enumerate_data_sources("etc/data/")
        ['google-adk-v1.0', 'google-financials', 'maxime_router', 'sample_docs', 'thalwil']
    """
    folder_path = pathlib.Path(folder_path_str)
    if not folder_path.is_dir():
        raise RuntimeError(f"{folder_path_str} is not a valid folder path.")

    return [p.name for p in folder_path.iterdir() if p.is_dir()]


# TODO: add some sort of error handling and optimize for 1M context window.
# TODO: local cache: local `.cache/buridone.md` - with some expiration heuristic (timestamp or other)
def build_document(folder_path_str: pathlib.Path) -> str:
    """Builds a single document string from files in a specified folder.

    Processes documents in the given folder using `process_docs.process_documents`
    and returns the result as a JSON string indicating status, content, and content size in bytes.

    Args:
        folder_path_str: The path to the folder containing the documents.

    Returns:
        A JSON string with keys 'status' ('ok' or 'error'), 'content'
        (the aggregated document string if status is 'ok'), 'content_size'
        (the size of the content in bytes if status is 'ok'), or 'message'
        (the error message if status is 'error').

    Example:
        >>> build_document(pathlib.Path("etc/data/sample_docs"))
        '{"status": "ok", "content": "# [File 1] doc1.txt\\nContent of doc1.\\n# [File 2] doc2.md\\n## Content of doc2.\\n", "content_size": 78}'
    """
    try:
        content = process_docs.process_documents(folder_path_str)
        content_size = len(content.encode('utf-8'))
        if content_size > WARNING_SIZE_BYTES:
            logging.warning("warning, 50% of model context window was consumed! Consider moving to proper RAG or nitting down your data source")
        return json.dumps({"status": "ok", "content": content, "content_size": content_size})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
