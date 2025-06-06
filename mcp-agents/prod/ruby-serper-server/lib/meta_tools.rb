require 'fast_mcp'
require 'json'

AGENT_VERSION =  File.read('./VERSION').strip rescue Errno::ENOENT


module MetaTools
  class MetaTool < FastMcp::Tool
    description "Returns metadata about the server (v#{AGENT_VERSION})"

    def call
      version = File.read('./VERSION').strip
      {
        name: 'serper-travel-agent',
        description: 'MCP server for Serper API travel searches',
        version: version,
        github_repo: "https://github.com/palladius/ai-friendly-agents/",
        author: "Riccardo Carlesso",
        # Add any other relevant metadata here
      }.to_json
    end
  end
end
