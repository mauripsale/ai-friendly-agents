
* [GREEN EMOJI] just stdio -> works
* [RED EMOJI] `just run-sse` SSE -> doesn't work

SSE should run on port 8931.

## bugs

```bash
just run-sse
bundle exec ruby sse_server.rb
sse_server.rb:97:in `<main>': uninitialized constant ModelContextProtocol::Transports::SseServer (NameError)

transport = MCP::Transports::SseServer.new(server)
                           ^^^^^^^^^^^
Did you mean?  ModelContextProtocol::Server
```
