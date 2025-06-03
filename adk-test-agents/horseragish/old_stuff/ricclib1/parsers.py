import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
from .colors import Color # Enjoy some colors in your parser output!

def normalize_headings(content: str) -> str:
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

def parse_pdf(file_path: Path, ignore_images: bool = True) -> Optional[str]:
    """
    Parses a PDF file and extracts text content.
    The ignore_images flag is noted; PyMuPDF's get_text("text") is primarily text-focused
    and thus aligns with token frugality.
    """
    text_content: str = ""
    if not file_path.exists():
        print(f"{Color.RED}Error: PDF file {file_path.name} not found.{Color.END}")
        return None
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text("text") + "\n" # "text" for frugal token usage
        doc.close()
        normalized_content = normalize_headings(text_content.strip())
        if not normalized_content:
            print(f"{Color.YELLOW}Warning: No text extracted from PDF {file_path.name}. It might be image-based or empty.{Color.END}")
        return normalized_content
    except Exception as e:
        print(f"{Color.RED}Error parsing PDF {file_path.name}: {e}{Color.END}")
        return None

def parse_markdown(file_path: Path) -> Optional[str]:
    """Reads a Markdown file and normalizes its headings."""
    if not file_path.exists():
        print(f"{Color.RED}Error: Markdown file {file_path.name} not found.{Color.END}")
        return None
    try:
        content = file_path.read_text(encoding="utf-8")
        return normalize_headings(content)
    except Exception as e:
        print(f"{Color.RED}Error reading Markdown {file_path.name}: {e}{Color.END}")
        return None

def parse_txt(file_path: Path) -> Optional[str]:
    """Reads a TXT file. Normalization is applied but less likely to change TXT content."""
    if not file_path.exists():
        print(f"{Color.RED}Error: TXT file {file_path.name} not found.{Color.END}")
        return None
    try:
        content = file_path.read_text(encoding="utf-8")
        # TXT files are unlikely to have markdown H1s, but normalization doesn't hurt.
        return normalize_headings(content)
    except Exception as e:
        print(f"{Color.RED}Error reading TXT {file_path.name}: {e}{Color.END}")
        return None

