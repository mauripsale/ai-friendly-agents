import os
import json
import requests
from datetime import datetime, timedelta

# Basic caching mechanism
CACHE_DIR = ".cache"

def get_cache_path(query_hash):
    return os.path.join(CACHE_DIR, f"{query_hash}.json")

def load_from_cache(query_hash):
    cache_path = get_cache_path(query_hash)
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return None

def save_to_cache(query_hash, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(query_hash)
    with open(cache_path, "w") as f:
        json.dump(data, f)

# --- Test for ilyazub/serpapi-mcp-server ---

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
if not SERPAPI_API_KEY:
    print("Error: SERPAPI_API_KEY environment variable not set.")
    exit(1)

# Assuming the server runs locally on port 8000
SERVER_URL = "http://localhost:8000"

def test_google_flights():
    print("Testing Google Flights...")
    # Example query based on GEMINI.md
    # direct flights for Zurich to Berlin on 9jul25 evening or 10jul morning and come back the same saturday.

    # Constructing a plausible query for Google Flights via SerpApi
    # This is an educated guess based on SerpApi's documentation structure
    query_params = {
        "engine": "google_flights",
        "departure_id": "ZRH",
        "arrival_id": "BER",
        "outbound_date": "2025-07-09", # Evening/Morning implies date is key
        "return_date": "2025-07-12", # Same Saturday
        # SerpApi might need more params like 'travel_class', 'adults', etc.
        # We'll start simple.
    }

    # Simple hash for caching - a more robust solution would hash the dict
    import hashlib
    query_hash = hashlib.md5(json.dumps(query_params, sort_keys=True).encode('utf-8')).hexdigest()

    cached_result = load_from_cache(query_hash)
    if cached_result:
        print("Found cached result.")
        print(json.dumps(cached_result, indent=2))
        return

    try:
        # Assuming the MCP server has a generic /search endpoint
        response = requests.get(f"{SERVER_URL}/search", params=query_params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        save_to_cache(query_hash, data)

        print("Received live result.")
        print(json.dumps(data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error testing Google Flights: {e}")

def test_google_hotels():
    print("Testing Google Hotels...")
    # Placeholder for Google Hotels test
    print("Google Hotels test not yet implemented.")
    pass

if __name__ == "__main__":
    test_google_flights()
    test_google_hotels()
