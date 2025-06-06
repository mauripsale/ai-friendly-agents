require 'mcp_on_ruby'

client = MCP::Client.new(url: "http://localhost:3000")
client.connect

# List available tools
tools = client.tools.list

# Call a tool
result = client.tools.call("weather.get_forecast",
  { location: "San Francisco" }
)
