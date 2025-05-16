import streamlit as st
import os
import uuid
from datetime import datetime
from . import database # Use relative import within package

DEFAULT_USER_EMAIL_PATTERN = "{user}@google.com"
DEFAULT_FALLBACK_EMAIL = "ricc@google.com"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
DEFAULT_REGION = "europe-west1"

# --- Helper Functions ---
def get_default_user_id():
    """Gets user ID from ENV or defaults."""
    try:
        user = os.environ.get("USER")
        if user:
            return DEFAULT_USER_EMAIL_PATTERN.format(user=user)
        else:
            st.sidebar.warning("⚠️ USER env var not set. Falling back.") # Show warning in sidebar
            return DEFAULT_FALLBACK_EMAIL
    except Exception as e:
        st.sidebar.warning(f"⚠️ Error getting username: {e}. Falling back.")
        return DEFAULT_FALLBACK_EMAIL

def get_default_gemini_model():
    return os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

def get_default_cloud_region():
    return os.environ.get("GOOGLE_CLOUD_LOCATION", DEFAULT_REGION)

# --- State Initialization ---
def initialize_session_state(db_file):
    """Initializes Streamlit's session state variables if not already done."""
    if "state_initialized" not in st.session_state:
        st.session_state.state_initialized = True
        st.session_state.debug_mode = os.environ.get("DEBUG", "false").lower() == "true"

        # Configuration
        st.session_state.user_id = get_default_user_id()
        st.session_state.gemini_model = get_default_gemini_model()
        st.session_state.cloud_region = get_default_cloud_region() # Region used for lookups

        # GCP Selection State
        st.session_state.project_id = None
        st.session_state.service_name = None
        # Store selected region with service for context, might differ from default GOOGLE_CLOUD_LOCATION
        st.session_state.selected_region = None # Set when service is selected
        st.session_state.available_projects = [] # Cache fetched projects
        st.session_state.available_services = [] # Cache fetched services

        # Investigation / Chat State
        st.session_state.investigations = {} # Populated by load_investigations_from_db
        st.session_state.current_investigation_id = None # ID of the active chat
        st.session_state.db_file = db_file # Store DB file path for easy access

        # View Control State
        # 'chat' = show chat interface for current_investigation_id
        # 'synoptic' = show info page for project_id/service_name
        st.session_state.view_mode = "chat" # Start in chat mode by default

        print("✨ Session state initialized.")
    # else:
        # print("Session state already initialized.") # Avoid noisy logs

# --- View Mode Control ---
def set_synoptic_view_mode():
    """Callback function to switch to synoptic view when a service is selected."""
    # This is called by the on_change of the service selectbox
    if st.session_state.project_id and st.session_state.service_name:
        print(f"Switching to synoptic view for {st.session_state.project_id}/{st.session_state.service_name}")
        st.session_state.view_mode = "synoptic"
        st.session_state.current_investigation_id = None # Deactivate any current chat
        # Store the region associated with this selection
        st.session_state.selected_region = st.session_state.cloud_region
    # Don't automatically rerun here, let Streamlit's natural flow handle it after on_change

def set_chat_view_mode(investigation_id):
    """Switches to chat view for a specific investigation."""
    if investigation_id in st.session_state.investigations:
        print(f"Switching to chat view for investigation: {investigation_id}")
        st.session_state.view_mode = "chat"
        st.session_state.current_investigation_id = investigation_id
        # Rerun is needed here to redraw the main panel immediately
        st.rerun()
    else:
        st.error(f"🚫 Investigation ID {investigation_id} not found!")


