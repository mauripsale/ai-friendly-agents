#!/bin/bash
set -euo pipefail

echo "🚀 Initializing project structure..."

# Create base directories
mkdir -p ricclib
mkdir -p data/sample_docs

# --- ricclib/colors.py ---
echo "🎨 Creating ricclib/colors.py..."
cat << 'EOF' > ricclib/colors.py
from typing import Final

class Color:
    """
    Simple ANSI color codes for terminal output.
    Because life's too short for monochrome logs! 😉
    """
    BLACK: Final[str] = "\033[30m"
    RED: Final[str] = "\033[31m"
    GREEN: Final[str] = "\033[32m"
    YELLOW: Final[str] = "\033[33m"
    BLUE: Final[str] = "\033[34m"
    MAGENTA: Final[str] = "\033[35m"
    CYAN: Final[str] = "\033[36m"
    WHITE: Final[str] = "\033[37m"
    GREY: Final[str] = "\033[90m" # Bright Black / Grey
    BRIGHT_RED: Final[str] = "\033[91m"
    BRIGHT_GREEN: Final[str] = "\033[92m" # Tenth color example

    # Formatting
    BOLD: Final[str] = "\033[1m"
    UNDERLINE: Final[str] = "\033[4m"
    
    # Reset
    END: Final[str] = "\033[0m"

    # Example usage:
    # print(f"{Color.GREEN}This is green text.{Color.END}")
    # print(f"{Color.BOLD}{Color.RED}This is bold red text.{Color.END}")

    @staticmethod
    def list_ten_typical() -> None:
        """Prints a list of 10 typical colors with examples."""
        print(f"{Color.BLACK}1. Black{Color.END}")
        print(f"{Color.RED}2. Red{Color.END}")
        print(f"{Color.GREEN}3. Green{Color.END}")
        print(f"{Color.YELLOW}4. Yellow{Color.END}")
        print(f"{Color.BLUE}5. Blue{Color.END}")
        print(f"{Color.MAGENTA}6. Magenta{Color.END}")
        print(f"{Color.CYAN}7. Cyan{Color.END}")
        print(f"{Color.WHITE}8. White (may depend on terminal theme){Color.END}")
        print(f"{Color.GREY}9. Grey{Color.END}")
        print(f"{Color.BRIGHT_RED}10. Bright Red{Color.END}")
        print(f"{Color.BOLD}Bold example{Color.END}")
        print(f"{Color.UNDERLINE}Underline example{Color.END}")

EOF

# --- ricclib/utils.py ---
echo "🛠️ Creating ricclib/utils.py..."
cat << 'EOF' > ricclib/utils.py
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

EOF

# --- ricclib/parsers.py ---
echo "📄 Creating ricclib/parsers.py..."
cat << 'EOF' > ricclib/parsers.py
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

EOF

# --- main.py ---
echo "✨ Creating main.py..."
cat << 'EOF' > main.py
import typer
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated # For Typer >0.9 for Optional flags

from ricclib.parsers import parse_pdf, parse_markdown, parse_txt
from ricclib.utils import find_files
from ricclib.colors import Color

app = typer.Typer(help="📄 Document Aggregator for LLMs 🤖\n\nCombines PDF, MD, and TXT files into one glorious Markdown string!")

