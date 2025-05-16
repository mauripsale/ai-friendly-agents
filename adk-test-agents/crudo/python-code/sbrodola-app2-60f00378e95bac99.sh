#!/bin/bash

# sbrodola.sh - Generates the initial file structure for the Streamlit App

# Create directories
mkdir -p lib/streamlit2
mkdir -p .cache # Ensure cache dir exists for example paths

# --- app2.py ---
cat << 'EOF' > app2.py
import streamlit as st
from lib.streamlit2.ui import build_ui
from lib.streamlit2.state import ensure_session_state_initialized
from lib.streamlit2.db import init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Cloud Run Investigator 🕵️‍♀️",
        page_icon="☁️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize SQLite Database
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        st.error(f"🚨 Failed to initialize database: {e}")
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        st.stop() # Stop execution if DB fails

    # Ensure session state has all necessary keys
    ensure_session_state_initialized()

    # Build the UI elements
    build_ui()

if __name__ == "__main__":
    logger.info("Starting Streamlit App...")
    main()
EOF

# --- lib/streamlit2/__init__.py ---
cat << 'EOF' > lib/streamlit2/__init__.py
# Makes lib/streamlit2 a Python package
EOF

# --- lib/streamlit2/config.py ---
cat << 'EOF' > lib/streamlit2/config.py
import os
from dotenv import load_dotenv
from typing import List

# Load .env file if it exists (useful for local development)
load_dotenv()

# --- Environment Variable Loading ---

DEFAULT_USER_ID = "ricc@google.com"
DEFAULT_MODEL = "gemini-1.5-flash-latest" # Using latest alias
DEFAULT_REGION = "europe-west1"
AVAILABLE_MODELS: List[str] = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"]

# 👤 User ID Configuration
def get_user_id() -> str:
    """Gets user ID from environment or defaults."""
    user = os.getenv("USER", None)
    email_domain = "@google.com" # Assuming google.com domain
    if user:
        return f"{user}{email_domain}"
    # Fallback if USER env var is not set
    try:
        # Attempt to get login name, handle potential errors
        login_name = os.getlogin()
        return f"{login_name}{email_domain}"
    except OSError:
        # If getlogin fails (e.g., in certain environments), use the hardcoded default
        return DEFAULT_USER_ID

# ♊ Gemini Model Configuration
def get_gemini_model() -> str:
    """Gets Gemini model from environment or defaults."""
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    if model not in AVAILABLE_MODELS:
        print(f"⚠️ Warning: Env Var GEMINI_MODEL ('{model}') is not in AVAILABLE_MODELS. Using default: {DEFAULT_MODEL}")
        return DEFAULT_MODEL
    return model

# 🌍 Cloud Region Configuration
def get_GOOGLE_CLOUD_LOCATION() -> str:
    """Gets Google Cloud region from environment or defaults."""
    return os.getenv("GOOGLE_CLOUD_LOCATION", DEFAULT_REGION)

