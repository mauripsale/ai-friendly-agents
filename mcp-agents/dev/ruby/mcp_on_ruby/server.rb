
# copied from readme

require 'mcp_on_ruby'

server = MCP::Server.new do |s|
  # Define a tool
  s.tool "weather.get_forecast" do |params|
    location = params[:location]
    { forecast: "Sunny", temperature: 72, location: location }
  end
  
  # Add a resource
  s.resource "user.profile" do
    { name: "John", email: "john@example.com" }
  end
end

server.start

