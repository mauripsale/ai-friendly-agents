## Folder content

This folder (as per [this article](https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399) ) contains 3 code files:

```bash
├── justfile                 # a number of sample actions.
├── python_agent_stdio.py    # 1. python stdio-transport MCP Client
└── stdio-serp-mcp.rb        # 1.  ruby stdio-transport MCP Server
└── ...
├── python_agent_http.py     # 2. an SSE-transport MCP Ruby on Rails client in python.
```

1. An STDIO-based client/server (note that the python script hard-calls the ruby script, so I needed to hardcode both the script and the ruby path!). This works beautifully in this folder.
2. An MCP client in python which calls a local Ruby on Rails app with a `CreateUser` and `ListUser` functionality. This needs an external RoR app with some
  devise-ish user creation functionality.

Note the python code uses Gemini via [Pydantic AI agents](https://ai.pydantic.dev/agents/).

## Thanks

This code follows strictly [this article](https://learnitnow.medium.com/bridging-the-gap-connecting-python-ai-agents-to-ruby-apps-with-mcp-614977012399) written by Siva Gollapalli
