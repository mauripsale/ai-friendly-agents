Help me create a simple Ruby MCP server that uses the Serper API to search Google Flights and Google Hotels.

* take implementation details from the working `../ruby-sse-fastmcp-hello-server`. Use `fast_mcp` gem as in there, its the best for the job.
* Create a set of FlightTools in a file `lib/flight_tools.rb`. As in https://mcpmarket.com/server/google-flights , make sure it has a search_one_way (single date) and a search_two_ways (2 dates).
* Create an empty set of HotelTools in a file `lib/flight_tools.rb` (just scaffold the file and import, maybe add a sample function)

Documentation

* SERP API flights  API is documented here: https://serpapi.com/google-flights-api, a sample flight result is here: https://serpapi.com/google-flights-results
* check a Sample colorful code I've written in the past: under `samples/serp-google-flights-search.rb`
* `.env` contains my SERPAPI_COM_API_KEY.
