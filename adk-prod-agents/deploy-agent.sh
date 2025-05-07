
set -euo pipefail

# agent name and also FOLDER. keeping it simple.
AGENT="$1"
SVC_NAME="adk-$AGENT"
# for now, region and user are grounded.

# DOES NOT WORK
GOOGLE_IAP_EXPRESSION3_DOESNT_WORK='("accessPolicies/518551280924/accessLevels/google_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_corp_ips" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_prod_ips" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/not_blocklisted_device_prodData" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/not_embargoed" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/not_embargoed_allowlist" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/not_embargoed_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/onsite_fullyTrusted_prodData" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/fullyTrusted_prodData_test_geo" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/onsite_minimallyTrusted_prodData" in request.auth.access_levels)'
GOOGLE_IAP_EXPRESSION1='("accessPolicies/518551280924/accessLevels/Google" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/Google_borg_sa_allowList" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/Google_corp_data_allowlist" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/caa_third_party_saas_app_enforced" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/caa_third_party_saas_app_enforced_with_basic" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/caa_third_party_saas_ios_device" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_corp_ips" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_prod_ips" in request.auth.access_levels)' # , TITLE=Google prod data VPC allowlist, access level for service perimeter Google to allow borg service accounts defined by each included project, Google corp data allowlist, Google-ThirdParty-SaaS-App-Enforced, Google-ThirdParty-SaaS-App-Enforced-With-Basic, Google-ThirdParty-SaaS-iOS-device, Corp IP Netblocks, Prod IP Netblocks
GOOGLE_IAP_EXPRESSION2='("accessPolicies/518551280924/accessLevels/accept_all" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/corp_critical_service_accounts_dev" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/corp_critical_service_accounts_prod" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_corp_ips" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/from_prod_ips" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/google_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/google_saml_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/google_wide_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/google_wide_saml_bypass" in request.auth.access_levels) || ("accessPolicies/518551280924/accessLevels/iap_mvp_service_accounts" in request.auth.access_levels)' # , TITLE=Accept All Access Level, Corp Service Accounts for Dev Instances of Critical Applications, Corp Service Accounts for Critical Applications Prod Tier, Corp IP Netblocks, Prod IP Netblocks, Google-Bypass, Google-SAML-Bypass, Google-WideBypass, Google-Wide-SAML-Bypass, IAP Service Accounts allowlist.



adk deploy cloud_run \
    --region="europe-west1" \
    --service_name="$SVC_NAME" \
    --with_ui \
    ./$AGENT

# BUG: Allow unauthenticated invocations to [adk-siculo] (y/N)?  y
# should be programmable via CLI, like --cloudrun-options="--allow.."

if [ -f .$AGENT.iap-already-setup.touch ] ; then
    echo IAP Already setup skipping.
else
    # First time
    echo First time set up IAP

    gcloud beta run services update "$SVC_NAME" \
        --region="europe-west1" \
        --iap

    echo ok. Now adding the binding.

    # if exists...
    if [ -f setup-iap-for-google.com-pvt.sh ]; then
        echo "google.com Riccardo script detected. Executing"
        ./setup-iap-for-google.com-pvt.sh "$1"
    fi

    gcloud beta iap web add-iam-policy-binding \
        --member=user:ricc@google.com \
        --role=roles/iap.httpsResourceAccessor \
        --region="europe-west1" \
        --resource-type=cloud-run \
        --service="$SVC_NAME" \
        --condition="expression=$GOOGLE_IAP_EXPRESSION1,title=Riccardo ADK Deploy Agent expr 1,description=Test Riccardo Google Internals to open IAP to himself from manhouse expr 1"


    #    --condition=expression=[expression],title=[title],description=[description].
    #  --condition='expression=request.time <
    #        timestamp("2019-01-01T00:00:00Z"),title=expires_end_of_2018,
    #        description=Expires at midnight on 2018-12-31'
    touch .$AGENT.iap-already-setup.touch
fi