# --- Investigation Management ---
def create_new_investigation(name=None, context_project=None, context_service=None, context_region=None, activate=True):
    """Creates a new investigation entry, optionally linked to a service."""
    investigation_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine name and initial message based on context
    if context_project and context_service:
        base_name = f"Investigate {context_service}"
        if not name:
             name = base_name
        initial_text = f"🕵️‍♂️ Starting investigation for Service:  in Project:  (Region: {context_region})"
    else:
        if not name:
            name = f"Investigation {timestamp}"
        initial_text = f"🕵️‍♂️ Starting new investigation: {name}"

    initial_message = {
        "role": "assistant",
        "content": {"parts": [{"text": initial_text }]} # Match Gemini structure
    }

    new_investigation = {
        "name": name,
        "created_at": timestamp,
        "history": [initial_message],
        # Store context with the investigation itself
        "project_id": context_project,
        "service_name": context_service,
        "region": context_region
    }
    st.session_state.investigations[investigation_id] = new_investigation

    # Persist immediately
    database.save_investigation(st.session_state.db_file, investigation_id, new_investigation)
    print(f"💾 Saved new investigation: {investigation_id} - {name}")

    if activate:
        # Switch view to chat mode for this new investigation
        set_chat_view_mode(investigation_id) # This handles state change + rerun
    # If not activating, no rerun needed here

def switch_investigation(investigation_id):
    """Switches the active investigation and view mode."""
    # Just call the view mode switcher
    set_chat_view_mode(investigation_id)

def delete_investigation(investigation_id):
    """Deletes an investigation from state and database."""
    if investigation_id in st.session_state.investigations:
        deleted_name = st.session_state.investigations[investigation_id].get('name', investigation_id)
        print(f"Deleting investigation: {investigation_id} - {deleted_name}")

        # Remove from state
        del st.session_state.investigations[investigation_id]

        # Remove from DB
        database.delete_investigation(st.session_state.db_file, investigation_id)

        # If the deleted one was active, deactivate chat view
        if st.session_state.current_investigation_id == investigation_id:
            st.session_state.current_investigation_id = None
            # Decide where to go: maybe synoptic if service selected, else default
            if st.session_state.project_id and st.session_state.service_name:
                 st.session_state.view_mode = "synoptic"
            else:
                 st.session_state.view_mode = "chat" # Will show fallback message
            print("Deactivated current investigation. Switching view.")

        st.toast(f"💥 Investigation '{deleted_name}' deleted!")
        st.rerun() # Rerun to update UI
    else:
        st.error(f"🚫 Cannot delete: Investigation ID {investigation_id} not found!")


def load_investigations_from_db():
    """Loads all investigations from the database into session state."""
    investigations_data = database.load_all_investigations(st.session_state.db_file)
    if isinstance(investigations_data, dict):
        st.session_state.investigations = investigations_data
        print(f"📚 Loaded {len(investigations_data)} investigations from DB.")
    else:
         # Handle potential error from load_all_investigations if it didn't return a dict
         st.error("Failed to load investigations correctly from database.")
         st.session_state.investigations = {}


def add_message_to_current_investigation(role: str, text: str = None, parts: list = None, chart_filename: str = None):
    """Adds a message to the history of the current investigation and saves."""
    current_id = st.session_state.get("current_investigation_id")
    if not current_id or current_id not in st.session_state.investigations:
        st.error("🚨 No active investigation to add message to!")
        return

    investigation = st.session_state.investigations[current_id]

    # --- Standardize message structure (example using content/parts) ---
    message_content_parts = []
    if text:
        message_content_parts.append({"text": text})
    if parts: # If parts are provided directly (e.g., from Gemini response)
        message_content_parts.extend(parts)

    # Create the message dictionary
    message = {
        "role": role,
        "content": {"parts": message_content_parts} # Gemini API structure
        # Add other metadata if needed, e.g., timestamp
    }
    # --- End Message Structure ---

    # Add chart info if provided (as metadata alongside content)
    if chart_filename:
        message["chart_filename"] = str(chart_filename) # Store as string path

    # Append message to history
    investigation["history"].append(message)

    # Update the investigation in session state
    st.session_state.investigations[current_id] = investigation

    # Save the updated investigation to DB
    database.save_investigation(st.session_state.db_file, current_id, investigation)
    # print(f"💬 Added message to investigation {current_id} and saved.") # Can be verbose

