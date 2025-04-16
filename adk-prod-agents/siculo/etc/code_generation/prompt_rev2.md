fantastic, now lets extend the script to also have a "database schema", as an array of table schemas iterateing through all the tables. we can leverage the two existing functions to get tables list, and schema per table.

I'd like this to return a data structure (array or dict, your choice).

then I'd like to have another fancy and colorful database schema visualizator which reads this structure and prints it nicely with colors and indentations.


## second part

This is AMAZING!

Now a small nit. as you can see in the User table the Type is aligned too much to the left, so Im afraid the first column needs to take into account also the HEADER legth (eg "Column Name" in this case)

---  DATABASE SCHEMA --- 🏛️
  Table: users
    Column Name  Type
    id     INTEGER
    name   TEXT
    email  TEXT

while you're at it, could you "power" the data structure to have also number of rows per table and filename for DB? Something from:

## current

{'users': {'id': 'INTEGER', 'name': 'TEXT', 'email': 'TEXT'}, 'products': {'sku': 'TEXT', 'description': 'TEXT', 'price': 'REAL'}}

## desired

{
    'db_filename': 'blah.db',
    'tables': [{
        'users': {
            'schema':  {'id': 'INTEGER', 'name': 'TEXT', 'email': 'TEXT'},
            'rows': 42
        },
         'products': {
            'schema': {'sku': 'TEXT', 'description': 'TEXT', 'price': 'REAL'},
            'rows': 10
        }
    }]
}
