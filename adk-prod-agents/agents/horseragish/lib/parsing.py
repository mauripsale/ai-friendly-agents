from pathlib import Path
from typing import Optional
import logging
from pdfminer.high_level import extract_text


def _normalize_headings(content: str) -> str:
    """
    Demotes H1 headings (# Blah) to H2 (## Blah) to avoid conflicts
    with the main file headers.
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
    """
    Parses a PDF file and extracts text content.
    Ignores images and thus aligns with token frugality.
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
    """Reads a Markdown file and normalizes its headings."""
    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file {file_path.name} not found.")
    try:
        content = file_path.read_text(encoding="utf-8")
        return _normalize_headings(content)
    except Exception as e:
        logging.error(f"Error reading Markdown {file_path.name}: {e}")
        raise e


def parse_txt(file_path: Path) -> Optional[str]:
    """Reads a TXT file. Normalization is applied but less likely to change TXT content."""
    if not file_path.exists():
        raise FileNotFoundError(f"TXT file {file_path.name} not found.")
    try:
        content = file_path.read_text(encoding="utf-8")
        # TXT files are unlikely to have markdown H1s, but normalization doesn't hurt.
        return _normalize_headings(content)
    except Exception as e:
        logging.error(f"Error reading TXT {file_path.name}: {e}")
        raise e
