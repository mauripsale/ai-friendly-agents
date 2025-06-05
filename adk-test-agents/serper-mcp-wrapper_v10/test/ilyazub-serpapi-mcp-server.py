import os
import json
import hashlib
from dotenv import load_dotenv
from mcp.client import Client

# Load environment variables
load_dotenv()

# Define cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(params):
    """Generates a unique cache key based on search parameters."""
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(params_str.encode('utf-8')).hexdigest()

def get_cached_response(cache_key):
    """Retrieves a cached response if it exists."""
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read()
    return None

def cache_response(cache_key, response):
    """Caches a response."""
    cache_file = os.path.join(CACHE_DIR, cache_key)
    with open(cache_file, 'w') as f:
        f.write(response)

async def test_search(client: Client, params: dict):
    """Tests the search tool with given parameters and caching."""
    cache_key = get_cache_key(params)
    cached_response = get_cached_response(cache_key)

    if cached_response:
        print(f"Using cached response for params: {params}")
        print(cached_response)
        return

    print(f"Making request for params: {params}")
    try:
        response = await client.search(**params)
        print("Response:")
        print(response)
        cache_response(cache_key, response)
    except Exception as e:
        print(f"Error during search: {e}")

async def main():
    # Initialize MCP client
    # The path should be relative to where the script is run from, or absolute.
    # Assuming the script is run from the project root.
    client = Client("third-party/serpapi-mcp-server/src/serpapi-mcp-server/server.py")

    # Test Google Flights
    flights_params = {
        "engine": "google_flights",
        "q": "direct flights from Zurich to Berlin",
        "date": "2025-07-09", # evening
        "return_date": "2025-07-12", # Saturday
        "hl": "en",
        "gl": "us"
    }
    await test_search(client, flights_params)

    # Test Google Hotels
    hotels_params = {
        "engine": "google_hotels",
        "q": "hotels in Paris",
        "check_in_date": "2025-12-10", # Example date
        "check_out_date": "2025-12-12", # Example date
        "hl": "en",
        "gl": "us"
    }
    await test_search(client, hotels_params)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
