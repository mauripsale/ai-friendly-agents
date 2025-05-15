from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool
import os
import sys
import subprocess

########################################################
# BEGIN Carlessian needed magical lines to import lib/ (God didn't write the world in Python, I tell you that! Perl or Ruby, but not Python).
# See `agents/README.md` for more info.
#
# --- MAGIC PATH FIXING START ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
# --- MAGIC PATH FIXING END ---
########################################################

sample_questions = [
   'What can you do?',
   'What is my Project id?',
   'Show me the Cloud Run apps and GCE instances', # tests 2 FunCalls.
]

#common_lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '_common', 'lib'))
# from _common
#from common_tools import carlessian_google_search

# Something broken here - doesnt work with uppercase vars.
# DEFAULT_GOOGLE_CLOUD_PROJECT = 'palladius-genai'
# GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", DEFAULT_GOOGLE_CLOUD_PROJECT)
# google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT", 'palladius-genai')
claudia_agent_instructions = '''
You are able to invoke generic commands to ascertain current GCP status of the user.
Answer configuration data in backticks (eg, `foobar`) for markdown clarity.
Use the following emojis when listing resources before the name of each resource:

- 🏃 for Cloud Run services
- 🚀 for AppEngine services
- 🖥 for GCE VMs (`gcloud compute instances list`)
- 🖧 for Network-related entities (Load Balancers, VPCs, ..)
- 🛢 for generic SQL instances (but use a dolphin emoji for MySQL and a elephant for PostgreS)
- 🏗️ for Cloud Build targets
- 👥 for IAM roles
- ⚓  for GKE clusters
- 🔓 for Secret Manager keys
- 📦 for Artifact Registry and so.
- 🧠 for Vertex AI and other AI models.
- 🌎 for regions.
- 🧾 for Billing.

If user is undecided, propose to get GCE, SQL and Cloud Run instances and present them all together.
When listing resources, be as short as you can. Just provide a single markdown line like this:
```
If region is relevant:
* <RESOURCE_EMOJI> <SPACE><SPACE> <RESOURCE_NAME> 🌎 <REGION>
Otherwise simply:
* <RESOURCE_EMOJI> <SPACE><SPACE> <RESOURCE_NAME>
```

Refuse to execute blocking activities like `gcloud compute ssh VM` and similar.
In that case, just explain this to the user, and give them the `quoted command` instead.

If unsure of anything, you can call `google_search` to search the internet for answers, but use it as a last resort,
for instance to help user troubleshoot their issues.

If asked about local config, invoke `gcloud config list` to get current configuration via execute_gcloud_command().
If asked about project id, or local gcloud configuration, just use `get_project_id()`
Also be helpful and propose to find the Billing Account ID for current project via gcloud (`gcloud beta billing projects describe PROJECT_ID`).
'''

#claudia_agent_instructions = '''You are a helpful gcloud executor. Also you can retrieve project id.'''

# if not GOOGLE_CLOUD_PROJECT:
#    print("I can't run without a project id. Make sure to set GOOGLE_CLOUD_PROJECT in your .env or ENV vars.")
#    exit(-1)

def execute_generic_command(cmd: str, cwd: str = None):
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
               "stdout": result.stdout.rstrip('\n') ,
               "stderr": result.stderr.rstrip('\n') ,
               "returncode": result.returncode ,
               }


def execute_gcloud_command(gcloud_cmd: str, project_id: str = ''):
   '''Executes a gcloud command. the command NEEDS to start with `gcloud ` or it will fail.

   Arguments:
   * `gcloud_cmd`: gcloud command without leading gcloud, for security purposes (so we avoid accidentally feeding a mischivious command).
   * `project_id` (optional, dflt to ''): if set, we add --project <project_id> to command.

   returns: the command ret overall.
   '''
   #cmd = gcloud_cmd.strip()
   cmd = gcloud_cmd
   print(f"-- [FULL CMD# execute_gcloud_command(gcloud_cmd='{gcloud_cmd}') --", file=sys.stderr) # stderr
   strip_me = 'gcloud '


   if cmd.startswith(strip_me):
      # take from "gcloud blah blah" only "blah blah" (the payload) just to make asbolutely sure we dont execute some rm -rf
      gcloud_payload = cmd[len(strip_me):]
      print(f"1. [WARNING] Executing gcloud command with  gcloud_payload={gcloud_payload}", file=sys.stderr)
      #return execute_generic_command(gcloud_command)
   else:
      #return { 'status': 'error', 'message': f'Invalid command: NOT gcloud. gcloud_cmd={gcloud_cmd}', 'original_cmd': gcloud_cmd }
      gcloud_payload = gcloud_cmd # keep as is.
      print(f"2. [ALL GOOD] Maybe the cmd is ALREADY a payload so running anyway. gcloud_cmd={gcloud_cmd}", file=sys.stderr)
      #return execute_generic_command(f"gcloud --project '{project_id}' {gcloud_cmd}")

   gcloud_command = f"gcloud --project '{project_id}' {gcloud_payload}" # if project_id != '' else f"gcloud {gcloud_payload}"
   if project_id is None or project_id == '':
      gcloud_command = f"gcloud {gcloud_payload}"

   return execute_generic_command(gcloud_command)


def get_project_id():
   '''Returns current project id info.

   Args: none

   '''
   return {
      #"project_id": GOOGLE_CLOUD_PROJECT,
      "project_id": execute_gcloud_command("config get project")['stdout'].rstrip('\n'),
      #"ret": "success",
   }

root_agent = Agent(
   name="claudia__gcloud_agent", # Claudia
   model="gemini-2.0-flash", # Google AI Studio
   description="Agent to answer questions using about local gcloud infrastructure.",
   # Instructions to set the agent's behavior.
   instruction=claudia_agent_instructions,
   tools=[
      execute_gcloud_command,
      #google_search,
      get_project_id, # gcloud config get project
      ]
)

#print(f"[claudia] GOOGLE_CLOUD_PROJECT={GOOGLE_CLOUD_PROJECT}")