# 🔑 API Key Configuration
def get_google_api_key() -> str | None:
    """Gets Google API Key from environment. No default."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set.")
    return api_key

# --- Application Configuration ---
# You could also define a dataclass here to hold these values
USER_ID: str = get_user_id()
GEMINI_MODEL: str = get_gemini_model()
GOOGLE_CLOUD_LOCATION: str = get_GOOGLE_CLOUD_LOCATION()
GOOGLE_API_KEY: str | None = get_google_api_key()
AVAILABLE_MODELS_LIST: List[str] = AVAILABLE_MODELS

# --- Database ---
DB_FILE = "convos.sqlite3"

# --- Cache Dirs ---
# Define base cache dir relative to app root for consistency
CACHE_BASE_DIR = ".cache"

EOF

# --- lib/streamlit2/state.py ---
cat << 'EOF' > lib/streamlit2/state.py
import streamlit as st
from .config import (
    USER_ID,
    GEMINI_MODEL,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_API_KEY,
    AVAILABLE_MODELS_LIST,
)
from typing import List, Dict, Any, Optional

def ensure_session_state_initialized():
    """Initializes Streamlit's session state with default values if they don't exist."""

    # --- Configuration ---
    if 'user_id' not in st.session_state:
        st.session_state.user_id = USER_ID
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = GEMINI_MODEL
    if 'cloud_region' not in st.session_state:
        st.session_state.cloud_region = GOOGLE_CLOUD_LOCATION
    if 'api_key' not in st.session_state:
        st.session_state.api_key = GOOGLE_API_KEY
        if not st.session_state.api_key:
             st.warning("🔑 Google API Key is not set. Gemini features will likely fail.", icon="🚨")
    if 'available_models' not in st.session_state:
        st.session_state.available_models = AVAILABLE_MODELS_LIST

    # --- Project/Service Selection ---
    if 'selected_project_id' not in st.session_state:
        st.session_state.selected_project_id = None
    if 'selected_service_id' not in st.session_state:
        st.session_state.selected_service_id = None
    if 'projects_list' not in st.session_state:
        st.session_state.projects_list = [] # Will be populated by API call
    if 'services_list' not in st.session_state:
        st.session_state.services_list = [] # Will be populated by API call

    # --- Investigation / Chat State ---
    if 'current_investigation_id' not in st.session_state:
        st.session_state.current_investigation_id = None # ID of the active chat
    if 'current_chat_messages' not in st.session_state:
        # Stores messages for the *currently viewed* investigation {role: 'user'/'assistant', content: str, chart: Optional[str]}
        st.session_state.current_chat_messages = []
    if 'investigation_titles' not in st.session_state:
         # Stores {investigation_id: title} for the sidebar list for the current project/service
        st.session_state.investigation_titles = {}

    # --- UI State ---
    if 'show_chat_interface' not in st.session_state:
        st.session_state.show_chat_interface = False # Controls showing chat vs synoptic

    # Add other state variables as needed
    # e.g., for storing fetched service details, charts, etc.
    if 'current_service_details' not in st.session_state:
        st.session_state.current_service_details = None # Dict from service.yaml
    if 'current_monitoring_charts' not in st.session_state:
        st.session_state.current_monitoring_charts = [] # List of chart file paths


# --- Helper functions to update state ---

def set_selected_project(project_id: Optional[str]):
    """Updates the selected project, resetting dependent state."""
    st.session_state.selected_project_id = project_id
    st.session_state.selected_service_id = None # Reset service when project changes
    st.session_state.services_list = []
    st.session_state.current_investigation_id = None
    st.session_state.show_chat_interface = False
    st.session_state.current_service_details = None
    st.session_state.current_monitoring_charts = []
    st.session_state.investigation_titles = {}


def set_selected_service(service_id: Optional[str]):
    """Updates the selected service, resetting dependent state."""
    st.session_state.selected_service_id = service_id
    st.session_state.current_investigation_id = None # Reset investigation when service changes
    st.session_state.show_chat_interface = False
    st.session_state.current_service_details = None # Will be re-fetched
    st.session_state.current_monitoring_charts = [] # Will be re-fetched
    st.session_state.investigation_titles = {} # Will be re-fetched


def set_current_investigation(investigation_id: Optional[int]):
    """Sets the active investigation ID and triggers chat view."""
    st.session_state.current_investigation_id = investigation_id
    st.session_state.show_chat_interface = (investigation_id is not None)
    # Reset messages, they will be loaded for the specific investigation
    st.session_state.current_chat_messages = []


def update_config(user_id: str, model: str, region: str):
    """Updates configuration values in session state."""
    st.session_state.user_id = user_id
    st.session_state.gemini_model = model
    st.session_state.cloud_region = region
    # Potentially trigger project/service list refresh if user/region changes impact permissions/availability
    # For simplicity, let's assume they might need manual refresh or handle in UI logic


def add_chat_message(role: str, content: str, chart_path: Optional[str] = None):
    """Adds a message to the current chat display in session state."""
    st.session_state.current_chat_messages.append(
        {"role": role, "content": content, "chart": chart_path}
    )

EOF

# --- lib/streamlit2/db.py ---
cat << 'EOF' > lib/streamlit2/db.py
import sqlite3
from .config import DB_FILE
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Database Initialization ---
def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Investigations table: Tracks individual chat sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    region TEXT NOT NULL,
                    title TEXT DEFAULT 'New Investigation',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Messages table: Stores messages for each investigation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    chart_filename TEXT, -- Store path to chart image if applicable
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id)
                )
            """)
            conn.commit()
            logger.info(f"Database '{DB_FILE}' initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database error during initialization: {e}", exc_info=True)
        raise # Re-raise the exception to be caught by the caller

