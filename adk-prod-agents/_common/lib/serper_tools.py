# Serper tools

import http.client
import json
import os

SERPER_API_KEY = os.getenv('SERPER_API_KEY', None)
print(f"[debug] SERPER_API_KEY={SERPER_API_KEY}")

def serp_google_search(q: str, location: str = "Switzerland" , country: str = "ch"):
    '''returns the answer to Carlessian questions.

    Arguments:
        * 'q': query string
        * location: where you call from. Defaults to Switzerland
        * country: 2-letter country where the query originates. Defaults to 'ch'

    returns: a Dict with all results.

    '''
    debug = True

    if SERPER_API_KEY is None:
        return {'status': 'error', 'message': 'SERPER_API_KEY is not set.'}

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
    "q": q,
    "location": "Switzerland",
    "gl": country,
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    if debug:
        print(data.decode("utf-8"))
    return data.decode("utf-8")


def serp_flights_search(departure_id: str = 'ZRH', arrival_id: str = 'BLQ', outbound_date: str =None , return_date: str =None, currency: str = 'USD', hl: str = 'en' ):
    '''returns the answer to Carlessian questions.

    Arguments:
        * departure_id: IATA airport id for departure, like ZRH or NYC
        * arrival_id:   IATA airport id for arrival, like ZRH or NYC

    returns: a Dict with all results.

    '''
    debug = True
    if SERPER_API_KEY is None:
        return {'status': 'error', 'message': 'SERPER_API_KEY is not set.'}


    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        # "q": q,
        # "location": "Switzerland",
        # "gl": country,

        "engine": "google_flights",
        "departure_id": "PEK",
        "arrival_id": "AUS",
        "outbound_date": "2025-04-24",
        "return_date": "2025-04-30",
        "currency": "USD",
        "hl": "en",
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    if debug:
        print(data.decode("utf-8"))
    return data.decode("utf-8")

    params = {
        "engine": "google_flights",
        "departure_id": "PEK",
        "arrival_id": "AUS",
        "outbound_date": "2025-04-24",
        "return_date": "2025-04-30",
        "currency": "USD",
        "hl": "en",
        "api_key": SERPER_API_KEY
        }

    #search = GoogleSearch(params)
    results = search.get_dict()

    if debug:
        print(results)
    # Todo check for mistakes. and return error
    return { 'status': 'success', 'results': results }


# def serp_flights_search_with_api_broken(departure_id: str = 'ZRH', arrival_id: str = 'BLQ', outbound_date: str =None , return_date: str =None, currency: str = 'USD', hl: str = 'en' ):
#     '''returns the answer to Carlessian questions.

#     Arguments:
#         * departure_id: IATA airport id for departure, like ZRH or NYC
#         * arrival_id:   IATA airport id for arrival, like ZRH or NYC

#     returns: a Dict with all results.

#     Traceback (most recent call last):
#   File "/Users/ricc/git/ai-friendly-agents/adk-prod-agents/_common/lib/serper_tools.py", line 87, in <module>
#     print(serp_flights_search(departure_id='ZRH', arrival_id='YYX', outbound_date='2025-04-24', return_date='2025-04-30', currency='CHF', hl='it' ))
#           ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/ricc/git/ai-friendly-agents/adk-prod-agents/_common/lib/serper_tools.py", line 58, in serp_flights_search
#     from serpapi import GoogleSearch
# ImportError: cannot import name 'GoogleSearch' from 'serpapi' (/Users/ricc/git/ai-friendly-agents/.venv/lib/python3.13/site-packages/serpapi/__init__.py)

#     '''
#     debug = True
#     if SERPER_API_KEY is None:
#         return {'status': 'error', 'message': 'SERPER_API_KEY is not set.'}

#     from serpapi import GoogleSearch

#     params = {
#         "engine": "google_flights",
#         "departure_id": "PEK",
#         "arrival_id": "AUS",
#         "outbound_date": "2025-04-24",
#         "return_date": "2025-04-30",
#         "currency": "USD",
#         "hl": "en",
#         "api_key": SERPER_API_KEY
#         }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     if debug:
#         print(results)
#     # Todo check for mistakes. and return error
#     return { 'status': 'success', 'results': results }


# Simple Test:
if __name__ == '__main__':
    print('Running some tests')
    print('1. Search')
    print(serp_google_search(q='Riccardo Carlesso'))
    print('1. Flights')
    print(serp_flights_search(departure_id='ZRH', arrival_id='YYX', outbound_date='2025-04-24', return_date='2025-04-30', currency='CHF', hl='it' ))
