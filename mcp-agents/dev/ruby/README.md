## Ruby gems

* 🔴 `mcp-rb`: don't use.
* 🟡 `mcp` (156): only supports STDIO. But will probably be the most used since it seems to be supported by Anthropic.
* ✅ `fast-mcp` (619). Works!
* ❓ [`rails-mcp-server`](https://github.com/maquina-app/rails-mcp-server) (160): I think this is a gem to MCPify an existing Rails application, like a TODO app.
    * Ricc, attach to Septober or create a new TODO app.
* ❓ [`mcp_on_ruby`](https://github.com/nagstler/mcp_on_ruby)  (70):

## Ruby MCP experiments

Here's a quick overview of the different Ruby MCP implementations found in this repo and elsewhere:

*   🔴 `mcp-rb-hello`: This directory contains an example based on the `mcp-rb` gem. The gem's README indicates it should **NOT** be used and is likely broken or deprecated. Avoid using this one.
*   ✅ `ruby-sdk`: This directory holds a copy of the official Ruby SDK code ([https://github.com/modelcontextprotocol/ruby-sdk](https://github.com/modelcontextprotocol/ruby-sdk)) and gem `mcp`. It seems to be the working SDK.
    *   🟡 The SDK supports **STDIO** and **SSE** transports, demonstrated by the examples in `ruby-sdk-example-stdio-server/`.
    *   🔌 The SSE example server likely runs on port **8931**.
    *   **How to use the examples:**
        *   **STDIO:** `cd ruby-sdk-example-stdio-server/ && bundle exec ruby stdio_server.rb`. Send JSON-RPC 2.0 messages to standard input.
        *   **SSE:** `cd ruby-sdk-example-stdio-server/ && bundle exec ruby sse_server.rb &`. Connect to `http://localhost:8931` (likely).
*   ✅ `fast-mcp` ([https://github.com/yjacquin/fast-mcp](https://github.com/yjacquin/fast-mcp), 619 🌟): This gem seems fully functional and supports **STDIO**, **HTTP**, and **SSE** transports. Full of emojis! ✨
    *   Example SSE server runs on port **9292**: `cd ruby/fast-mcp-hello-server && bundle exec ruby rack_middleware.rb`. Connect to `http://localhost:9292/mcp/sse`.
    *   There's a great and *working* integration article ([https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399](https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399)) covering Ruby/Python integration.
*   ❓ `mcp_on_ruby` ([https://github.com/nagstler/mcp_on_ruby](https://github.com/nagstler/mcp_on_ruby), 65 🌟): Seems to support HTTP and STDIO transports. Haven't tried it yet.
*   ❓ `rails-mcp-server` ([https://github.com/maquina-app/rails-mcp-server](https://github.com/maquina-app/rails-mcp-server)): Integrates with Rails and Claude Desktop. Haven't tried yet.

---

**Emoji Key:**

🔴: Broken/Deprecated
🟡: Works but with some limitations (e.g., transport support)
✅: Fully functional
❓: Status unknown / Haven't tried yet
🔌: Port information
✨: Added because the user likes emojis and fast-mcp is "full of emojis".
