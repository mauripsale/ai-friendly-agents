
require 'fast_mcp'

# Define tools for AI models to use
server = FastMcp::Server.new(name: 'popular-users', version: '1.0.0')

# Define a tool by inheriting from FastMcp::Tool
class CreateUserTool < FastMcp::Tool
  description "Create a user"
    # These arguments will generate the needed JSON to be presented to the MCP Client
    # And they will be validated at run time.
    # The validation is based off Dry-Schema, with the addition of the description.
  arguments do
    required(:first_name).filled(:string).description("First name of the user")
    optional(:age).filled(:integer).description("Age of the user")
    required(:address).hash do
      optional(:street).filled(:string)
      optional(:city).filled(:string)
      optional(:zipcode).filled(:string)
    end
  end

  def call(first_name:, age: nil, address: {})
    User.create!(first_name:, age:, address:)
  end
end

# Register the tool with the server
server.register_tool(CreateUserTool)

# Share data resources with AI models by inheriting from FastMcp::Resource
class PopularUsers < FastMcp::Resource
  uri "file://popular_users.json"
  resource_name "Popular Users"
  mime_type "application/json"

  def content
    JSON.generate(User.popular.limit(5).as_json)
  end
end

# Register the resource with the server
server.register_resource(PopularUsers)

# Accessing the resource through the server
server.read_resource(PopularUsers.uri)

# Notify the resource content has been updated to clients
server.notify_resource_updated(PopularUsers.uri)
