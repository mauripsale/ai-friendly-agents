Self:

# Demo  Prod Agents

`$ cd adk-prod-agents`

There are many agents here, I'm providing some demo ideas


## Siculo 9/10 (easy)

1. Make sure the DB is built. this is NOT working on remote Cloud Run version.
2. Show from CLI: `adk run siculo/`
3. Ask: `what can you do? tell me the DB filename, and show me the tables`
4. Switch to UI: `ask web --port 8080` or whatever port u want, dflt is 8000.
5. In the UI ask the same, but then ask this:
6. Ask: `Show me all DB schemas. For each DB table, generate a markdown table with column name and type. If it looks like a primary key, make it bold and underlined. If its a foreign key, make it italic.`


## Trixie (hard)

Trixie a bit harder to set up, as you need to set up a Service Account, and then add your trixes to the config json file.

This is the demo vision, not implemented yet.

**Read only scenario**

Imagine this:
* You speak to ADK UI agent, while presenting the spreadsheet
* You ask about some obvious data crunching, like listing names of things.
* Then, in front of audience, you modify 1-2 cells. then you ask same question again.
* Audience observes the different response -> 😮 WOW moment.

**R/W scenatio**

(this is not implemented yet as code doesnt allow writing yet).

1. You speak to ADK UI agent, while presenting the spreadsheet.
2. You ask about some obvious data crunching, like listing names of things.
3. then you ask to ADD a line -> audience should see the line appear. -> double 😮😮 WOW moment.
4. you re-ask the same READ question as before, as in step 2. The answer should be updated with new element which audience CAN SEE.
