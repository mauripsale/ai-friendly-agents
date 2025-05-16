#!/bin/bash

# sbrodola.sh - Generates the Streamlit Cloud Run Investigator structure (v2)

echo "🚀 Creating directories..."
mkdir -p lib/streamlit
mkdir -p .cache # Just in case it doesn't exist

echo "🎨 Ensuring color library placeholder exists (if needed)..."
# Add color lib generation here if it wasn't present from previous run

echo "🐍 Creating/Updating Python files..."

# --- app.py ---
cat << EOF > app.py
import streamlit as st
import os
from pathlib import Path
import yaml # Need yaml for parsing service config

# Assuming your existing libs are importable
from lib.streamlit import state, ui, database, helpers

# --- App Configuration ---
APP_TITLE = "Cloud Run Investigator 🕵️‍♂️☁️"
DB_FILE = Path("convos.sqlite3")
CACHE_DIR = Path(".cache") # Base cache directory

st.set_page_config(page_title=APP_TITLE, layout="wide")
# No main title here, let the view render its own title/header

# --- Initialization ---
# Ensure DB exists
database.initialize_database(DB_FILE)

# Initialize session state (config, investigations, etc.)
# Pass db_file for potential use during init
state.initialize_session_state(db_file=DB_FILE)

# --- Load Data ---
# Load investigations from DB into session state ONLY if they haven't been loaded yet in this session
if "investigations_loaded" not in st.session_state:
    print("Attempting to load investigations from DB...")
    state.load_investigations_from_db() # Populates st.session_state.investigations
    st.session_state.investigations_loaded = True # Mark as loaded for this session
    # Decide initial state AFTER loading
    if not st.session_state.investigations:
         print("No investigations found in DB, creating welcome message.")
         # Only create welcome if DB is truly empty after load attempt
         state.create_new_investigation(name="👋 Welcome - Start Here!", activate=True)
    elif not st.session_state.current_investigation_id:
        # If loaded but none selected, select the most recent (optional)
        try:
            most_recent_id = list(st.session_state.investigations.keys())[0] # Assumes load sorts desc
            st.session_state.current_investigation_id = most_recent_id
            print(f"Auto-selected most recent investigation: {most_recent_id}")
        except IndexError:
             print("Loaded investigations but list is unexpectedly empty.")


# --- UI Rendering ---
# Render the sidebar (controls, investigation list)
# Pass callback for service selection change
ui.render_sidebar(cache_dir=CACHE_DIR, service_select_callback=state.set_synoptic_view_mode)

# --- Main Panel Logic ---
# Decide whether to show Synoptic View or Chat Interface
selected_project = st.session_state.get("project_id")
selected_service = st.session_state.get("service_name")
current_investigation_id = st.session_state.get("current_investigation_id")
view_mode = st.session_state.get("view_mode", "chat") # Default to chat if no mode set

if view_mode == "synoptic" and selected_project and selected_service:
    st.title(f"🔭 Synoptic View: {selected_service}")
    # Render the synoptic info page for the selected service
    ui.render_synoptic_view(
        project_id=selected_project,
        service_name=selected_service,
        region=st.session_state.cloud_region,
        cache_dir=CACHE_DIR
    )
elif current_investigation_id and current_investigation_id in st.session_state.investigations:
     st.title(f"💬 Chat: {st.session_state.investigations[current_investigation_id].get('name', 'Investigation')}")
     # Render the chat interface for the active investigation
     ui.render_chat_interface(db_file=DB_FILE)
else:
    # Fallback / Initial state before anything is selected or if current investigation is deleted
    st.title(APP_TITLE)
    st.info("👈 Select a Project and Service, or an existing Investigation from the sidebar.")
    # Optionally show welcome message or tutorial here if desired

# Optional: Add footer or debug info
# st.sidebar.markdown("---")
# if st.session_state.get("debug_mode"):
#    with st.expander("🐛 Session State Debug"):
#       st.json(st.session_state)

EOF

# --- lib/__init__.py ---
touch lib/__init__.py

# --- lib/streamlit/__init__.py ---
touch lib/streamlit/__init__.py

# --- lib/streamlit/state.py ---
cat << EOF > lib/streamlit/state.py
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
        initial_text = f"🕵️‍♂️ Starting investigation for Service: `{context_service}` in Project: `{context_project}` (Region: {context_region})"
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

