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
