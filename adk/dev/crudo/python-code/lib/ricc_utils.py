'''
Use me:

from lib.ricc_utils import save_to_file

'''

import json
from typing import Any
from . import ricc_colors as C  # Assuming ricc_colors.py is in the same directory

def save_to_file(filepath: str, data: Any):
    """Saves data to a file, handling different data types.

    Args:
        filepath: The path to the file where data should be saved.
        data: The data to be saved. Can be a string, dictionary, or list.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                f.write(data)
            elif isinstance(data, (dict, list)):
                json.dump(data, f, indent=4, default=str)  # Use json for structured data
            else:
                f.write(str(data))  # Fallback to string conversion
        print(f"{C.CACHE_ICON} {C.green('File saved successfully:')} {filepath}")
    except Exception as e:
        print(f"{C.ERROR_ICON} {C.red('Error saving to file:')} {filepath}: {e}")


def get_projects_by_user_faker(email: str):
    '''TODO ricc: make this better'''
    print("FIXME Riccardo - fix me with proper/smart project listing (nit: ricc@ sees 11k projects)")
    ricc_personal_projects =  [
        'palladius-genai',  # 272932496670 a few nice ones
        'pincopallo',
        'ric-cccwiki',
        'vulcanina',
        'ror-goldie', # plenty of PROD ones!
        ]
    ricc_work_projects = ricc_personal_projects + [
        'onramp-staging-379211',  # Onramp staging
        'serverlessusability', # Steve Fadden test one (PN: 291336490793)
        'ricc-genai', # empty
        #'amsterdam-demo-tmp-crun2049', # i believe this is just Riccardo's Cloud runner demo - useless.
        'cloud-runner-2049', # https://github.com/NucleusEngineering/2049/blob/main/.demoplate/project
                            # https://pantheon.corp.google.com/run/detail/europe-north1/cloud-runner-2049/metrics?e=TroubleshootingUiAdminLaunch::TroubleshootingUiAdminControl&invt=AbuTVA&mods=logs_tg_staging&project=cloud-runner-2049
    ]
    # if SvcAcct likely only its project will be available
    if email == 'cloudrun-ricc-devops-agent@onramp-staging-379211.iam.gserviceaccount.com':
        return [ 'onramp-staging-379211' ]
    if email == 'cloudrun-ricc-devops-agent@palladius-genai.iam.gserviceaccount.com':
        return [ 'palladius-genai' ]
    if email == 'palladiusbonton@gmail.com':
        return ricc_personal_projects
    if email == 'ricc@google.com':
        return sorted(ricc_work_projects)


# def my_projects():
#     my_email = `gcloud config get account`
#     return get_projects_by_user(my_email)

#
