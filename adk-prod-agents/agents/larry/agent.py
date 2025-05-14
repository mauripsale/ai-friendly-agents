from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

sample_questions = [
   'What time is it in Zurich right now?',
   'Whats the weather like in Zurich right now? Give me Min, Max and current. Do NOT use Fahrenheit',
]

root_agent = Agent(
   # A unique name for the agent.
   name="larry__basic_search_agent", # Larry
   # The Large Language Model (LLM) that agent will use.
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="You are an expert researcher. You always stick to the facts. Add emojis to your output as you see fit.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search]
)
