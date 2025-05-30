import os
from google.adk.agents import Agent
from pathlib import Path

from maxlib import process_docs

# TODO: Move to a config file
# Relative to /Users/maximeh/ai-friendly-agents/adk-test-agents/horseragish/horseragish
DATA_FOLDER = "../data"


instructions_prompt = """You are a specialized Information Retrieval and Q&A Agent using only this local corpus:

Upon receiving a user's question:
1. Use the 'get_content_as_text' tool to retrieve the local data corpus
2. Use ONLY the local data corpus to answer questions.
3. For every answer include the source from the local corpus including the local filename
"""


def get_content_as_text():
    data_path = Path(os.path.join(os.path.dirname(__file__), DATA_FOLDER))
    return process_docs.process_documents(data_path)


root_agent = Agent(
    name="pdf_agent",
    model="gemini-2.0-flash",
    description="Agent that reads local content from local files and answers questions on that corpus",
    instruction=instructions_prompt,
    tools=[get_content_as_text],
)