# --- Investigation Management ---
def create_investigation(project_id: str, service_id: str, region: str, title: str = "New Investigation") -> int:
    """Creates a new investigation record and returns its ID."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO investigations (project_id, service_id, region, title) VALUES (?, ?, ?, ?)",
                (project_id, service_id, region, title)
            )
            conn.commit()
            new_id = cursor.lastrowid
            logger.info(f"Created investigation ID: {new_id} for {project_id}/{service_id}")
            return new_id
    except sqlite3.Error as e:
        logger.error(f"Failed to create investigation for {project_id}/{service_id}: {e}", exc_info=True)
        raise

def get_investigations_for_service(project_id: str, service_id: str, region: str) -> List[Dict[str, Any]]:
    """Retrieves all investigations (id, title) for a specific project, service, and region."""
    investigations = []
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row # Return rows as dict-like objects
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at FROM investigations WHERE project_id = ? AND service_id = ? AND region = ? ORDER BY created_at DESC",
                (project_id, service_id, region)
            )
            investigations = [dict(row) for row in cursor.fetchall()]
            logger.debug(f"Found {len(investigations)} investigations for {project_id}/{service_id}")
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve investigations for {project_id}/{service_id}: {e}", exc_info=True)
        # Return empty list on error
    return investigations

def update_investigation_title(investigation_id: int, new_title: str):
    """Updates the title of an existing investigation."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE investigations SET title = ? WHERE id = ?",
                (new_title, investigation_id)
            )
            conn.commit()
            logger.info(f"Updated title for investigation ID: {investigation_id}")
    except sqlite3.Error as e:
        logger.error(f"Failed to update title for investigation {investigation_id}: {e}", exc_info=True)
        raise


# --- Message Management ---
def save_message(investigation_id: int, role: str, content: str, chart_filename: Optional[str] = None):
    """Saves a message to the database."""
    if not isinstance(investigation_id, int) or investigation_id <= 0:
        logger.error(f"Invalid investigation_id provided to save_message: {investigation_id}")
        return # Or raise error

    if role not in ['user', 'assistant']:
         logger.error(f"Invalid role provided to save_message: {role}")
         return # Or raise error

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (investigation_id, role, content, chart_filename) VALUES (?, ?, ?, ?)",
                (investigation_id, role, content, chart_filename)
            )
            conn.commit()
            logger.debug(f"Saved message for investigation {investigation_id}, role: {role}")
    except sqlite3.Error as e:
        logger.error(f"Failed to save message for investigation {investigation_id}: {e}", exc_info=True)
        raise


