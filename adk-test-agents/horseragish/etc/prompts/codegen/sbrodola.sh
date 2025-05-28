#!/bin/bash
set -euo pipefail # Stop at first big error, because we're professionals! 😎

echo "🚀 Greetings, fellow coder! Let's conjure up some Python magic! ✨"

# Create directory structure
echo "�� Creating directory structure (ricclib and friends)..."
mkdir -p ricclib
touch ricclib/__init__.py

# Create ricclib/colors.py
echo "🎨 Painting with ANSI: ricclib/colors.py (Because life's too short for monochrome logs!)"
cat << 'EOF' > ricclib/colors.py
# ricclib/colors.py
from typing import Dict

class AnsiColors:
    """A simple class to add ANSI colors to terminal output. 🌈"""
    COLORS: Dict[str, str] = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "orange": "\033[38;5;208m", # A nice, zesty orange
        "purple": "\033[38;5;93m",  # A regal purple
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }

    @staticmethod
    def colorize(text: str, color_name: str) -> str:
        """Colorizes the given text with the specified ANSI color."""
        color_code = AnsiColors.COLORS.get(color_name.lower())
        if color_code:
            return f"{color_code}{text}{AnsiColors.COLORS['reset']}"
        return text

    # Adding the 10 most typical colors as methods for convenience
    @staticmethod
    def red(text: str) -> str: return AnsiColors.colorize(text, "red")
    @staticmethod
    def green(text: str) -> str: return AnsiColors.colorize(text, "green")
    @staticmethod
    def yellow(text: str) -> str: return AnsiColors.colorize(text, "yellow")
    @staticmethod
    def blue(text: str) -> str: return AnsiColors.colorize(text, "blue")
    @staticmethod
    def magenta(text: str) -> str: return AnsiColors.colorize(text, "magenta")
    @staticmethod
    def cyan(text: str) -> str: return AnsiColors.colorize(text, "cyan")
    @staticmethod
    def white(text: str) -> str: return AnsiColors.colorize(text, "white")
    @staticmethod
    def black(text: str) -> str: return AnsiColors.colorize(text, "black")
    @staticmethod
    def orange(text: str) -> str: return AnsiColors.colorize(text, "orange")
    @staticmethod
    def purple(text: str) -> str: return AnsiColors.colorize(text, "purple")

    @staticmethod
    def bold(text: str) -> str: return AnsiColors.colorize(text, "bold")
    @staticmethod
    def underline(text: str) -> str: return AnsiColors.colorize(text, "underline")

if __name__ == "__main__":
    print(AnsiColors.red("This is red! Success! 🔥"))
    print(AnsiColors.green(f"{AnsiColors.bold('This is green and bold!')} Success! 🌿"))
    print(AnsiColors.underline(AnsiColors.blue("This is blue and underlined.")) + " Success! 💧")
    print(AnsiColors.orange("This is orange, how a-peeling! 🍊"))
    print(AnsiColors.purple("Feeling royal in purple! 👑"))
    print(AnsiColors.cyan("Cyan-tifically proven to be cool! 🧪"))
    print(AnsiColors.magenta("Magenta-nificent! 💖"))
    print(AnsiColors.white("White as freshly fallen snow. ❄️"))
    print(AnsiColors.black("Black, the new... well, it's always been cool. 🖤"))
EOF

# Create ricclib/markdown_utils.py
echo "🛠️ Crafting Markdown demotion utilities: ricclib/markdown_utils.py (No H1 shall pass!... as an H1, anyway)"
cat << 'EOF' > ricclib/markdown_utils.py
# ricclib/markdown_utils.py
import re
from typing import List

def demote_markdown_headers(markdown_content: str) -> str:
    """
    Demotes all Markdown headers within a string by one level.
    For example, '# Title' becomes '## Title', and '## Subtitle' becomes '### Subtitle'.
    This prevents H1 headers from individual files clashing with the
    main '# [File X] filename' headers in the consolidated output.
    """
    lines: List[str] = markdown_content.splitlines()
    processed_lines: List[str] = []
    for line in lines:
        match = re.match(r"^(#+)\s+(.*)", line)
        if match:
            hashes = match.group(1)
            title_text = match.group(2)
            # Add one more '#' to demote the header.
            # Max markdown header level is typically H6, but for this purpose,
            # just adding one '#' is sufficient to ensure it's not an H1.
            demoted_header = f"#{hashes} {title_text}"
            processed_lines.append(demoted_header)
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)

