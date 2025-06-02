import os
import logging
from .lib.ricc_colors import darkgray
#from .lib.ricc_protobuf_converter import ProtobufConverter

from .lib.ricc_cloud_run import get_cloud_run_revisions, get_cloud_run_endpoints, get_cloud_run_logs, get_cloud_run_logs_for_date
from .lib.ricc_gcp import default_project_and_region_instructions
from .lib.ricc_system import current_time, current_place
from .lib.ricc_net import check_url_endpoint
from .lib.ricc_cloud_monitoring import * # RiccCloudMonitoring, gfc_generate_cloud_run_requests_vs_latency_chart, gfc_generate_cloud_run_instance_chart, gfc_generate_cloud_run_network_chart
from .lib.tools.wietse_gcloud import execute_gcloud_command

from dotenv import load_dotenv
load_dotenv()
# Configure the logger
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)

# This might come from a different env... we might have to re-define it in main.
#if not GOOGLE_CLOUD_PROJECT:
if 'GOOGLE_CLOUD_PROJECT' not in globals():
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
#if not GCP_REGION:
GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", 'gemini-2.0-flash-001')
FAVORITE_CLOUD_RUN_SERVICE = os.getenv("FAVORITE_CLOUD_RUN_SERVICE", None)
CONSTANTS_DEFINED_IN = 'constants.py' # redefinable, sweet!
DOTENV_DESCRIPTION = os.getenv("DOTENV_DESCRIPTION")
CONSTANTS_VERSION = '2.0'

# def setup_env_variables_from_dotenv(dotenv_filename):
#     GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
#     GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
#     GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
#     GEMINI_MODEL = os.getenv("GEMINI_MODEL", 'gemini-2.0-flash-001')
#     FAVORITE_CLOUD_RUN_SERVICE = os.getenv("FAVORITE_CLOUD_RUN_SERVICE", None)

DEBUG = False

# Create a global instance of the converter
RCM = RiccCloudMonitoring()

##########################################################################################
# Note: the meta prompt is in: `01-prova-python/etc/strict_project_region_instructions.prompt`
##########################################################################################
RICC_SIMPLIFIED_FUNCTIONS = [
    # defauilt stuff
    default_project_and_region_instructions,
    current_time, # good for RAG and Logs context.
    current_place, # good to know WHERE user is, and their TZ prefs.
    check_url_endpoint, # good to test if it actually works E2E
    get_cloud_run_endpoints,
    get_cloud_run_revisions,
    get_cloud_run_logs,
    #get_cloud_run_logs_for_date,
    #TODO_SOON get_cloud_run_config,
    #TODO_LATER update_cloud_run_memory
    # Cloud Monitoring
    gfc_generate_cloud_run_requests_vs_latency_chart,
    gfc_generate_cloud_run_instance_chart,
    gfc_generate_cloud_run_network_chart,
    gfc_generate_cloud_run_cpu_memory_chart,
    # def get_cloud_run_endpoints(project_id: str, region: str, ignore_cache: bool = False) -> Dict[str, Any]:
    # def get_cloud_run_revisions(project_id: str, region: str, service_name: str, max_results: int = 10, ignore_cache: bool = False) -> Dict[str, Any]:
    # def get_cloud_run_config(project_id: str, region: str, service_name: str, revision_name: str, ignore_cache: bool = False) -> Dict[str, Any]:
    # def get_cloud_run_logs(project_id: str, region: str, service_name: str, revision_name: str, ignore_cache: bool = False, hours_ago: int = 1) -> Dict[str, Any]:
    # def update_cloud_run_memory(project_id: str, region: str, service_name: str, memory_limit: str) -> Dict[str, Any]:

    # Generic gcloud command...
    execute_gcloud_command,  # from

]


def deb(str):
    global DEBUG
    if DEBUG:
        print(f"#DEBUG# {darkgray(str)}")

