
'''SERP API
Serpevedrde is HArry potter, hence ⚡🧙
'''
import os
import logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from serpapi import GoogleSearch

api_key = os.getenv('SERPAPI_COM_API_KEY')


def serpapi_search_flights(src: str, dst: str, outbound_date: str, return_date: str):
    '''
    inputs:
      * src: start airport, IANA id, like 'MUC' or 'JFK'.
      * dst: end airport, IANA id, like 'MUC' or 'JFK'.
      * outbound_date: date of first flight (in YYYY-MM-DD format)
      * return_date: date of return flight (in YYYY-MM-DD format)
    '''
    logging.warning(f"⚡🧙 serp_search_flights from '{src}' to {dst} on '{outbound_date}' -> {return_date}")

    api_key = os.getenv('SERPAPI_COM_API_KEY')

    params = {
      "api_key": api_key,
      "engine": "google_flights",
      "hl": "en",
      #"gl": "us",
      "departure_id": src, # eg "CDG",
      "arrival_id": dst,  # eg "ZRH"
      "outbound_date":  outbound_date, # "2025-05-06",
      "return_date": return_date, # "2025-05-12",
      #"currency": "USD"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)
    return results

def serpapi_search_hotels(query_str: str, check_in_date: str, check_out_date: str, n_adults: int = 2, n_children: int = 0, children_ages: list[int] = [], min_rating: int = 7):
  '''Searches for hotels on certain dates.

      inputs:
      * query_str: sample Google search to convey location and other aspects (eg "Ryokan Tokyo", "hotel Zurich city center", "B&B Dublin countryside", ..)
      * check_in_date: date of check-in at hotel (in YYYY-MM-DD format)
      * check_out_date: date of check out from hotel (in YYYY-MM-DD format)
      * n_adults: number of adults (default: 2)
      * n_children: number of children (default: 0)
      * children_ages: list of ages of children (default: [], example: [5,8,10])
      * min_rating: minimum rating in 0-10 scale. (eg "7" is 7+/10). Default: 7

  More docs: https://serpapi.com/google-hotels-api
  '''
  # TODO: min_price, max_price

  children_ages_str = ','.join(map(str, children_ages))


  params = {
    "api_key": api_key,
    "engine": "google_hotels",
    "q": query_str,
    "hl": "en",
    "gl": "us",
    "check_in_date": check_in_date,
    "check_out_date": check_out_date,
    "adults": n_adults,
    "children": n_children,
    "children_ages": children_ages_str,
    "rating": min_rating,
    #"no_rooms": 1,
    #"currency": "USD"
  }
  search = GoogleSearch(params)
  results = search.get_dict()
  return results



def serpapi_google_search(q: str):
    logging.warning(f"⚡🧙 serp_google_search for q='{q}'")
    return f'{q} is so hot right now'
