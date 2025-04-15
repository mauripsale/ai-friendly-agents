import argparse
import sys
import os
import json # To pretty-print the output dictionary

# Ensure the lib directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))

# Now import the function from the lib module
from sheets_utils import get_sheet_content

# Define command-line arguments
parser = argparse.ArgumentParser(description="Fetch data from a Google Sheet tab.")
parser.add_argument("sheet_id", help="The ID of the Google Sheet.")
parser.add_argument("tab_name", help="The name of the tab within the sheet.")
parser.add_argument("-l", "--limit", type=int, default=10,
                    help="Maximum number of data rows to retrieve (default: 10).")
# We could add --debug later if needed, perhaps to set logging level

if __name__ == "__main__":
    args = parser.parse_args()

    try:
        sheet_data = get_sheet_content(
            sheet_id=args.sheet_id,
            tab_name=args.tab_name,
            limit_rows=args.limit
        )
        # Pretty print the result
        print(json.dumps(sheet_data, indent=2, ensure_ascii=False))

    except Exception as e:
        # Error logging is handled within the function,
        # but we print a final message here for the user.
        print(f"\n❌ An error occurred. Please check the logs above. Error type: {type(e).__name__}", file=sys.stderr)
        sys.exit(1) # Exit with a non-zero status code to indicate failure