EOF

# --- lib/streamlit/ui.py ---
cat << EOF > lib/streamlit/ui.py
import streamlit as st
from pathlib import Path
import time # For simulating streaming
import yaml # For parsing service.yaml in synoptic view

# Use relative imports for modules within the streamlit package
from . import state, helpers, database

# Import specific functions needed for UI (selectors, etc.)
# Ensure these exist and have correct signatures in your core libs!
try:
    from lib.ricc_gcp import get_projects_by_user
except ImportError:
    st.error("Failed to import get_projects_by_user from lib.ricc_gcp")
    # Define a dummy function to avoid crashing the app immediately
    def get_projects_by_user(user_id): return []
try:
    from lib.ricc_cloud_run import get_cloud_run_endpoints
except ImportError:
    st.error("Failed to import get_cloud_run_endpoints from lib.ricc_cloud_run")
    def get_cloud_run_endpoints(project_id, region): return []
try:
    from lib.ricc_genai import generate_content_with_function_calling # Placeholder!
    # Define a dummy if needed for testing UI without full backend
    # def generate_content_with_function_calling(**kwargs):
    #     yield "Simulated response chunk 1..."
    #     time.sleep(0.5)
    #     yield "Simulated response chunk 2."

except ImportError:
     st.error("Failed to import generate_content_with_function_calling from lib.ricc_genai")
     # Define dummy generator
     def generate_content_with_function_calling(**kwargs):
         yield "ERROR: Gemini function not imported."


# --- Constants ---
USER_AVATAR = "🧑‍💻"
MODEL_AVATAR = "🤖"
DELETE_ICON = "🗑️" # Or "💥" or "❌"

