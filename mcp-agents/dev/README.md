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


More on MCP :
* MCP Specs: https://modelcontextprotocol.io/introduction


Testing suite (awesome): `npx @modelcontextprotocol/inspector`

* http://127.0.0.1:6274/#resources

## Working SSE/HTTP servers

See on `../prod/`.

### Python

The protocol is well documented and well established. Again, all samples seem to point to STDIO :(

See under `python/`

### Ruby

See under `ruby/`

