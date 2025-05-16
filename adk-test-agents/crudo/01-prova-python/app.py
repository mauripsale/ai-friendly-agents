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

