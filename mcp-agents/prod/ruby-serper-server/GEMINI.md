Help me create a simple Ruby MCP server that uses the Serper API to search Google Flights and Google Hotels.

* take implementation details from the working `../ruby-sse-fastmcp-hello-server`. Use `fast_mcp` gem as in there, its the best for the job.
* Create a set of FlightTools in a file `lib/flight_tools.rb`. As in https://mcpmarket.com/server/google-flights , make sure it has a search_one_way (single date) and a search_two_ways (2 dates).
* Create an empty set of HotelTools in a file `lib/flight_tools.rb` (just scaffold the file and import, maybe add a sample function)

## Documentation

* SERP API flights  API is documented here: https://serpapi.com/google-flights-api, a sample flight result is here: https://serpapi.com/google-flights-results
* check a Sample colorful code I've written in the past: under `samples/serp-google-flights-search.rb`
* `.env` contains my SERPAPI_COM_API_KEY.

## testing the app

Please do not the app with `ruby server.rb &` since its difficult to troubleshoot or kill for me.
Also remember to have SERP_API_KEY inside or it wont worj without the ENV wont work.
feel free to use my `justfile` command which conveniently loads the env for me and for you.

## CHANGELOG

Whenever you do changes in the code, make sure to:

1. bump the version accordingly in `VERSION` (semantic versioning), usually by 0.0.1.
2. If its meaningful change, update `CHANGELOG.md` accordingly.

## README

Ensure the readme keeps an update list of tools and a way to invoke the script.

Tools should be grouped by bulletpoints, linked to the file which describes them, and have the list of the function_call. Optional should be italic, mandatory underlined. function name bold.

*   ✈️ [FlightTools](lib/flight_tools.rb)
    *   **SearchOneWay**(`departure_id`, `arrival_id`, `outbound_date`, *`adults`*, *`currency`*, *`hl`*): Search for one-way flights using Serper API.