if __name__ == '__main__':
    print("🧪 Testing markdown_utils.py...")
    test_md_content = """# Original H1
Some text.
## Original H2
# Another Original H1
No leading space should not be a header.
#Also not a header
   # Indented H1, also not a header by strict markdown, but good to test
###### H6 Header
"""
    expected_output = """## Original H1
Some text.
### Original H2
## Another Original H1
No leading space should not be a header.
#Also not a header
   # Indented H1, also not a header by strict markdown, but good to test
####### H6 Header""" # Note: H6 becomes H7 essentially.
    
    demoted = demote_markdown_headers(test_md_content)
    print("\nOriginal Markdown:")
    print(test_md_content)
    print("\nDemoted Markdown:")
    print(demoted)

    assert demote_markdown_headers("# Title") == "## Title"
    assert demote_markdown_headers("## Subtitle") == "### Subtitle"
    assert demote_markdown_headers("Not a header") == "Not a header"
    assert demote_markdown_headers("  # Not a header (leading space)") == "  # Not a header (leading space)"
    print("✅ markdown_utils.py basic tests passed! Headers demoted as expected.")
EOF

# Create ricclib/file_parser.py
echo "📄 Assembling the mighty file parser: ricclib/file_parser.py (It reads, it transforms, it conquers!)"
cat << 'EOF' > ricclib/file_parser.py
# ricclib/file_parser.py
import os
from pathlib import Path
from typing import List, Tuple, Optional, Set

# Ensure pypdf is installed: pip install pypdf
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    # We'll define a dummy PdfReader if not available so type hints don't break,
    # but actual PDF processing will fail informatively.
    class PdfReader: # type: ignore
        def __init__(self, stream):
            pass
        @property
        def pages(self):
            return []

from .markdown_utils import demote_markdown_headers
from .colors import AnsiColors # For pretty printing during processing

def parse_pdf_to_markdown(file_path: Path, ignore_images: bool = True) -> str:
    """
    Parses a PDF file and extracts text content.
    If pypdf is not available, returns an error message.
    """
    if not PYPDF_AVAILABLE:
        return f"[Error: pypdf library not found. Cannot parse PDF {file_path.name}. Please run: pip install pypdf]"
    
    try:
        reader = PdfReader(file_path)
        text_parts: List[str] = []
        if not reader.pages:
             return f"[Info: PDF {file_path.name} has no pages or could not be read.]"

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
            else:
                text_parts.append(f"[No text extracted from page {page_num + 1} of {file_path.name}]")
        
        full_text = "\n\n".join(filter(None, text_parts)) # Join non-empty parts with double newline for paragraph breaks

        if not ignore_images:
            # This is purely informational as basic text extraction doesn't handle images.
            full_text += "\n\n[Note: `ignore_images` is false. Image content itself is not extracted by this basic parser, but text related to them might be.]"
        
        return full_text.strip()
    except FileNotFoundError:
        return f"[Error: PDF file not found at {file_path}]"
    except Exception as e: # Catching pypdf's specific exceptions might be better
        return f"[Error parsing PDF {file_path.name}: {e}]"

