import streamlit as st
from lib.ricc_utils import get_projects_by_user_faker # Assuming this exists
from lib.ricc_cloud_run import get_cloud_run_endpoints, get_cloud_run_endpoints_names # Assuming this exists
from lib.ricc_cloud_run import get_cloud_run_service_yaml_dict # Assuming we add this helper
from lib.ricc_cloud_monitoring import get_monitoring_chart_paths # Assuming we add/use this
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
from .config import CACHE_BASE_DIR

logger = logging.getLogger(__name__)

# --- Project & Service Fetching ---

# @st.cache_data(ttl=3600) # Cache for 1 hour
def fetch_projects(user_id: str) -> List[str]:
    """Fetches list of projects for the user. Uses faker for now."""
    logger.info(f"Fetching projects for user: {user_id}")
    try:
        # Replace faker with actual GCP call when ready
        # from lib.ricc_gcp_projects import get_projects_for_user
        # projects = get_projects_for_user(user_email=user_id)
        # return [p['projectId'] for p in projects] # Adjust based on actual return format
        return get_projects_by_user_faker(user_id)
    except Exception as e:
        logger.error(f"Error fetching projects for {user_id}: {e}", exc_info=True)
        st.error(f"🚨 Failed to fetch projects: {e}")
        return []

# @st.cache_data(ttl=600) # Cache for 10 minutes
def fetch_services(project_id: str, region: str) -> List[str]:
    """Fetches list of Cloud Run services for a project and region."""
    logger.info(f"Fetching services for project: {project_id} in region: {region}")
    if not project_id or not region:
        return []
    try:
        # Replace with actual GCP call
        service_names = get_cloud_run_endpoints_names(project_id=project_id, region=region)
        print(f"DEB service_names: {service_names}")
        #print(f"DEB services . keys: {services.keys()}")
        #service_names = [s['name'] for s in services] # Adjust based on actual API response
        #print(f"DEB service_namesL {service_names}")
        return service_names
        #                       service_names = [ srv_dict['name'] for srv_dict in endpoints_answer['services'] ]
        # Assuming get_cloud_run_endpoints returns a list of service names
        #return get_cloud_run_endpoints(project_id=project_id, region=region)
    except Exception as e:
        # Provide more context in the error message
        st.error(f"🚨 Failed to fetch Cloud Run services for project '{project_id}' in region '{region}': {e}")
        logger.error(f"Error fetching services for {project_id} in {region}: {e}", exc_info=True)
        return []

# --- Service Details & Monitoring ---

def get_service_cache_dir(project_id: str, service_id: str) -> Path:
    """Constructs the expected cache directory path for a service."""
    # Ensure components are valid directory names (basic sanitization)
    safe_project = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in project_id)
    safe_service = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in service_id)
    return Path(CACHE_BASE_DIR) / safe_project / "cloud-run" / safe_service

# @st.cache_data(ttl=300) # Cache for 5 minutes
def fetch_service_details(project_id: str, service_id: str, region: str) -> Optional[Dict[str, Any]]:
    """
    Fetches and parses the service.yaml file from the conventional cache location.
    Placeholder: In reality, you might fetch this live or ensure the cache is populated.
    """
    logger.info(f"Fetching service details for {project_id}/{service_id}")
    if not project_id or not service_id:
        return None

    # --- Placeholder: Fetch or Ensure Cache ---
    # This assumes a background process or previous step populated the cache.
    # You might need to add logic here to *fetch* the service details using
    # ricc_cloud_run.get_service(project_id, region, service_id) and save it
    # if the cached file doesn't exist or is too old.
    # service_data = get_cloud_run_service_yaml_dict(project_id, region, service_id) # Ideal
    # For now, we just read the expected file path.

    cache_dir = get_service_cache_dir(project_id, service_id)
    yaml_path = cache_dir / "service.yaml"
    print(f"RICCARDO fetch_service_details(): yaml_path={yaml_path} ")

    if not yaml_path.is_file():
        st.warning(f"📄 Service definition file not found at expected location: {yaml_path}", icon="❓")
        logger.warning(f"Cache miss: service.yaml not found at {yaml_path}")
        # Optionally, try fetching live here
        # try:
        #     service_dict = get_cloud_run_service_yaml_dict(project_id, region, service_id) # Assumes this func exists
        #     # Optionally save it back to cache here for next time
        #     return service_dict
        # except Exception as e:
        #      logger.error(f"Failed to fetch live service details for {service_id}: {e}")
        #      st.error(f"🚨 Failed to fetch live details for {service_id}")
        return None

    try:
        with open(yaml_path, 'r') as f:
            service_dict = yaml.safe_load(f)
        logger.info(f"Successfully loaded service details from {yaml_path}")
        return service_dict
    except yaml.YAMLError as e:
        st.error(f"🚨 Failed to parse service definition file ({yaml_path}): {e}")
        logger.error(f"YAML parsing error for {yaml_path}: {e}", exc_info=True)
        return None
    except OSError as e:
        st.error(f"🚨 Failed to read service definition file ({yaml_path}): {e}")
        logger.error(f"File read error for {yaml_path}: {e}", exc_info=True)
        return None


# @st.cache_data(ttl=300) # Cache for 5 minutes
def fetch_monitoring_charts(project_id: str, service_id: str) -> List[Path]:
    """
    Finds monitoring chart image files in the conventional cache location.
    Placeholder: Assumes charts are pre-generated and saved.
    """
    logger.info(f"Fetching monitoring charts for {project_id}/{service_id}")
    if not project_id or not service_id:
        return []

    # --- Placeholder: Ensure Cache Population ---
    # Similar to service details, this assumes charts exist. You might need
    # logic using ricc_cloud_monitoring to generate/fetch these charts
    # if they are missing or stale.
    # chart_paths = get_monitoring_chart_paths(project_id, region, service_id) # Ideal

    cache_dir = get_service_cache_dir(project_id, service_id)
    charts_dir = cache_dir / "mon-charts"

    if not charts_dir.is_dir():
        logger.warning(f"Monitoring charts directory not found: {charts_dir}")
        # No need to show a warning in UI unless explicitly desired
        return []

    try:
        # Find common image file types
        chart_files = list(charts_dir.glob('*.png')) + \
                      list(charts_dir.glob('*.jpg')) + \
                      list(charts_dir.glob('*.jpeg')) + \
                      list(charts_dir.glob('*.gif'))
        chart_files.sort() # Sort alphabetically for consistent order
        logger.info(f"Found {len(chart_files)} charts in {charts_dir}")
        return chart_files
    except OSError as e:
        st.error(f"🚨 Failed to access monitoring charts directory ({charts_dir}): {e}")
        logger.error(f"Error accessing chart dir {charts_dir}: {e}", exc_info=True)
        return []

