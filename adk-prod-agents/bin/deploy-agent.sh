
set -euo pipefail

set -x


VERSION="0.2"
# agent name and also FOLDER. keeping it simple.
AGENT="$1"
SVC_NAME="adk-$AGENT"
REGION="europe-west1"

# for now, region and user are grounded.

echo "🚀 [Deploy v$VERSION ng] ADK Service for '$AGENT' in project: $PROJECT_ID"

gcloud config set project "$PROJECT_ID"

echo Checking folder exists...

ls -al "agents/$AGENT"

# TODO: fix the allow authenticated, maybe there's a gcloud env var to set it as dflt?
# like:  gcloud config set run/allow_unauthenticated true
# https://cloud.google.com/sdk/gcloud/reference/config/set
# Allows just: cluster, cluster_location, platform and region. Damn.

adk deploy cloud_run \
    --region="$REGION" \
    --service_name="$SVC_NAME" \
    --with_ui \
    agents/$AGENT

# BUG: Allow unauthenticated invocations to [adk-siculo] (y/N)?  y
# should be programmable via CLI, like --cloudrun-options="--allow.."

if [ -f .$AGENT.iap-already-setup.touch ] ; then
    echo IAP Already setup skipping.
else
    # First time
    echo First time set up IAP

    gcloud beta run services update "$SVC_NAME" \
        --region="$REGION" \
        --iap

    echo ok. Now adding the binding.

    # if exists...
    if [ -f setup-iap-for-google.com-pvt.sh ]; then
        echo "[💛💛💛] google.com Riccardo script detected. Executing"
        ./setup-iap-for-google.com-pvt.sh "$1"
    fi

    touch .$AGENT.iap-already-setup.touch
fi