# --- Data Loading ---
# @st.cache_data # Cache results based on investigation_id
def load_messages(investigation_id: int) -> List[Dict[str, Any]]:
    """Loads all messages for a given investigation ID, ordered by timestamp."""
    messages = []
    if not isinstance(investigation_id, int) or investigation_id <= 0:
        logger.warning(f"Invalid investigation_id requested for loading messages: {investigation_id}")
        return []

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row # Return rows as dict-like objects
            cursor = conn.cursor()
            cursor.execute(
                """SELECT role, content, chart_filename, timestamp
                   FROM messages
                   WHERE investigation_id = ?
                   ORDER BY timestamp ASC""",
                (investigation_id,)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            logger.debug(f"Loaded {len(messages)} messages for investigation {investigation_id}")
    except sqlite3.Error as e:
        logger.error(f"Failed to load messages for investigation {investigation_id}: {e}", exc_info=True)
        # Return empty list on error
    return messages

EOF

# --- lib/streamlit2/gcp_helpers.py ---
cat << 'EOF' > lib/streamlit2/gcp_helpers.py
import streamlit as st
from lib.ricc_utils import get_projects_by_user_faker # Assuming this exists
from lib.ricc_cloud_run import get_cloud_run_endpoints # Assuming this exists
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
        # services = get_cloud_run_services(project_id=project_id, region=region)
        # return [s['metadata']['name'] for s in services] # Adjust based on actual API response
        # Assuming get_cloud_run_endpoints returns a list of service names
        return get_cloud_run_endpoints(project_id=project_id, region=region)
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

EOF


# --- lib/streamlit2/ui.py ---
cat << 'EOF' > lib/streamlit2/ui.py
import streamlit as st
from .state import (
    update_config, set_selected_project, set_selected_service,
    set_current_investigation, add_chat_message
)
from .gcp_helpers import (
    fetch_projects, fetch_services, fetch_service_details, fetch_monitoring_charts
)
from .db import (
    create_investigation, get_investigations_for_service, load_messages, save_message
)
from lib.ricc_genai import GeminiChatSession # Assuming this exists
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# --- UI Building Blocks ---

def display_configuration_editor():
    """Displays the configuration section in the sidebar."""
    with st.sidebar.expander("⚙️ Configuration", expanded=False):
        st.caption("Current Settings:")
        st.write(f"👤 User: `{st.session_state.user_id}`")
        st.write(f"♊ Model: `{st.session_state.gemini_model}`")
        st.write(f"🌍 Region: `{st.session_state.cloud_region}`")
        st.write(f"🔑 API Key Set: `{'Yes' if st.session_state.api_key else 'No 🚨'}`")

        st.divider()
        st.caption("Edit Settings:")

        # Use a form for editing to update all at once
        with st.form("config_form"):
            new_user_id = st.text_input("User Email", value=st.session_state.user_id)
            new_model = st.selectbox(
                "Gemini Model",
                options=st.session_state.available_models,
                index=st.session_state.available_models.index(st.session_state.gemini_model)
                     if st.session_state.gemini_model in st.session_state.available_models else 0
            )
            new_region = st.text_input("Cloud Region", value=st.session_state.cloud_region)
            # API key editing is generally discouraged in UI for security
            # Consider instructing users to set the ENV VAR instead.
            # new_api_key = st.text_input("API Key (optional)", value=st.session_state.api_key or "", type="password")

            submitted = st.form_submit_button("💾 Save Configuration")
            if submitted:
                if not new_user_id or not new_region:
                     st.warning("User ID and Region cannot be empty.")
                else:
                    update_config(new_user_id, new_model, new_region)
                    st.success("Configuration updated!")
                    st.rerun() # Rerun to reflect changes immediately


def display_investigation_list():
    """Displays the list of investigations in the sidebar."""
    with st.sidebar.expander("📜 Investigations", expanded=True):
        if not st.session_state.selected_project_id or not st.session_state.selected_service_id:
            st.caption("Select a Project and Service first.")
            return

        st.caption(f"For: `{st.session_state.selected_project_id} / {st.session_state.selected_service_id}`")

        # Fetch investigation titles if not already loaded for this service
        # This avoids redundant DB queries on every rerun unless the service changes
        # Note: If titles can change, this caching needs invalidation logic
        if not st.session_state.investigation_titles:
            investigations_data = get_investigations_for_service(
                st.session_state.selected_project_id,
                st.session_state.selected_service_id,
                st.session_state.cloud_region
            )
            # Store titles keyed by ID
            st.session_state.investigation_titles = {inv['id']: inv['title'] for inv in investigations_data}

        if not st.session_state.investigation_titles:
            st.caption("No investigations yet for this service.")
            return

        # Display investigations, highlight the active one
        for inv_id, inv_title in st.session_state.investigation_titles.items():
            button_type = "primary" if inv_id == st.session_state.current_investigation_id else "secondary"
            if st.button(f"📄 {inv_title or f'Investigation {inv_id}'}", key=f"inv_btn_{inv_id}", use_container_width=True, type=button_type):
                if st.session_state.current_investigation_id != inv_id:
                    set_current_investigation(inv_id)
                    # Force rerun ONLY if selection changed to load messages and switch view
                    st.rerun()
                # If already selected, clicking again does nothing here.


def build_sidebar():
    """Builds the sidebar UI elements."""
    st.sidebar.title("Cloud Run Investigator 🕵️‍♀️")
    st.sidebar.divider()

    display_configuration_editor()
    st.sidebar.divider()
    display_investigation_list()


def display_project_service_selector():
    """Displays dropdowns for selecting project and service."""
    st.subheader("🎯 Select Project and Service")

    # --- Project Selector ---
    # Fetch projects only if the list is empty or user changed
    # (Simple check - could be more robust based on user/config changes)
    if not st.session_state.projects_list:
        st.session_state.projects_list = fetch_projects(st.session_state.user_id)

    # Prepare options, adding a placeholder if needed
    project_options = ["<Select a Project>"] + st.session_state.projects_list
    current_project_index = 0
    if st.session_state.selected_project_id and st.session_state.selected_project_id in st.session_state.projects_list:
        current_project_index = project_options.index(st.session_state.selected_project_id)

    selected_project = st.selectbox(
        "Google Cloud Project",
        options=project_options,
        index=current_project_index,
        key="project_selector",
        # on_change=lambda: set_selected_project(st.session_state.project_selector if st.session_state.project_selector != "<Select a Project>" else None)
    )
    # Handle selection change manually to reset dependencies
    if selected_project != "<Select a Project>" and selected_project != st.session_state.selected_project_id:
         set_selected_project(selected_project)
         st.rerun() # Rerun to fetch services for the new project
    elif selected_project == "<Select a Project>" and st.session_state.selected_project_id is not None:
         set_selected_project(None)
         st.rerun() # Rerun to clear service selector


    # --- Service Selector (dependent on Project) ---
    if st.session_state.selected_project_id:
        # Fetch services only if project is selected and list is empty or project changed
        # This logic is implicitly handled by set_selected_project resetting services_list
        if not st.session_state.services_list:
             st.session_state.services_list = fetch_services(
                 st.session_state.selected_project_id,
                 st.session_state.cloud_region
             )

        service_options = ["<Select a Service>"] + st.session_state.services_list
        current_service_index = 0
        if st.session_state.selected_service_id and st.session_state.selected_service_id in st.session_state.services_list:
            current_service_index = service_options.index(st.session_state.selected_service_id)

        selected_service = st.selectbox(
            f"Cloud Run Service (in {st.session_state.cloud_region})",
            options=service_options,
            index=current_service_index,
            key="service_selector",
            # on_change=lambda: set_selected_service(st.session_state.service_selector if st.session_state.service_selector != "<Select a Service>" else None)
        )
        # Handle selection change manually
        if selected_service != "<Select a Service>" and selected_service != st.session_state.selected_service_id:
            set_selected_service(selected_service)
            st.rerun() # Rerun to fetch details for the new service
        elif selected_service == "<Select a Service>" and st.session_state.selected_service_id is not None:
            set_selected_service(None)
            st.rerun() # Rerun to clear details view

    else:
        st.caption("Select a project to see available Cloud Run services.")


def display_synoptic_view():
    """Displays the detailed synoptic view for the selected service."""
    project = st.session_state.selected_project_id
    service = st.session_state.selected_service_id
    region = st.session_state.cloud_region

    st.header(f"🔎 Synoptic View: {service}")
    st.caption(f"Project: `{project}` | Region: `{region}`")

    # Fetch details if not already loaded for this service
    if st.session_state.current_service_details is None:
        st.session_state.current_service_details = fetch_service_details(project, service, region)

    service_details = st.session_state.current_service_details

    if not service_details:
        st.warning("Could not load service details. Cannot display synoptic view.", icon="⚠️")
        # Maybe add a button to retry fetching?
    else:
        st.subheader("Configuration Summary")
        try:
            # Safely extract data using .get() with defaults
            container = service_details.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [{}])[0]
            limits = container.get('resources', {}).get('limits', {})
            cpu_limit = limits.get('cpu', 'N/A')
            memory_limit = limits.get('memory', 'N/A')
            env_vars = container.get('env', [])
            image_uri = container.get('image', 'N/A') # Corrected key based on gcloud output 'image'
            service_urls = service_details.get('status', {}).get('url', 'N/A') # Primary URL

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="CPU Limit ⚙️", value=cpu_limit)
            with col2:
                st.metric(label="Memory Limit 💾", value=memory_limit)
            with col3:
                st.link_button("🔗 Service URL", service_urls)


            st.write(f"**Base Image:** `{image_uri}`")

            with st.expander("Environment Variables"):
                if env_vars:
                    # Filter out variables with valueFrom (like secrets) for cleaner display
                    display_vars = {var['name']: var.get('value', '******') for var in env_vars if 'value' in var}
                    if display_vars:
                         st.dataframe(display_vars)
                    else:
                         st.caption("No simple key-value environment variables defined.")
                else:
                    st.caption("No environment variables defined.")

        except Exception as e:
            st.error(f"🚨 Error parsing service details: {e}")
            logger.error(f"Error parsing service details dict for {service}: {e}", exc_info=True)


    # --- Monitoring Charts ---
    st.subheader("📊 Monitoring Charts")
    # Fetch chart paths if not already loaded
    if not st.session_state.current_monitoring_charts:
        st.session_state.current_monitoring_charts = fetch_monitoring_charts(project, service)

    chart_paths = st.session_state.current_monitoring_charts

    if not chart_paths:
        st.caption("No monitoring charts found in the cache.")
    else:
        # Display charts, potentially in columns
        num_cols = 3 # Adjust as needed
        cols = st.columns(num_cols)
        for i, chart_path in enumerate(chart_paths):
            try:
                with cols[i % num_cols]:
                    st.image(str(chart_path), caption=chart_path.name, use_column_width=True)
            except Exception as e:
                 st.warning(f"Could not load chart: {chart_path.name} ({e})")
                 logger.warning(f"Failed to load image {chart_path}: {e}", exc_info=True)


    st.divider()

    # --- Investigation Buttons ---
    st.subheader("Investigations")

    # Button to start a new investigation
    if st.button("➕ Start New Investigation", type="primary"):
        try:
            new_inv_id = create_investigation(project, service, region)
            set_current_investigation(new_inv_id)
             # Add new investigation to the sidebar list immediately
            st.session_state.investigation_titles[new_inv_id] = f"Investigation {new_inv_id}"
            st.rerun() # Switch to chat view
        except Exception as e:
            st.error(f"🚨 Failed to create new investigation: {e}")
            logger.error(f"Failed to create investigation via button: {e}", exc_info=True)

    # Buttons for existing investigations (fetched in sidebar logic, use titles from state)
    if st.session_state.investigation_titles:
        st.write("Continue existing investigation:")
        cols = st.columns(3) # Adjust layout as needed
        i = 0
        for inv_id, inv_title in st.session_state.investigation_titles.items():
             # Skip the currently active one if already in chat view (though we aren't here)
            # if inv_id == st.session_state.current_investigation_id: continue

            # Place button in columns
            with cols[i % len(cols)]:
                if st.button(f"▶️ {inv_title or f'Investigation {inv_id}'}", key=f"cont_inv_{inv_id}", use_container_width=True):
                    set_current_investigation(inv_id)
                    st.rerun() # Switch to chat view
            i += 1


