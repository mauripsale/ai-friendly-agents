
# 1. global improts
from google.adk.agents import Agent
import logging
import dotenv
import os
from typing import List, Dict, Any, Tuple, Optional, Type

# 2. local improts
from .lib.sqlite_agent import * # SQLiteAgent, print_database_schema
from .lib.colors import Color

########################################
# ENV part - with dotenv of course.
dotenv.load_dotenv()

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#DEFAULT_DB_FILE = 'siculo/my_test_db.sqlite'
DEFAULT_DB_FILE = 'siculo/google_events.sqlite'


# ENV -> vars
DB_FILE = os.getenv("DB_FILE", DEFAULT_DB_FILE)
ALLOW_WRITES = os.getenv("ALLOW_WRITES", False)
DEBUG = os.getenv("DEBUG", False)

SingletonAgent = SQLiteAgent(filename=DB_FILE, write_access=ALLOW_WRITES, debug=DEBUG)

# -- Tool part --

def tool_get_database_details():
    '''
        Retrieves enhanced details for all tables, including schema and row counts.

        Returns:
            Dict[str, Any]: A dictionary containing 'db_filename' and 'table_details'.
                            'table_details' is a dict mapping table names to their
                            schema and row count ({'schema': {...}, 'rows': int}).
                            Row count is -1 if it cannot be determined.
    '''
    return SingletonAgent.get_database_details()

def tool_execute_sql(sql_query: str):
    '''Executes a generic SQL query on the DB.'''
    print(f"Executing query.. ```{sql_query}```") # todo color blue
    return SingletonAgent.execute_sql(sql_query)

# def tool_execute_natural_language_query(nl_query: str):
#     '''Executes a natural language query on the DB.'''
#     return SingletonAgent.execute_natural_language_query(nl_query)

def tool_list_tables():
    '''Lists all user-defined tables in the database.'''
    return SingletonAgent.list_tables()

def tool_get_table_schema(table_name: str):
    '''Retrieves the schema (column names and types) for a given table.'''
    return SingletonAgent.get_table_schema(table_name)

def tool_get_full_schema()-> Dict[str, Dict[str, str]]:
    '''Retrieves the schema for all tables in the database.'''
    return SingletonAgent.get_full_schema()

def tool_get_colorful_database_schema_markdown():
    '''Takes the enhanced database details and prints a colorful representation.'''
    database_details = SingletonAgent.get_database_details()
    # TODO wrap with try..
    ret = database_schema_to_colorful_markdown(database_details)
    return {
        "status": "success",
        "result": ret,
    }

    #return { "status": "success", "log": "Database schema printed to console. Sorry Gemini you cant see it but it was beautiful" }
# --- Agent ---


root_agent = Agent(
   name="salvatore_siculo__sql_agent", # Salvatore "SQL" Siculo
   model="gemini-2.0-flash", # might not be enough..
   description="Agent to answer questions on SQL databases. ",
   # Instructions to set the agent's behavior.
   instruction="You are a SQL expert. You'll be able to look at DB structure and answer questions about it."
            "You will use tools to access schema, tables, and rows. You'll be able to execute generic SQL for one given multi-DB file."
            "Currently just supports sqlite3.",
   tools=[
       tool_get_database_details,
       tool_execute_sql,
       tool_list_tables,
       tool_get_table_schema,
       tool_get_full_schema,
       #tool_print_database_schema,
       tool_get_colorful_database_schema_markdown,
       ],
)


# if __name__ == "__main__":
#     print("-- rough testing of agent tool calling --")
#     print(tool_print_database_schema())
