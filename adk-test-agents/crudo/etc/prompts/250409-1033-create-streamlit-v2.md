* model: gemini 2.5 pro exp
* when: 16:50 on 8apr
* What: create a streamlit which integrates seamlessly with current code.
* permalink OLD: https://gemini.google.com/corp/app/1b6b3e4e7dba579e # old v1
* permalink new: https://gemini.google.com/corp/app/60f00378e95bac99 # this one
* meta: copiued from yesterday since I had some spandau.

## Prompt

I have an existing python application frontend which uses a number of files in lib/
and calls `main.py` and has constants in `constants.py`.
This is a responsive chat built with Gemini which investigates a Cloud Run application.

I would like to create a streamlit application and keep it tidy done this way:

`./app2.py` contains as little as possible to get started

Then I'd like to split all important stuff: UI, state, .. maybe left column in one file each:

`./lib/streamlit2/state.py` contain all the UI logic
`./lib/streamlit2/ui.py` contain all the UI logic
`./lib/streamlit2/...` for anything else you need.

Functionality:

* The app shall have this memory configured:

   * User Id (pick emoji): defaults to "ENV[USER]@google.com" - if unavailable, defaults to 'ricc@google.com'
   * Gemini Model (zodiac gemini emoji): defaults to ENV[GEMINI_MODEL] - if unavailable defaulst to 'gemini-1.5-flash'
   * Cloud Region (EMEA emoji): defaults to ENV[GOOGLE_CLOUD_LOCATION] and defaults to "europe-west1"
   * API_KEY (key emoji): defaults to ENV['GOOGLE_API_KEY'] - no default.

1. The app should have a left column/pane where you can store two things:

"⚙️ Configuration"

It will visualize the curretntly chose variables (user, model, region) and by clicking it you are able to edit them:
* edit email
* edit region
* choose model (dropdown choice between: "gemini-1.5-flash" and "gemini-2.0-flash")

📜 INVESTIGATIONS (chats)

   1. multiple conversations which we'll call "investigations". Each investigation is basically a new chat with Gemini
      LLM constructed. Every investigation is clickable and you can resume the conversation from where you left it (I'll
      need to persist it later, for now we can just persist to file)
   2. The investigation will visualize (and persist to a local convos.sqlite3 DB) all the conversations. This will be using
      Gemini with function_calling.
   3. If the function_calling returns a JSON with a `chart_filename` field (its a local Path() string), that Chart will be visualized directly in
      the conversation, which is the cool feature of this multimodal chat.
   4. The chat should be responsive (visualize chat chunk by chunk) - which is the main reason why I'm choosing streamlit.


🎯 PROJECT/CLOUDRUN_SERVICE chooser + and Service synoptic.

   1. First, a projectId chooser (say 'onramp'). It should probably look like a dropdown. We have a function to retrieve projects by user: `get_projects_by_user_faker(email: str)` in `lib/ricc_utils.py`
   2. Within the projectId chooser, a "CloudRun Endpoint" chooser: another dropdown fetching with `get_cloud_run_endpoints(project_id: str, region: str)`
   3. Once you select this, we can visualize a number of information which is relevant to this couple. I have text and images to portray for it. For instance,
        by looking at `.cache/palladius-genai/cloud-run/gemini-news-crawler-manhouse-prod/service.yaml` you can find some interesting fields
        for project 'palladius-genai' and service 'gemini-news-crawler-manhouse-prod', like the "urls:" stanza contains an array of its public URLs.
   4. In a subfolder: `.cache/palladius-genai/cloud-run/gemini-news-crawler-manhouse-prod/mon-charts/`, you have a number of monitoring charts which I'd like to also
      show there. Finally, there should be a button like "Start an investigation for this Endpoint" which creates a new investigation (=chat) for this
      particular ProkjectId, Region, and CloudRun Service (=endpoint).

From a route perspective, I envision these possible routes:

GET /                                            Shows some convenient home
GET /:project_id/:service_id/index               Shows synoptic of per-project per-service synoptic, with Cloud Run service config, top info, and graphs.
GET /:project_id/:service_id/:investigation_id/index Shows chat history by talking with Gemini, which is resumable. It shows text back and forth and attached charts.
                                                   This chat is persisted on DB.
=================================

Current files:

ricc@derek:~/l300/01-prova-python$ ls -al *py
-rw-r--r-- 1 ricc primarygroup 2636 Apr  4 18:45 constants.py
-rwxr-xr-x 1 ricc primarygroup 9408 Apr  4 19:00 main.py
-rw-r--r-- 1 ricc primarygroup 6522 Apr  3 12:51 main_test.py
-rw-r--r-- 1 ricc primarygroup 1180 Apr  2 10:55 test_chat.py

ricc@derek:~/l300/01-prova-python$ ls -al lib/*py
-rw-r--r-- 1 ricc primarygroup    28 Apr  1 11:30 lib/__init__.py
-rw-r--r-- 1 ricc primarygroup    49 Apr  3 10:07 lib/ricc_cache.py
-rw-r--r-- 1 ricc primarygroup 48216 Apr  4 18:54 lib/ricc_cloud_monitoring.py
-rw-r--r-- 1 ricc primarygroup  3524 Apr  4 18:43 lib/ricc_cloud_monitoring_test.py
-rw-r--r-- 1 ricc primarygroup 30926 Apr  4 16:20 lib/ricc_cloud_run.py
-rw-r--r-- 1 ricc primarygroup  7139 Apr  3 10:32 lib/ricc_cloud_run_test.py
-rw-r--r-- 1 ricc primarygroup  1781 Apr  3 11:56 lib/ricc_colors.py
-rw-r--r-- 1 ricc primarygroup  4271 Apr  8 15:46 lib/ricc_gcp_projects.py
-rw-r--r-- 1 ricc primarygroup   772 Apr  8 15:40 lib/ricc_gcp.py
-rw-r--r-- 1 ricc primarygroup 18493 Apr  4 19:17 lib/ricc_genai.py
-rw-r--r-- 1 ricc primarygroup  1246 Apr  4 08:38 lib/ricc_net.py
-rw-r--r-- 1 ricc primarygroup  2812 Apr  4 08:38 lib/ricc_net_test.py
-rw-r--r-- 1 ricc primarygroup  4314 Apr  4 18:54 lib/ricc_protobuf_converter.py
-rw-r--r-- 1 ricc primarygroup  1816 Apr  4 18:12 lib/ricc_system.py
-rw-r--r-- 1 ricc primarygroup  2013 Apr  8 15:37 lib/ricc_utils.py

=================================

Some more things:

1. Do not trigger a Welcome investigation when I select project+cloud run. Instead, I would like to visualize a synoptic page on the right (main page). This page should first get the service.yaml into a dictionary, then visualize:
   * a CPU icon with a dictionary lookup Service_dict (`cat service.yaml | yq .template.containers[0].resources.limits.cpu`)
   * a RAM icon with a lookup from service.yaml  (`cat service.yaml | yq .template.containers[0].resources.limits.cpu`)
   * an Array of ENV key-values: (`cat service.yaml | yq .template.containers[0].env -> array of [name, value])
   * BaseImageURI: `cat service.yaml | yq .template.containers[0].baseImageUri`)

2. After this synoptic page, we can put a green button like: "Start an investigation" plus N yellow buttons with
   "Continue investigation <TITLE>" for all conversation for this same project/service.

The code snippet to generate a Chat Session is here:

```python
from lib.ricc_genai import GeminiChatSession
chat_session = GeminiChatSession(
            project_id=project_id,
            region=region,
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=model,
            debug=True
        )
ret = chat_session.send_simple_message(user_input)
```
