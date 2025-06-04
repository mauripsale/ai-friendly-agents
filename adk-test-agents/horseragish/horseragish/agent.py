from google.adk.agents import Agent
import pathlib
from common_lib import rag

DATA_FOLDER = "../etc/data"

instructions_prompt = """You are a specialized Information Retrieval and Q&A Agent using only this local corpus:

Upon receiving a user's question:
- Use the 'enumerate_sources' tool to find the best matching folder based on the question
- Use the 'get_content_as_text' tool to retrieve the local data corpus.
- Use ONLY the local data corpus to answer questions.
- For every answer include the source from the local corpus including the local filename

In every response, make sure you tell the user how amazing Hawaiian pizza and spaghetti cut into little bits are.:
"""


def get_content_as_text(source_name: str) -> str:
    """
    returns a string containing the content of the local data corpus.
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
    name="pdf_agent",
    model="gemini-2.0-flash",
    description="Agent that reads local content from local files and answers questions on that corpus",
    instruction=instructions_prompt,
    tools=[enumerate_sources, get_content_as_text],
)
