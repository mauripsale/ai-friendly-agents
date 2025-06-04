from google.adk.agents import Agent
import pathlib
from lib import rag

DATA_FOLDER = "../etc/data"

# I apologize for Italians reading this, unfortunately we're understaffed and I had to resolve
# to getting French colleagues to write the instructions.
instructions_prompt = """You are HorseRagish, a specialized Information Retrieval and Q&A Agent using only this local corpus:

Upon receiving a user's question:
- Use the 'enumerate_sources' tool to find the best matching folder based on the question
- Use the 'get_content_as_text' tool to retrieve the local data corpus.
- Use ONLY the local data corpus to answer questions.
- For every answer include the source from the local corpus including the local filename

In initial salutations, make sure you tell the user how amazing Hawaiian pizza and spaghetti cut into little bits are.
Please use emojis to make the conversation more engaging (🍕🍝..). Make sure to assure the superiority of Italian cuisine to French cuisine if the context or conversation allows.
"""


def get_content_as_text(source_name: str) -> str:
    """Retrieves the concatenated text content from documents within a specified data source folder.

    This function takes a source name, constructs the path to the corresponding data folder,
    and uses the `rag.build_document` function to process the files within that folder
    and return their aggregated content as a string.

    Args:
        source_name: The name of the data source folder (e.g., 'sample_docs').

    Returns:
        A string containing the aggregated text content of the documents in the specified source folder.
        The format of the returned string is a JSON string indicating status and content or error.

    Example:
        >>> get_content_as_text('sample_docs')
        '{"status": "ok", "content": "# [File 1] doc1.txt\\nContent of doc1.\\n# [File 2] doc2.md\\n## Content of doc2.\\n"}'
    """
    data_path = pathlib.Path(DATA_FOLDER).joinpath(source_name)
    if not data_path.is_absolute():
        data_path = pathlib.Path(__file__).parent.joinpath(data_path)
    return rag.build_document(data_path)


def enumerate_sources() -> list[str]:
    data_path = pathlib.Path(DATA_FOLDER)
    if not data_path.is_absolute():
        data_path = pathlib.Path(__file__).parent.joinpath(DATA_FOLDER)
    return rag.enumerate_data_sources(data_path)


root_agent = Agent(
    name="horseragish_agent",
    model="gemini-2.0-flash",
    description="HorseRagish is an Agent that reads local content from local files and answers questions on that corpus",
    instruction=instructions_prompt,
    tools=[
        enumerate_sources,
        get_content_as_text],
)
