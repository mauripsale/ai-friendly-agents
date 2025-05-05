
## Search API - so many options!

There are a number of API out there with a decent free usage to test Google APIs.


* https://serper.dev/
* https://serpapi.com/ # Working now.
*  sth . io

## INSTALL

I've put the code under `_common/` (note: the '_' makes it invisible to adk).
To see the code in common, Gemini suggests to do this way:

```bash
PYTHONPATH="./_common/lib:$PYTHONPATH" adk run serpeverde/
```

You need to explicitly add the `_common/lib/` to the `PYTHONPATH` for the code to find common API code. This will be fixed in a future release.

## Getting a Key

1. Sign up to https://serpapi.com
2. Get an API Key.
3. Add it to your `.env` as `SERPAPI_COM_API_KEY=...`
4. Try running the agent and asking for a flight or hotel.

## serper.dev (not implemented yet)

No python gem needed.
sample python code: https://serper.dev/playground

```python
import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "apple inc"
})
headers = {
  'X-API-KEY': 'YOUR_KEY_HERE',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

## serpapi.com

Gem needed: https://pypi.org/project/serpapi/ (new)
Gem old: https://github.com/serpapi/google-search-results-python
Package: https://pypi.org/project/google-search-results/
sample python code: https://serpapi.com/playground
API Docs: https://serpapi.com/search-api

```python

from serpapi import GoogleSearch

params = {
  "api_key": "YOUR_KEY_HERE", # ENV[SERPAPI_COM_API_KEY]
  "engine": "google_flights",
  "hl": "en",
  "gl": "us",
  "departure_id": "CDG",
  "arrival_id": "AUS",
  "outbound_date": "2025-05-06",
  "return_date": "2025-05-12",
  "currency": "USD"
}

search = GoogleSearch(params)
results = search.get_dict()
```
