## About

Trixie, of course, is a Google Sheet agent. It allows you to see some of your Google Sheets and have a smart prompt on a
per-trix basis (see `etc/` for an inspiration).

It's a bit hard to set up as you need to create a Service Account, download the key, give it as ENV to the script, and
share the Sheets with this SA. However, this set up is pretty easy to test locally... until it works.

## INSTALL (wip)

To use this agent, you need to have:

1. An explicit list of sheets. See a sample one in `etc/`
2. A service account to use to retrieve information.

Some ENV Variables set up ad hoc:

* `GOOGLE_APPLICATION_CREDENTIALS`, eg `trixie/private/trix-populator-key.json`. Bug: this doesnt always work as the agent is called from different directories. Solution: give it an ABSOLUTE path.
* `JSON_SHEET_FILE` (eg =`etc/riccardo.json`). Same bug as above. Sorry. Will fix it some day.
* `ALLOW_WRITE` (default: false). If set to `True`, this will trigger some warnings and allow the agent to also WRITE. Note write is both managed by this ENV (globally) and on a per-sheet base.
  Finally you can just control this by NOT giving EDIT to your service account. So you have THREE levels of security. If you break your sheet, it's totally on *you* :) Also, **SHIYF** - Sheets history is your friend. #comingsoon

Instructions to set up service account:

* Python quickstart: https://developers.google.com/workspace/sheets/api/quickstart/python
* Video on how to create a SA: https://www.youtube.com/watch?v=asrCdWFrF0A&t=1s

Don't forget to give access to your sheet to the SA. Or, you can start with a PUBLIC sheet (eg [Riccardo's countries visited](https://docs.google.com/spreadsheets/d/1e2wW40dnFkWN2KX2q5sIavV0vujPWZgSvEq09qdHqQ8/edit?gid=0#gid=0)).
