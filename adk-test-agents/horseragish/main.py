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
