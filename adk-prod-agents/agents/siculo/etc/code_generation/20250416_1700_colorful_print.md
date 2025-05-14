fantastic, it works like a charm! Now 2 things for the print_database_schema.

Lets call it `database_schema_to_colorful_markdown()`

1. Lets create a COPY of it which uses Color instead of an argument  color_lib: Type[Color].
2. returns a big colorful string, rather than printing it. this is good with gemini tool calling.
3. Kudos to you if you're able to return colorful MARKDOWN instead of text.

Here's the code in case you've lost it:

--------------------------------------------

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

