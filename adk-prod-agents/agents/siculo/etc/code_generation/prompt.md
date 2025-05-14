I'd like to create a gemini agent which is able, given a sqlite3 database to do the following:

* show databases
* given a DB, show tables
* given tables, show schema (column name / type )
* execute generic SQL given a SQL string.
* execute generic SQL given a natural language (probably leveraging the above and pre-fetching the schema).

can you draft for me a class and a number of methods? I presume the constructor will just accept two parameters: filename:str and write_access:bool (dflt: FALSE).

Let's make sure the write_access logic is ensured in the SQL ezecution logic.
