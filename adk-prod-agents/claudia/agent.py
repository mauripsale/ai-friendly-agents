from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

#from .._common.tools.code_exec import execute

def execute(cmd: str, cwd: str = None):
   pass
   print(f"TODO - implement execute of: '{cmd}'")
   return { "ret": "success", "result": "my-project-id-todo" }


def execute_gcloud_command(gcloud_cmd: str):
   return execute("gcloud " + gcloud_cmd)


root_agent = Agent(
   name="claudia__gcloud_agent", # Claudia
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using about local gcloud infrastructure.",
   # Instructions to set the agent's behavior.
   instruction=""
      "You are able to invoke generic commands to ascertain current GCP status of the user."
      "You will use `gcloud config list` to get current configuration an save it to agent's memory."
      "Answer configuration data in backticks (eg, `foobar`)."
      "",
      #"You speak with an Italian accent and add itailan emojis all the time.",
   # Add google_search tool to perform grounding with Google search.
   tools=[execute_gcloud_command]
)
