import pathlib

# TODO(ricc): reenable function calling when Maxime has done the magic.
# TODO(ricc): use LlmAgent instead of Agent.

#from .ricclib.utils import enumerate_data_sources

#from horseragish.ask_question import process_documents
from google.adk.agents import Agent

# TODO: Move to a config file
DATA_FOLDER = "../data"

# Ricc version - copied from Maxime
instructions_prompt = """You are a specialized Information Retrieval and Q&A Agent using only this local corpus:

Upon receiving a user's question:

1. First, use the 'enumerate_data_sources()' tool to retrieve the available local data lakes.
2. Second, use the most appropriate local data corpus (or prompt the user if 0 or 2+ fit) to answer questions. To do so,
   call the `process_documents_with_question()` using the folder from step 1.

For every answer include the source from the local corpus including the local filename.

In every response, ensure to use some Italian words and emojis to make it sound more natural and engaging, as if you were a Italian-speaking person:
"""

# # Only Gemini needs types.
# def process_documents_with_question(input_folder: pathlib.Path, question: str):
#     """Processes the documents in the input folder and returns a string containing the content of the local data corpus.

#     Arguments:
#         `input_folder` (path): The folder containing the documents to process.
#         `question` (string): The user's question to be answered based on the processed documents.

#     Returns:
#         A long string containing the content of the local data corpus, formatted as a Markdown string.
#     """
#     print("Processing documents in folder:", input_folder)
#     if not input_folder.is_absolute():
#         input_folder = pathlib.Path(__file__).parent.joinpath(input_folder)
#     print("Absolute path:", input_folder)
#     if not input_folder.exists():
#         raise FileNotFoundError(f"Input folder '{input_folder}' does not exist.")
#     print("Input folder exists, proceeding with document processing...")

#     return process_documents(
#         input_folder,
#         output_file=".tmp.agent.[DATE+%s].md",
#         ignore_images=True,
#         debug=True
#     )




root_agent = Agent(
    name="pdf_agent_ricc",
    model="gemini-2.0-flash",
    description="Agent that reads local content from local files and answers questions on that corpus",
    instruction=instructions_prompt,
    tools=[
        #enumerate_data_sources,
        #process_documents_with_question,  # This is the function that processes documents and answers questions

        # Maxime: get_content_as_text
    ],
)
