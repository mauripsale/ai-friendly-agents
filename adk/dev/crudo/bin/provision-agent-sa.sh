#!/bin/bash

# sbrodola.sh - Creates and configures the DevOps Agent Service Account
# Usage:
#   ./sbrodola.sh [TARGET_PROJECT_ID]
#
# If TARGET_PROJECT_ID is provided, it uses that project.
# Otherwise, it attempts to use the project set in gcloud config.

# Example: bin/sbrodola.sh onramp-staging-379211

set -e # Exit immediately if a command exits with a non-zero status.
set -u # Treat unset variables as an error when substituting.
# set -o pipefail # Causes a pipeline to return the exit status of the last command in the pipe that failed

# --- Configuration ---
SA_NAME="cloudrun-ricc-devops-agent"
SA_DISPLAY_NAME="Cloud Run DevOps Agent (go/crun-devops-agent-ug)" # Super-Smart link to User Guide! wOOt!
SA_DESCRIPTION="Service account for Python agent to monitor and troubleshoot Cloud Run, view logs/metrics, and query BQ."
# Get the currently authenticated user - this user will be allowed to impersonate the new SA
IMPERSONATING_USER=$(gcloud config get-value account 2>/dev/null || echo "") # Handle potential error if not logged in

# --- Helper Functions (with colors! ✨) ---
# Define some colors using tput
C_RESET=$(tput sgr0 || echo "") # Add fallbacks for non-tty
C_BOLD=$(tput bold || echo "")
C_GREEN=$(tput setaf 2 || echo "")
C_YELLOW=$(tput setaf 3 || echo "")
C_CYAN=$(tput setaf 6 || echo "")

info() {
    echo "${C_CYAN}${C_BOLD}INFO:${C_RESET} $1"
}

warn() {
    echo "${C_YELLOW}${C_BOLD}WARN:${C_RESET} $1"
}

success() {
    echo "${C_GREEN}${C_BOLD}SUCCESS:${C_RESET} $1"
}

# --- Determine Project ID ---
PROJECT_ID=""
SOURCE_MSG=""
if [[ -n "${1:-}" ]]; then # Check if $1 (first argument) is set and not empty
    PROJECT_ID="$1"
    SOURCE_MSG="(from command line argument)"
    info "Using Project ID specified via command line: ${PROJECT_ID}"
else
    info "No Project ID provided via argument, attempting to use gcloud config..."
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "") # Avoid noisy error if not set
    if [[ -n "${PROJECT_ID}" ]]; then
        SOURCE_MSG="(from gcloud config)"
        info "Using Project ID from gcloud config: ${PROJECT_ID}"
    else
        PROJECT_ID="your-gcp-project-id" # Set placeholder if gcloud config fails or is empty
        SOURCE_MSG="(NOT FOUND - Using Placeholder)"
        warn "Could not determine Project ID from gcloud config."
    fi
fi


# --- Sanity Checks ---
if [[ "${PROJECT_ID}" == "your-gcp-project-id" ]] || [[ -z "${PROJECT_ID}" ]]; then
    warn "Project ID is invalid or missing."
    warn "Please set it via 'gcloud config set project YOUR_PROJECT_ID' or provide it as the first argument to this script:"
    warn "Usage: $0 [TARGET_PROJECT_ID]"
    exit 1
fi

if [[ -z "${IMPERSONATING_USER}" ]]; then
    warn "Could not determine the current gcloud authenticated user. Please run 'gcloud auth login' or 'gcloud auth activate-service-account'."
    exit 1
fi

info "Effective Project ID: ${PROJECT_ID} ${SOURCE_MSG}"
info "Service Account Name: ${SA_NAME}"
info "User to grant impersonation rights: ${IMPERSONATING_USER}"
echo "--------------------------------------------------"
# Make confirmation message clearer about the project being used
read -p "Proceed with creating/updating SA in project '${PROJECT_ID}'? (y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
echo "--------------------------------------------------"


# --- Main Logic ---

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Create the Service Account (if it doesn't exist)
info "Attempting to create Service Account: ${SA_NAME} in project ${PROJECT_ID}"
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" > /dev/null 2>&1; then
    warn "Service Account ${SA_EMAIL} already exists in project ${PROJECT_ID}. Skipping creation."
else
    gcloud iam service-accounts create "${SA_NAME}" \
        --project="${PROJECT_ID}" \
        --display-name="${SA_DISPLAY_NAME}" \
        --description="${SA_DESCRIPTION}"
    success "Service Account ${SA_EMAIL} created in project ${PROJECT_ID}."
fi

# 2. Grant IAM Roles to the Service Account
info "Granting IAM roles to ${SA_EMAIL} in project ${PROJECT_ID}..."

ROLES=(
    "roles/viewer"              # Project-level read-only access
    "roles/run.viewer"          # View Cloud Run services, revisions, jobs, etc.
    "roles/logging.viewer"      # View logs
    "roles/monitoring.viewer"   # View monitoring dashboards and data
    "roles/bigquery.dataViewer" # Read data from BigQuery tables
    "roles/bigquery.jobUser"    # Run BigQuery jobs (like queries)
    # Add any other specific *read-only* or troubleshooting roles needed here
    "roles/vertexai.user"       # Adedd by Ricc to be able to use Vertex. Note Gemini1.5 doesnt work for some projects like onramp-staging.
)

for ROLE in "${ROLES[@]}"; do
    info "--> Granting role: ${ROLE}"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${ROLE}" \
        --condition=None # Explicitly setting no condition
done

success "Granted necessary IAM roles to ${SA_EMAIL} in project ${PROJECT_ID}."

# 3. Grant the *current user* permission to impersonate the new Service Account
info "Granting impersonation permission (${C_BOLD}roles/iam.serviceAccountTokenCreator${C_RESET}) to ${C_BOLD}${IMPERSONATING_USER}${C_RESET} on SA ${C_BOLD}${SA_EMAIL}${C_RESET}..."
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
    --project="${PROJECT_ID}" \
    --member="user:${IMPERSONATING_USER}" \
    --role="roles/iam.serviceAccountTokenCreator"

success "User ${IMPERSONATING_USER} can now impersonate ${SA_EMAIL} in project ${PROJECT_ID}."
echo "--------------------------------------------------"
success "🎉 All done! Service account ${SA_NAME} is ready for impersonation in project ${PROJECT_ID}."
echo "--------------------------------------------------"
