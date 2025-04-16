# main.py (or maybe sqlite_agent_app.py?)
import argparse
import os
from lib.sqlite_agent import SQLiteAgent, print_database_schema
from lib.colors import Color
from typing import Dict, Type, Any # Added Type for type hinting the Color class


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
            #full_schema_data = agent.get_full_schema()
            #print(full_schema_data)
            # Pass the Color class itself to the function
            #print_database_schema(full_schema_data, Color)
            database_details = agent.get_database_details()
            # Pass the new structure and the Color class to the updated print function
            print_database_schema(database_details, Color)

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
