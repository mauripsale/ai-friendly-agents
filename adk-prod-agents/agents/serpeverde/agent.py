'''This is a SERP serper.dev agent
Needs SERP API KEY.

This is also the first Carlessian agent which uses ./_common/lib/ stuff. I want to build a new universe where funCall
is in a common place.

This agent uses lib/ in the NG way, Gemini-aided.
'''

from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool
import os
import sys
import logging

########################################################
# BEGIN Carlessian needed magical lines to import lib/ (God didn't write the world in Python, I tell you that! Perl or Ruby, but not Python).
# --- MAGIC PATH FIXING START ---
current_dir = os.path.dirname(os.path.abspath(__file__))
#print(f"1. __file__:    {__file__}")
#print(f"2. current_dir: {current_dir}")
# Go up two levels to reach the project root
# current_dir: .../your_project/agents/my_awesome_agent
# parent_dir_1: .../your_project/agents
# parent_dir_2 (project_root): .../your_project
project_root = os.path.dirname(os.path.dirname(current_dir))
#print(f"3. os.path.dirname(current_dir): {os.path.dirname(current_dir)}")
#print(f"4. project_root: {project_root}")
# Add the project root to sys.path so Python can find 'lib'
# We insert at index 0 to give it highest priority
sys.path.insert(0, project_root)
# --- MAGIC PATH FIXING END ---
########################################################


#from common_tools import carlessian_google_search, serp_search_flights
# Imports from the new 'agents/lib' location
from lib.common_serpapi_tools import * # serpapi_google_search, serpapi_search_flights
from lib.common_time_tools import get_day_today

#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


aaa = [
   'show me flights from zurich to porto for tomorrow', # asks for flights but AI asks are you sure,.
   'show me flights from zurich to porto for tomorrow. And before you ask, YES Im sure and aware of API costs. Proceed!', # asks for flights but AI asks are you sure,.
]

SERPEVERDE_INSTRUCTIONS = """You are an expert researcher. You always stick to the facts. Add Harry Potter quotes to your output as you see fit.
If you get inquiries about flights or travel, make sure to call `get_day_today` to then know what date is "tomorrow" or "next saturday"
"""

root_agent = Agent(
   name="serpeverder__serper_client", # Larry
   model="gemini-2.0-flash", # Google AI Studio
   description="""Agent to answer questions using SERP API, mostly on Flights and Hotels and such.
   Can also leverage Maps API to map Lat/Long to an actual place and address.

   Since these API calls are VERY expensive, please let the user know before each call. If a call triggers multiple calls,
   for instance "find the address for these 5 hotels", make it clear it costs 5 API calls and confirm with user before executing it.
   Note the `get_day_today` tool is an exception, that's totally free.

   ## Flights

   When providing **flights** info, please provide options in tabular format with [day, cost, company, HH:MM (departure), HH:MM (arrival), duration, num_layovers ].
   User always prefers ZERO layovers, unless there's a huge price gap. Title of table: [ Day, $$, Company, Dept, Arriv, Dur, ⏸️ ].

   ## Hotels

   When providing **hotels** info, try to fetch also address information given Lat/Long (after confirming with user). Put price
   info in parenthesis and in **BOLD**, and use star emojis (eg 4 stars -> ⭐⭐⭐⭐). Make sure to add the hotel description verbatim (or summarize if its above 160 chars).
   Finally add amenities in italic, like sauna, pool, restaurant, beach front and such.
   To optimize space, try to use emoji in spite of strings for amenities (and only for amenities).
   If there's a permalink for the hotel (either a Google link, or Maps, or the hotel website), please link the bold hotel name with the most appropriate URL you find in the data provided.
   """,
   instruction=SERPEVERDE_INSTRUCTIONS,
   # Add google_search tool to perform grounding with Google search.
   tools=[
      #carlessian_google_search,
      serpapi_search_flights,
      serpapi_search_hotels,
      #serpapi_google_search,
      # TODO - convert lat,long to address.
      serpapi_google_maps,
      get_day_today,
      ]
)