def display_chat_interface():
    """Displays the chat interface for the current investigation."""
    investigation_id = st.session_state.current_investigation_id
    project = st.session_state.selected_project_id
    service = st.session_state.selected_service_id
    region = st.session_state.cloud_region
    model = st.session_state.gemini_model
    api_key = st.session_state.api_key

    if not investigation_id:
        st.error("No investigation selected.")
        return

    # Try to get title from sidebar cache, fallback to ID
    title = st.session_state.investigation_titles.get(investigation_id, f"Investigation {investigation_id}")
    st.header(f"💬 Investigation: {title}")
    st.caption(f"Service: `{project} / {service}` | Model: `{model}`")

    # Load messages if not already loaded or if investigation changed
    if not st.session_state.current_chat_messages:
        st.session_state.current_chat_messages = load_messages(investigation_id)

    # Display chat messages from history
    for msg in st.session_state.current_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart"):
                try:
                    # Ensure chart path is valid before displaying
                    chart_path = Path(msg["chart"])
                    if chart_path.is_file():
                        st.image(str(chart_path), caption="Generated Chart")
                    else:
                        st.caption(f"[Chart not found: {msg['chart']}]")
                        logger.warning(f"Chart file not found during display: {chart_path}")
                except Exception as e:
                     st.caption(f"[Error loading chart: {e}]")
                     logger.warning(f"Error loading chart image {msg['chart']}: {e}", exc_info=True)


    # --- Chat Input ---
    if prompt := st.chat_input("Ask Gemini about this service..."):
        # 1. Save and display user message immediately
        logger.info(f"[Invest. {investigation_id}] User: {prompt}")
        save_message(investigation_id, "user", prompt)
        add_chat_message("user", prompt) # Add to session state for immediate display

        # Ensure API key is available
        if not api_key:
            st.error("🚨 GOOGLE_API_KEY is not configured. Cannot contact Gemini.")
            st.stop()

        # 2. Prepare for and call Gemini
        try:
            # Instantiate Gemini Chat Session (consider caching/reusing?)
            # This might need adjustment based on your GeminiChatSession implementation
            # especially regarding how history is passed and function calling is handled.
            chat_session = GeminiChatSession(
                project_id=project,
                region=region,
                # api_key=api_key, # Assuming the class handles the key internally if needed
                model_name=model, # Ensure correct parameter name
                # Pass previous messages if required by your class
                # history=st.session_state.current_chat_messages # Adjust format as needed
                debug=True # Or link to a debug flag
            )

            # Display thinking indicator
            with st.chat_message("assistant"):
                with st.spinner("🤔 Gemini is thinking..."):
                    # --- This is the core Gemini interaction ---
                    # Replace with your actual function call method
                    # This needs to handle potential function calls and streaming.

                    # Example: Simple text generation (replace with your actual call)
                    # response_stream = chat_session.send_simple_message_stream(prompt)
                    # full_response = st.write_stream(response_stream)

                    # Example: Function calling (conceptual)
                    # Assume send_message returns text and potentially structured data
                    # for function calls/charts. You'll need to adapt this precisely.
                    response_data = chat_session.send_message_with_function_calling(
                         user_input=prompt,
                         # Potentially pass available tools/functions here
                    )

                    # --- Process Gemini Response ---
                    assistant_text = response_data.get("text", "Sorry, I couldn't process that.")
                    chart_info = response_data.get("chart_filename") # Assuming this structure

                    logger.info(f"[Invest. {investigation_id}] Assistant: {assistant_text[:100]}...")
                    if chart_info:
                        logger.info(f"[Invest. {investigation_id}] Assistant generated chart: {chart_info}")


            # 3. Save and display assistant message(s)
            save_message(investigation_id, "assistant", assistant_text, chart_filename=chart_info)
            add_chat_message("assistant", assistant_text, chart_path=chart_info)

            # 4. Rerun to display the new messages from session state
            st.rerun()

        except Exception as e:
            error_msg = f"🚨 An error occurred while interacting with Gemini: {e}"
            st.error(error_msg)
            logger.error(f"Gemini interaction failed for Invest {investigation_id}: {e}", exc_info=True)
            # Optionally save an error message to the chat history?
            # save_message(investigation_id, "assistant", f"Error: {e}")
            # add_chat_message("assistant", f"Error: {e}")
            # st.rerun()


