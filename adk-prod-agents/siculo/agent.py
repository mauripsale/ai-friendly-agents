from google.adk.agents import Agent
#from google.adk.tools import google_search  # Import the tool

root_agent = Agent(
   name="salvatore_siculo__sql_agent", # Salvatore "SQL" Siculo
   model="gemini-2.0-flash", # might not be enough..
   description="Agent to answer questions on SQL databases. ",
   # Instructions to set the agent's behavior.
   instruction="You are a SQL expert. You'll be able to look at DB structure and answer questions about it."
            "You will use tools to access schema, tables, and rows. You'll be able to execute generic SQL for one given multi-DB file."
            "Currently just supports sqlite3.",
   tools=[],
)
