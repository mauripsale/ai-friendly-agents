'''This is a SERP serper.dev agent
Needs SERP API KEY.

This is also the first Carlessian agent which uses ./_common/lib/ stuff. I want to build a new universe where funCall
is in a common place.
PYTHONPATH="./_common/lib:$PYTHONPATH"

'''

from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool
import os
import sys
import logging
#from serpapi import GoogleSearch


# Calculate the path to _common/lib relative to this script
# sys.argv[0] is the script path
# os.path.dirname gets the directory
# os.path.abspath makes it absolute
# os.path.join builds paths safely
# '..', '..' goes up two directories from siculo/main.py to the project root
common_lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '_common', 'lib'))

# Add the path to sys.path if it's not already there
if common_lib_path not in sys.path:
   sys.path.insert(0, common_lib_path) # Insert at the beginning to prioritize it


#from common_tools import carlessian_google_search, serp_search_flights
# from _common.lib - needs
#from serper_tools import serp_google_search
from common_serpapi_tools import * # serpapi_google_search, serpapi_search_flights
from common_time_tools import get_day_today

from google.adk.agents import Agent

#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


SERPEVERDE_INSTRUCTIONS = """You are an expert researcher. You always stick to the facts. Add Harry Potter quotes to your output as you see fit.
If you get inquiries about flights or travel, make sure to call `get_day_today` to then know what date is "tomorrow" or "next saturday"
"""

root_agent = Agent(
   name="serpeverder__serper_client", # Larry
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using SERP API, mostly on Flights and Hotels and such.",
   instruction=SERPEVERDE_INSTRUCTIONS,
   # Add google_search tool to perform grounding with Google search.
   tools=[
      #carlessian_google_search,
      serpapi_search_flights,
      serpapi_search_hotels,
      serpapi_google_search,
      get_day_today,
      ]
)
