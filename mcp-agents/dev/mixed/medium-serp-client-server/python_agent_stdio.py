from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import asyncio
import os

# Path to your Ruby executable and the script
ruby_executable = '/usr/local/google/home/ricc/.rbenv/shims/ruby' # TODO ~ adjust as needed
#ruby_executable = '/Users/sgollapalli/.rvm/rubies/ruby-3.3.7/bin/ruby' # Adjust as needed
#script_path = '/Users/sgollapalli/work/ruby_agents/serp-mcp.rb' # Adjust as needed
script_path = './stdio-serp-mcp.rb' # Adjust as needed

# Configure the MCP server connection via stdio
server = MCPServerStdio(
    ruby_executable,
    args=[script_path]
)

# Initialize the Agent, providing the MCP server configuration
agent = Agent('google-gla:gemini-1.5-flash', mcp_servers=[server]) # Replace with your desired LLM

async def main(query):
    print(f"Running agent for query: '{query}'...")
    # Run the MCP server process within a context manager
    async with agent.run_mcp_servers():
        result = await agent.run(f"Please get the SERP results for the query: {query}")

    print("***********************")
    print("Agent Output:")
    print(result.output)
    print("***********************")

if __name__ == "__main__":
    query = input("Please enter a search query: ")
    # Ensure SERP_API_KEY is set in your environment where the Ruby script runs
    # export SERP_API_KEY='your_api_key'
    asyncio.run(main(query))
