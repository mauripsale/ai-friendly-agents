import os
import json
import hashlib
import asyncio
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters

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

from mcp.client.session import ClientSession

async def test_search(client: ClientSession, params: dict):
    """Tests the search tool with given parameters and caching."""
    cache_key = get_cache_key(params)
    cached_response = get_cached_response(cache_key)

    if cached_response:
        print(f"Using cached response for params: {params}")
        print(cached_response)
        return

    print(f"Making request for params: {params}")
    try:
        # Assuming the server exposes a 'search' tool
        response = await client.call_tool("search", arguments=params)
        print("Response:")
        print(response)
        cache_response(cache_key, response)
    except Exception as e:
        print(f"Error during search: {e}")

async def main():
    # Initialize MCP client to connect to the running server
    # The server is expected to be running via stdio
    server_params = StdioServerParameters(command="uv", args=["run", "python", "third-party/serpapi-mcp-server/src/serpapi-mcp-server/server.py"])
    async with stdio_client(server_params) as client:
        # Test Google Flights
        flights_params = {
            "engine": "google_flights",
            "q": "flights from New York to London",
            "date": "2025-12-01", # Example date
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
    asyncio.run(main())
