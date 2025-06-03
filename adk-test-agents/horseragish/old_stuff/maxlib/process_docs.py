import logging
from pathlib import Path
from typing import List, Optional

from ricclib.parsers import parse_pdf, parse_markdown, parse_txt
from ricclib.utils import find_files
from ricclib.colors import Color


def process_documents(input_folder: Path) -> str:

    if not input_folder.exists():
        raise RuntimeError(f'{input_folder} does not exist')
    if not input_folder.is_dir():
        raise RuntimeError(f'{input_folder} is not a directory')
    
    logging.debug(f'Looking for files in {input_folder}')

    allowed_extensions = [".pdf", ".md", ".txt"]
    files_to_process = find_files(input_folder, allowed_extensions)

    if not files_to_process:
        raise RuntimeError("No files to process in local corpus")
    
    logging.debug(f'Found {len(files_to_process)} files to process.')

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
            content = parse_pdf(file_path, ignore_images=True)
        elif extension == ".md":
            content = parse_markdown(file_path)
        elif extension == ".txt":
            content = parse_txt(file_path)
        else:
            raise RuntimeError(f'Unexpected extension: {extension}')

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
            f"{Color.RED}Processed {len(files_to_process)} files, but all failed or yielded no content. No output generated.{Color.END}"
        )
    elif not files_to_process:  # Should be caught earlier, but as a safeguard
        raise RuntimeError("No files found to process.")
    else:  # No files processed successfully, or all files were empty
        logging.info(
            f"{Color.YELLOW}No content was aggregated. All processed files might have been empty or resulted in no text.{Color.END}"
        )

    if failed_files > 0:
        logging.warning(
            f"{Color.YELLOW}⚠️  {failed_files} file(s) could not be processed or yielded no content. Check logs above.{Color.END}"
        )
