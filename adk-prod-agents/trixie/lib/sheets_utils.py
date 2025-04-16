import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional, Any
import logging # Let's add some logging for good measure! 🪵

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# used by main - todo refactor to all use the same.
def get_sheet_content(
    sheet_id: str,
    tab_name: str,
    limit_rows: int = 10
) -> List[Dict[str, Any]]:
    """Fetches data from a specific tab within a Google Sheet.

    Retrieves rows from the specified Google Sheet tab and returns them as a
    list of dictionaries, using the first row as headers. Authentication relies
    on Application Default Credentials (ADC). Ensure your environment is
    configured correctly (e.g., `gcloud auth application-default login` or
    `GOOGLE_APPLICATION_CREDENTIALS` environment variable set).

    Args:
        sheet_id: The ID of the Google Sheet. You can find this in the Sheet's URL
                  (e.g., '1_SOME_RANDOM_CHARS_AND_NUMBERS_XYZ').
        tab_name: The exact name of the tab (sheet) within the spreadsheet
                  you want to read from (e.g., 'Sheet1', 'My Data Tab'). Case-sensitive!
        limit_rows: The maximum number of *data* rows (excluding the header) to retrieve.
                    Defaults to 10. Fetches `limit_rows + 1` total rows initially.

    Returns:
        A list of dictionaries, where each dictionary represents a row.
        The keys of the dictionaries are taken from the first row (header)
        of the specified tab. Returns an empty list if the tab is empty,
        an error occurs, or no data rows are found after the header.

    Raises:
        google.auth.exceptions.DefaultCredentialsError: If ADC are not configured.
        googleapiclient.errors.HttpError: If the Google Sheets API call fails
                                          (e.g., invalid sheet ID, tab name, permissions).
        ValueError: If the sheet/tab exists but contains no data or only a header row.
    """
    creds = None
    data = [] # Initialize data as an empty list

    try:
        # Attempt to load Application Default Credentials (ADC)
        creds, _ = google.auth.default(scopes=SCOPES)
        logging.info("Successfully loaded Application Default Credentials.")

        # Build the Sheets API service
        service = build('sheets', 'v4', credentials=creds)
        logging.info("Google Sheets API service built successfully.")

        # --- Constructing the range ---
        # We fetch limit_rows + 1 to account for the header row.
        # We don't specify columns, fetching all columns present in the requested rows.
        range_name = f"'{tab_name}'!1:{limit_rows + 1}"
        logging.info(f"Requesting range: {range_name} from sheet ID: {sheet_id}")

        # --- Call the Sheets API ---
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        if not values:
            logging.warning(f"No data found in sheet '{sheet_id}', tab '{tab_name}'. Returning empty list.")
            return [] # Return empty list if the sheet/tab is completely empty

        # --- Process the results ---
        headers = values[0] # First row is assumed to be the header
        logging.info(f"Headers found: {headers}")

        if len(values) <= 1:
             logging.warning(f"Only header row found in sheet '{sheet_id}', tab '{tab_name}'. Returning empty list.")
             return [] # Return empty list if only header exists

        # Take only the requested number of data rows (up to limit_rows)
        data_rows = values[1:limit_rows + 1]

        # Convert rows to list of dictionaries
        for row in data_rows:
            # Ensure row has the same number of elements as headers, pad with None if shorter
            padded_row = row + [None] * (len(headers) - len(row))
            # Truncate row if longer than headers (less common, but possible)
            truncated_row = padded_row[:len(headers)]
            data.append(dict(zip(headers, truncated_row)))

        logging.info(f"Successfully retrieved {len(data)} data rows.")


    except google.auth.exceptions.DefaultCredentialsError as e:
        logging.error(f"ADC Error: Failed to find default credentials. Ensure you're logged in "
                      f"(`gcloud auth application-default login`) or GOOGLE_APPLICATION_CREDENTIALS is set. {e}")
        raise # Re-raise the exception after logging
    except HttpError as err:
        logging.error(f"Google Sheets API Error: {err.status_code} - {err.error_details}")
        # You could add more specific error handling here based on status codes
        if err.status_code == 404:
             logging.error(f" -> Sheet ID '{sheet_id}' or Tab '{tab_name}' might not exist or is inaccessible.")
        elif err.status_code == 403:
             logging.error(f" -> Permission denied. Ensure the identity used by ADC "
                           f"(user or service account) has read access to the sheet.")
        raise # Re-raise the exception after logging
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise # Re-raise the exception

    return data



# # --- Version 2 Function ---

# def get_sheet_content_v2(
#     sheet_id: str,
#     tab_name: str,
#     limit_rows: int = 10,
#     relevant_columns: Optional[List[str]] = None,
#     cleanup_rows_and_columns: bool = True
# ) -> List[Dict[str, Any]]:
#     """[V2] Fetches and optionally cleans data from a Google Sheet tab.

#     Retrieves rows, converts them to dictionaries using the first row as headers,
#     and applies optional filtering/cleaning steps. Authentication relies on ADC.

