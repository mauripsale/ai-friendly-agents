
# god bless Gemini for this:

# List tables
python main.py my_test_db.sqlite list-tables

# Show schema for 'users' table
python main.py my_test_db.sqlite show-schema users

# Execute a safe SQL query
python main.py my_test_db.sqlite exec-sql "SELECT name, email FROM users WHERE id = 1"

# Attempt a write query (will fail without --allow-writes)
python main.py my_test_db.sqlite exec-sql "INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')"

# Allow and execute a write query
python main.py my_test_db.sqlite --allow-writes exec-sql "INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')"

# Try the (simulated) natural language query
python main.py my_test_db.sqlite exec-nl "Show me the first few users"
python main.py my_test_db.sqlite exec-nl "count the products"

# test full schema
python main.py my_test_db.sqlite show-full-schema
