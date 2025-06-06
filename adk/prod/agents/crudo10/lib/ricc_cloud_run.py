# lib/ricc_cloud_run.py
# Does the heavy lifting with Google Cloud Run APIs! 

import os
import json
import time
import datetime
import yaml
from pathlib import Path
from typing import Dict, Any, Optional # , Callable, List,
import logging
import pytz # Added for timezone handling

from google.cloud import run_v2, logging_v2
from google.protobuf.json_format import MessageToDict
from google.api_core.exceptions import NotFound

from . import ricc_colors as C # Assuming ricc_colors.py is in the same dir
from .ricc_protobuf_converter import PROTOBUF_CONVERTER
from .ricc_system import log_function_called
#from lib.ricc_system import function_called, log_function_called
#from .ricc_funcall_wrapper import ricc_fun_call_wrapper

# --- Configuration ---
CACHE_DIR = Path(".cache")
CACHE_OBSOLESCENCE_SECONDS = 3600 # 1 hour

# Configure the logger
logger = logging.getLogger(__name__)

# --- Caching Utilities ---


def _get_cache_path(
    project_id: str,
    region: str,
    service_name: Optional[str] = None,
    version_name: Optional[str] = None,
    data_type: str = "json", # or 'yaml', 'txt'
    filename_prefix: str = ""
) -> Path:
    """Constructs the deterministic cache path.

    Includes improved filename logic from v2, especially for logs, incorporating the filename_prefix.
    """
    base_path = CACHE_DIR / project_id  / "cloud-run" # / region
    if service_name:
        base_path /= service_name
        if version_name:
            base_path /= version_name

    base_path.mkdir(parents=True, exist_ok=True) # Ensure directory exists

    # --- Modified Cache Filename Logic (from v2) ---
    # Incorporate prefix into the filename logic more directly
    base_filename = filename_prefix if filename_prefix else "data"

    # Determine filename based on data_type and context
    if data_type == "logs.txt" and service_name and version_name:
        filename = f"{base_filename}_logs.txt" # e.g., 20240515_logs.txt
    elif data_type == "versions.json" and service_name and not version_name:
        filename = "versions.json"
    elif data_type == "endpoints.json" and not service_name and not version_name:
        filename = "endpoints.json"
    elif data_type == "config.yaml" and service_name and version_name:
        filename = "config.yaml"
    elif data_type == "service.yaml" and service_name:
        filename = "service.yaml"
    else:
        # Fallback or handle other specific types
        filename = f"{base_filename}.{data_type}"
    # --- End Modification ---

    return base_path / filename


