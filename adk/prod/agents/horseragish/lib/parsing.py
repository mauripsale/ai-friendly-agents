from pathlib import Path
from typing import Optional
import logging
from pdfminer.high_level import extract_text


def _normalize_headings(content: str) -> str:
    """Normalizes markdown headings by demoting H1 headings to H2.

    This prevents conflicts with main document headers.

    Args:
        content: The input string content, potentially containing markdown headings.

    Returns:
        The content string with H1 headings demoted to H2.

    Example:
        >>> _normalize_headings("# Title\n## Subtitle")
        '## Title\n## Subtitle'
    """
    lines = content.splitlines()
    processed_lines: list[str] = []
    for line in lines:
        if line.startswith("# "):
            processed_lines.append(f"#{line}")  # Demote H1 to H2
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)


def parse_pdf(file_path: Path) -> Optional[str]:
    """Parses a PDF file and extracts text content.

    Ignores images and thus aligns with token frugality.

    Args:
        file_path: The path to the PDF file.

    Returns:
        The extracted text content as a string, or None if no text was extracted.

    Raises:
        FileNotFoundError: If the specified PDF file does not exist.
        Exception: If an error occurs during PDF parsing.

    Example:
        >>> parse_pdf(Path("document.pdf"))
        'Extracted text from PDF.'
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file {file_path.name} not found.")
    try:
        normalized_content = _normalize_headings(extract_text(file_path).strip())
        if not normalized_content:
            logging.warning(
                f"No text extracted from PDF {file_path.name}. It might be image-based or empty."
            )
        return normalized_content
    except Exception as e:
        logging.error(f"Error parsing PDF {file_path.name}: {e}")
        raise e


def parse_markdown(file_path: Path) -> Optional[str]:
    """Reads a Markdown file and normalizes its headings.

    Args:
        file_path: The path to the Markdown file.

    Returns:
        The content of the Markdown file with normalized headings, or None if an error occurs.

    Raises:
        FileNotFoundError: If the specified Markdown file does not exist.
        Exception: If an error occurs during file reading or heading normalization.

    Example:
        >>> parse_markdown(Path("notes.md"))
        '## My Notes\nContent here.'
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file {file_path.name} not found.")
    try:
        content = file_path.read_text(encoding="utf-8")
        return _normalize_headings(content)
    except Exception as e:
        logging.error(f"Error reading Markdown {file_path.name}: {e}")
        raise e


def parse_txt(file_path: Path) -> Optional[str]:
    """Reads a TXT file and normalizes its headings.

    Normalization is applied but less likely to change TXT content.

    Args:
        file_path: The path to the TXT file.

    Returns:
        The content of the TXT file with normalized headings, or None if an error occurs.

    Raises:
        FileNotFoundError: If the specified TXT file does not exist.
        Exception: If an error occurs during file reading or heading normalization.

    Example:
        >>> parse_txt(Path("document.txt"))
        'Plain text content.'
    """
    if not file_path.exists():
        raise FileNotFoundError(f"TXT file {file_path.name} not found.")
    try:
        content = file_path.read_text(encoding="utf-8")
        # TXT files are unlikely to have markdown H1s, but normalization doesn't hurt.
        return _normalize_headings(content)
    except Exception as e:
        logging.error(f"Error reading TXT {file_path.name}: {e}")
        raise e
