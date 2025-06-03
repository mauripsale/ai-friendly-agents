
import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters

_allowed_path = os.path.dirname(os.path.abspath(__file__))

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='enterprise_assistant',
    instruction=f"""Help user accessing their file systems, wrapping an existing `server-filesystem` MCP server.

Allowed directory: {_allowed_path}
    """,
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    '-y',  # Arguments for the command
                    '@modelcontextprotocol/server-filesystem',
                    _allowed_path,
                ],
            ),
            # don't want agent to do write operation
            # you can also do below
            # tool_filter=lambda tool, ctx=None: tool.name
            # not in [
            #     'write_file',
            #     'edit_file',
            #     'create_directory',
            #     'move_file',
            # ],
            # tool_filter=[
            #     'read_file',
            #     'read_multiple_files',
            #     'list_directory',
            #     'directory_tree',
            #     'search_files',
            #     'get_file_info',
            #     'list_allowed_directories',
            # ],
        )
    ],
)
