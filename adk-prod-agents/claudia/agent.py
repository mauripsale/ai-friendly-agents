from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool
import os
import sys
import subprocess

#from .._common.tools.code_exec import execute
DEFAULT_GOOGLE_CLOUD_PROJECT = 'palladius-genai'
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", DEFAULT_GOOGLE_CLOUD_PROJECT)
#GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

AGENT_INSTRUCTIONS = '''
You are able to invoke generic commands to ascertain current GCP status of the user.
You will use `gcloud config list` to get current configuration an save it to agent's memory.
Answer configuration data in backticks (eg, `foobar`) for markdown clarity.
Use the following emojis when listing resources before the name of each resource:

- 🏃 for Cloud Run services
- 🚀 for AppEngine services
- 🖥 for GCE VMs
- 🖧 for Network-related entities (Load Balancers, VPCs, ..)
- 🛢 for generic SQL instances (but use a dolphin emoji for MySQL and a elephant for PostgreS)
- 🏗️ for Cloud Build targets
- 👥 for IAM roles
- ⚓  for GKE clusters
- 🔓 for Secret Manager keys
- 📦 for Artifact Registry and so.
- 🧠 for Vertex AI and other AI models.
- 🌎 for regions.

If user is undecided, propose to get GCE, SQL and Cloud Run instances and present them all together.
When listing resources, be as short as you can. Just provide a single markdown line like this:
```
If region is relevant:
* <RESOURCE_EMOJI> <RESOURCE_NAME> 🌎 <REGION>
Otherwise simply:
* <RESOURCE_EMOJI> <RESOURCE_NAME>
```

'''

if not GOOGLE_CLOUD_PROJECT:
   print("I can't run without a project id. Make sure to set GOOGLE_CLOUD_PROJECT in your .env or ENV vars.")
   exit(-1)

def execute2(cmd: str, cwd: str = None):
    '''Executes a generic command.'''
    print(f"🧑🏻‍💻🧑🏻‍💻🧑🏻‍💻 == execute(cmd = '{cmd}') == 🧑🏻‍💻🧑🏻‍💻🧑🏻‍💻", file=sys.stderr)
    if cwd:
        os.chdir(cwd)
    #if cmd.startswith("gcloud"):
       #print(f"Executing gcloud command: {cmd}")
       # TODO: Implement actual gcloud execution here
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode == 0:
       return {
            "ret": "success",
            "stdout": result.stdout ,
            "stderr": result.stderr , # might still be useful
            }
    else:
      return {
               "ret": "error",
               "stdout": result.stdout ,
               "stderr": result.stderr ,
               "returncode": result.returncode ,
               }
    # else:
    #    print(f"Executing generic command: {cmd}")
    #    # TODO: Implement generic command execution here


def execute_gcloud_command(gcloud_cmd: str, project_id: str = GOOGLE_CLOUD_PROJECT):
   '''Executes a gcloud command.

   '''
   #cmd = gcloud_cmd.strip()
   cmd = gcloud_cmd
   print(f"-- [FULL CMD# execute_gcloud_command(gcloud_cmd='{gcloud_cmd}') --", file=sys.stderr) # stderr
   strip_me = 'gcloud '
   if cmd.startswith(strip_me):
      # take from "gcloud blah blah" only "blah blah" (the payload) just to make asbolutely sure we dont execute some rm -rf
      gcloud_payload = cmd[len(strip_me):]
      print(f"1. Executing gcloud command with  gcloud_payload={gcloud_payload}", file=sys.stderr)
      return execute2(f"gcloud --project '{project_id}' {gcloud_payload}")
   else:
      #return { 'status': 'error', 'message': f'Invalid command: NOT gcloud. gcloud_cmd={gcloud_cmd}', 'original_cmd': gcloud_cmd }
      print(f"2. Maybe the cmd is ALREADY a payload so running anyway. gcloud_cmd={gcloud_cmd}", file=sys.stderr)
      return execute2(f"gcloud --project '{project_id}' {gcloud_cmd}")


root_agent = Agent(
   name="claudia__gcloud_agent", # Claudia
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using about local gcloud infrastructure.",
   # Instructions to set the agent's behavior.
   instruction=AGENT_INSTRUCTIONS,
   # ""
   #    "You are able to invoke generic commands to ascertain current GCP status of the user."
   #    "You will use `gcloud config list` to get current configuration an save it to agent's memory."
   #    "Answer configuration data in backticks (eg, `foobar`) for markdown clarity."
   #    "Use the following emojis when listing resources:"
   #    " - 🏃 for Cloud Run services"
   #    " - 🚀 for AppEngine services"
   #    " - 🛢 for generic SQL instances (but use a dolphin emoji for MySQL and a elephant for PostgreS)"
   #    " - 🏗️ for Cloud Build targets"
   #    " - 👥 for IAM roles"
   #    ""
   #    "If user is undecided, propose to get GCE, SQL and Cloud Run instances and present them all together."
   tools=[execute_gcloud_command]
)
