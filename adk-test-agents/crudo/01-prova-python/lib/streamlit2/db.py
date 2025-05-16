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

