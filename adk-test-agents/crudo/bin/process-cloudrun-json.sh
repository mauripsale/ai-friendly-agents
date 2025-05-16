#!/bin/bash

# --- process-cloudrun-json.sh ---
# Desc: Takes the JSON inventory of Cloud Run services and outputs
#       a tab-separated list of Project ID, Service Name, and Console URL.
# Requires: jq (JSON processor)

INPUT_JSON="${1:-cloud_run_services_inventory4user.json}"

# --- Safety Checks ---
# 1. Is jq installed?
if ! command -v jq &> /dev/null; then
    echo "💥 Oopsie! The command 'jq' was not found." >&2
    echo "   Please install jq to process the JSON. (e.g., 'sudo apt-get install jq' or 'brew install jq')" >&2
    exit 1
fi

# 2. Does the input file exist?
if [[ ! -f "$INPUT_JSON" ]]; then
    echo "💥 Whoops! Input file '$INPUT_JSON' not found." >&2
    echo "   Did you run the first Ruby script to generate it?" >&2
    exit 1
fi

echo "📊 Processing '$INPUT_JSON' to generate service list with URLs..."
echo

# --- Header ---
# Use printf for potentially better tab handling across systems
printf "Project ID\tService Name\tCloud Run Console URL\n"
printf "----------\t------------\t---------------------\n"

# --- Processing with jq ---
# -r = raw output (strings without quotes)
#
# Logic breakdown:
# 1. to_entries[]             -> Stream each project {key: "proj_id", value: data}
# 2. select(.value | type == "array") -> Only keep projects where 'value' is an array (i.e., has services listed, not an error)
# 3. select(.value | length > 0) -> Further filter to only those with *at least one* service in the array
# 4. .key as $project_id       -> Store the project ID (key) in a variable $project_id
# 5. .value[]                 -> Iterate through each service object in the 'value' array
# 6. select(.name and .region) -> Make sure the service object actually has name and region (robustness)
# 7. .name as $service_name | .region as $region -> Store name and region in variables
# 8. Construct the output string using variables, separated by tabs (\t)
#    The URL is built using the standard Cloud Console pattern.
jq -r '
  to_entries[]
  | select(.value | type == "array" and length > 0)
  | .key as $project_id
  | .value[]
  | select(.name and .region)
  | .name as $service_name | .region as $region
  | "\($project_id)\t\($service_name)\t\( "https://console.cloud.google.com/run/detail/\($region)/\($service_name)?project=\($project_id)" )"
' "$INPUT_JSON"

echo
echo "✅ Done! You can now easily navigate to your services."

