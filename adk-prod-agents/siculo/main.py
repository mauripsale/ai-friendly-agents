# main.py (or maybe sqlite_agent_app.py?)
import argparse
import os
from lib.sqlite_agent import SQLiteAgent
from lib.colors import Color
from typing import Dict, Type, Any # Added Type for type hinting the Color class



def print_database_schema(db_details: Dict[str, Any], color_lib: Type[Color]):
    """Takes the enhanced database details and prints a colorful representation."""
    db_filename = db_details.get('db_filename', 'N/A')
    table_details = db_details.get('table_details', {})

    print(f"\n{color_lib.bold(color_lib.magenta('--- DATABASE DETAILS ---'))} 🏛️")
    print(f"  {color_lib.yellow('File:')} {color_lib.green(db_filename)}")

    if not table_details:
        print(f"  {color_lib.yellow('No tables found or schema could not be retrieved.')}")
        print(f"{color_lib.magenta('------------------------')}\n")
        return

    print(f"{color_lib.magenta('------------------------')}")

    for i, (table_name, details) in enumerate(table_details.items()):
        schema = details.get('schema', {})
        rows = details.get('rows', -1) # Get row count, default to -1 if missing
        row_text = f"{rows} rows" if rows >= 0 else "? rows" # Handle -1 or missing rows

        if i > 0:
            print(f"{color_lib.magenta('------------------------')}") # Separator line

        print(f"  {color_lib.bold(color_lib.blue(f'Table: {table_name}'))} ({color_lib.grey(row_text)})")

        if not schema:
            print(f"    {color_lib.grey('(No columns found or schema error for this table)')}")
            continue

        # --- ALIGNMENT FIX ---
        # Calculate padding, including header lengths
        header_col_name = "Column Name"
        header_type = "Type"
        try:
            max_name_len = max(len(header_col_name), max(len(name) for name in schema.keys()) if schema else 0)
            max_type_len = max(len(header_type), max(len(ctype) for ctype in schema.values()) if schema else 0)
        except ValueError:
             max_name_len = len(header_col_name)
             max_type_len = len(header_type)
        # --- END ALIGNMENT FIX ---

        header_line = f"    {color_lib.underline(f'{header_col_name:<{max_name_len}}  {header_type:<{max_type_len}}')}"
        print(header_line)

        for col_name, col_type in schema.items():
            # Calculate colored type length for alignment (important!)
            colored_type = color_lib.cyan(col_type)
            # Python's ljust/alignment counts visible characters, color codes are non-printing
            # We need the visible length for alignment calculation, but print the colored string.
            # A simple approach: pad the colored string using the calculated max_type_len.
            # Note: This might not be perfect if types themselves contain ANSI codes, but okay for standard types.
            print(f"    {col_name:<{max_name_len}}  {colored_type}") # Let terminal handle alignment of colored text - usually works ok

    print(f"{color_lib.magenta('------------------------')}\n")


# --- Add the Schema Visualizer Function ---
def print_database_schema_DELETEME(schema_data: Dict[str, Dict[str, str]], color_lib: Type[Color]):
    """Takes the full schema data and prints a colorful representation."""
    print(f"\n{color_lib.bold(color_lib.magenta('---  DATABASE SCHEMA ---'))} 🏛️")

    if not schema_data:
        print(f"  {color_lib.yellow('No tables found or schema could not be retrieved.')}")
        print(f"{color_lib.magenta('-------------------------')}\n")
        return

    for i, (table_name, columns) in enumerate(schema_data.items()):
        if i > 0:
            print("") # Add a blank line between tables

        print(f"  {color_lib.bold(color_lib.blue(f'Table: {table_name}'))}")

        if not columns:
            print(f"    {color_lib.grey('(No columns found or schema error for this table)')}")
            continue

        # Calculate padding for alignment within this table
        try:
            # Added check in case columns dict is empty but wasn't caught above
            max_name_len = max(len(name) for name in columns.keys()) if columns else 10
            max_type_len = max(len(ctype) for ctype in columns.values()) if columns else 10
        except ValueError: # Handles potential issues if column names/types are weird
             max_name_len = 10
             max_type_len = 10


        header = f"    {color_lib.underline(f'{'Column Name':<{max_name_len}}  {'Type':<{max_type_len}}')}"
        print(header)

        for col_name, col_type in columns.items():
            print(f"    {col_name:<{max_name_len}}  {color_lib.cyan(col_type):<{max_type_len + len(color_lib.cyan('')) + len(color_lib.END)}}") # Adjust for color codes length

    print(f"{color_lib.magenta('-------------------------')}\n")


