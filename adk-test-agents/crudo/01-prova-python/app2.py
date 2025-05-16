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
