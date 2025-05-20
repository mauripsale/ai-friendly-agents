

.. and it works!

## SSE instructions


* Working code: https://github.com/yjacquin/fast-mcp/blob/main/examples/rack_middleware.rb
* MCP service: http://localhost:9292/mcp/sse

```bash
# runs server on port 9292. MCP endpoints:
# 🐆 - http://localhost:9292/mcp/sse (SSE endpoint)
# 🐆 - http://localhost:9292/mcp/messages (JSON-RPC endpoint)
$ bundle exec ruby rack_middleware.rb#

```
