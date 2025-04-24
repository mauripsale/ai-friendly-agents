from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

#from common_tools import carlessian_google_search, serp_search_flights
from serper_tools import serp_google_search

from google.adk.agents import Agent

root_agent = Agent(
   name="serpeverder__serper_client", # Larry
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using SERP API, mostly on Flights and Hotels and such.",
   instruction="You are an expert researcher. You always stick to the facts. Add Harry Potter quotes to your output as you see fit.",
   # Add google_search tool to perform grounding with Google search.
   tools=[
      #carlessian_google_search,
      #serp_search_flights,
      serp_google_search
      ]
)
