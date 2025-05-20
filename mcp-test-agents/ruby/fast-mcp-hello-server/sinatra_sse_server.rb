# require 'fast_mcp'
# require 'sinatra'
# #require './app'

# #run App

# # Create an MCP server
# server = FastMcp::Server.new(
#   name: 'my-ai-server',
#   version: '1.0.0',
# )

# #server.transport = 'sse'

# # Define a tool by inheriting from FastMcp::Tool
# class SummarizeTool < FastMcp::Tool
#   description "Summarize a given text"

#   arguments do
#     required(:text).filled(:string).description("Text to summarize")
#     optional(:max_length).filled(:integer).description("Maximum length of summary")
#   end

#   def call(text:, max_length: 100)
#     # Your summarization logic here
#     text.split('.').first(3).join('.') + '...'
#   end
# end

# # Register the tool with the server
# server.register_tool(SummarizeTool)

# # Create a resource by inheriting from FastMcp::Resource
# class StatisticsResource < FastMcp::Resource
#   uri "data/statistics"
#   resource_name "Usage Statistics"
#   description "Current system statistics"
#   mime_type "application/json"

#   def content
#     JSON.generate({
#       users_online: 120,
#       queries_per_minute: 250,
#       popular_topics: ["Ruby", "AI", "WebDev"]
#     })
#   end
# end

# # Register the resource with the server
# server.register_resource(StatisticsResource)

# # Start the server
# #server.start

# # # Create a simple Rack application
# # https://github.com/yjacquin/fast-mcp/blob/main/examples/rack_middleware.rb
# app_from_docs = lambda do |_env|
#   [200, { 'Content-Type' => 'text/html' },
#    ['<html><body><h1>Hello from Rack!</h1><p>This is a simple Rack app with MCP middleware.</p></body></html>']]
# end


# sample_app = Sinatra.new do
#   get '/' do
#     'Hello, world!'
#   end

#   get '/sse' do
#     content_type 'text/event-stream'
#     stream :keep_open do |out|
#       out << "data: 1. Hello from SSE!\n\n"
#       sleep 1
#       out << "data: 2. Another message from SSE!\n\n"
#     end
#   end
# end

# # These are both broken: :)
# #server.start_rack app: sample_app, port: 4567
# #server.start_rack app: app_from_docs, port: 4567
