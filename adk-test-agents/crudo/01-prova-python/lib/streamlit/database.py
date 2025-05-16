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


