# lib/sqlite_agent.py
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
import re
import logging

from .colors import Color # Assuming it's in the same lib folder


# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Potentially use your color lib here too for logging if desired
# from .colors import Color # Assuming it's in the same lib folder

class SQLiteAgent:
    """
    An agent to interact with a SQLite3 database, with controlled write access
    and potential for natural language queries (via LLM).
    """
    _WRITE_OPERATIONS = re.compile(
        r"^\s*(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|REPLACE)\s+",
        re.IGNORECASE
    )

    def __init__(self, filename: str, write_access: bool = False, debug: bool = False):
        """
        Initializes the SQLiteAgent.

        Args:
            filename (str): The path to the SQLite database file.
                            It will be created if it doesn't exist.
            write_access (bool): If True, allows write operations (default: False).
            debug (bool): If True, enable verbose logging.
        """
        if not isinstance(filename, str) or not filename:
            raise ValueError("Database filename must be a non-empty string. 🤔")

        self.db_filename: str = filename
        self.allow_writes: bool = write_access
        self.debug: bool = debug

        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Debugging enabled. Let's get nerdy! 🤓")

        logging.info(f"Agent initialized for database: {self.db_filename}")
        logging.info(f"Write access: {'ENABLED ✅' if self.allow_writes else 'DISABLED ❌'}")

        # Test connection on init to catch immediate issues like permissions
        try:
            with self._connect() as conn:
                logging.debug(f"Successfully connected to {self.db_filename} for initial check.")
                pass # Just check if connection works
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database '{self.db_filename}' on init: {e}")
            raise ConnectionError(f"Could not connect to database: {e}") from e

    def _connect(self) -> sqlite3.Connection:
        """Establishes a connection to the SQLite database."""
        try:
            # isolation_level=None means autocommit mode for writes outside transactions
            # Using a context manager (`with`) handles commit/rollback implicitly for transactions
            conn = sqlite3.connect(self.db_filename, timeout=10) # Add a timeout
            # Return rows as dictionary-like objects
            conn.row_factory = sqlite3.Row
            logging.debug(f"Opened connection to {self.db_filename}")
            return conn
        except sqlite3.Error as e:
            logging.error(f"SQLite connection error to {self.db_filename}: {e}")
            raise

    def _is_write_query(self, sql_query: str) -> bool:
        """Checks if the SQL query performs a write operation."""
        return bool(self._WRITE_OPERATIONS.match(sql_query))

    def list_tables(self) -> List[str]:
        """Lists all user-defined tables in the database."""
        logging.debug("Attempting to list tables.")
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        tables: List[str] = []
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                tables = [row['name'] for row in results]
                logging.info(f"Found {len(tables)} tables: {tables}")
        except sqlite3.Error as e:
            logging.error(f"Error listing tables: {e}")
            # Decide if you want to raise or return empty list
            # raise # Or return []
        return tables

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """
        Retrieves the schema (column names and types) for a given table.

        Args:
            table_name (str): The name of the table.

        Returns:
            Dict[str, str]: A dictionary mapping column names to their data types.
                            Returns empty dict if table not found or error occurs.
        """
        if not isinstance(table_name, str) or not table_name.isidentifier():
             logging.warning(f"Invalid table name provided: {table_name}")
             # Avoid potential SQL injection, even with PRAGMA
             return {}

        logging.debug(f"Attempting to get schema for table: {table_name}")
        query = f"PRAGMA table_info({table_name});" # PRAGMA doesn't support placeholders
        schema: Dict[str, str] = {}
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                if not results:
                     logging.warning(f"Table '{table_name}' not found or has no columns.")
                     return {}
                # Column info: cid, name, type, notnull, dflt_value, pk
                schema = {row['name']: row['type'] for row in results}
                logging.info(f"Schema for '{table_name}': {schema}")
        except sqlite3.Error as e:
            logging.error(f"Error getting schema for table '{table_name}': {e}")
            # raise # Or return {}
        return schema

    def execute_sql(self, sql_query: str, params: Tuple = ()) -> List[Dict[str, Any]] | str:
        """
        Executes a given SQL query string.

        Args:
            sql_query (str): The SQL query to execute.
            params (Tuple): Optional parameters to pass to the query for safety.

        Returns:
            List[Dict[str, Any]] | str: A list of dictionaries for SELECT results,
                                         or a status message string for other operations.

        Raises:
            PermissionError: If a write operation is attempted and write_access is False.
            sqlite3.Error: If there's an issue executing the query.
        """
        logging.debug(f"Attempting to execute SQL: {sql_query[:100]}..." + (" (with params)" if params else ""))

        is_write = self._is_write_query(sql_query)

        if is_write and not self.allow_writes:
            logging.warning(f"Blocked write operation (write access disabled): {sql_query[:100]}...")
            raise PermissionError("Write operations are disabled for this agent instance. ⛔️")

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                logging.debug(f"Executing with params: {params}")
                cursor.execute(sql_query, params)

                if is_write:
                    # No need to explicitly call conn.commit() here,
                    # the 'with' context manager handles it on successful exit.
                    rowcount = cursor.rowcount
                    logging.info(f"Write operation successful. Rows affected: {rowcount}")
                    return f"Write operation successful. Rows affected: {rowcount} 👍"
                else:
                    # Assuming it's a SELECT or similar if not a write
                    results = cursor.fetchall()
                    # Convert sqlite3.Row objects to standard dicts
                    dict_results = [dict(row) for row in results]
                    logging.info(f"Read operation successful. Fetched {len(dict_results)} rows.")
                    logging.debug(f"First few results: {dict_results[:3]}")
                    return dict_results

        except sqlite3.Error as e:
            logging.error(f"Error executing SQL: {sql_query[:100]}... Error: {e}")
            # Re-raise the exception so the caller knows something went wrong
            raise


    def get_full_schema(self) -> Dict[str, Dict[str, str]]:
        """
        Retrieves the schema for all tables in the database.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are table names
                                      and values are dictionaries representing
                                      the schema for that table (column_name -> column_type).
                                      Returns an empty dict if no tables are found or an error occurs.
        """
        logging.info("Attempting to retrieve full database schema.")
        full_schema: Dict[str, Dict[str, str]] = {}
        try:
            table_names = self.list_tables()
            if not table_names:
                logging.warning("No tables found in the database.")
                return {}

            logging.debug(f"Found tables: {table_names}. Fetching schema for each.")
            for table_name in table_names:
                # Reuse the existing method to get schema for each table
                table_schema = self.get_table_schema(table_name)
                # get_table_schema already handles logging for individual tables
                full_schema[table_name] = table_schema

            logging.info(f"Successfully retrieved schema for {len(full_schema)} table(s).")
            return full_schema

        except Exception as e:
            # Catch potential errors during the process, although underlying methods handle most SQLite errors
            logging.error(f"An unexpected error occurred while retrieving the full schema: {e}")
            # Depending on desired behavior, you might return partial schema or empty
            return full_schema # Return whatever was gathered so far, or {}

    def _get_full_schema_description(self) -> str:
        """Helper to generate a schema description string for the LLM.
        """
        schema_parts = []
        try:
            tables = self.list_tables()
            if not tables:
                return "The database contains no tables."

            for table in tables:
                schema = self.get_table_schema(table)
                if schema:
                    columns_str = ", ".join([f"{name} ({type})" for name, type in schema.items()])
                    schema_parts.append(f"Table '{table}': [{columns_str}]")
                else:
                     schema_parts.append(f"Table '{table}': (Could not retrieve schema)") # Should not happen if list_tables worked
            return "\n".join(schema_parts)
        except Exception as e:
            logging.error(f"Failed to get full schema description: {e}")
            return f"Error retrieving schema: {e}" # Provide error info to LLM context potentially


    def execute_natural_language_query(self, nl_query: str) -> List[Dict[str, Any]] | str:
        """
        Takes a natural language query, attempts to convert it to SQL using an LLM
        (placeholder for now), and executes it.

        Args:
            nl_query (str): The natural language query.

        Returns:
            List[Dict[str, Any]] | str: The results from execute_sql or an error message.
        """
        logging.info(f"Received natural language query: {nl_query}")

        # 1. Get Schema
        logging.debug("Fetching full database schema for LLM context.")
        schema_description = self._get_full_schema_description()
        logging.debug(f"Schema description:\n{schema_description}")

        # 2. Construct Prompt for LLM (e.g., Gemini)
        #    This is where the magic (and potential chaos 🤪) happens!
        prompt = f"""
        Given the following SQLite database schema:
        --- Schema Start ---
        {schema_description}
        --- Schema End ---

        And the user's query: "{nl_query}"

        Generate a single, valid SQLite SQL query to answer the user's query based *only* on the provided schema.
        - Respond *only* with the SQL query, nothing else (no explanations, no greetings).
        - Ensure the query syntax is correct for SQLite.
        """
        if not self.allow_writes:
             prompt += "\n- IMPORTANT: The generated query MUST be a read-only query (e.g., SELECT). Do NOT generate INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, or REPLACE statements."
        else:
             prompt += "\n- Write operations (INSERT, UPDATE, DELETE, etc.) are allowed if they directly match the user's request and the schema."


        logging.debug(f"Constructed LLM Prompt:\n{prompt}")

        # 3. --- LLM Interaction Placeholder ---
        #    Replace this section with actual calls to your chosen LLM API (like Gemini)
        logging.warning("LLM interaction is currently simulated! Returning a placeholder query.")
        print(Color.yellow("\n[SIMULATING LLM CALL] - Sending the following prompt to the LLM:")) # Use your color lib
        print(Color.blue(prompt)) # Use your color lib

        # ** SIMULATED RESPONSE **
        # This is where you'd get the actual SQL from the LLM response
        # Handle potential errors from the LLM call itself here
        generated_sql = "SELECT 'Simulated SQL based on:', column_name FROM your_table LIMIT 1;" # Placeholder!
        # A slightly more realistic placeholder based on common requests:
        if "list" in nl_query.lower() or "show" in nl_query.lower():
             tables = self.list_tables()
             if tables:
                 generated_sql = f"SELECT * FROM {tables[0]} LIMIT 5;" # Just guess the first table
             else:
                 generated_sql = "SELECT 'Database has no tables' AS Status;"
        elif "count" in nl_query.lower():
             tables = self.list_tables()
             if tables:
                 generated_sql = f"SELECT COUNT(*) FROM {tables[0]};"
             else:
                 generated_sql = "SELECT 0 AS count;" # Or error message

        print(Color.yellow(f"[SIMULATED LLM RESPONSE] - Received SQL: {generated_sql}\n")) # Use your color lib
        # ** END SIMULATION **

        if not generated_sql or not isinstance(generated_sql, str) or generated_sql.strip() == "":
             logging.error("LLM did not return a valid SQL query string.")
             return "Error: The language model failed to generate a SQL query. 🤖❓"

        generated_sql = generated_sql.strip().rstrip(';') # Clean up potential trailing semicolon

        # 4. Execute the generated SQL (using the existing method for safety checks)
        logging.info(f"Executing SQL generated from NL query: {generated_sql}")
        try:
            # The execute_sql method already handles the write access check
            return self.execute_sql(generated_sql)
        except PermissionError as e:
             logging.error(f"LLM generated a write query, but write access is disabled: {generated_sql}")
             return f"Error: The language model generated a write query ('{generated_sql[:50]}...'), which is not allowed. {e} 🚫"
        except sqlite3.Error as e:
             logging.error(f"Error executing SQL generated by LLM ('{generated_sql[:100]}...'): {e}")
             return f"Error executing the generated SQL: {e}. The generated query might be invalid: '{generated_sql}'"
        except Exception as e:
             logging.error(f"Unexpected error during NL query execution: {e}")
             return f"An unexpected error occurred: {e}"



    def get_database_details(self) -> Dict[str, Any]:
        """
        Retrieves enhanced details for all tables, including schema and row counts.

        Returns:
            Dict[str, Any]: A dictionary containing 'db_filename' and 'table_details'.
                            'table_details' is a dict mapping table names to their
                            schema and row count ({'schema': {...}, 'rows': int}).
                            Row count is -1 if it cannot be determined.
        """
        logging.info("Attempting to retrieve full database details (schema and row counts).")
        db_details: Dict[str, Any] = {
            'db_filename': self.db_filename,
            'table_details': {}
        }
        table_details_dict: Dict[str, Dict[str, Any]] = {}

        try:
            table_names = self.list_tables()
            if not table_names:
                logging.warning("No tables found in the database.")
                db_details['table_details'] = {}
                return db_details

            logging.debug(f"Found tables: {table_names}. Fetching details for each.")
            for table_name in table_names:
                table_schema = self.get_table_schema(table_name)
                row_count = -1 # Default to -1 (unknown)

                # --- Get Row Count ---
                # Basic quoting for table names to handle spaces/keywords, escape quotes within
                # NOTE: This is basic quoting, might not cover all edge cases.
                # More robust parsing/quoting might be needed for complex names.
                quoted_table_name = f'"{table_name.replace("\"", "\"\"")}"'
                count_sql = f"SELECT COUNT(*) FROM {quoted_table_name};"
                try:
                    # Use execute_sql as it handles connection and cursor
                    # We expect a result like [{'COUNT(*)': 42}]
                    count_result = self.execute_sql(count_sql)
                    if isinstance(count_result, list) and count_result:
                         # The key might vary slightly depending on DB/driver nuances,
                         # but 'COUNT(*)' is standard for SQLite's default row factory.
                         # Accessing the first (and only) key of the first row's dict is safer.
                        first_row = count_result[0]
                        if first_row:
                            count_key = list(first_row.keys())[0] # Get the actual key name ('COUNT(*)')
                            row_count = first_row[count_key]
                            logging.debug(f"Row count for {table_name}: {row_count}")
                        else:
                             logging.warning(f"Could not determine row count for table '{table_name}' - empty row returned.")
                    else:
                         logging.warning(f"Could not determine row count for table '{table_name}' - unexpected result from count query: {count_result}")

                except sqlite3.Error as e:
                    logging.error(f"Error counting rows for table '{table_name}': {e}")
                except Exception as e:
                    logging.error(f"Unexpected error counting rows for table '{table_name}': {e}")
                # --- End Row Count ---

                table_details_dict[table_name] = {
                    'schema': table_schema,
                    'rows': row_count
                }

            db_details['table_details'] = table_details_dict
            logging.info(f"Successfully retrieved details for {len(table_details_dict)} table(s).")
            return db_details

        except Exception as e:
            logging.error(f"An unexpected error occurred while retrieving database details: {e}")
            # Return partial results if available
            db_details['table_details'] = table_details_dict
            return db_details