def build_main_area():
    """Builds the main content area based on the current state."""

    # 1. Always display selectors at the top
    display_project_service_selector()
    st.divider()

    # 2. Conditional display: Synoptic View or Chat Interface
    if st.session_state.current_investigation_id and st.session_state.show_chat_interface:
        # If an investigation is selected, show the chat
        display_chat_interface()
    elif st.session_state.selected_project_id and st.session_state.selected_service_id:
        # If project/service selected but no active chat, show synoptic view
        display_synoptic_view()
    else:
        # Initial state or after deselecting project/service
        st.info("👋 Select a Google Cloud Project and Cloud Run Service to begin.", icon="☁️")


def build_ui():
    """Constructs the entire Streamlit UI."""
    build_sidebar()
    build_main_area()

EOF


# --- lib/ricc_colors.py ---
# (Adding a basic color library as requested previously)
cat << 'EOF' > lib/ricc_colors.py
# Basic ANSI escape codes for colors
# Reference: https://gist.github.com/chrisbuilds/76914e33a0a54e96e7828d5846c5c04d

# Standard Colors
COLOR_BLACK = "\033[0;30m"
COLOR_RED = "\033[0;31m"
COLOR_GREEN = "\033[0;32m"
COLOR_YELLOW = "\033[0;33m"
COLOR_BLUE = "\033[0;34m"
COLOR_PURPLE = "\033[0;35m"
COLOR_CYAN = "\033[0;36m"
COLOR_WHITE = "\033[0;37m"

