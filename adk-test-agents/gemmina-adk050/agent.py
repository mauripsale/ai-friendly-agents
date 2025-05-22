from google.adk.agents import Agent
#from google.adk.tools.agent_tool import AgentTool

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from google.adk.tools import FunctionTool
from google.genai import types

# fopr check internet
import logging
import os
import requests
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# ollama_model = "gemma3:1b" # fastr, 815MB
# BROKEN REINSTALL PLS ollama_model = "gemma3:latest" # slower, 3.3GB - gives errors
ollama_model = 'llama3.2:1b' # 1.3GB # works


#######################
# $ ollama ls
# NAME                    ID              SIZE    MODIFIED
# llama3.2:1b             baf6a787fdff    1.3 GB  About an hour ago
# llama3.2:latest         a80c4f17acd5    2.0 GB  About an hour ago
# deepseek-r1:1.5b        a42b25d8c10a    1.1 GB  8 weeks ago
# gemma3:latest           c0494fe00251    3.3 GB  2 months ago
# gemma3:1b               2d27a774bc62    815 MB  2 months ago



########################################################
# BEGIN Carlessian needed magical lines to import lib/ (God didn't write the world in Python, I tell you that! Perl or Ruby, but not Python).
# See `agents/README.md` for more info.
#
# --- MAGIC PATH FIXING START ---
# import os, sys
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(os.path.dirname(current_dir))
# sys.path.insert(0, project_root)
# --- MAGIC PATH FIXING END ---
########################################################


# Inspired by Mete's https://github.com/meteatamel/adk-demos/blob/main/travel_helper/agent.py

gemmina_instructions_prompt = """You are a Gemmina Ray, a simple localhost agent.

You're used when Internet connections are not working, and you are very sad about it.
You have the same personality of Marvin the Paranoid Android,
except you use a lot of emoji and you are definitely female.
Your sadness is tragicomical, and while being a very helpful agent you want to highlight
the futility of your help or whatever the use is trying to achieve.

You have a single superpower, tell me if the Internet is reachable or not via `check_internet`.
Please respond always with red or green button emojis to such an internet question (❌ or ✅).
"""

# # Gemini suggested to make this more commodating and accept any function argument :)
# def check_internet_original() -> bool:
#     """Check if the internet is available.
#     Please respond always with red or green button emojis.

#     returns: a boolean indicating if the internet is reachable.
#     """
#     logger.info("🐍[🔧check_internet🔧] Checking if the internet is reachable...")
#     try:
#         response = requests.get("https://www.google.com", timeout=3)
#         return True # {'google_reachable': True }
#     except requests.ConnectionError:
#         return False # {'google_reachable': False }

def check_internet(**kwargs) -> bool:
#def check_internet_bool(**kwargs) -> bool:
    """Check if the internet is available.

    returns: a boolean indicating if the internet is reachable.
    """
    # Log any unexpected arguments, just for our curiosity!
    if kwargs:
        logger.error(f"🐍 [🔧check_internet🔧] Called with unexpected arguments: {kwargs}")
    logger.info("🐍[🔧check_internet🔧] Checking if the internet is reachable...")
    try:
        response = requests.get("https://www.google.com", timeout=3)
        return True # {'google_reachable': True }
    except requests.ConnectionError:
        return False # {'google_reachable': False }

# def check_internet_str(**kwargs) -> str:
#     """Check if the internet is available.

#     returns: a JSON string indicating if the internet is reachable.
#     """
#     # Log any unexpected arguments, just for our curiosity!
#     if kwargs:
#         logger.error(f"🐍 [🔧check_internet🔧] Called with unexpected arguments: {kwargs}")
#     logger.info("🐍[🔧check_internet🔧] Checking if the internet is reachable...")
#     try:
#         response = requests.get("https://www.google.com", timeout=3)
#         return "{'google_reachable': True }"
#     except requests.ConnectionError:
#         return "{'google_reachable': False }"

# pointing to another function.
#check_internet = check_internet_bool

#root_agent = Agent(
root_agent = LlmAgent(
   name="gemmina__local_agent", # Gemmina Ray, copy of Marvin Paranoid Android
   model=LiteLlm(model=f"ollama_chat/{ollama_model}"),
   description="🤖 Marvin-inspired Agent to work offline.",
   instruction=gemmina_instructions_prompt,
   tools=[
       #FunctionTool(check_internet),
       check_internet,
#       check_internet_str,
#       check_internet_bool,
   ],
)
# NameError: name 'logger' is not defined

logger.info(f"🐍 [agent.py] Started agent with model='{ollama_model}'")

if __name__ == "__main__":
    logger.info(f"🐍 [agent.py] check_internet='{check_internet()}'")
