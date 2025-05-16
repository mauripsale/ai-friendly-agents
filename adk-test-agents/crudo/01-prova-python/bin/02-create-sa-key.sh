# Make sure you are operating in the correct project context first!
# EITHER set it globally (if you only have one config active):
# gcloud config set project your-gcp-project-id

# OR specify the project for this command if you have multiple configs:
# gcloud config set project your-gcp-project-id --configuration=YOUR_CURRENT_CONFIG_NAME

set -euo pipefail

# Define variables (replace with your actual project)
#export MYPROJECT="${1:-palladius-genai}" # Or the project you want the key for
export MYPROJECT="${1:-onramp-staging-379211}" # Or the project you want the key for
export SA_NAME="cloudrun-ricc-devops-agent"
export SA_EMAIL="${SA_NAME}@${MYPROJECT}.iam.gserviceaccount.com"
export KEY_FILE_PATH="./private/${MYPROJECT}-${SA_NAME}-key.json" # Choose a path/name

echo "Creating key file for ${SA_EMAIL} in project ${MYPROJECT}..."
echo "Key will be saved to: ${KEY_FILE_PATH}"
echo "If this fail, probably you failed to create the SA before: $SA_EMAIL. Call provision-agent-sa.sh first!"

# Create the key
gcloud iam service-accounts keys create "${KEY_FILE_PATH}" \
    --iam-account="${SA_EMAIL}" \
    --project="${MYPROJECT}"

echo "✅ Key file created at ${KEY_FILE_PATH}. GUARD IT WELL! 💂‍♀️"



#MYPROJECT="$1"

# Define the configuration name using the project ID
export CONFIG_NAME="devops-sa-for-${MYPROJECT}"

echo "Creating gcloud configuration: ${CONFIG_NAME}..."
gcloud config configurations create "${CONFIG_NAME}" ||
    gcloud config configurations activate "${CONFIG_NAME}"
# Note: This automatically activates the new configuration.

echo "Setting project property within ${CONFIG_NAME}..."
gcloud config set project "${MYPROJECT}"

echo "Activating Service Account ${SA_EMAIL} within configuration ${CONFIG_NAME} using key ${KEY_FILE_PATH}..."
gcloud auth activate-service-account --key-file="${KEY_FILE_PATH}"
# Note you need to run it multiple times
# This command sets the 'account' property in the current configuration (CONFIG_NAME) to the SA.

echo "✅ Configuration ${CONFIG_NAME} created and activated."
echo "   Project set to: ${MYPROJECT}"
echo "   Active account set to: ${SA_EMAIL}"

# Verify (optional)
echo "Current gcloud configuration:"
gcloud config list
