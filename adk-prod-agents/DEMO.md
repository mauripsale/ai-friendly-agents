Self:

# Demo  Prod Agents

`$ cd adk-prod-agents`

There are many agents here, I'm providing some demo ideas


## Siculo 9/10 (easy)

1. Make sure the DB is built. this is NOT working on remote Cloud Run version.
2. Show from CLI: `adk run siculo/`
3. Ask: `what can you do? tell me the DB filename, and show me the tables`
4. Switch to UI: `adk web --port 8080` or whatever port u want, dflt is 8000.
5. In the UI ask the same, but then ask this:
6. Ask: `Show me all DB schemas. For each DB table, generate a markdown table with column name and type. If it looks like a primary key, make it bold and underlined. If its a foreign key, make it italic.`

## Larry 8/10 (easy)

this is a very easy, ZERO-dependency agent, it just needs an API KEY or Vertex.
This is a wrapper around Google Search, so you can ask anything.

1. Ask: `show me weather forecast for mallorca next 7 days, and show me with emoji and day by day in tabular format`.

There's little wow factor. The system just googles.

## Trixie 9/10 (hard)

Trixie a bit harder to set up, as you need to set up a Service Account, and then add your trixes to the config json file.

If you call it from `adk-prod-agents/`, you need to add ENV vars like these:

```bash
# Note the "trixie/" part in these vars.
GOOGLE_APPLICATION_CREDENTIALS="trixie/private/my-service-account-key.json" \
JSON_SHEET_FILE="trixie/etc/sheets_config.json" \
```

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

**Riccardo-only demo**

This works with Riccardo as it needs code/JSON/keys that only the author has. Feel free to take inspiration and use it for your demo.

Use the PUBLIC trixes.

1. Start with CLI to test it works: `just run-trixie `
2. Ask: `What spreadsheets do you know and what are they about?`

Sample answer:
```
[Trixie__Google_Sheets_reader_v2]: OK. I have access to three spreadsheets:

1.  **Riccardo countries visited as of 15 apr 2025 (public)**: This sheet tracks the countries visited by Riccardo, as of April 15, 2025. The sheet ID is `...`, tab name is `Pubblico`. It includes columns like `country`, `name`, `RiccardoC`, and `Note Ric`. It contains 247 rows and I should skip the first 3 lines.
2.  **Some funny translations from English to Italian and beyond**: This sheet contains funny translations from English to Italian and German. The sheet ID is `...`, tab name is `Sheet1`. Relevant columns include `English`, `German`, and `Italian`.
3.  **GDG / DevFest events for 2025, concentrating on Italy ones the most.**: This sheet lists public events co-sponsored by Google and run by Communities, focusing on Italian events for 2025. The sheet ID is `...`, tab name is `DevFests`. Relevant columns include `event_name`, `city`, `country`, `date_start`, `date_end`, `event_year`, `cfp_link`, `website`, `organizers`, `expected_size`, `dow_start`, `dow_end`, and `duration`. It contains ~30 events.
```
3. Ask something about one sheet, like: `ok now list all GDG next events by date showing name, start date, and DOW of the date start`
4. Now ask: `do not show the ones in the past`. This will trigger the `get_day_today()` tool call.
5. Switch to UI: `adk web --port 8080`. Choose Trixie.
6. Ask: `Any devfests in Switzerland?`

Possible answer:
Yes, there is one DevFest in Switzerland listed:
DevFest Zurich in Zurich, Switzerland. However, the listed date for this event is 2018-10-20, so it is not an upcoming event.

7. Ask: `Which day of week was it, and whats the URL?`

