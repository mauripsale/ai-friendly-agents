
## Current MCP bug (fixed)


```
Error: missing required keys in params:
 - q, /usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/serp_api_search.rb:178:in `check_params'
/usr/local/google/home/ricc/.rbenv/versions/3.2.1/lib/ruby/gems/3.2.0/gems/google_search_results-2.2.0/lib/search/google_search.rb:36:in `initialize'
/usr/local/google/home/ricc/git/ai-friendly-agents/mcp-agents/prod/ruby-serper-server/lib/flight_tools.rb:32:in `new'
/usr/local/google/home/ricc/git/ai-friendly-agents/mcp-agents/prod/ruby-serper-server/lib/flight_tools.rb:32:in `call'
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
```

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

Available options:

1 - Round trip (default)
2 - One way
3 - Multi-city
