# Demo  Prod Agents

`$ cd adk-prod-agents`

There are many agents here, I'm providing some demo ideas


## Siculo 9/10

1. Make sure the DB is built. this is NOT working on remote Cloud Run version.
2. Show from CLI: `adk run siculo/`
3. Ask: `what can you do? tell me the DB filename, and show me the tables`
4. Switch to UI: `adk web --port 8080` or whatever port u want, dflt is 8000.
5. In the UI ask the same, but then ask this:
6. Ask: `Show me all DB schemas. For each DB table, generate a markdown table with column name and type. If it looks like a primary key, make it bold and underlined. If its a foreign key, make it italic.`
