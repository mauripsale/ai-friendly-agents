This is Riccardo experimenting with MCP.

Future ideas ([some servers](https://modelcontextprotocol.io/examples#reference-implementations)):

* Try the [GDrive MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive)
* Try the [GMaps server](https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps) (typescript)
* Try the [Sqlite server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) (python). Looks like Anthropic is competing with my Siculo :)

## More resources

* Claude desktop for Linux: https://github.com/aaddrick/claude-desktop-debian
* Inspect MCP: `npx @modelcontextprotocol/inspector`

## About MCP

The default protocol seems to be `STDIO`, which is weird. Never seen something like this.

## Python

The protocol is well documented and well established. Again, all

## Ruby

1. `ruby-sdk`. :yellow: The official gem only supports **STDIO**. the gem is not pushed anywhere, so I took the code and pushed it to
  [model_context_protocol_riccardo](https://rubygems.org/gems/model_context_protocol_riccardo), and apologizing here.
    * Please see an example server in `ruby-sdk-example-stdio-server/`
1. [mcp-rb](https://github.com/funwarioisii/mcp-rb). :yellow: Very simple gem, oriented to Sinatra. Only supports **stdio** and ping.
    * Please see an example server in `mcp-ruby-hello/`
2. [mcp_on_ruby](https://github.com/nagstler/mcp_on_ruby). Seems to support  HTTP and STDIO transports.
    * havent truied it yet.
3. [fast-mcp](https://github.com/yjacquin/fast-mcp). Sull of emojis. ✅ Seems to support ALL transports! STDIO, HTTP, and SSE.
