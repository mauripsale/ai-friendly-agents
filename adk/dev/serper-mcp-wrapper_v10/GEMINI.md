I want to create an ADK agent that uses an existing Serper MCP wrapper.

Existing SERP API MCP servers:

* https://github.com/ilyazub/serpapi-mcp-server SERP API.
* Maybe https://github.com/NightTrek/Serper-search-mcp
* https://github.com/marcopesani/mcp-server-serper

Kudos if you can find something more recent or well-maintained, eg under this umbrella: https://github.com/modelcontextprotocol/

## Software development in stages

I would like to do this:

1. Check .env for my SERPER API key: `SERPER_DEV_API_KEY`. Please test
2. Initialize the folder with `uv`. I want to make sure to use google-adk version `1.2.0`. Do whats needed to start this. Put reqs in a `requirements.txt` if possible. Create the `.toml` file!
3. Write a little python script which connects to one of these MCP server and verifies that it ACTUALLY work. Note that I use the free SERP API with 1000 queries per month, so go EASY on queries. Possibly implement some sort of caching mechanism under `.cache/` in case you want to call the same request again. Let's start with
   1.  `test/ilyazub-serpapi-mcp-server.py` and so on until we find one that works.
   2.  Concentrate on my two favorite use cases: **Google Flights** and **Google Hotels**.
4. Once you demonstrate it works, we can then work on integrating it into an ADK agent, called `Serper McPie`. We will put the code in `agent.py` and `__init__.py` as google-adk dictates with a `LlmAgent` construct.  You can take inspiration for ADK 1.1.0 in this repo, under:
   1. https://github.com/google/adk-python/ (official)
   2. https://medium.com/google-cloud/whats-new-in-agent-development-kit-adk-v1-0-0-fe8d79384bbd (what changes in v1.x vs 0.5)
   3. `../../rag` (if u need sth local)
   4. Note this codebase uses a mix of 0.5 and 1.1 and 1.2 just came out.
   5. MCP for ADK is documented here: https://google.github.io/adk-docs/tools/mcp-tools/

A sample, working MCP agent code is in `../../rag/adk_agent_samples/mcp_agent/agent.py`

Remember we're under `git`. I'm  doing everything under `main` but if you need to try something risky, please work in a feature branch.
## Artifacts

* Create/maintain a justfile which contains all the commands to run:
  * list: just -l
  * test-ilyazub: tests the first MCP server with something like SERPAPI_API_KEY=your_api_key_here

## examples

* Check direct flights for Zurich to Berlin on 9jul25 evening or 10jul morning (I need to speak on thu avo at 15:30 in Berlin Messe) and come back the same saturday. Use these dates for your tests :)