def read_text_file(file_path: Path) -> str:
    """Reads a plain text or Markdown file, replacing errors."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file {file_path.name}: {e}]"

def process_file(file_path: Path, ignore_images: bool) -> Optional[Tuple[str, str]]:
    """
    Processes a single file based on its extension.
    Returns a tuple of (file_name, processed_content_markdown) or None if not supported/empty.
    The returned content will have its internal headers demoted.
    """
    file_name = file_path.name
    extension = file_path.suffix.lower()
    raw_content: Optional[str] = None

    print(AnsiColors.cyan(f"  🔎 Inspecting '{AnsiColors.bold(str(file_path))}' (type: {extension})..."))

    if extension == ".pdf":
        raw_content = parse_pdf_to_markdown(file_path, ignore_images)
    elif extension in [".txt", ".md", ".markdown"]:
        raw_content = read_text_file(file_path)
    else:
        print(AnsiColors.yellow(f"  ⚠️ Unsupported file type: {file_name}. Skipping like a happy stone on water!"))
        return None

    if raw_content is None or not raw_content.strip(): # Check if content is empty or only whitespace
        print(AnsiColors.yellow(f"  🤷 No content extracted or file empty: {file_name}. Moving on!"))
        return None

    content_markdown = demote_markdown_headers(raw_content)
    print(AnsiColors.green(f"  ✅ Processed and headers demoted for: {file_name}"))
    return file_name, content_markdown

def process_folder(folder_path_str: str, ignore_images: bool = True) -> str:
    """
    Recursively processes all supported files (PDF, TXT, MD) in a folder.
    Combines their content into a single Markdown string, ready for an LLM feast!
    """
    folder_path = Path(folder_path_str)
    if not folder_path.is_dir():
        error_msg = f"# Error: Folder Not Found!\n\nOh dear, I put on my explorer hat 🤠, but couldn't find the folder: `{folder_path_str}`. Are you sure it exists?"
        print(AnsiColors.red(error_msg))
        return error_msg

    print(AnsiColors.magenta(f"📂 Scanning folder: {AnsiColors.bold(str(folder_path.resolve()))} (Recursive: True, Ignore Images: {ignore_images})"))

    all_files_content: List[str] = []
    file_counter = 0
    # Define the extensions we're interested in, like a VIP list for files!
    supported_extensions: Set[str] = {".pdf", ".txt", ".md", ".markdown"}
    
    # Recursively glob for files and then sort them for consistent ordering.
    # This makes the output predictable, which is nice.
    discovered_files = sorted([
        p for p in folder_path.rglob('*') 
        if p.is_file() and p.suffix.lower() in supported_extensions
    ])

    if not discovered_files:
        info_msg = f"# Information\n\nNo supported files (PDF, TXT, MD, MARKDOWN) found in `{folder_path_str}` or its subdirectories. Tumbleweeds... 🌵"
        print(AnsiColors.yellow(info_msg))
        return info_msg
    
    print(AnsiColors.blue(f"Found {len(discovered_files)} supported files. Let the great concatenation commence! 📜➕📜"))

    for file_path in discovered_files:
        result = process_file(file_path, ignore_images)
        if result:
            file_name, content_markdown = result
            file_counter += 1
            # This is the H1 header for each file's section in the combined output
            header = f"# [File {file_counter}] {file_name}\n\n"
            # Add a nice Markdown horizontal rule as a separator, because we're fancy.
            all_files_content.append(header + content_markdown + "\n\n---\n\n") 

    if not all_files_content:
        return f"# Information\n\nWell, this is awkward. Supported files were found in `{folder_path_str}`, but no content could be extracted. Perhaps they were shy? 😶"

    final_markdown = "".join(all_files_content).strip()
    # Clean up the trailing separator if it exists from the last file
    if final_markdown.endswith("\n\n---\n\n"):
        final_markdown = final_markdown[:-len("\n\n---\n\n")]
    elif final_markdown.endswith("\n\n---"): # Just in case of slight variation
         final_markdown = final_markdown[:-len("\n\n---")]
        
    return final_markdown.strip() # Final strip for good measure

if __name__ == '__main__':
    # This part is for testing the module directly if you wish.
    # Usually, you'd run main.py.
    print(AnsiColors.bold("\n🦄 Running file_parser.py directly for a magical test drive...\n"))
    
    test_dir = Path("temp_test_docs_parser_ricc") # Unique name
    test_dir.mkdir(exist_ok=True)
    sub_dir = test_dir / "subdir_alpha"
    sub_dir.mkdir(exist_ok=True)

    print(f"Populating test directory: {test_dir.resolve()}")
    (test_dir / "file_A.txt").write_text("Hello from text file A.\n# This is an H1 in file_A.txt\nSome more text.")
    (test_dir / "document_B.md").write_text("# Top Title in MD B\nThis is markdown content.\n## A Subheading\n* List item 1\n* List item 2")
    (sub_dir / "notes_C.txt").write_text("Notes from the subdirectory C.\n# Subdir H1 Notes\nImportant stuff here."))
    (test_dir / "archive.zip").write_text("This is a zip file, should be politely ignored.")
    (test_dir / "empty_D.md").write_text("   \n   \n   ") # File with only whitespace

    # For a PDF test, you'd manually place a small PDF here or mock pypdf.
    # For instance, if you have 'dummy.pdf' in the same directory as sbrodola.sh:
    # if Path("dummy.pdf").exists():
    #    import shutil
    #    shutil.copy("dummy.pdf", test_dir / "sample_E.pdf")
    #    print("Copied dummy.pdf for testing.")
    # else:
    #    print(AnsiColors.yellow("Warning: dummy.pdf not found for PDF parsing test."))

    print(AnsiColors.yellow("\n--- Simulating processing of the test directory (expect PDF errors if pypdf is missing or no PDF present) ---"))
    output_md = process_folder(str(test_dir), ignore_images=True)
    
    print(AnsiColors.green("\n--- Consolidated Markdown Output (from file_parser test) ---"))
    print(output_md)
    print(AnsiColors.green("--- End of Consolidated Markdown ---"))

    # print(f"To clean up, manually delete: {test_dir.resolve()}")
    print(AnsiColors.purple("\nTest run of file_parser.py complete. If you see a beautifully structured Markdown, give yourself a high five! 🙌"))
EOF

# Create main.py
echo " मुख्य Executing the grand orchestrator script generator: main.py (The conductor of our file symphony!)"
cat << 'EOF' > main.py
# main.py
import argparse
from pathlib import Path
import sys # For sys.exit, because sometimes we just need to stop.

# Attempt to import our local heroes from ricclib
try:
    from ricclib.file_parser import process_folder
    from ricclib.colors import AnsiColors
except ImportError as e:
    # This is a critical error, the script can't run without its modules.
    # Using a raw print here as AnsiColors might not be available.
    print(f"[CRITICAL ERROR] Oh no! Failed to import modules from 'ricclib': {e}")
    print("Please ensure 'ricclib' directory and its Python files (colors.py, file_parser.py, markdown_utils.py, __init__.py) exist where I expect them (same directory as me, main.py).")
    print("Also, super important: have you installed 'pypdf'? If not, please run: pip install pypdf")
    sys.exit(1) # Abandon ship!

def main():
    """
    Main function to parse arguments and orchestrate the file processing.
    Your friendly neighborhood document muncher! 🍪 Ready to serve your LLM.
    """
    parser = argparse.ArgumentParser(
        description=AnsiColors.colorize("📚 Docu-Aggregator 3000: Gathers PDF, TXT, & MD files, processes them, and outputs a single Markdown string fit for an LLM king (or queen)! 👑", "magenta"),
        formatter_class=argparse.RawTextHelpFormatter, # Allows for more control over help text formatting
        epilog=f"""
{AnsiColors.cyan("Example invocations (try these!):")}
  {AnsiColors.green('python main.py ./my_research_papers --output_file research_digest.md')}
  {AnsiColors.green('python main.py "path/with spaces/docs" --no-ignore-images --debug')}