# Bold Colors
COLOR_BOLD_BLACK = "\033[1;30m"
COLOR_BOLD_RED = "\033[1;31m"
COLOR_BOLD_GREEN = "\033[1;32m"
COLOR_BOLD_YELLOW = "\033[1;33m"
COLOR_BOLD_BLUE = "\033[1;34m"
COLOR_BOLD_PURPLE = "\033[1;35m"
COLOR_BOLD_CYAN = "\033[1;36m"
COLOR_BOLD_WHITE = "\033[1;37m"

# Underline
TEXT_UNDERLINE = "\033[4m"

# Reset Code
COLOR_RESET = "\033[0m"

# Simple function to colorize text for terminal output
def colorize(text: str, color_code: str) -> str:
    """Applies ANSI color code to text and resets."""
    return f"{color_code}{text}{COLOR_RESET}"

# Example Usage (if run directly)
if __name__ == "__main__":
    print(f"This is {colorize('important', COLOR_BOLD_RED)} text.")
    print(f"This is {colorize('information', COLOR_BLUE)}.")
    print(f"This is {colorize('a warning', COLOR_YELLOW)}.")
    print(f"This is {colorize(colorize('underlined green', TEXT_UNDERLINE), COLOR_GREEN)}.")

EOF


# --- lib/__init__.py ---
# (Ensure this exists if not already there)
touch lib/__init__.py

# --- Make runnable ---
chmod +x sbrodola.sh

echo "✅ File structure created successfully!"
echo "🚀 To run the app:"
echo "   1. Ensure dependencies are installed: pip install streamlit google-generativeai pyyaml google-cloud-monitoring google-cloud-run google-cloud-resource-manager sqlalchemy python-dotenv"
echo "   2. Make sure GOOGLE_API_KEY environment variable is set (e.g., in a .env file or export GOOGLE_API_KEY='your-key')."
echo "   3. Run: streamlit run app2.py"
echo "🔧 Remember to implement the actual GCP calls and Gemini function calling logic where placeholders exist (e.g., in gcp_helpers.py, ui.py chat section)."
