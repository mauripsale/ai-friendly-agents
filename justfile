
list:
    just -l


migration-6jun:
    bin/migration-6jun.sh


# Runs the MCP Inspector. Probably slitens on pt 6277 but u care about http://localhost:6274/#resources
mcp-inspector:
    npx @modelcontextprotocol/inspector
