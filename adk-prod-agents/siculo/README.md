
I want to create a sqlite3 DB inspector. Then once it works, I want to extend to PG/MY and other DBs as well.

note the agent is still TBD.

## INSTALL

Nothing to do, really :)

1. Generate fake DB to test script: `just create-db`.
2. Run tests: `just test`
3. run main script (a swiss army knife to ask questions to a sqlite DB). `python main.py --help`.
    * Or simply `just run` for instant gratification:

![alt text](image-1.png)

## TODOs

Still missing:

* agent working (yup, Im not neglecting that, but I need a working MVP first).
* SQL magic (get SQL from cli).

