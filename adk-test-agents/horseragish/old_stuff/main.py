import typer
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated  # For Typer >0.9 for Optional flags

from maxlib import process_docs

app = typer.Typer(
    help="📄 Document Aggregator for LLMs 🤖\n\nCombines PDF, MD, and TXT files into one glorious Markdown string!"
)


@app.command()
def process_documents(
    input_folder: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            help="Folder containing documents (PDF, MD, TXT) to process.",
        ),
    ],
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output-file",
            "-o",
            help="File to save the combined markdown. Prints to stdout if not provided.",
        ),
    ] = None,
    ignore_images: Annotated[
        bool,
        typer.Option(
            "--ignore-images/--include-images",
            help="[default: --ignore-images] Focus on text extraction for PDFs to optimize tokens. (Currently uses text-only extraction regardless)",
        ),
    ] = True,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug", "-d", help="Enable debug output. Let's see what's cookin'!"
        ),
    ] = False,
) -> None:
    """
    Processes PDF, TXT, and Markdown files from a folder into a single markdown string,
    prefixed with file identifiers and with H1 headings demoted.
    Ready to be fed to your favorite high-context LLM! 🧠
    """
    # Maxime
    # return process_docs.process_documents(
    #     input_folder, output_file, ignore_images, debug
    # )
    if debug:
        print(f"{Color.CYAN}--- Debug Mode Activated ---{Color.END}")
        print(f"Processing documents from: {Color.YELLOW}{input_folder}{Color.END}")
        print(f"Ignore images in PDFs (token optimization): {Color.YELLOW}{ignore_images}{Color.END}")
        print(f"Output destination: {Color.YELLOW}{output_file if output_file else 'stdout'}{Color.END}")
        Color.list_ten_typical()
        print(f"{Color.MAGENTA}Note on google-adk: The google-adk functionality will be added to a future agent.py and not used by this script.{Color.END}")


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