#     Args:
#         sheet_id: The ID of the Google Sheet.
#         tab_name: The exact name of the tab (sheet).
#         limit_rows: The maximum number of *final* data rows to return after
#                     any filtering. Defaults to 10. Fetches `limit_rows + 1`
#                     initial rows (plus header) to allow filtering.
#         relevant_columns: An optional list of column header names to keep.
#                           If None or empty (default), all columns are considered.
#                           Filtering happens before cleanup.
#         cleanup_rows_and_columns: If True (default), performs cleaning:
#                                  1. Removes key-value pairs where the value is
#                                     None or an empty string ("").
#                                  2. Removes rows that become entirely empty *after*
#                                     step 1 (and after considering only relevant_columns).
#                                  If False, returns the raw data (respecting
#                                  relevant_columns if provided).

#     Returns:
#         A list of dictionaries representing the processed rows. The number of
#         rows returned will be at most `limit_rows`. Returns an empty list
#         if the tab is empty, no data remains after filtering, or an error occurs.

#     Raises:
#         google.auth.exceptions.DefaultCredentialsError: If ADC are not configured.
#         googleapiclient.errors.HttpError: If the Google Sheets API call fails.
#         ValueError: If the sheet/tab exists but contains no data or only a header row.
#     """
#     creds = None
#     processed_data = []
#     # Use a slightly larger fetch limit initially to account for potential empty rows being filtered out later
#     # Fetch enough to potentially fill limit_rows *after* filtering. A simple heuristic: fetch 2x or +10?
#     # Let's fetch limit_rows + 10 initially, plus the header. Max 1000 rows to be safe?
#     initial_fetch_limit = min(limit_rows + 10, 1000) # Fetch a bit more, max 1000 data rows + header
#     logging.info(f"[V2] Target rows: {limit_rows}. Initial fetch estimate: {initial_fetch_limit} data rows.")

#     try:
#         creds, _ = google.auth.default(scopes=SCOPES)
#         logging.info("[V2] Loaded ADC.")
#         service = build('sheets', 'v4', credentials=creds)
#         logging.info("[V2] Sheets API service built.")

#         # Fetch initial_fetch_limit + 1 (for header) rows
#         range_name = f"'{tab_name}'!1:{initial_fetch_limit + 1}"
#         logging.info(f"[V2] Requesting range: {range_name} from sheet ID: {sheet_id}")

#         sheet = service.spreadsheets()
#         result = sheet.values().get(
#             spreadsheetId=sheet_id,
#             range=range_name
#         ).execute()

#         values = result.get('values', [])

#         if not values:
#             logging.warning(f"[V2] No data found in sheet '{sheet_id}', tab '{tab_name}'.")
#             return []

#         headers = values[0]
#         logging.info(f"[V2] Headers found: {headers}")

#         if len(values) <= 1:
#              logging.warning(f"[V2] Only header row found in sheet '{sheet_id}', tab '{tab_name}'.")
#              return []

#         initial_data_rows = values[1:] # All fetched data rows (list of lists)
#         logging.info(f"[V2] Initially fetched {len(initial_data_rows)} data rows.")

#         # --- Start Processing ---
#         intermediate_data = []

#         # 1. Convert raw rows to list of dictionaries
#         for row in initial_data_rows:
#             padded_row = row + [None] * (len(headers) - len(row))
#             truncated_row = padded_row[:len(headers)]
#             intermediate_data.append(dict(zip(headers, truncated_row)))

#         # 2. Filter by relevant_columns (if provided)
#         if relevant_columns:
#             logging.info(f"[V2] Filtering by relevant columns: {relevant_columns}")
#             filtered_by_cols_data = []
#             # Ensure relevant_columns is a set for faster lookup
#             relevant_set = set(relevant_columns)
#             for row_dict in intermediate_data:
#                  # Keep only keys that are in the relevant_set
#                 filtered_row = {k: v for k, v in row_dict.items() if k in relevant_set}
#                 # Keep the row even if it becomes empty at this stage, cleanup handles empty rows later
#                 filtered_by_cols_data.append(filtered_row)
#             intermediate_data = filtered_by_cols_data
#             logging.info(f"[V2] Data after column filtering: {len(intermediate_data)} rows.")
#         else:
#             logging.info("[V2] No relevant_columns filter applied.")


#         # 3. Apply cleanup (if enabled)
#         if cleanup_rows_and_columns:
#             logging.info("[V2] Applying cleanup (empty values and empty rows)...")
#             cleaned_data = []
#             for row_dict in intermediate_data:
#                 # Remove keys with None or "" values
#                 cleaned_row_dict = {
#                     k: v for k, v in row_dict.items() if v is not None and v != ""
#                 }
#                 # Only add the row if it's not empty after cleaning
#                 if cleaned_row_dict:
#                     cleaned_data.append(cleaned_row_dict)
#             intermediate_data = cleaned_data
#             logging.info(f"[V2] Data after cleanup: {len(intermediate_data)} non-empty rows.")
#         else:
#              logging.info("[V2] Skipping cleanup.")

#         # 4. Apply final limit_rows
#         processed_data = intermediate_data[:limit_rows]
#         logging.info(f"[V2] Returning final {len(processed_data)} rows (limit was {limit_rows}).")


#     except google.auth.exceptions.DefaultCredentialsError as e:
#         logging.error(f"[V2] ADC Error: {e}")
#         raise
#     except HttpError as err:
#         logging.error(f"[V2] Google Sheets API Error: {err.status_code} - {err.error_details}")
#         raise
#     except Exception as e:
#         logging.error(f"[V2] An unexpected error occurred: {e}", exc_info=True)
#         raise

#     return processed_data

# # --- End of V2 Function ---
