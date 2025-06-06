# serp-mcp.rb


require 'fast_mcp'
require 'google_search_results'
require 'dotenv'
# Load environment variables from .env file
require 'dotenv/load'

# require "bundler/inline"
# gemfile do
#   source "https://rubygems.org"
#   gem "fast-mcp"
#   gem 'rack'
#   gem "google_search_results"
# end

SERP_API_KEY = ENV['SERP_API_KEY']
# Check if the SERP_API_KEY is set
if SERP_API_KEY.nil?
  raise "Please set the SERP_API_KEY environment variable."
end

# Create an MCP server
server = FastMcp::Server.new(name: 'my-ai-server', version: '1.0.0')

# Define a tool by inheriting from FastMcp::Tool
class SerpTool < FastMcp::Tool
  # Corrected description
  description "Generates SERP results for a given query"

  arguments do
    required(:query).filled(:string).description("The search query")
  end

  def call(query:)
    # Note: Using ENV var might cause issues at the agent level in some setups.
    # Hardcoding the key for this example, but use secure methods in production.
    # Example: search = GoogleSearch.new(q: query, serp_api_key: 'YOUR_HARDCODED_KEY')
    search = GoogleSearch.new(q: query, serp_api_key: ENV['SERP_API_KEY'])

    search.get_hash
  end
end

# Register the tool with the server
server.register_tool(SerpTool)

# Start the server (will listen via stdio when run by MCPServerStdio)
server.start
