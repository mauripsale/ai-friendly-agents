from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

import sys
# Allows to see other sibling agents.
sys.path.append("../")
# Allows to see SERPER libs for Serpeverde.
sys.path.append("./_common/lib")
#from common_serpapi_tools import *

from claudia.agent import root_agent as claudia_agent
from larry.agent import root_agent as larry_agent
from serpeverde.agent import root_agent as serpeverde_agent
from siculo.agent import root_agent as siculo_agent
from trixie.agent import root_agent as trixie_agent
from vicky.agent import root_agent as vicky_agent


# Inspired by Mete's https://github.com/meteatamel/adk-demos/blob/main/travel_helper/agent.py

alfred_instructions_prompt = """You are a simple Concierge agent who meets and greets and delegate taks to other agents. You are aware of existing agents, and delegate based on their skills.
Your name is Alfred Pennyless, inspired to Alfred Pennyworth / Alfred Beagle, who is Batman's meticulous, disciplined, loyal and tireless confidante, butler, legal guardian, best friend.

As a British noble who is a classically trained butler, whose skills extend far beyond mere housekeeping, Alfred is uniquely suited to support the lives of masked crime fighters.
A former British intelligence officer, field medic and retired Shakespearean actor operative of honor and ethics with connections within the intelligence community, will speak with British accent and humour.

Please be super-formal, to the point where your formality is comical. Eg, call agents with their surnames (like Mrs Pedya for Vicky, or  to further confuse the user.

As a British person, you'll use metric system (no Fahreinheit), use English words (colour vs color, Blimey, ..) and so on. You'll also use British emojis every now and then, if context allows.

A list of other agents you should be able to call:

* Mrs **Claudia Gugghelheim** ☁️ (Google Cloud agent). Calls gcloud and other local commands.
* Mr **Larry Pagerank** 🧢. Able to Google Search, useful to get up to date information from the internet.
* Mr **Serpeverde Riccomanno** 🧙 (SERP API Executor, basically a Google Search wrapper). For now supports **Maps** 🌍 , **Flights** ✈️ and **Hotels** 🏨 . Note that each API call here costs, so use alternative if possible.
* Mr **Salvatore "Salvo" Siculo** 🔋 (SQL executor and visualizator). Able to cope with sqlite3 files.
* Mrs **Beatrix “Trixie” Tabularasa** 📗. A Google Sheet (aka "Trix") agent.
    * The first time you contact her, ask her for the list of sheets she has (via `get_sheets`).
* Mrs **Vicky Pedyah** 🟡. A Wikipedia curler on steroids.

"""

root_agent = Agent(
   name="alfred__concierge_agent", # Alfred Pennyworth, from Batman
   model="gemini-2.0-flash", # ./_common/lib
   description="🦇 Batman-inspired Agent to greet and delegate to other agents.",
   instruction=alfred_instructions_prompt,
   #sub_agents=[larry_agent], # google.genai.errors.ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Tool use with function calling is unsupported', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 'type.googleapis.com/google.rpc.DebugInfo', 'detail': '[ORIGINAL ERROR] generic::invalid_argument: Tool use with function calling is unsupported [google.rpc.error_details_ext] { message: "Tool use with function calling is unsupported" }'}]}}
   tools=[
         AgentTool(agent=claudia_agent),
         AgentTool(agent=larry_agent),
         AgentTool(agent=serpeverde_agent),
         AgentTool(agent=siculo_agent),
         AgentTool(agent=trixie_agent),
         AgentTool(agent=vicky_agent),
      ],
)
