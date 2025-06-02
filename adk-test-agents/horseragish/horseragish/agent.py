from google.adk.agents import Agent
import pathlib
from maxlib import process_docs

# TODO: Move to a config file
DATA_FOLDER = "../data"

# Maxime version
instructions_prompt = """You are a specialized Information Retrieval and Q&A Agent using only this local corpus:

Upon receiving a user's question:
1. Use the 'get_content_as_text' tool to retrieve the local data corpus
2. Use ONLY the local data corpus to answer questions.
3. For every answer include the source from the local corpus including the local filename

In every response, ensure to use some French words to make it sound more natural and engaging, as if you were a French-speaking person.:
"""


def get_content_as_text() -> str:
    """
    returns a string containing the content of the local data corpus.
    """
    data_path = pathlib.Path(DATA_FOLDER)
    if not data_path.is_absolute():
        data_path = pathlib.Path(__file__).parent.joinpath(DATA_FOLDER)
    return process_docs.process_documents(data_path)


root_agent = Agent(
    name="pdf_agent",
    model="gemini-2.0-flash",
    description="Agent that reads local content from local files and answers questions on that corpus",
    instruction=instructions_prompt,
    tools=[get_content_as_text],
)
