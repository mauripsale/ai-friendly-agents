# python_agent_http.py

# From this article: https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
import asyncio


# Riccardo SSE endpoint configured in Rails
    #url='http://localhost:3000/mcp/sse', # Default localhost SSE endpoint configured in Rails
rails_url = 'http://localhost:8080/mcp/sse' # Default localhost SSE endpoint configured in Rails

# Configure the MCP server connection via HTTP/SSE
# Ensure your Rails server is running (e.g., `rails s`)
# If authentication is enabled, provide the token:
# headers = {'Authorization': 'Bearer your-secure-token'}
server = MCPServerHTTP(
    url=rails_url,
    # headers=headers # Uncomment if using authentication
)

# Initialize the Agent
agent = Agent('google-gla:gemini-1.5-flash', mcp_servers=[server]) # Replace with your desired LLM

async def main():
    print(f"Running agent connected to Rails MCP server at {rails_url}...")
    # The context manager ensures proper connection handling for SSE
    async with agent.run_mcp_servers():
        # Ask the agent to use one of the tools defined in Rails
        #result = await agent.run("Get me a list of all users.")
        # Example for creating a user:
        #result = await agent.run("Create a new user named 'Alice2' with email 'alice2@example.com' and password 'very-difficult'.")
        result = await agent.run("Get me a list of all chats.")

    print("***********************")
    print("Agent Output:")
    def str_to_cyan(text):
        return f"\033[96m{text}\033[0m"

    print(str_to_cyan(result.output))
    print("***********************")

if __name__ == "__main__":
    asyncio.run(main())
