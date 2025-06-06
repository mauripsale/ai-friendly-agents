# config.ru

require 'bundler'
Bundler.require

require_relative 'server'

# Create the MCP middleware
mcp_app = FastMcp.rack_middleware(
  # A basic Rack app that does nothing, as MCP will handle requests
  lambda { |env| [200, { 'Content-Type' => 'text/plain' }, ['']] },
  name: 'serper-travel-agent', version: '1.0.0',
  logger: Logger.new($stdout)
) do |server|
  # Register the tools defined in server.rb
  server.register_tool(FlightTools::SearchOneWay)
  server.register_tool(FlightTools::SearchTwoWays)
  server.register_tool(HotelTools::SearchHotels)

  # TODO: Register any necessary resources here
end

# Run the Rack application with Puma
run mcp_app
