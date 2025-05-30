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
    return process_docs.process_documents(
        input_folder, output_file, ignore_images, debug
    )


if __name__ == "__main__":
    app()