def _write_cache(path: Path, data: Any):
    """Writes data to a cache file (JSON, YAML, or text)."""
    print(f"{C.CACHE_ICON} Writing cache to: {path} for data ({data.__class__.__name__})", flush=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            converted_data = PROTOBUF_CONVERTER.convert(data)
            if converted_data:
                print(f"Custom JSON conversion applied for: {type(data).__name__}")
                if path.suffix == '.json':
                    json.dump(converted_data, f, indent=2, default=str)
                elif path.suffix == '.yaml':
                    yaml.dump(converted_data, f, indent=2, default_flow_style=False, sort_keys=False)
            elif path.suffix == '.json':
                json.dump(data, f, indent=2, default=str) # Use default=str for complex types
            elif path.suffix == '.yaml':
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                f.write(str(data))
    except TypeError as e:
        logger.warning(f"{C.WARN_ICON} Unhandled data type for caching: {type(data).__name__}. Please add a converter to ProtobufConverter. Error: {e}")
        raise
    except Exception as e:
        print(f"{C.ERROR_ICON} Error writing cache to {path}: {e}", flush=True)

def _read_cache(path: Path) -> Optional[Any]:
    """Reads data from a cache file if it exists."""
    if not path.exists():
        return None
    print(f"{C.CACHE_ICON} Reading cache from: {path}", flush=True)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix == '.json':
                return json.load(f)
            elif path.suffix == '.yaml':
                return yaml.safe_load(f)
            else:
                return f.read()
    except Exception as e:
        print(f"{C.ERROR_ICON} Error reading cache from {path}: {e}", flush=True)
        return None


def _is_cache_valid(path: Path) -> bool:
    """Checks if the cache file exists and is not obsolete."""
    if not path.exists():
        return False
    try:
        file_mod_time = path.stat().st_mtime
        is_valid = (time.time() - file_mod_time) < CACHE_OBSOLESCENCE_SECONDS
        if not is_valid:
             print(f"{C.WARN_ICON} Cache expired: {path}", flush=True)
        return is_valid
    except Exception as e:
         print(f"{C.ERROR_ICON} Error checking cache validity for {path}: {e}", flush=True)
         return False

def _save_service_to_yaml(service: run_v2.Service, project_id: str, region: str, service_name: str):
    """Saves a Cloud Run service object to a YAML file in the cache."""
    cache_path = _get_cache_path(project_id, region, service_name, data_type="service.yaml")
    _write_cache(cache_path, service)
    print(f"{C.INFO_ICON} Service '{service_name}' saved to YAML cache: {cache_path}", flush=True)

# --- Cloud Run API Functions ---
# Note: These functions are designed to be called by Gemini via Function Calling.
# They include the caching logic and print statements for debugging/verbosity.

def get_pantheon_url(service_name, project_id, region):
    '''Get developer console (we call it Pantheon) permalink to Cloud Run..

    Example: https://pantheon.corp.google.com/run/detail/europe-west1/gemini-chat-dev/metrics
    Example: https://pantheon.corp.google.com/run/detail/us-central1/latency-simulator/metrics&project=PROJECT_ID

    '''
    default_endpoint = 'revisions' # could also be ''
#    return f"https://console.cloud.google.com/run/detail/{region}/{project_id}/{service_name}/{default_endpoint}"
    return f"https://console.cloud.google.com/run/detail/{region}/{service_name}/{default_endpoint}?project={project_id}&"

#@ricc_fun_call_wrapper
def get_cloud_run_endpoints(project_id: str, region: str, ignore_cache: bool = False) -> Dict[str, Any]:
    """
    Retrieves all Cloud Run service names and their URLs for a given project and region.

    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region (e.g., 'us-central1').
        ignore_cache: If True, bypasses the cache and fetches fresh data.

    TODO(ricc): add `gcloud run services list --format json` info which contains sth like this:

    Returns:
        A dictionary containing a list of services or an error message.
        Each service includes 'name' and 'uri'.
    """
    #print(f"{C.CLOUD_ICON} Function called: get_cloud_run_endpoints(project_id={project_id}, region={region}, ignore_cache={ignore_cache})", flush=True)
    log_function_called(f"get_cloud_run_endpoints(project_id={project_id}, region={region}, ignore_cache={ignore_cache})")

    cache_path = _get_cache_path(project_id, region, data_type="endpoints.json")

    if not ignore_cache and _is_cache_valid(cache_path):
        cached_data = _read_cache(cache_path)
        if cached_data:
            print(f"{C.CACHE_ICON} Returning cached endpoint data.", flush=True)
            return {"status": "success_cache", "services": cached_data}

    print(f"{C.INFO_ICON} Cache invalid or ignored. Fetching fresh data from GCP...", flush=True)
    try:
        client = run_v2.ServicesClient()
        parent = f"projects/{project_id}/locations/{region}"
        request = run_v2.ListServicesRequest(parent=parent)
        services_list = []
        # gcloud run services list --format json
        for service in client.list_services(request=request):
             # Extract only relevant info to keep it clean
             ### RICC toggle brekpoint
             #print(f"CR - RICC ALOPrints: service={service}")
             #
             short_service_name = service.name.split('/')[-1] # Get the short name
             service_info = {
                 "name": short_service_name,
                 "uri": service.uri,
                 "last_modifier": service.update_time.rfc3339() if service.update_time else "N/A", # Example field
                 # Add other useful fields like latest revision, traffic split etc. if needed
                 # Irrelevant
                 #"labels": service.labels,
                 # Too big
                 "conditions": service.conditions,
                 "latest_ready_revision": service.latest_ready_revision,
                 "containers__image": service.template.containers[0].image if service.template.containers else "N/A (no container found)",
                 "pantheon_url": get_pantheon_url(short_service_name, project_id, region),
                 "schema_carlessian_version": '1.1', # this is for Ricc to version this schema.
             }
             services_list.append(service_info)
             _save_service_to_yaml(service, project_id, region, service_info["name"])

        _write_cache(cache_path, services_list)
        return {"status": "success_api", "services": services_list}

    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in get_cloud_run_endpoints: {e}", flush=True)
        return {"status": "error", "message": f"Failed to list Cloud Run services: {e}"}


def get_cloud_run_endpoints_names(project_id: str, region: str, ignore_cache: bool = False): # returns an array -> Dict[str, Any]:
    cloud_run_endpoints_dict = get_cloud_run_endpoints(project_id=project_id, region=region, ignore_cache=ignore_cache)
    services = cloud_run_endpoints_dict['services']
    return [ s['name'] for s in services ]

#@ricc_fun_call_wrapper
def get_cloud_run_revisions(project_id: str, region: str, service_name: str, max_results: int = 10, ignore_cache: bool = False) -> Dict[str, Any]:
    """
    Retrieves all revision names for a specific Cloud Run service. Can be filtered by max_results to just provide the lastest revision(s).


    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region.
        service_name: The name of the Cloud Run service.
        max_results: The maximum number of revisions to retrieve (default=10).
        ignore_cache: If True, bypasses the cache. (default: False)

    Docs: TODO

    Returns:
        A dictionary containing a list of revision names or an error message.
    """
    #print(f"{C.CLOUD_ICON} Function called: get_cloud_run_revisions(project_id={project_id}, region={region}, service_name={service_name}, ignore_cache={ignore_cache})", flush=True)
    log_function_called(f"get_cloud_run_revisions(project_id={project_id}, region={region}, service_name={service_name}, ignore_cache={ignore_cache})")
    cache_path = _get_cache_path(project_id, region, service_name=service_name, data_type="versions.json")

    if not ignore_cache and _is_cache_valid(cache_path):
        cached_data = _read_cache(cache_path)
        if cached_data:
             print(f"{C.CACHE_ICON} Returning cached version data.", flush=True)
             return {"status": "success_cache", "revisions": cached_data}

    print(f"{C.INFO_ICON} Cache invalid or ignored. Fetching fresh data from GCP...", flush=True)
    try:
        client = run_v2.RevisionsClient()
        #print(f"parent={parent}")
        parent = f"projects/{project_id}/locations/{region}/services/{service_name}"
        request = run_v2.ListRevisionsRequest(parent=parent)

        revisions_list = []
        i = 0
        for revision in client.list_revisions(request=request):
             if not revision.containers:
                 continue
             i += 1
             if i > max_results:
                 break
             #print(f"- Revision #{i}: {revision.name}")
             #print(revision.containers[0].ports)
             revision_info = {
                 "name": revision.name.split('/')[-1], # Short name
                 "create_time": revision.create_time.rfc3339() if revision.create_time else "N/A",
                 "image": revision.containers[0].image if revision.containers else "N/A",
                 "revision_pantheon_url": "TODO very complex",
#                 "https://console.cloud.google.com/run/detail/europe-west1/gemini-news-crawler-dev/revisions?invt=AbtyHQ&project=palladius-genai&pageState=(%22cloudRunServiceRevisionsTable%22:(%22f%22:%22%255B%257B_22k_22_3A_22_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22gemini-news-crawler-dev-00118-47z_5C_22_22_2C_22s_22_3Atrue%257D%255D%22))"

                 #"containers": revision.containers if revision.containers else "N/A",
                 #"log_uri2": revision.log_uri if revision.log_uri else "N/A",
                 #"labels": revision.labels if revision.labels else "N/A",

                 #"memory_limit": revision.containers[0].resources if revision.containers[0].resources else "N/A",
                 #"memory_limit": revision.containers[0].resources.limits["memory"] if revision.containers[0].resources else "N/A",
                 #"containers":
                 # Add scaling info, tags, etc. if desired
                 "the_whole_proto": MessageToDict(revision._pb),  # Convert the entire protobuf object to a dictionary
             }
             revisions_list.append(revision_info)

        #print("fuori dal ciclo for")
        # Sort by creation time, newest first
        revisions_list.sort(key=lambda x: x.get("create_time", ""), reverse=True)

        _write_cache(cache_path, revisions_list)
        return {"status": "success_api", "revisions": revisions_list}

    except NotFound:
         print(f"{C.WARN_ICON} Service not found: {service_name}", flush=True)
         return {"status": "error", "message": f"Cloud Run service '{service_name}' not found in region '{region}'."}
    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in get_cloud_run_revisions: {e}", flush=True)
        return {"status": "error", "message": f"Failed to list revisions for {service_name}: {e}"}

def get_cloud_run_config(project_id: str, region: str, service_name: str, revision_name: str, ignore_cache: bool = False) -> Dict[str, Any]:
    """
    Retrieves the configuration (as YAML) for a specific Cloud Run revision.

    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region.
        service_name: The name of the Cloud Run service.
        revision_name: The name of the Cloud Run revision.
        ignore_cache: If True, bypasses the cache.

    Returns:
        A dictionary containing the YAML configuration string or an error message.
    """
    #print(f"{C.CLOUD_ICON} Function called: get_cloud_run_config(..., revision_name={revision_name}, ignore_cache={ignore_cache})", flush=True)
    log_function_called(f"get_cloud_run_config(..., revision_name={revision_name}, ignore_cache={ignore_cache})")
    cache_path = _get_cache_path(project_id, region, service_name, revision_name, data_type="config.yaml")

    if not ignore_cache and _is_cache_valid(cache_path):
        cached_data = _read_cache(cache_path)
        if cached_data:
             print(f"{C.CACHE_ICON} Returning cached config data.", flush=True)
             return {"status": "success_cache", "config_yaml": cached_data}

    print(f"{C.INFO_ICON} Cache invalid or ignored. Fetching fresh config from GCP...", flush=True)
    try:
        client = run_v2.RevisionsClient()
        name = f"projects/{project_id}/locations/{region}/services/{service_name}/revisions/{revision_name}"
        request = run_v2.GetRevisionRequest(name=name)
        revision = client.get_revision(request=request)

        # Convert the protobuf message to a dictionary, then to YAML
        # Filter out some potentially noisy fields if needed
        revision_dict = MessageToDict(revision._pb)

        # Simple example: extract key fields or dump the whole thing
        config_data = {
            "revision_name": revision.name.split('/')[-1],
            "service_name": revision.service.split('/')[-1],
            "create_time": revision.create_time.rfc3339() if revision.create_time else None,
            "container": {
                "image": revision.containers[0].image if revision.containers else None,
                "resources": MessageToDict(revision.containers[0].resources._pb) if revision.containers else None,
                "env": [MessageToDict(env._pb) for env in revision.containers[0].env] if revision.containers else None,
                "ports": [MessageToDict(port._pb) for port in revision.containers[0].ports] if revision.containers else None,
            },
            "scaling": MessageToDict(revision.scaling._pb) if revision.scaling else None,
            "service_account": revision.service_account,
            "log_uri": revision.log_uri,
            # Add other fields as needed
        }

        yaml_output = yaml.dump(config_data, default_flow_style=False, sort_keys=False)

        _write_cache(cache_path, yaml_output)
        return {"status": "success_api", "config_yaml": yaml_output}

    except NotFound:
         print(f"{C.WARN_ICON} Revision not found: {revision_name}", flush=True)
         return {"status": "error", "message": f"Cloud Run revision '{revision_name}' not found for service '{service_name}'."}
    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in get_cloud_run_config: {e}", flush=True)
        return {"status": "error", "message": f"Failed to get config for revision {revision_name}: {e}"}

# --- get_cloud_run_logs (from v1) ---
# This function primarily fetches logs based on the current date and hours_ago.
def get_cloud_run_logs(
    project_id: str,
    region: str,
    service_name: str,
    revision_name: str,
    hours_ago: int = 1,
    day_str: Optional[str] = None, # New optional parameter YYYYMMDD
    ignore_cache: bool = False
) -> Dict[str, Any]:
    """
    Retrieves logs for a specific Cloud Run revision.

    It fetches logs ending at the current time on the specified `day_str` (defaults to today)
    and going back `hours_ago`. It's safe to look back up to Logging retention limits (e.g., 30 days).

    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region.
        service_name: The name of the Cloud Run service.
        revision_name: The name of the Cloud Run revision.
        hours_ago: How many hours back to fetch logs from the end time (default 1).
        day_str: Optional day (YYYYMMDD format) to set the end time for the log query.
                 If None, defaults to the current day (today).
        ignore_cache: If True, bypasses the cache.

    Returns:
        A dictionary containing the log entries as a string or an error message.
    """
    log_function_called(f"get_cloud_run_logs(service={service_name}, rev={revision_name}, hours={hours_ago}, day={day_str}, ignore_cache={ignore_cache})")
    #print("💤💤💤 TODO RICCARDO - add permaURL to Logs for this. So I can click while I wait... 💤💤💤")

    # --- Determine End Time ---
    now_utc = datetime.datetime.now(pytz.utc)
    try:
        if day_str:
            target_date = datetime.datetime.strptime(day_str, "%Y%m%d").date()
            # Combine target date with current time (UTC)
            end_time = now_utc.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            print(f"{C.INFO_ICON} Using specified day {day_str}, end time set to: {end_time.isoformat()}", flush=True)
        else:
            # Default to current time if day_str is not provided
            end_time = now_utc
            day_str = now_utc.strftime("%Y%m%d") # Set day_str for cache filename
            print(f"{C.INFO_ICON} No day specified, using current time: {end_time.isoformat()}", flush=True)
    except ValueError:
        print(f"{C.ERROR_ICON} Invalid day_str format: '{day_str}'. Please use YYYYMMDD.", flush=True)
        ret = {"status": "error", "message": f"Invalid day format: '{day_str}'. Use YYYYMMDD."}
        print(f"get_cloud_run_logs ret = {ret}")
        return ret

    # --- Calculate Start Time ---
    start_time = end_time - datetime.timedelta(hours=hours_ago)

    # --- Cache Handling ---
    # Include day_str in the cache filename prefix
    cache_filename_prefix = f"{day_str}_h{hours_ago}"
    cache_path = _get_cache_path(
        project_id, region, service_name, revision_name,
        data_type="logs.txt",
        filename_prefix=cache_filename_prefix
    )

    if not ignore_cache and _is_cache_valid(cache_path):
        cached_data = _read_cache(cache_path)
        if cached_data:
            print(f"{C.CACHE_ICON} Returning cached log data from {cache_path}.", flush=True)
            return {"status": "success_cache", "logs": cached_data}

    print(f"{C.INFO_ICON} Cache invalid or ignored ({cache_path}). Fetching fresh logs from GCP Logging...", flush=True)
    try:
        client = logging_v2.Client(project=project_id)
        # Construct the filter using calculated start and end times
        log_filter = (
            f'resource.type="cloud_run_revision" '
            f'resource.labels.project_id="{project_id}" '
            f'resource.labels.location="{region}" '
            f'resource.labels.service_name="{service_name}" '
            f'resource.labels.revision_name="{revision_name}" '
            f'timestamp >= "{start_time.isoformat()}" '
            f'timestamp <= "{end_time.isoformat()}" ' # Add end timestamp constraint
            #f'severity>=ERROR'
            f'severity>=WARNING'
        )
        print(f"{C.INFO_ICON} Using log filter: {log_filter}", flush=True)
        print(f"🌎 Pantheon URL : https://pantheon.corp.google.com/logs/query;query={log_filter}&project={project_id}")
        # https://pantheon.corp.google.com/logs/query;query=resource.type%20%3D%20%22cloud_run_revision%22%0Aresource.labels.service_name%20%3D%20%22gemini-news-crawler-prod%22%0Aresource.labels.location%20%3D%20%22europe-west1%22%0A%20severity%3E%3DDEFAULT;storageScope=project;cursorTimestamp=2025-04-22T09:23:32.264589Z;duration=P1D?e=TroubleshootingUiAdminLaunch::TroubleshootingUiAdminControl&invt=AbtwIg&project=palladius-genai&mods=logs_tg_staging

        log_entries = []
        # Be mindful of page size and potential large log volumes
        for entry in client.list_entries(filter_=log_filter, order_by=logging_v2.DESCENDING, page_size=100): # Get latest first
            log_line = f"{entry.timestamp.isoformat()} [{entry.severity}] "
            if entry.payload is not None:
                 if isinstance(entry.payload, dict):
                      log_line += json.dumps(entry.payload)
                 else:
                      log_line += str(entry.payload)
            log_entries.append(log_line)

        # Reverse to show oldest first in the final output string
        log_output = "\n".join(reversed(log_entries))

        if not log_output:
            log_output = f"--- No logs found for {revision_name} between {start_time.isoformat()} and {end_time.isoformat()} ---"

        _write_cache(cache_path, log_output)
        return {"status": "success_api", "logs": log_output}

    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in get_cloud_run_logs: {e}", flush=True)
        ret = {"status": "error", "message": f"Failed to get logs for revision {revision_name}: {e}"}
        print(f"get_cloud_run_logs ret = {ret}")
        return ret
# --- End get_cloud_run_logs ---


# --- Potentially Destructive Actions (Use with Caution!) ---

def update_cloud_run_memory(project_id: str, region: str, service_name: str, memory_limit: str) -> Dict[str, Any]:
    """
    Updates the memory limit for a Cloud Run service. Requires confirmation outside this function.

    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region.
        service_name: The name of the Cloud Run service to update.
        memory_limit: The new memory limit (e.g., "512Mi", "1Gi", "2048M").

    Returns:
        A dictionary indicating success or failure of the update operation start.
    """
    #print(f"{C.WARN_ICON}{C.BOLD} Function called: update_cloud_run_memory(..., service_name={service_name}, memory_limit={memory_limit})", flush=True)
    log_function_called(f"update_cloud_run_memory(service_name={service_name}, memory_limit={memory_limit}) {C.WARN_ICON}  This is a potential MUTATION {C.WARN_ICON}")
    #print(f"{C.WARN_ICON} This is a potentially modifying operation!", flush=True)

    try:
        client = run_v2.ServicesClient()
        service_path = f"projects/{project_id}/locations/{region}/services/{service_name}"

        # Get the current service to modify it
        get_request = run_v2.GetServiceRequest(name=service_path)
        service = client.get_service(request=get_request)

        # --- Modify the template's container resources ---
        # This assumes one container, adjust if you have multiple
        if not service.template.containers:
             return {"status": "error", "message": f"Service {service_name} has no containers defined."}

        # It's crucial to modify the existing object, not create a new one
        # Ensure resources object exists
        if not service.template.containers[0].resources:
             service.template.containers[0].resources = run_v2.ResourceRequirements()

        service.template.containers[0].resources.limits = {"memory": memory_limit}
        # Optionally also set CPU limits if needed: service.template.containers[0].resources.limits["cpu"] = "1"

        # --- Prepare Update Request ---
        # Only include fields that are being changed in the update_mask
        # Here we are changing the template (specifically container resources)
        update_mask = {"paths": ["template"]}

        request = run_v2.UpdateServiceRequest(
            service=service,
            update_mask=update_mask,
        )

        # --- Execute Update ---
        print(f"{C.INFO_ICON} Sending update request to Cloud Run API...", flush=True)
        operation = client.update_service(request=request)

        # The update is asynchronous. We return the operation name.
        # The caller (Gemini/main loop) could potentially poll this later if needed.
        print(f"{C.INFO_ICON} Update operation started: {operation.operation.name}", flush=True)
        # Let's wait for it for simplicity in this example, but add a timeout
        # result = operation.result(timeout=300) # Wait up to 5 minutes

        # For now, just return that the operation started
        return {
             "status": "success",
             "message": f"Update operation initiated for {service_name}. New deployment starting.",
             "operation_name": operation.operation.name,
        }

    except NotFound:
         print(f"{C.WARN_ICON} Service not found during update attempt: {service_name}", flush=True)
         return {"status": "error", "message": f"Cloud Run service '{service_name}' not found for update."}
    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in update_cloud_run_memory: {e}", flush=True)
        # Provide more context if possible
        return {"status": "error", "message": f"Failed to update memory for service {service_name}: {e}"}




# --- get_cloud_run_logs_for_date (from v2) ---
# This function provides more granular control over the log retrieval time range.
# Note: This function was still under development and might be half broken as per user.
def get_cloud_run_logs_for_date(
    project_id: str,
    region: str,
    service_name: str,
    revision_name: str,
    end_timestamp_date: str,
    end_timestamp_time: Optional[str] = None,
    timezone: Optional[str] = "UTC",
    time_delta_hours: float = 1.0,
    ignore_cache: bool = False,
) -> Dict[str, Any]:
    """
    Retrieves logs for a specific Cloud Run revision within a specified date and time range.
"""

    Args:
        project_id: The Google Cloud Project ID.
        region: The Google Cloud Region.
        service_name: The name of the Cloud Run service.
        revision_name: The name of the Cloud Run revision.
        end_timestamp_date: The end date for the log retrieval (YYYY-MM-DD).
        end_timestamp_time: The end time for the log retrieval (HH:MM:SS). Optional, defaults to 23:59:59.
        timezone: The timezone for the end timestamp (e.g., "UTC", "Europe/Rome"). Optional, defaults to UTC.
        time_delta_hours: The time delta in hours (float) to go back from the end timestamp.
        ignore_cache: If True, bypasses the cache.

    Returns:
        A dictionary containing the log entries as a string or an error message.
    """
    log_function_called(
        f"get_cloud_run_logs_for_date(service_name={service_name}, revision_name={revision_name}, end_timestamp_date={end_timestamp_date}, end_timestamp_time={end_timestamp_time}, timezone={timezone}, time_delta_hours={time_delta_hours}, ignore_cache={ignore_cache})"
    )

    # Cache filename doesn't include time parameters to keep it simple, just caches the *last fetch*
    # Use a more specific prefix for the cache file
    cache_filename_prefix = f"{end_timestamp_date}_h{time_delta_hours}"
    cache_path = _get_cache_path(
        project_id, region, service_name, revision_name,
        data_type="logs.txt", # Keep data_type simple
        filename_prefix=cache_filename_prefix # Use prefix for specificity
    )


    # Cache validity check considers the *last fetch* time, not the log timestamps themselves
    if not ignore_cache and _is_cache_valid(cache_path):
        cached_data = _read_cache(cache_path)
        if cached_data:
            print(f"{C.CACHE_ICON} Returning cached log data from {cache_path}.", flush=True)
            # Note: Cached logs might be older than the requested time range if cache is hit
            return {"status": "success_cache", "logs": cached_data}

    print(
        f"{C.INFO_ICON} Cache invalid or ignored ({cache_path}). Fetching fresh logs from GCP Logging...",
        flush=True,
    )

    try:
        # --- Construct the end timestamp ---
        if end_timestamp_time:
            end_timestamp_str = f"{end_timestamp_date}T{end_timestamp_time}"
        else:
            end_timestamp_str = f"{end_timestamp_date}T23:59:59"  # Default to end of day

        # Parse the end timestamp and handle timezone
        try:
            end_timestamp = datetime.datetime.fromisoformat(end_timestamp_str)
        except ValueError:
            print(
                f"{C.ERROR_ICON} Invalid end timestamp format: {end_timestamp_str}. Please use YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD.",
                flush=True,
            )
            return {
                "status": "error",
                "message": f"Invalid end timestamp format: {end_timestamp_str}",
            }

        # Handle timezone
        tz = pytz.utc # Default to UTC
        if timezone != "UTC":
            try:
                tz = pytz.timezone(timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                print(
                    f"{C.ERROR_ICON} Invalid timezone: {timezone}. Using UTC instead.",
                    flush=True,
                )
                timezone = "UTC" # Correct the timezone variable as well

        # Localize or replace timezone info
        if tz == pytz.utc:
             end_timestamp = end_timestamp.replace(tzinfo=pytz.utc)
        else:
             # Assume naive datetime fromisoformat needs localization
             try:
                 end_timestamp = tz.localize(end_timestamp)
             except ValueError: # Handle case where it might already be aware (less likely with fromisoformat)
                 end_timestamp = end_timestamp.astimezone(tz)


        # --- Calculate the start timestamp ---
        start_timestamp = end_timestamp - datetime.timedelta(
            hours=time_delta_hours
        )

        # --- Construct the log filter ---
        client = logging_v2.Client(project=project_id)
        log_filter = (
            f'resource.type="cloud_run_revision" '
            f'resource.labels.project_id="{project_id}" '
            f'resource.labels.location="{region}" '
            f'resource.labels.service_name="{service_name}" '
            f'resource.labels.revision_name="{revision_name}" '
            f'timestamp >= "{start_timestamp.isoformat()}" '
            f'timestamp <= "{end_timestamp.isoformat()}" '
            f"severity>=WARNING"
        )
        print(f"{C.INFO_ICON} Using log filter: {log_filter}", flush=True)

        log_entries = []
        # Be mindful of page size and potential large log volumes
        for entry in client.list_entries(
            filter_=log_filter, order_by=logging_v2.DESCENDING, page_size=100
        ):  # Get latest first
            log_line = f"{entry.timestamp.isoformat()} [{entry.severity}] "
            if entry.payload is not None:
                if isinstance(entry.payload, dict):
                    log_line += json.dumps(entry.payload)
                else:
                    log_line += str(entry.payload)
            log_entries.append(log_line)

        # Reverse to show oldest first in the final output string
        log_output = "\n".join(reversed(log_entries))

        if not log_output:
            log_output = f"--- No logs found for {revision_name} between {start_timestamp.isoformat()} and {end_timestamp.isoformat()} ---"

        _write_cache(cache_path, log_output)
        return {"status": "success_api", "logs": log_output}

    except Exception as e:
        print(f"{C.ERROR_ICON} API Error in get_cloud_run_logs_for_date: {e}", flush=True)
        return {
            "status": "error",
            "message": f"Failed to get logs for revision {revision_name}: {e}",
        }



def get_cloud_run_service_yaml_dict(project_id, region, service_id):
    '''This code is actually in lib/streamlit/helpers.py'''
    return {} #  {"error": 'PASS todo implement'}