# --- Sidebar Rendering ---
def render_sidebar(cache_dir: Path, service_select_callback):
    """Renders the sidebar content."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"User: {st.session_state.user_id}")
        st.caption(f"Model: {st.session_state.gemini_model}")
        st.caption(f"Region: {st.session_state.cloud_region}") # Default region for lookups

        st.markdown("---")

        # --- Project & Service Selection ---
        st.header("🎯 Select Service")

        # Project Selector
        if not st.session_state.get('available_projects'):
             with st.spinner("Fetching projects..."):
                  try:
                       st.session_state.available_projects = get_projects_by_user(st.session_state.user_id)
                       # Assuming returns list of strings (Project IDs) based on previous fix
                  except Exception as e:
                       st.error(f"Failed to get projects: {e}")
                       st.session_state.available_projects = []

        # Use a temporary variable to hold selection before committing to state if needed,
        # but binding with 'key' and using 'on_change' is standard.
        st.selectbox(
            "Select GCP Project:",
            options=st.session_state.available_projects,
            index=None if not st.session_state.project_id else st.session_state.available_projects.index(st.session_state.project_id),
            key="project_id", # Binds to session state automatically
            placeholder="Choose a project...",
            # No on_change needed here, service selector depends on it
        )

        # Service Selector (only if project is selected)
        selected_service_name = None
        if st.session_state.project_id:
             # Fetch services if project changes or services aren't loaded for this project
             # This could be more efficient by caching per project_id
             current_services = st.session_state.get(f"services_{st.session_state.project_id}", [])
             if not current_services:
                 with st.spinner(f"Fetching Cloud Run services for {st.session_state.project_id}..."):
                    try:
                        current_services = get_cloud_run_endpoints(
                            project_id=st.session_state.project_id,
                            region=st.session_state.cloud_region # Use default region for discovery
                        )
                        st.session_state[f"services_{st.session_state.project_id}"] = current_services
                    except Exception as e:
                        st.error(f"Failed to get services for {st.session_state.project_id}: {e}")
                        current_services = []

             # Get current index for the selectbox if a service is already selected
             try:
                 current_service_index = current_services.index(st.session_state.service_name) \
                     if st.session_state.service_name and st.session_state.service_name in current_services \
                     else None
             except ValueError:
                 current_service_index = None # Service name in state not found in list

             st.selectbox(
                  f"Select Cloud Run Service ({st.session_state.cloud_region}):",
                  options=current_services,
                  index=current_service_index,
                  key="service_name", # Binds to session state
                  placeholder="Choose a service...",
                  on_change=service_select_callback # Call state function to change view mode
             )

        st.markdown("---")

        # --- Investigation Management ---
        st.header("📜 Investigations")

        # Button to create a new, generic investigation
        if st.button("➕ New Blank Investigation", use_container_width=True):
             state.create_new_investigation(activate=True) # Will switch view to chat

        # List existing investigations with delete buttons
        if st.session_state.investigations:
            # Sort investigations, e.g., by creation date descending
            sorted_investigations = sorted(
                st.session_state.investigations.items(),
                key=lambda item: item[1].get('created_at', '0'),
                reverse=True
            )

            active_inv_id = st.session_state.get("current_investigation_id")
            view_mode = st.session_state.get("view_mode")

            for inv_id, inv_data in sorted_investigations:
                inv_name = inv_data.get('name', 'Untitled Investigation')
                # Use columns for name button and delete button
                col1, col2 = st.columns([0.85, 0.15]) # Adjust ratio as needed

                with col1:
                     # Highlight if active chat, otherwise secondary
                     button_type = "primary" if view_mode == "chat" and inv_id == active_inv_id else "secondary"
                     if st.button(inv_name, key=f"inv_btn_{inv_id}", type=button_type, use_container_width=True):
                         state.switch_investigation(inv_id) # Switches view to chat

                with col2:
                     if st.button(DELETE_ICON, key=f"del_btn_{inv_id}", help=f"Delete '{inv_name}'", use_container_width=True):
                         # Confirmation could be added here using a modal or expander if desired
                         state.delete_investigation(inv_id)
                         # state.delete_investigation handles rerun

        else:
            st.caption("No investigations yet.")

# --- Synoptic View Rendering ---
def render_synoptic_view(project_id: str, service_name: str, region: str, cache_dir: Path):
    """Renders the informational view for a selected Cloud Run service."""

    st.markdown(f"**Project:** `{project_id}` | **Region:** `{region}`")

    with st.spinner(f"Loading details for `{service_name}`..."):
        # Use the existing helper, but we need the parsed dict now
        service_yaml_content, service_urls, monitor_charts = helpers.load_service_data_from_cache(
            cache_dir, project_id, service_name
        )

    if not service_yaml_content:
        st.error(f"Could not load `service.yaml` from cache for {service_name}. Cannot display details.")
        return # Stop rendering if core info is missing

    # Parse the YAML content
    service_dict = None
    try:
        service_dict = yaml.safe_load(service_yaml_content)
    except yaml.YAMLError as e:
        st.error(f"Error parsing service.yaml: {e}")
        st.text(service_yaml_content) # Show raw content on error

    # --- Display Key Information ---
    st.subheader("📊 Key Metrics & Config")
    col1, col2, col3 = st.columns(3)

    cpu_limit = "N/A"
    memory_limit = "N/A"
    base_image = "N/A"
    env_vars = []

    if service_dict: # Safely extract data if parsing succeeded
        try:
            # Safe navigation using .get() with defaults
            container = service_dict.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [{}])[0] # Get first container
            resources = container.get('resources', {})
            limits = resources.get('limits', {})
            cpu_limit = limits.get('cpu', 'N/A')
            memory_limit = limits.get('memory', 'N/A') # Corrected key from user request (was cpu)
            base_image = container.get('image', 'N/A') # Corrected key from user request (was baseImageUri)

            # Extract Env Vars
            raw_env_vars = container.get('env', [])
            env_vars = [{"Name": env.get('name'), "Value": env.get('value', env.get('valueFrom'))} # Handle value/valueFrom
                        for env in raw_env_vars if env.get('name')]

        except (AttributeError, IndexError, TypeError) as e:
            st.warning(f"Could not extract all details from service.yaml structure: {e}")

    with col1:
        st.metric(label="💻 CPU Limit", value=cpu_limit)
    with col2:
        st.metric(label="💾 Memory Limit", value=memory_limit) # Corrected label/icon
    with col3:
         if base_image != "N/A":
             st.metric(label="📦 Base Image", value=base_image.split('/')[-1].split(':')[0], help=base_image) # Show image name, full on hover
         else:
             st.metric(label="📦 Base Image", value="N/A")


    # --- Display URLs ---
    if service_urls:
        st.subheader("🔗 URLs")
        for url in service_urls:
            st.code(url, language=None)
    else:
        st.caption("No public URLs found in service status.") # Clarified source


    # --- Display Environment Variables ---
    if env_vars:
        st.subheader("🔑 Environment Variables")
        # Improve display compared to raw dict list
        st.dataframe(env_vars, use_container_width=True)
    else:
        st.caption("No environment variables found in container spec.")


    # --- Display Monitoring Charts ---
    if monitor_charts:
        st.subheader("📈 Monitoring Charts")
        # Use columns for better layout
        num_cols = min(len(monitor_charts), 3) # Max 3 cols
        cols = st.columns(num_cols)
        col_idx = 0
        for chart_path in monitor_charts:
            with cols[col_idx % num_cols]:
                try:
                    st.image(str(chart_path), caption=chart_path.name, use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading {chart_path.name}: {e}")
            col_idx += 1
    else:
        st.caption("No monitoring charts found in cache.")

    st.markdown("---")

    # --- Investigation Buttons ---
    st.subheader("🚀 Investigations for this Service")

    # Button to start a NEW investigation specific to this service
    if st.button(f"➕ Start New Investigation for {service_name}", type="primary"):
        state.create_new_investigation(
            context_project=project_id,
            context_service=service_name,
            context_region=region, # Pass the region associated with this service
            activate=True # This will switch view to chat
        )

    # Find existing investigations related to this service
    related_investigations = []
    for inv_id, inv_data in st.session_state.investigations.items():
        # Check if context matches the currently selected service
        if (inv_data.get('project_id') == project_id and
            inv_data.get('service_name') == service_name and
            inv_data.get('region') == region):
             related_investigations.append((inv_id, inv_data))

    if related_investigations:
        st.markdown("**Continue existing investigation:**")
        # Sort related investigations maybe?
        related_investigations.sort(key=lambda item: item[1].get('created_at', '0'), reverse=True)
        for inv_id, inv_data in related_investigations:
            if st.button(f"▶️ Continue: {inv_data.get('name', 'Untitled')}", key=f"continue_{inv_id}"):
                state.switch_investigation(inv_id) # Switches view to chat
    else:
        st.caption("No previous investigations found specifically for this service.")


# --- Chat Interface Rendering ---
def render_chat_interface(db_file):
    """Renders the main chat area and handles user input."""
    # Title is now handled in app.py based on view mode

    current_id = st.session_state.get("current_investigation_id")
    if not current_id or current_id not in st.session_state.investigations:
        st.info("No active investigation selected.") # Should generally not be reached if logic in app.py is correct
        return

    investigation = st.session_state.investigations[current_id]

    # Display chat messages from history
    for message in investigation.get("history", []):
        role = message.get("role")
        avatar = USER_AVATAR if role == "user" else MODEL_AVATAR
        with st.chat_message(role, avatar=avatar):
            # Display text content (handle potential structures)
            content = message.get("content") # Expects dict like {"parts": [{"text": ...}]}
            full_text = ""
            if isinstance(content, dict) and "parts" in content:
                 full_text = "\n".join([part.get("text", "") for part in content.get("parts", []) if "text" in part])

            if full_text:
                st.markdown(full_text) # Render markdown

            # Display charts if available (check for key outside 'content')
            chart_filename = message.get("chart_filename")
            if chart_filename:
                chart_path = Path(chart_filename)
                if chart_path.is_file():
                    try:
                        st.image(str(chart_path), caption=f"📊 Chart: {chart_path.name}")
                    except Exception as e:
                        st.error(f"Failed to display chart {chart_path.name}: {e}")
                else:
                    st.warning(f"Chart file not found: {chart_filename}")

    # Chat input - Capture user prompt
    if prompt := st.chat_input(f"Ask Gemini about '{investigation.get('name', 'this investigation')}'..."):
        # 1. Add user message to state and display it immediately
        # Use the standardized message structure
        state.add_message_to_current_investigation(role="user", text=prompt) # Persists here
        # Rerun happens naturally after state update, or explicitly if needed

        # Display the user message that was just added to history
        with st.chat_message("user", avatar=USER_AVATAR):
             st.markdown(prompt)

        # 2. Prepare history for Gemini (check what your function expects)
        # Send the full history up to the user's latest message
        gemini_history = investigation["history"]

        # 3. Call Gemini (handle streaming and function calling)
        try:
            with st.chat_message("assistant", avatar=MODEL_AVATAR):
                message_placeholder = st.empty()
                full_response_text = ""
                final_chart_filename = None

                # --- Streaming Call ---
                # Replace with your actual function call using the prepared history
                response_stream = generate_content_with_function_calling(
                    model_name=st.session_state.gemini_model,
                    # Pass the full prompt or just the latest message? Depends on your function
                    prompt=prompt, # Or maybe construct a prompt object if needed
                    history=gemini_history, # Pass the conversation history
                    # Pass tools definition for function calling here!
                    # tools=YOUR_FUNCTION_DEFINITIONS
                )

                # Process the stream from Gemini
                stream_content_parts = []
                for chunk in response_stream:
                     # Assuming chunk is an object with text or function call parts
                     # This part depends heavily on your Gemini library's streaming response format!
                     # Example: adapt based on actual chunk structure
                     if hasattr(chunk, 'text'):
                          text_chunk = chunk.text
                          full_response_text += text_chunk
                          message_placeholder.markdown(full_response_text + "▌") # Simulate cursor
                          stream_content_parts.append({"text": text_chunk})
                     elif hasattr(chunk, 'function_call'):
                          # Handle function call received mid-stream or at the end
                          # TODO: Implement function call execution logic here
                          st.warning(f"Function call received: {chunk.function_call}")
                          # result = execute_my_tool(chunk.function_call)
                          # Need to send result back to model... complex flow.
                          pass
                     # Check for chart filename if returned specially
                     if hasattr(chunk, 'chart_filename'): # Or however your function returns it
                          final_chart_filename = chunk.chart_filename


                message_placeholder.markdown(full_response_text) # Final text

                # TODO: If function calling requires a second turn, handle it here.
                # This usually involves sending the function result back to the model.

                # Display chart if generated during the response processing
                if final_chart_filename:
                    chart_path = Path(final_chart_filename)
                    if chart_path.is_file():
                         try:
                              st.image(str(chart_path), caption=f"📊 Generated Chart: {chart_path.name}")
                         except Exception as e:
                              st.error(f"Failed display generated chart {chart_path.name}: {e}")
                    else:
                         st.warning(f"Generated chart file not found: {final_chart_filename}")


            # 4. Add final assistant response (potentially just text if chart displayed above)
            # Use the collected stream parts for accurate history
            state.add_message_to_current_investigation(
                 role="assistant",
                 parts=stream_content_parts, # Save the structured parts
                 chart_filename=final_chart_filename # Store chart path with message
            )
            # Rerun not strictly needed here, but might help refresh state cleanly. Consider if issues arise.
            # st.rerun()

        except Exception as e:
            st.error(f"🤖 Oops! Error calling Gemini: {e}")
            # Optionally add error message to chat history
            state.add_message_to_current_investigation(role="assistant", text=f"Error during generation: {e}")
            st.rerun() # Rerun after error to show the error message in chat history

EOF


# --- lib/streamlit/database.py ---
cat << EOF > lib/streamlit/database.py
import sqlite3
import json
from pathlib import Path
import streamlit as st # For error reporting potentially
from contextlib import closing

def _get_connection(db_file: Path):
    """Establishes a connection to the SQLite database."""
    try:
        # Check if the directory exists, create if not (important for initial run)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_file, check_same_thread=False) # check_same_thread=False needed for Streamlit
        conn.execute("PRAGMA foreign_keys = ON;") # Good practice
        return conn
    except sqlite3.Error as e:
        st.error(f"🚨 Database connection error to {db_file}: {e}")
        return None

def initialize_database(db_file: Path):
    """Creates the database and table if they don't exist."""
    if db_file.exists():
        # print(f"Database {db_file} already exists.") # Less verbose
        # Add schema migration logic here if needed in the future
        return

    print(f"Creating database table in {db_file}...")
    conn = _get_connection(db_file)
    if not conn: return # Stop if connection failed

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TEXT,
                    project_id TEXT, -- Context: Project ID associated with the investigation
                    service_name TEXT, -- Context: Service name associated
                    region TEXT,      -- Context: Region associated
                    history TEXT      -- Store history as JSON string
                )
            """)
            conn.commit()
        print("Database table 'investigations' created or verified.")
    except sqlite3.Error as e:
        st.error(f"🚨 Database Error during table initialization: {e}")
    finally:
        if conn: conn.close()

def save_investigation(db_file: Path, investigation_id: str, investigation_data: dict):
    """Saves or updates a single investigation in the database."""
    conn = _get_connection(db_file)
    if not conn: return

    try:
        with closing(conn.cursor()) as cursor:
            # Serialize history to JSON string
            history_json = json.dumps(investigation_data.get("history", []))

            cursor.execute("""
                INSERT INTO investigations (id, name, created_at, project_id, service_name, region, history)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    created_at=excluded.created_at, -- Should this update? Maybe not. Let's keep original creation time.
                    project_id=excluded.project_id,
                    service_name=excluded.service_name,
                    region=excluded.region,
                    history=excluded.history
            """, (
                investigation_id,
                investigation_data.get("name"),
                investigation_data.get("created_at"), # Keep original created_at
                investigation_data.get("project_id"),
                investigation_data.get("service_name"),
                investigation_data.get("region"),
                history_json
            ))
            conn.commit()
        # print(f"Saved investigation {investigation_id} to DB.") # Can be verbose
    except sqlite3.Error as e:
        st.error(f"🚨 Database Error saving investigation {investigation_id}: {e}")
    except json.JSONDecodeError as e:
        st.error(f"🚨 JSON Error serializing history for investigation {investigation_id}: {e}")
    finally:
        if conn: conn.close()


def load_all_investigations(db_file: Path) -> dict:
    """Loads all investigations from the database, returns empty dict on failure."""
    investigations = {}
    conn = _get_connection(db_file)
    if not conn: return investigations # Return empty if connection failed

    try:
        with closing(conn.cursor()) as cursor:
            # Ensure table exists before querying
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='investigations'")
            if cursor.fetchone() is None:
                print("Warning: 'investigations' table not found during load.")
                initialize_database(db_file) # Attempt to create it
                return investigations # Return empty for now

            cursor.execute("SELECT id, name, created_at, project_id, service_name, region, history FROM investigations ORDER BY created_at DESC") # Load newest first
            rows = cursor.fetchall()
            for row in rows:
                inv_id, name, created_at, project_id, service_name, region, history_json = row
                try:
                    history = json.loads(history_json) if history_json else []
                    investigations[inv_id] = {
                        "id": inv_id, # Include ID in the dict value as well
                        "name": name,
                        "created_at": created_at,
                        "project_id": project_id,
                        "service_name": service_name,
                        "region": region,
                        "history": history
                    }
                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ Could not parse history for investigation {inv_id}: {e}. Skipping history.")
                    investigations[inv_id] = {
                        "id": inv_id, "name": name, "created_at": created_at, "project_id": project_id,
                        "service_name": service_name, "region": region, "history": []
                    } # Load with empty history
    except sqlite3.Error as e:
        st.error(f"🚨 Database Error loading investigations: {e}")
        # Return empty dict on load failure
        return {}
    finally:
        if conn: conn.close()

    return investigations

def delete_investigation(db_file: Path, investigation_id: str):
    """Deletes a single investigation from the database."""
    conn = _get_connection(db_file)
    if not conn: return

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("DELETE FROM investigations WHERE id = ?", (investigation_id,))
            conn.commit()
            if cursor.rowcount > 0:
                 print(f"Deleted investigation {investigation_id} from DB.")
            else:
                 print(f"Warning: Tried to delete {investigation_id}, but it was not found in DB.")
    except sqlite3.Error as e:
        st.error(f"🚨 Database Error deleting investigation {investigation_id}: {e}")
    finally:
        if conn: conn.close()


EOF

# --- lib/streamlit/helpers.py ---
# (No significant changes needed here based on request, ensure load_service_data_from_cache is robust)
# Re-generate it just to be safe if previous version wasn't saved.
cat << EOF > lib/streamlit/helpers.py
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

EOF


echo "✅ Done creating/updating files."
echo "👉 Next steps:"
echo "1. Ensure dependencies are installed (streamlit, google-cloud-..., pyyaml)."
echo "2. Review the generated files, especially TODOs and placeholders for function calls and YAML parsing logic."
echo "3. Test the selection flow: Project -> Service -> Synoptic View -> Start/Continue Investigation -> Chat View."
echo "4. Test deleting investigations using the sidebar button."
echo "5. Implement the actual Gemini function calling logic and potential function execution."
echo "6. Run the app: streamlit run app.py"
