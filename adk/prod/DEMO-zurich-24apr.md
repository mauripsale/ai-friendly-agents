# Demo  Prod Agents

Since no time, just go with UI.

```bash
cd adk/prod
just web
```

## 1. Larry

1. Ask: `I'm flying to Mallorca tomorrow. Show me weather forecast for mallorca next 7 days, and show me with emoji and day by day in tabular format`.
2. Ask: `where is the GDG Cloud Zurich event of april?`

## 2. Siculo 9/10 (easy)

Zurich🇨🇭

* Any event happening this month?
* Tell me all data around the GDG Cloud Zurich of this month.
* Add a new GDG Cloud Zurich event for next month on the. 20 of may.
* Add the 2 Daniels and Riccardo as registrars.
* any other event in zurich?


## 3. Trixie

Zurich🇨🇭

1. Ask: `What spreadsheets do you know and what are they about?`
2. Ask something about one sheet, like: `ok now list all GDG next events by date showing name, start date, and DOW of the dates`
3. Now ask: `do not show the ones in the past`. This will trigger the `get_day_today()` tool call.
4. Ask: `Any devfests in Switzerland?`
5. Ask: `Which day of week was it, and whats the URL?`
6. Show me current events for October 2025, complete with DoW.
