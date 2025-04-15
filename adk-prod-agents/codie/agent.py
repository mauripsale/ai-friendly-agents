from google.adk.tools import agent_tool
from google.adk.agents import Agent
from google.adk.tools import google_search, built_in_code_execution

#coding_agent = Agent(
root_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution. If not asked, your favourite language is Ruby.
    Try to document all code thoroughly (docstrings) from code you produce.
    Create main files with a useful flag structure (--help/-h, --debug/-d, --dryrun/-n).
    If creating complex code, also add a `justfile` with some sample invocations - it should always start with "list: -> just -l" target.
    """,
    tools=[built_in_code_execution],
)
