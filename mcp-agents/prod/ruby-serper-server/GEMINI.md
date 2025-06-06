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

## Another bug for oneway ticket


Error: `return_date` is required if `type` is `1` (Round trip)., /usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/serp_api_search.rb:143:in `rescue in get_results'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/serp_api_search.rb:136:in `get_results'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/serp_api_search.rb:50:in `get_json'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/serp_api_search.rb:64:in `get_hash'
/usr/local/google/home/ricc/git/ai-friendly-agents/mcp-agents/prod/ruby-serper-server/lib/flight_tools.rb:34:in `call'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/tool.rb:193:in `call_with_schema_validation!'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/server.rb:326:in `handle_tools_call'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/server.rb:176:in `handle_request'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/transports/rack_transport.rb:548:in `process_json_request_with_server'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/transports/rack_transport.rb:530:in `handle_message_request_with_server'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/transports/rack_transport.rb:228:in `handle_mcp_request'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/fast-mcp-1.5.0/lib/mcp/transports/rack_transport.rb:130:in `call'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/rack-3.1.16/lib/rack/builder.rb:277:in `call'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/configuration.rb:279:in `call'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/request.rb:99:in `block in handle_request'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/thread_pool.rb:390:in `with_force_shutdown'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/request.rb:98:in `handle_request'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/server.rb:472:in `process_client'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/server.rb:254:in `block in run'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/puma-6.6.0/lib/puma/thread_pool.rb:167:in `block in spawn_thread'

i think the issue can be solved like this:

# type (optional):  Parameter defines the type of the flights.
# Available options:
# 1 - Round trip (default)
# 2 - One way
# 3 - Multi-city


