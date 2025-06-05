import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_DEV_API_KEY")

# Ensure API key is present
if not SERPER_API_KEY:
    raise ValueError("SERPER_DEV_API_KEY not found in environment variables. Please set it in the .env file.")

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='Serper McPie',
    instruction='I am an agent that can search for flights and hotels using the Serper API via an MCP server.',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='uv',
                args=[
                    "run",
                    "python",
                    "third-party/serpapi-mcp-server/src/serpapi-mcp-server/server.py",
                ],
                env={
                    "SERPAPI_API_KEY": SERPER_API_KEY # Pass the API key as an environment variable
                }
            ),
            # Optionally filter tools if needed
            # tool_filter=['search']
        )
    ],
)
