# server.rb

require 'bundler/setup'
Bundler.require

require 'fast_mcp'
require 'rack'
require 'rack/handler/puma'
require 'logger'
require_relative 'lib/flight_tools'
require_relative 'lib/hotel_tools'
require_relative 'lib/meta_tools'

# Create a simple Rack application (can be a basic one as MCP handles requests)
app = lambda do |_env|
  [200, { 'Content-Type' => 'text/plain' }, ['MCP server is running']]
end

# Create the MCP middleware
mcp_app = FastMcp.rack_middleware(
  app,
  name: 'serper-travel-agent', version: '1.0.0',
  logger: Logger.new($stdout)
) do |server|
  # Register the tools defined in lib/
  server.register_tool(FlightTools::SearchOneWay)
  server.register_tool(FlightTools::SearchTwoWays)
  server.register_tool(FlightTools::SearchOneWay)
  server.register_tool(FlightTools::SearchTwoWays)
  server.register_tool(HotelTools::SearchHotels)
  server.register_tool(MetaTools::MetaTool)

  # TODO: Define and register any necessary resources here
end

# Run the Rack application with Puma
puts '🐆 Starting Rack application with MCP middleware on http://localhost:9292'
puts '🐆 MCP endpoints:'
puts '🐆   - http://localhost:9292/mcp/sse (SSE endpoint)'
puts '🐆   - http://localhost:9292/mcp/messages (JSON-RPC endpoint)'
puts '🐆 Press Ctrl+C to stop'

# Use the Puma server directly instead of going through Rack::Handler
require 'puma'
require 'puma/configuration'
require 'puma/launcher'

app = Rack::Builder.new { run mcp_app }
config = Puma::Configuration.new do |user_config|
  user_config.bind 'tcp://localhost:9292'
  user_config.app app
end

launcher = Puma::Launcher.new(config)
launcher.run