@app.command()
def process_documents(
    input_folder: Annotated[Path, typer.Argument(
        exists=True, file_okay=False, dir_okay=True, readable=True,
        help="Folder containing documents (PDF, MD, TXT) to process."
    )],
    output_file: Annotated[Optional[Path], typer.Option(
        "--output-file", "-o",
        help="File to save the combined markdown. Prints to stdout if not provided."
    )] = None,
    ignore_images: Annotated[bool, typer.Option(
        "--ignore-images/--include-images",
        help="[default: --ignore-images] Focus on text extraction for PDFs to optimize tokens. (Currently uses text-only extraction regardless)"
    )] = True,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Enable debug output. Let's see what's cookin'!")] = False,
) -> None:
    """
    Processes PDF, TXT, and Markdown files from a folder into a single markdown string,
    prefixed with file identifiers and with H1 headings demoted.
    Ready to be fed to your favorite high-context LLM! 🧠
    """
    if debug:
        print(f"{Color.CYAN}--- Debug Mode Activated ---{Color.END}")
        print(f"Processing documents from: {Color.YELLOW}{input_folder}{Color.END}")
        print(f"Ignore images in PDFs (token optimization): {Color.YELLOW}{ignore_images}{Color.END}")
        print(f"Output destination: {Color.YELLOW}{output_file if output_file else 'stdout'}{Color.END}")
        Color.list_ten_typical()
        print(f"{Color.MAGENTA}Note on google-adk: The google-adk (Google AI Developer Kit) is for on-device AI (e.g., Android) and not used by this script.{Color.END}")


    allowed_extensions = [".pdf", ".md", ".txt"]
    files_to_process = find_files(input_folder, allowed_extensions)

    if not files_to_process:
        print(f"{Color.YELLOW}🤔 No supported files (PDF, MD, TXT) found in '{input_folder}'. Sad trombone... 🎺{Color.END}")
        raise typer.Exit(code=1)

    if debug:
        print(f"{Color.GREEN}Found {len(files_to_process)} files to process:{Color.END}")
        for f_path_idx, f_path_val in enumerate(files_to_process):
            print(f"  {f_path_idx+1}. {Color.CYAN}{f_path_val.name}{Color.END}")

    all_content_parts: List[str] = []
    successful_files: int = 0
    failed_files: int = 0

    for i, file_path in enumerate(files_to_process):
        content: Optional[str] = None
        file_header = f"# [File {i+1}] {file_path.name}\n" # Ensure newline after header
        
        if debug:
            print(f"{Color.BLUE}Processing ({i+1}/{len(files_to_process)}): {file_path.name}...{Color.END}")

        try:
            if file_path.suffix.lower() == ".pdf":
                content = parse_pdf(file_path, ignore_images)
            elif file_path.suffix.lower() == ".md":
                content = parse_markdown(file_path)
            elif file_path.suffix.lower() == ".txt":
                content = parse_txt(file_path)
            # No else needed due to find_files filtering

            if content is not None:
                all_content_parts.append(file_header)
                all_content_parts.append(content + "\n") # Add newline after content
                successful_files += 1
            else:
                # Error message already printed by the parser
                if debug:
                     print(f"{Color.YELLOW}Skipping {file_path.name} due to parsing error or no content.{Color.END}")
                failed_files +=1

        except Exception as e:
            print(f"{Color.RED}😱 Oh no! An unexpected error occurred while processing {file_path.name}: {e}{Color.END}")
            if debug:
                import traceback
                traceback.print_exc()
            failed_files += 1
            
    # Add an extra newline between file entries if there's content
    final_markdown = "\n".join(all_content_parts).strip() # Join with single newline, then strip trailing

    if final_markdown:
        if output_file:
            try:
                output_file.write_text(final_markdown, encoding="utf-8")
                print(f"{Color.GREEN}🎉 Success! Combined markdown written to: {output_file}{Color.END}")
            except Exception as e:
                print(f"{Color.RED}💥 Error writing to output file {output_file}: {e}{Color.END}")
                if debug:
                    print(f"{Color.YELLOW}Dumping to stdout instead due to file error:{Color.END}\n{final_markdown}")
                raise typer.Exit(code=1)
        else:
            # Print to stdout if no output file specified
            print(final_markdown)
    elif successful_files == 0 and failed_files > 0:
         print(f"{Color.RED}Processed {len(files_to_process)} files, but all failed or yielded no content. No output generated.{Color.END}")
         raise typer.Exit(code=1)
    elif not files_to_process : # Should be caught earlier, but as a safeguard
        pass # Already handled
    else: # No files processed successfully, or all files were empty
        print(f"{Color.YELLOW}No content was aggregated. All processed files might have been empty or resulted in no text.{Color.END}")


    if debug:
        print(f"{Color.CYAN}--- Processing Summary ---{Color.END}")
        print(f"Total files found: {len(files_to_process)}")
        print(f"Successfully processed: {Color.GREEN}{successful_files}{Color.END}")
        print(f"Failed or no content: {Color.RED if failed_files > 0 else Color.GREY}{failed_files}{Color.END}")

    if failed_files > 0:
        print(f"{Color.YELLOW}⚠️  {failed_files} file(s) could not be processed or yielded no content. Check logs above.{Color.END}")
        # Optionally raise an error if any file fails
        # raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

EOF

# --- Dummy files for testing ---
echo "�� Creating sample data/sample_docs/doc1.txt..."
cat << 'EOF' > data/sample_docs/doc1.txt
This is a test text file.
It has some simple lines.

# This looks like an H1 but it's in a TXT file.
The script should still demote it if it processes TXT files for headings.
EOF

echo "📄 Creating sample data/sample_docs/doc2.md..."
cat << 'EOF' > data/sample_docs/doc2.md
# Markdown Document Title

This is a **markdown** document.
It has a list:
- Item 1
- Item 2

## A Subheading
Some more text.

# Another H1 in Markdown
This should be demoted.
EOF

echo "📄 Creating sample data/sample_docs/empty.md..."
cat << 'EOF' > data/sample_docs/empty.md
EOF


echo "🐍 Creating a dummy PDF is complex in bash. Please add a sample.pdf to data/sample_docs/ for full testing."
echo "You can create one from any text editor's 'Print to PDF' option."
echo "For example, create 'sample.pdf' with the text '# PDF Test H1 \n Some PDF content.'"

# --- UV Environment Setup ---
echo "🔧 Setting up uv environment..."
if ! command -v uv &> /dev/null
then
    echo "uv could not be found. Please install uv first."
    echo "See: https://github.com/astral-sh/uv"
    exit 1
fi

# Create virtual environment
uv venv .venv --python $(which python3 || which python) # Use system python3 or python

echo ""
echo "✅ Project setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   ${BOLD_TEXT}source .venv/bin/activate${RESET_TEXT}"
echo "2. Install dependencies using uv:"
echo "   ${BOLD_TEXT}uv pip install typer PyMuPDF typing-extensions${RESET_TEXT}"
echo "3. Run the script (example):"
echo "   ${BOLD_TEXT}python main.py data/sample_docs/ -o combined_output.md --debug${RESET_TEXT}"
echo "   (Ensure you have a PDF file in data/sample_docs/ for full PDF testing)"
echo ""
echo "Happy processing! 🎉"

