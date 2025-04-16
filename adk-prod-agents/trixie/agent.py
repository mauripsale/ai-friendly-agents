import os
import json
import datetime
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

from google.adk.agents import Agent
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field, ValidationError # Import Pydantic

import dotenv
dotenv.load_dotenv()

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly'] # Assuming read-only for now based on ADC scope
DEFAULT_SHEET_CONFIG_FILE = 'etc/sheets_config.json' # Default filename if ENV is not set

# --- Pydantic Model for Sheet Configuration ---
class SheetConfig(BaseModel):
    """Pydantic model for validating individual sheet configurations."""
    sheet_id: str = Field(..., description="The Google Sheet ID.") # Mandatory
    tab: str = Field(..., description="The exact name of the tab within the sheet.") # Mandatory
    description: str = Field(..., description="A brief description of the sheet/tab content.") # Mandatory

    # Optional but recommended fields
    relevant_columns: Optional[List[str]] = Field(None, description="Specific columns to prioritize or filter by.")
    context: Optional[str] = Field(None, description="Additional context for the LLM about the data or how to use it.")
    skip_first_n_lines: int = Field(0, description="Number of data rows to skip after the header row.", ge=0) # Non-negative integer

    # Other optional fields from original structure
    access: str = Field("read-only", description="Access level required (e.g., 'read-only', 'read-write'). Currently informational.")
    url: Optional[str] = Field(None, description="Optional URL for user reference.")

# --- Environment Variable Handling ---
# Get the JSON file path from ENV, with a default
JSON_SHEET_FILE_PATH_STR = os.getenv('JSON_SHEET_FILE', DEFAULT_SHEET_CONFIG_FILE)
#JSON_SHEET_FILE_PATH = Path(f"trixie/{JSON_SHEET_FILE_PATH_STR}" ) # locally to this code.
JSON_SHEET_FILE_PATH = Path(JSON_SHEET_FILE_PATH_STR) # locally to this code.

print(f"⚙️ JSON_SHEET_FILE_PATH_STR: {JSON_SHEET_FILE_PATH_STR}")
print(f"⚙️ JSON_SHEET_FILE_PATH:     {JSON_SHEET_FILE_PATH}")
print(f"⚙️ is it a file?!?:          {JSON_SHEET_FILE_PATH.is_file()}")
print(f"⚙️ CWD:                      {os.getcwd()}")
print(f"⚙️ GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')} # not necessary but useful..")

if not JSON_SHEET_FILE_PATH.is_file():
    print("⛔ ⚙️ config not found, my existence is futile.")
    exit(-1)
# You could add other ENV vars here if needed, e.g., for Service Accounts if you re-introduce write access logic
# READ_ONLY_SERVICE_ACCOUNT_EMAIL = os.getenv("READ_ONLY_SERVICE_ACCOUNT_EMAIL", "<NOT PROVIDED! Fix your ENV>")


# --- Core Functions ---


