I want to create an application in Python which is able to use
`google-genai` capabilities to assess my Cloud Run app on GCP in current PROJECT_ID,
provided via `.env`.

I want to use function calling to provide the following Cloud run functionality:

1. Get all Cloud Run endpoints for a project (input: project_id(STRING)). Endpoint  should be a FQDN containing also project_id
2. Get all Cloud Run Versions for a Run endpoint (input: endpoint_fqdn(STRING))
3. Get all Logs for a Run version (input: endpoint_fqdn(STRING)). Output should also be a run_version_fqdn containing project and endpoint name in it.
4. Get YAML configuration for a single Run version (contains all important metadata like: date of launch, principal which launched it, ENV configuration, and so on.)
   Again, input: endpoint_fqdn
5. Get logs for a single run endpoint+version.

Since API calls take time, particularly for logs, all data should be cached locally and deterministically in form of files, in an intelligently nested way, for instance:

Caching file system sample:

* .cache/<PROJECT_ID>/cloud-run/endpoints.json
* .cache/<PROJECT_ID>/cloud-run/<ENDPOINT_NAME>/versions.json
* .cache/<PROJECT_ID>/cloud-run/<ENDPOINT_NAME>/<VERSION_NAME>/config.yaml
* .cache/<PROJECT_ID>/cloud-run/<ENDPOINT_NAME>/<VERSION_NAME>/YYYYMMDD-HHMMSS-logs.txt

Function call should check for cache hit, with obsolescence of 1 hour.
Function calls will have an optional `ignore_cache: False` by default. If true, they will bypass cache,
for instance when super-fresh logs need to be checked.

Please write the skeleton code, providing this:

* .env
* requirements.txt
* main.py                 # simple main with just ARGV processing.
* lib/ricc_colors.py      # contains yellow(str), green(str), .. simple functionality
* lib/ricc_cloud_run.py   # contains all Cloud Run functions
* lib/ricc_genai.py       # contains all Gemini genai calls.
* You can come up with additional files, under `lib/`

The main interface should be a CLI chat. A debug/verbose toggle should enable us to show debug messages
and verbose should enable/disable a STDOUT log of Gemini Function Calling.

A chat should look something like:

🧑: “How are my Cloud Run endpoints doing?”
⚒️ <fc: retrieve cloud run endpoints and last 10 revisions each>
♊:: you have “myapp-dev” and “myapp-prod”, both deployed 7 minuets ago. PROD is in good standing, but dev update didn't work, so Run is still running the previous version.
🧑:User: Can you tell me what went wrong there?
⚒️ <fc: retrieve logs for “myapp-dev”(N) and  “myapp-dev”(N-1) and also metadata YAML  for both>
♊:The logs from latest version claim there is not sufficient memory. No other ENV variables have been changed that I know of. I can suppose the new docker image requires more RAM. You can try to increase the CRun RAM with this gcloud run update … command. Would you like me to do it for you? If yes, please tell me that you’re sure and the name of the app.
🧑:Yes, I’m sure, for “myapp-dev”.
⚒️ <fc: updates Cloud Run with 4x RAM>
♊: Done. [Since this is a low risk.]