def main():
    parser = argparse.ArgumentParser(description="Interact with a SQLite Database using an Agent. 🕵️‍♂️")
    parser.add_argument("db_file", help="Path to the SQLite database file.")
    parser.add_argument("--allow-writes", action="store_true", help="Allow write operations (INSERT, UPDATE, DELETE, etc.). Be careful! 💣")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging. 🐞")

    # --- Commands ---
    subparsers = parser.add_subparsers(dest="command", help="Action to perform")

    # List Tables
    parser_list = subparsers.add_parser("list-tables", help="List all tables in the database. 📜")

    # Show Schema
    parser_schema = subparsers.add_parser("show-schema", help="Show the schema for a specific table. 🧬")
    parser_schema.add_argument("table_name", help="The name of the table.")

    # --- Add New Command for Full Schema ---
    parser_full_schema = subparsers.add_parser("show-full-schema", help="Display the schema for ALL tables. 🏛️")

    # Execute SQL
    parser_sql = subparsers.add_parser("exec-sql", help="Execute a raw SQL query. ⚡️")
    parser_sql.add_argument("sql_query", help="The SQL query string.")

    # Execute Natural Language Query (Placeholder)
    parser_nl = subparsers.add_parser("exec-nl", help="Execute a query described in natural language (via LLM). 🗣️➡️📊")
    parser_nl.add_argument("natural_language_prompt", help="The natural language query.")


    args = parser.parse_args()

    if not os.path.exists(args.db_file):
        print(f"{Color.red('Error:')} Database file not found: {args.db_file} 🤷‍♀️")
        return

    try:
        agent = SQLiteAgent(filename=args.db_file, write_access=args.allow_writes, debug=args.debug)

        if args.command == "list-tables":
            tables = agent.list_tables()
            print(f"{Color.bold('Tables found:')} ({len(tables)})")
            for table in tables:
                print(f"- {table}")

        elif args.command == "show-schema":
            schema = agent.get_table_schema(args.table_name)
            print(f"{Color.bold(f'Schema for table:')} {Color.blue(args.table_name)}")
            if schema:
                # Find max length for alignment
                max_name_len = max(len(name) for name in schema.keys())
                max_type_len = max(len(type) for type in schema.values())
                print(f"  {Color.underline(f'{'Column Name':<{max_name_len}}  {'Type':<{max_type_len}}')}")
                for name, type in schema.items():
                    print(f"  {name:<{max_name_len}}  {type:<{max_type_len}}")
            else:
                print(f"  {Color.yellow('Could not retrieve schema or table is empty/invalid.')}")

  # --- Handle New Command ---
        elif args.command == "show-full-schema":
            full_schema_data = agent.get_full_schema()
            print(full_schema_data)
            # Pass the Color class itself to the function
            print_database_schema(full_schema_data, Color)

        elif args.command == "exec-sql":
            print(f"{Color.yellow('Executing SQL:')} {args.sql_query}")
            results = agent.execute_sql(args.sql_query)
            print(f"{Color.green('--- Results ---')}")
            if isinstance(results, str): # Status message
                print(results)
            elif results:
                 # Basic table print
                headers = results[0].keys()
                print(" | ".join(headers))
                print("-|-".join(['-' * len(h) for h in headers]))
                for row in results:
                    print(" | ".join([str(row[h]) for h in headers]))
            else:
                print("{Color.yellow('Query executed, but returned no results (or it was not a SELECT query).')}")
            print(f"{Color.green('-------------')}")


        elif args.command == "exec-nl":
            print(f"{Color.yellow('Processing Natural Language Query:')} {args.natural_language_prompt}")
            results = agent.execute_natural_language_query(args.natural_language_prompt)
            print(f"{Color.green('--- Results ---')}")
            if isinstance(results, str): # Status message or error
                print(results)
            elif results:
                 # Basic table print (same as above)
                headers = results[0].keys()
                print(" | ".join(headers))
                print("-|-".join(['-' * len(h) for h in headers]))
                for row in results:
                    print(" | ".join([str(row[h]) for h in headers]))
            else:
                 print("{Color.yellow('Query executed, but returned no results.')}")
            print(f"{Color.green('-------------')}")


    except PermissionError as e:
        print(f"{Color.red('Permission Denied:')} {e} 🙅‍♀️")
    except Exception as e:
        print(f"{Color.red('An unexpected error occurred:')} {e} 💥")
        if args.debug:
            import traceback
            traceback.print_exc() # Show stack trace if in debug mode

if __name__ == "__main__":
    #print(Color.blue("Ciao. Qui color funge."))
    main()
