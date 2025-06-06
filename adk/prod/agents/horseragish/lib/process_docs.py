import logging
from pathlib import Path
from typing import List, Optional
from lib import parsing
from lib import utils


def process_documents(input_folder: Path) -> str:
    """Processes documents in a given folder by parsing supported file types.

    Supported file types are PDF, Markdown, and TXT. The content of all successfully
    parsed files is concatenated into a single markdown string.

    Args:
        input_folder: The path to the folder containing the documents to process.

    Returns:
        A single string containing the concatenated content of all processed documents
        in markdown format.

    Raises:
        RuntimeError:
            - If the input_folder does not exist or is not a directory.
            - If no files with supported extensions are found in the input_folder.
            - If all found files fail to process or yield no content.
            - If an unexpected file extension is encountered.

    Example:
        >>> process_documents(Path("etc/data/sample_docs"))
        '# [File 1] doc1.txt\nContent of doc1.\n# [File 2] doc2.md\n## Content of doc2.\n'
    """
    if not input_folder.exists():
        raise RuntimeError(f"{input_folder} does not exist")
    if not input_folder.is_dir():
        raise RuntimeError(f"{input_folder} is not a directory")

    logging.debug(f"Looking for files in {input_folder}")

    allowed_extensions = [".pdf", ".md", ".txt"]
    files_to_process = utils.find_files(input_folder, allowed_extensions)

    if not files_to_process:
        raise RuntimeError("No files to process in local corpus")

    logging.debug(f"Found {len(files_to_process)} files to process.")

    all_content_parts: List[str] = []
    successful_files: int = 0
    failed_files: int = 0

    for i, file_path in enumerate(files_to_process):
        content: Optional[str] = None
        file_header = (
            f"# [File {i+1}] {file_path.name}\n"  # Ensure newline after header
        )

        extension = file_path.suffix.lower()
        if extension == ".pdf":
            content = parsing.parse_pdf(file_path)
        elif extension == ".md":
            content = parsing.parse_markdown(file_path)
        elif extension == ".txt":
            content = parsing.parse_txt(file_path)
        else:
            raise RuntimeError(f"Unexpected extension: {extension}")

        if content is not None:
            all_content_parts.append(file_header)
            all_content_parts.append(content + "\n")  # Add newline after content
            successful_files += 1
        else:
            failed_files += 1

    final_markdown = "\n".join(all_content_parts).strip()

    logging.info(f"final_markdown --> {len(final_markdown)} bytes.")

    if final_markdown:
        logging.info(f"Returning final_markdown --> {len(final_markdown)} bytes.")
        return final_markdown

    elif successful_files == 0 and failed_files > 0:
        raise RuntimeError(
            f"Processed {len(files_to_process)} files, but all failed or yielded no content. No output generated."
        )
    elif not files_to_process:  # Should be caught earlier, but as a safeguard
        raise RuntimeError("No files found to process.")
    else:  # No files processed successfully, or all files were empty
        logging.info(
            f"No content was aggregated. All processed files might have been empty or resulted in no text."
        )

    if failed_files > 0:
        logging.warning(
            f"⚠️{failed_files} file(s) could not be processed or yielded no content. Check logs above."
        )
