#!/bin/bash


# Example using sqlite3 cli

DBFILE="${1:-my_test_db.sqlite}"

echo Creating DB and setting ...
(
echo "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);"
echo "  INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');"
echo "  INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');"
echo "CREATE TABLE products (sku TEXT PRIMARY KEY, description TEXT, price REAL);"
echo "  INSERT INTO products (sku, description, price) VALUES ('WDG001', 'Magic Widget', 19.99);"
echo "  INSERT INTO products (sku, description, price) VALUES ('RIC042', 'HHTTG Book', 41.99);"
echo .quit
) | sqlite3 "$DBFILE"

echo OK.  "$DBFILE" created.
