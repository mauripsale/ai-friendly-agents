import streamlit as st
from pathlib import Path
import yaml # Requires PyYAML: pip install pyyaml

# Define expected cache structure relative to project/service
SERVICE_YAML_NAME = "service.yaml"
MONITORING_CHARTS_DIR = "mon-charts"

# Cache the data loading to avoid hitting disk/network repeatedly for the same service
# TTL (time-to-live) set to 5 minutes (300 seconds)
@st.cache_data(ttl=300)
def load_service_data_from_cache(cache_dir: Path, project_id: str, service_name: str):
    """
    Loads service.yaml content, extracts URLs, and finds monitoring chart images
    from the predefined cache structure.

    Args:
        cache_dir: Base cache directory (e.g., Path(".cache")).
        project_id: The GCP project ID.
        service_name: The Cloud Run service name.

    Returns:
        Tuple: (service_yaml_content_str, list_of_urls, list_of_chart_paths)
               Returns (None, [], []) if core data (service.yaml) is not found.
    """
    # Construct paths based on the expected cache layout
    service_cache_dir = cache_dir / project_id / "cloud-run" / service_name
    service_yaml_path = service_cache_dir / SERVICE_YAML_NAME
    charts_dir_path = service_cache_dir / MONITORING_CHARTS_DIR

    print(f"Attempting to load cache data from: {service_cache_dir}")

    service_yaml_content = None
    urls = []
    chart_paths = []

    # 1. Load service.yaml content
    if service_yaml_path.is_file():
        try:
            with open(service_yaml_path, 'r', encoding='utf-8') as f:
                service_yaml_content = f.read() # Return raw string content
            print(f"Successfully read: {service_yaml_path}")
        except Exception as e:
            st.warning(f"⚠️ Error reading {service_yaml_path}: {e}")
            service_yaml_content = f"# Error reading file: {e}" # Show error instead of content
    else:
        print(f"Cache miss: {service_yaml_path} not found.")
        # Return None for content if the essential YAML is missing
        return None, [], []

    # 2. Attempt to parse YAML to extract URLs (best effort)
    try:
        service_data = yaml.safe_load(service_yaml_content)
        if isinstance(service_data, dict): # Ensure parsing didn't fail badly
            # Navigate safely: check keys exist before accessing using .get()
            status = service_data.get('status', {})
            # Primary URL often directly under status
            main_url = status.get('url')
            if main_url:
                 urls.append(main_url)
            # URLs associated with traffic splits
            traffic_list = status.get('traffic', [])
            if isinstance(traffic_list, list):
                for traffic_item in traffic_list:
                     if isinstance(traffic_item, dict):
                          url = traffic_item.get('url')
                          # Add only if it's different from the main URL
                          if url and url not in urls:
                              urls.append(url)
        else:
             print("Warning: Parsed service.yaml content is not a dictionary.")

    except yaml.YAMLError as e:
        st.warning(f"⚠️ Could not parse {service_yaml_path} to extract URLs: {e}")
    except AttributeError as e:
         st.warning(f"⚠️ Unexpected structure in {service_yaml_path} when looking for URLs: {e}")

    # 3. Find monitoring charts (common image formats)
    if charts_dir_path.is_dir():
        print(f"Scanning for charts in: {charts_dir_path}")
        found_charts = []
        for item in charts_dir_path.iterdir(): # Use iterdir for efficiency
            # Check if it's a file and has a common image extension
            if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
                found_charts.append(item)
        chart_paths = sorted(found_charts) # Sort alphabetically by path
        print(f"Found {len(chart_paths)} chart(s).")
    else:
         print(f"Charts directory not found: {charts_dir_path}")


    return service_yaml_content, urls, chart_paths

# Add any other Streamlit-specific helper functions here, e.g., for parsing specific YAML sections robustly.