{AnsiColors.purple("May your tokens be efficiently used and your LLM insights be plentiful! ✨")}
"""
    )
    parser.add_argument(
        "input_folder",
        type=str,
        help=AnsiColors.colorize("Path to the folder stuffed with your precious documents (PDF, TXT, MD).\nI'll bravely venture into subdirectories too! 🗺️", "blue"),
    )
    parser.add_argument(
        "--output_file",
        "-o", # A classic short flag
        type=str,
        default="consolidated_llm_feed.md", # A descriptive default
        help=AnsiColors.colorize("Where should I scribe the final epic Markdown? (default: consolidated_llm_feed.md) 📝", "blue"),
    )
    parser.add_argument(
        "--ignore_images", # Becomes args.ignore_images
        action=argparse.BooleanOptionalAction, # Gives --ignore-images and --no-ignore-images
        default=True, # Sensible default for token optimization
        help=AnsiColors.colorize("PDF Image Handling: '--ignore-images' (default) focuses on text for token saving. \n'--no-ignore-images' includes a note about potential image context (basic text extraction doesn't render images).", "blue"),
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help=AnsiColors.colorize("Activate Debug Mode! 🕵️‍♀️ Get ready for a flood of fascinating operational details.", "yellow"),
    )

    args = parser.parse_args()

    if args.debug:
        print(AnsiColors.yellow("🕵️‍♂️ Debug mode is ON! We're going deep undercover into the land of files..."))
        print(f"  {AnsiColors.bold('Input Folder:')} {Path(args.input_folder).resolve()}")
        print(f"  {AnsiColors.bold('Output File:')} {Path(args.output_file).resolve()}")
        print(f"  {AnsiColors.bold('Ignore Images in PDF:')} {args.ignore_images}")
        print(AnsiColors.yellow("-" * 40))

    print(AnsiColors.green(f"🚀 All systems go! Processing folder: {AnsiColors.bold(args.input_folder)}"))
    if PYPDF_AVAILABLE: # Check if pypdf was successfully imported in file_parser
        print(AnsiColors.cyan("   (PDF processing capability: ENABLED via pypdf 📄��)"))
    else:
        print(AnsiColors.red("   (PDF processing capability: DISABLED - pypdf library not found! PDFs will be skipped or show errors. 📄❌)"))
        print(AnsiColors.yellow("    Please install it with: pip install pypdf"))


    # The main act!
    consolidated_markdown = process_folder(args.input_folder, args.ignore_images)

    output_path = Path(args.output_file)
    try:
        # Ensure the directory for the output file exists, otherwise 'open' might cry.
        output_path.parent.mkdir(parents=True, exist_ok=True) 
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(consolidated_markdown)
        
        # Check if the output was just an error/info message from process_folder
        if consolidated_markdown.startswith(("# Error", "# Information")):
             final_message = f"✋ Hold your horses! The process finished, but the output file '{AnsiColors.bold(str(output_path.resolve()))}' seems to contain only operational messages (like errors or info that no files were found). You should probably check its content."
             print(AnsiColors.yellow(final_message))
        else:
            final_message = f"🎉 Ta-da! All documents have been masterfully blended into: {AnsiColors.bold(str(output_path.resolve()))}"
            print(AnsiColors.green(final_message))
            print(AnsiColors.magenta("Your LLM is about to receive a beautifully prepared data feast! Bon appétit! 🧑‍🍳"))

        # Optional: print a snippet if debug or if content is very short (likely an error/info message)
        if args.debug or len(consolidated_markdown) < 500 : # Increased length for snippet
            print(AnsiColors.cyan("\n--- Snippet of Generated Content (or Full Content if Short) ---"))
            lines = consolidated_markdown.splitlines()
            if len(lines) > 20 and not args.debug: # Show more for debug
                for line in lines[:10]: print(line)
                print(AnsiColors.yellow("... (content truncated for brevity) ..."))
                for line in lines[-10:]: print(line)
            else:
                print(consolidated_markdown) # Print all if short or if debug is on
            print(AnsiColors.cyan("--- End of Snippet ---"))

    except IOError as e:
        print(AnsiColors.red(f"💥 Oh snap! A gremlin interfered with writing to {output_path}: {e}"))
        print(AnsiColors.yellow("Maybe check the path or permissions? Or perhaps offer the gremlin a cookie? 🍪"))
        if len(consolidated_markdown) < 3000: # Avoid terminal flooding
            print(AnsiColors.yellow("\n💡 Here's the content I tried to save (might be long!):\n"))
            print(consolidated_markdown)
    except Exception as e:
        print(AnsiColors.red(f"🚨 Whoopsie! An unexpected interstellar anomaly (aka error) occurred: {e}"))
        print(AnsiColors.yellow("If this looks serious, you might want to consult your local tech shaman or rubber duck. 🦆"))

if __name__ == "__main__":
    # This is where the journey begins when you type `python main.py ...`
    # Make sure to import PYPDF_AVAILABLE for the main function to use
    try:
        from ricclib.file_parser import PYPDF_AVAILABLE
    except ImportError: # Should have been caught earlier, but defensive
        PYPDF_AVAILABLE = False
    main()
EOF

# Make sbrodola.sh executable (though you run it with bash sbrodola.sh)
# chmod +x sbrodola.sh # Not strictly necessary if running with 'bash sbrodola.sh'

echo ""
echo "✅ Et Voilà! All Python files have been generated and are waiting in the wings! 🎭"
echo "Your 'ricclib' directory is set up, and 'main.py' is ready for action."
echo ""
echo "Next Steps:"
echo "1. If you haven't already, install the PDF parsing library:"
echo "   ${BOLD}pip install pypdf${RESET}" # Assuming BOLD and RESET are defined or use raw
echo "   (I've added checks, but it's good to have it ready!)"
echo ""
echo "2. Run the main script with your folder:"
echo "   ${BOLD}python main.py ./your_data_folder --output_file all_docs.md${RESET}"
echo "   Replace './your_data_folder' with the actual path to your documents."
echo ""
echo "Happy data wrangling, and may your LLM generate pure gold! 💰😉"
