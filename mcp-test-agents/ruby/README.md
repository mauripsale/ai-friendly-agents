
Ruby MCP experiments.


1. 🟡 [ruby-sdk](https://github.com/modelcontextprotocol/ruby-sdk).(48 🌟) :yellow: The official gem only supports **STDIO**. the gem is not pushed anywhere, so I took the code and pushed it to
  [model_context_protocol_riccardo](https://rubygems.org/gems/model_context_protocol_riccardo), and apologizing here.
    * 🟡 Please see an example server in `ruby-sdk-example-stdio-server/`
1. 🟡 [mcp-rb](https://github.com/funwarioisii/mcp-rb) (178 🌟). :yellow: Very simple gem, oriented to Sinatra. Only supports **stdio** and ping.
    * 🟡 Please see an example server in `mcp-ruby-hello/`
1. ✅ [fast-mcp](https://github.com/yjacquin/fast-mcp) (619 🌟). Sull of emojis. ✅ Seems to support ALL transports! STDIO, HTTP, and SSE.
    * ✅ Was able to get an SSE server up and running: http://localhost:9292/mcp/sse in `ruby/fast-mcp-hello-server$ bundle exec ruby rack_middleware.rb`
    * ✅ [Nice & *working* integration article](https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399) Ruby/python
1. ? [mcp_on_ruby](https://github.com/nagstler/mcp_on_ruby) (65 🌟). Seems to support  HTTP and STDIO transports.
    * havent tried it yet.
1. https://github.com/maquina-app/rails-mcp-server (integrates with Rails, and Claude Desktop). Havent tried yet


🟡: works but with some limitations (usually only STDIO transport supported).
✅: fully functional
🔴: broken
