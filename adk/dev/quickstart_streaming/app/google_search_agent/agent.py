from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

root_agent = Agent(
   # A unique name for the agent.
   name="basic_search_agent",
   # The Large Language Model (LLM) that agent will use.
#   model="gemini-2.0-flash-live-001", # Google AI Studio
   #model="gemini-2.0-flash-live", # Google AI Studio
   #model="gemini-2.0-flash", # Riccardo patch.
   model="gemini-2.0-flash-live-preview-04-09", # Vertex AI Studio
   # A short description of the agent's purpose.
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="You are an expert researcher. You always stick to the facts and never make up facts. You add emojis to your answers to be more relatable.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search]
)
