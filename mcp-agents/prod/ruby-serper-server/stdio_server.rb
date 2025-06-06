# stdio_server.rb

require 'bundler/setup'
Bundler.require

require 'fast_mcp'
require 'json'
require_relative 'lib/flight_tools'
require_relative 'lib/hotel_tools'
require_relative 'lib/meta_tools'

# Create a FastMCP server instance for STDIO
server = FastMcp::Server.new(
  name: 'serper-travel-agent-stdio', # Give it a slightly different name
  version: File.read('./VERSION').strip,
  logger: Logger.new($stderr) # Log to stderr for STDIO
)

# Register the tools
server.register_tool(FlightTools::SearchOneWay)
server.register_tool(FlightTools::SearchTwoWays)
server.register_tool(HotelTools::SearchHotels)
server.register_tool(MetaTools::MetaTool)

puts "🐆 Starting STDIO MCP server (serper-travel-agent-stdio v#{server.version})..." # Log to stdout for user info

# Process requests from STDIN
while line = $stdin.gets
  begin
    request = JSON.parse(line)
    response = server.process_request(request)
    $stdout.puts response.to_json
    $stdout.flush # Ensure the response is sent immediately
  rescue JSON::ParserError => e
    $stderr.puts "Error parsing JSON request: #{e.message}"
    # Optionally send a JSON-RPC error response
  rescue => e
    $stderr.puts "Error processing request: #{e.message}"
    $stderr.puts e.backtrace.join("\n")
    # Optionally send a JSON-RPC error response
  end
end

$stderr.puts "🐆 STDIO MCP server stopped."