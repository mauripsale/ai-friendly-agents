import streamlit as st
from .config import (
    USER_ID,
    GEMINI_MODEL,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_API_KEY,
    AVAILABLE_MODELS_LIST,
)
from typing import List, Dict, Any, Optional



# Make sure these are imported or available in the file's scope
from typing import List, Dict, Any, Optional
import re  # Import the regex module
import logging

# Assuming logger is configured in app2.py or elsewhere
logger = logging.getLogger(__name__)

# Pre-compile the regex for efficiency
# This looks for '.cache/' preceded by a quote (single or double)
# and captures the path inside the quotes (group 1 or 2)
# It allows an optional './' before '.cache/'
CHART_PATH_REGEX = re.compile(r"'(?:\./)?(\.cache/[^']+)'|\"(?:\./)?(\.cache/[^\"]+)\"")


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


def add_chat_message_REMOVEME(role: str, content: str, chart_path: Optional[str] = None):
    """Adds a message to the current chat display in session state."""
    # find chart_path as a regex and add the first to the session
    # print each one of those in debug.
    st.session_state.current_chat_messages.append(
        {"role": role, "content": content, "chart": chart_path}
    )


def add_chat_message(role: str, content: str, chart_path: Optional[str] = None):
    """
    Adds a message to the current chat display in session state.
    Automatically detects file paths like '.cache/...' in quotes
    within the assistant's content if a chart_path isn't explicitly provided.
    """
    detected_chart_path = chart_path  # Prioritize explicitly passed path

    # Only attempt regex detection for assistant messages if no path was passed
    if role == 'assistant' and content and detected_chart_path is None:
        logger.debug("Assistant message with no explicit chart_path, scanning content...")
        match = CHART_PATH_REGEX.search(content)
        if match:
            # Extract the path from the first matching group (group 1 for single quotes, 2 for double)
            extracted_path = match.group(1) or match.group(2)
            if extracted_path:
                detected_chart_path = extracted_path
                logger.info(f"✅ Detected chart path via regex: '{detected_chart_path}'")
            else:
                # This case should be rare with the current regex structure
                 logger.debug(f"Regex matched but failed to extract path from groups: {match.groups()}")
        else:
            logger.debug("No '.cache/...' path found in quotes within the assistant content.")

    # Append the message with the original or detected chart path
    st.session_state.current_chat_messages.append(
        {"role": role, "content": content, "chart": detected_chart_path}
    )
    # Add some logging to see what's being added
    logger.debug(
        f"Adding message to state: role={role}, chart={detected_chart_path}, content='{content[:60]}...'"
    )