# Updated return type hint
def get_sheets() -> Dict[str, Any]:
    """
    Reads sheet configurations from a JSON file specified by JSON_SHEET_FILE env var,
    validates them using Pydantic.

    Returns:
        A dictionary with the following structure:
        On success:
        {
            "result": "success",
            "sheets": [list_of_validated_sheet_config_dictionaries]
        }
        On failure (file not found, JSON error, etc.):
        {
            "result": "error",
            "error_message": "Description of the error",
            "sheets": []
        }
        Note: Individual validation errors for specific sheet entries inside the JSON
        will be logged, but won't cause a top-level error return unless the file
        itself is unreadable or fundamentally invalid (e.g., not a JSON list).
        If the file is readable but contains *no* valid entries, it will return
        success with an empty 'sheets' list.
    """
    validated_sheets = []
    if not JSON_SHEET_FILE_PATH.is_file():
        error_msg = f"Sheet configuration file not found: {JSON_SHEET_FILE_PATH}"
        logging.error(error_msg)
        # Return error dictionary
        return {"result": "error", "error_message": error_msg, "sheets": []}

    try:
        with open(JSON_SHEET_FILE_PATH, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                error_msg = f"Error decoding JSON from {JSON_SHEET_FILE_PATH}: {e}"
                logging.error(error_msg)
                # Return error dictionary
                return {"result": "error", "error_message": error_msg, "sheets": []}

        # Check if the top-level structure is a list
        if not isinstance(data, list):
            error_msg = f"Sheet configuration file {JSON_SHEET_FILE_PATH} does not contain a JSON list at the top level."
            logging.error(error_msg)
             # Return error dictionary
            return {"result": "error", "error_message": error_msg, "sheets": []}

        logging.info(f"Loaded {len(data)} potential sheet configurations from {JSON_SHEET_FILE_PATH}.")
        original_count = len(data)

        for i, entry in enumerate(data):
            try:
                # Validate using Pydantic
                config = SheetConfig(**entry)
                 # Convert Pydantic model to dict for the final list
                validated_sheets.append(config.dict())

                # Log warnings for missing recommended fields (only if validation succeeded)
                if config.relevant_columns is None:
                    logging.warning(f"Sheet config #{i+1} (ID: {config.sheet_id}, Tab: {config.tab}) is missing 'relevant_columns'.")
                if config.context is None:
                     logging.warning(f"Sheet config #{i+1} (ID: {config.sheet_id}, Tab: {config.tab}) is missing 'context'.")

            except ValidationError as e:
                # Log validation errors for individual entries but continue processing others
                logging.error(f"Validation failed for sheet configuration #{i+1} in {JSON_SHEET_FILE_PATH}: {e}")
            except Exception as e:
                 # Log unexpected errors during validation of a specific item
                 logging.error(f"Unexpected error processing sheet configuration #{i+1}: {e}", exc_info=True)

        # Log final count and return success dictionary
        logging.info(f"Successfully validated {len(validated_sheets)} sheet configurations out of {original_count} entries found.")
        return {"result": "success", "sheets": validated_sheets}

    except IOError as e:
        error_msg = f"Error reading file {JSON_SHEET_FILE_PATH}: {e}"
        logging.error(error_msg)
         # Return error dictionary
        return {"result": "error", "error_message": error_msg, "sheets": []}
    except Exception as e:
        # Catch-all for unexpected errors during file handling or processing logic
        error_msg = f"An unexpected error occurred in get_sheets: {e}"
        logging.error(error_msg, exc_info=True) # Log traceback for unexpected errors
         # Return error dictionary
        return {"result": "error", "error_message": error_msg, "sheets": []}


#TODO: def get_sheets(json_file_path: Path = None ) -> List[Dict[str, Any]]:
def get_sheets_old_returning_an_array() -> List[Dict[str, Any]]:
    """
    Reads sheet configurations from a JSON file specified by JSON_SHEET_FILE env var,
    validates them using Pydantic, and returns a list of valid configurations as dictionaries.

    Returns:
        A list of dictionaries, where each dictionary represents a validated sheet configuration.
        Returns an empty list if the file is not found, is invalid JSON, or contains no valid entries.
    """
    validated_sheets = []
    print(f"⚙️ CWD2:                     {os.getcwd()}")

    if not JSON_SHEET_FILE_PATH.is_file():
        logging.error(f"Sheet configuration file not found: {JSON_SHEET_FILE_PATH}")
        return []

    print("get_sheets() called. File FOUND!")

    try:
        with open(JSON_SHEET_FILE_PATH, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                logging.error(f"Sheet configuration file {JSON_SHEET_FILE_PATH} does not contain a list.")
                return []

        logging.info(f"Loaded {len(data)} sheet configurations from {JSON_SHEET_FILE_PATH}.")
        print(f"⚙️ Config file found! {green(JSON_SHEET_FILE_PATH)}")

        for i, entry in enumerate(data):
            try:
                # Validate using Pydantic
                config = SheetConfig(**entry)
                validated_sheets.append(config.dict()) # Convert back to dict for consistency if needed, or return SheetConfig objects

                # Check for missing non-mandatory but suggested fields and log warnings
                if config.relevant_columns is None:
                    logging.warning(f"Sheet config #{i+1} (ID: {config.sheet_id}, Tab: {config.tab}) is missing 'relevant_columns'.")
                if config.context is None:
                     logging.warning(f"Sheet config #{i+1} (ID: {config.sheet_id}, Tab: {config.tab}) is missing 'context'.")
                # No warning needed for skip_first_n_lines as it has a default (0)

            except ValidationError as e:
                logging.error(f"Validation failed for sheet configuration #{i+1} in {JSON_SHEET_FILE_PATH}: {e}")
            except Exception as e:
                 logging.error(f"Unexpected error processing sheet configuration #{i+1}: {e}")


    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {JSON_SHEET_FILE_PATH}: {e}")
        return []
    except IOError as e:
        logging.error(f"Error reading file {JSON_SHEET_FILE_PATH}: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_sheets: {e}")
        return []

    logging.info(f"Successfully validated {len(validated_sheets)} sheet configurations.")
    return validated_sheets


def get_day_today() -> str:
    '''Gets today's date in YYYY-MM-DD format'''
    return str(datetime.date.today()) # Use date() for just the date part


def get_sheet_content_v2(
    sheet_id: str,
    tab_name: str,
    limit_rows: int = 10,
    relevant_columns: Optional[List[str]] = None,
    cleanup_rows_and_columns: bool = True,
    skip_first_n_lines: int = 0 # New parameter
) -> List[Dict[str, Any]]:
    """[V2] Fetches, optionally skips initial data rows, and cleans data from a Google Sheet tab.

    Retrieves rows, uses the first fetched row as headers, skips specified data rows,
    converts remaining rows to dictionaries, and applies optional filtering/cleaning.
    Authentication relies on Application Default Credentials (ADC).

    Args:
        sheet_id: The ID of the Google Sheet.
        tab_name: The exact name of the tab (sheet).
        limit_rows: The maximum number of *final* data rows to return after
                    any filtering/skipping. Defaults to 10.
        relevant_columns: An optional list of column header names to keep.
                          If None or empty (default), all columns are kept initially.
                          Filtering happens before cleanup.
        cleanup_rows_and_columns: If True (default), performs cleaning:
                                 1. Removes key-value pairs where the value is
                                    None or an empty string ("").
                                 2. Removes rows that become entirely empty *after*
                                    step 1 (and after considering only relevant_columns).
                                 If False, returns the raw data (respecting
                                 relevant_columns if provided).
        skip_first_n_lines: The number of data rows to skip *after* the header row.
                           Defaults to 0. Must be non-negative.

    Returns:
        A list of dictionaries representing the processed rows. The number of
        rows returned will be at most `limit_rows`. Returns a list containing
        a single dictionary with an 'error' or 'warning' key in case of issues.

    Raises:
        ValueError: If skip_first_n_lines is negative.
        google.auth.exceptions.DefaultCredentialsError: If ADC are not configured (handled internally now).
        googleapiclient.errors.HttpError: If the Google Sheets API call fails (handled internally now).
    """
    processed_data = []
    if skip_first_n_lines < 0:
        logging.error(f"[V2] Invalid argument: skip_first_n_lines cannot be negative ({skip_first_n_lines}).")
        return [{"error": "skip_first_n_lines cannot be negative."}]

    # Heuristic: Fetch enough rows to cover header, skipped rows, and the desired limit after potential filtering.
    # Fetch header(1) + skipped_rows + limit_rows + buffer(10)
    initial_fetch_limit = skip_first_n_lines + limit_rows + 10
    # Add a reasonable max fetch limit to avoid fetching excessively large sheets unintentionally
    max_fetch = 2000
    rows_to_fetch = min(initial_fetch_limit + 1, max_fetch) # +1 for the header row

    logging.info(f"[V2] Target rows: {limit_rows}. Skip: {skip_first_n_lines}. Initial fetch estimate: {rows_to_fetch-1} data rows.")

    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        logging.info("[V2] Loaded ADC.")
        service = build('sheets', 'v4', credentials=creds)
        logging.info("[V2] Sheets API service built.")

        # Fetch rows_to_fetch rows starting from row 1
        range_name = f"'{tab_name}'!1:{rows_to_fetch}"
        logging.info(f"[V2] Requesting range: {range_name} from sheet ID: {sheet_id}")

        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        if not values:
            logging.warning(f"[V2] No data found in sheet '{sheet_id}', tab '{tab_name}'.")
            return [{"warning": f"No data found in sheet '{sheet_id}', tab '{tab_name}'."}]

        headers = values[0]
        logging.info(f"[V2] Headers found: {headers}")

        # Check if there are enough rows for the header + skipped rows
        if len(values) <= 1 + skip_first_n_lines:
             logging.warning(f"[V2] Not enough data rows ({len(values)-1}) after header to skip {skip_first_n_lines} rows in sheet '{sheet_id}', tab '{tab_name}'.")
             return [{"warning": f"Not enough data rows after header to skip {skip_first_n_lines} in sheet '{sheet_id}', tab '{tab_name}'."}]

        # --- Start Processing ---
        # 1. Select data rows *after* the header
        all_data_rows = values[1:]

        # 2. Skip the specified number of initial data rows
        if skip_first_n_lines > 0:
            logging.info(f"[V2] Skipping first {skip_first_n_lines} data rows.")
            data_rows_to_process = all_data_rows[skip_first_n_lines:]
            logging.info(f"[V2] Processing {len(data_rows_to_process)} rows after skipping.")
        else:
            data_rows_to_process = all_data_rows
            logging.info(f"[V2] Processing {len(data_rows_to_process)} rows (no skipping).")


        # 3. Convert raw rows to list of dictionaries
        intermediate_data = []
        for row in data_rows_to_process:
            # Pad row with None if it's shorter than headers
            padded_row = row + [None] * (len(headers) - len(row))
            # Ensure row isn't longer than headers (shouldn't happen with Sheets API but safe)
            truncated_row = padded_row[:len(headers)]
            intermediate_data.append(dict(zip(headers, truncated_row)))

        # 4. Filter by relevant_columns (if provided)
        if relevant_columns:
            logging.info(f"[V2] Filtering by relevant columns: {relevant_columns}")
            filtered_by_cols_data = []
            relevant_set = set(relevant_columns) # Use set for efficient lookup
            for row_dict in intermediate_data:
                filtered_row = {k: v for k, v in row_dict.items() if k in relevant_set}
                filtered_by_cols_data.append(filtered_row)
            intermediate_data = filtered_by_cols_data
            logging.info(f"[V2] Data after column filtering: {len(intermediate_data)} rows.")
        else:
            logging.info("[V2] No relevant_columns filter applied.")

        # 5. Apply cleanup (if enabled)
        if cleanup_rows_and_columns:
            logging.info("[V2] Applying cleanup (empty values and empty rows)...")
            cleaned_data = []
            for row_dict in intermediate_data:
                # Remove keys with None or "" values
                cleaned_row_dict = {
                    k: v for k, v in row_dict.items() if v is not None and v != ""
                }
                # Only add the row if it's not empty *after* cleaning
                if cleaned_row_dict:
                    cleaned_data.append(cleaned_row_dict)
            intermediate_data = cleaned_data
            logging.info(f"[V2] Data after cleanup: {len(intermediate_data)} non-empty rows.")
        else:
             logging.info("[V2] Skipping cleanup.")

        # 6. Apply final limit_rows
        processed_data = intermediate_data[:limit_rows]
        logging.info(f"[V2] Returning final {len(processed_data)} rows (limit was {limit_rows}).")


    except google.auth.exceptions.DefaultCredentialsError as e:
        logging.error(f"[V2] ADC Error: {e}")
        return [{"error": f"ADC Error: {e}"}]
    except HttpError as err:
        logging.error(f"[V2] Google Sheets API Error: {err.status_code} - {err.error_details}")
        return [{"error": f"Google Sheets API Error: {err.status_code} - {err.error_details}"}]
    except Exception as e:
        logging.error(f"[V2] An unexpected error occurred in get_sheet_content_v2: {e}", exc_info=True)
        return [{"error": f"An unexpected error occurred: {e}"}]

    logging.info(f"[V2] Successfully processed request for sheet '{sheet_id}', tab '{tab_name}'.")
    return processed_data


# --- Agent Definition ---
root_agent = Agent(
    name="Trixie__Google_Sheets_reader_v2", # Renamed slightly
    model="gemini-2.0-flash-exp", # Or your preferred model
    description=(
        """Agent to answer questions about Google Sheets content configured externally.
        Reads sheet metadata (ID, tab, description, columns, context, rows_to_skip) from a configuration source.
        Uses Application Default Credentials (ADC) for read-only access by default.
        Agent Version: 2.0 (External Config + Skip Rows)
        """
    ),
    instruction=(
        """Hi, I'm Trixie! 👋 I can help you explore data in specific Google Sheets.
        My access is configured externally. Use `get_sheets` to see which sheets I know about and get their details (like sheet ID, tab name, description, relevant columns, context, and how many initial data rows I should skip by default).
        When you ask me to fetch data, I'll use the `get_sheet_content_v2` tool. Please provide the `sheet_id` and `tab_name` from the list you get via `get_sheets`.
        I will automatically use the 'relevant_columns' listed for that sheet to keep the output focused, unless you specifically ask for 'all columns'.
        I will also automatically skip the number of initial data rows specified in the configuration (`skip_first_n_lines` from `get_sheets`).
        Use `get_day_today` to get today's date (YYYY-MM-DD) for time-sensitive questions (e.g., past/future events).
        Since data is often shown in markdown, please present tabular information as Markdown Tables.

        My default access is READ-ONLY via ADC. Write operations are currently disabled for safety.
        """
        # Removed the PIN logic as write access isn't implemented/scoped here
    ),
    tools=[
        get_day_today,
        get_sheets,
        get_sheet_content_v2,
        ],
)

# --- Example of how to run (for testing) ---
if __name__ == '__main__':
    logging.info("--- Testing Agent Functions ---")

    # Set the environment variable for testing if not set externally
    if 'JSON_SHEET_FILE' not in os.environ:
        os.environ['JSON_SHEET_FILE'] = DEFAULT_SHEET_CONFIG_FILE # 'riccardo.json' # Make sure this file exists
        logging.info(f"Temporarily set JSON_SHEET_FILE to '{os.environ['JSON_SHEET_FILE']}'")

    # Test get_sheets
    print("\n--- Testing get_sheets() ---")
    sheets_config = get_sheets_old_returning_an_array() # get_sheets()
    print(f"Found {len(sheets_config)} valid sheet configurations:")
    # Print descriptions for verification
    for config in sheets_config:
         print(f"- ID: {config.get('sheet_id')}, Tab: {config.get('tab')}, Desc: {config.get('description')}, Skip: {config.get('skip_first_n_lines')}")


    # Test get_day_today
    print("\n--- Testing get_day_today() ---")
    today = get_day_today()
    print(f"Today's date: {today}")

    # Test get_sheet_content_v2 (if a valid config was found)
    print("\n--- Testing get_sheet_content_v2() ---")
    if sheets_config:
        # Example: Fetch from the first sheet in the config
        test_config = sheets_config[0]
        sheet_id_to_test = test_config.get('sheet_id')
        tab_name_to_test = test_config.get('tab')
        cols_to_test = test_config.get('relevant_columns') # Use relevant columns from config
        skip_lines_test = test_config.get('skip_first_n_lines', 0) # Use skip lines from config

        print(f"Fetching data for Sheet ID: {sheet_id_to_test}, Tab: {tab_name_to_test}, Skip: {skip_lines_test}, Relevant Cols: {cols_to_test}")
        # NOTE: This requires Application Default Credentials to be configured!
        try:
            content = get_sheet_content_v2(
                sheet_id=sheet_id_to_test,
                tab_name=tab_name_to_test,
                limit_rows=5, # Fetch fewer rows for testing
                relevant_columns=cols_to_test,
                skip_first_n_lines=skip_lines_test
            )
            print("Fetched Content (first 5 rows):")
            import pprint
            pprint.pprint(content)
        except Exception as e:
             print(f"Error during get_sheet_content_v2 test: {e}") # Catch any unexpected error during the test call
    else:
        print("Skipping get_sheet_content_v2 test as no valid sheet configurations were loaded.")

    print("\n--- Agent Ready (if ADC are configured) ---")
    # To run the agent itself, you would typically use the ADK framework execution methods, not run the script directly like this.
