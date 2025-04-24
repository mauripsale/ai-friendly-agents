
'''SERP API
Serpevedrde is HArry potter, hence ⚡🧙
'''
import logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def serp_search_flights(src: str, dst: str, date: str):
    '''
    inputs:
      * src: start airport, IANA id, like 'MUC' or 'JFK'.
      * dst: end airport, IANA id, like 'MUC' or 'JFK'.
      * date: date in YYYY-MM-DD format.
    '''
    logging.warning(f"⚡🧙 serp_search_flights from '{src}' to {dst} on '{date}' - TODO implement me")
    return [f"no flights tomorrow from '{src}' to {dst} on '{date}' - TODO implement me"]


def serp_google_search(q: str):
    logging.warning(f"⚡🧙 serp_google_search for q='{q}'")
    return f'{q} is so hot right now'
