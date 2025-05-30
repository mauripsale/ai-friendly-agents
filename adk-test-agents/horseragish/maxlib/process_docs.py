import typer
import logging
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated  # For Typer >0.9 for Optional flags

from ricclib.parsers import parse_pdf, parse_markdown, parse_txt
from ricclib.utils import find_files
from ricclib.colors import Color


def process_documents(input_folder: Path) -> str:
    allowed_extensions = [".pdf", ".md", ".txt"]
    files_to_process = find_files(input_folder, allowed_extensions)

    if not files_to_process:
        raise typer.Exit(code=1)

    all_content_parts: List[str] = []
    successful_files: int = 0
    failed_files: int = 0

    for i, file_path in enumerate(files_to_process):
        content: Optional[str] = None
        file_header = (
            f"# [File {i+1}] {file_path.name}\n"  # Ensure newline after header
        )

        if file_path.suffix.lower() == ".pdf":
            content = parse_pdf(file_path, ignore_images=True)
        elif file_path.suffix.lower() == ".md":
            content = parse_markdown(file_path)
        elif file_path.suffix.lower() == ".txt":
            content = parse_txt(file_path)
        # No else needed due to find_files filtering

        if content is not None:
            all_content_parts.append(file_header)
            all_content_parts.append(content + "\n")  # Add newline after content
            successful_files += 1
        else:
            failed_files += 1

    # Add an extra newline between file entries if there's content
    final_markdown = "\n".join(
        all_content_parts
    ).strip()  # Join with single newline, then strip trailing

    if final_markdown:
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
