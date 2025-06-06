To the non-AI observer: this is a list of directives for `gemini-cli`. More about it in a future blog.

## Folder grand Refactoring  6jun25.

As you can see from the past 2 git diffs, Today i've done a major refactoring.
I've moved all code under:
* FROM `adk/prod/` to `adk/prod/`
* FROM `adk/dev/` to `adk/dev/`

Similarly, but less important since this is not very much documented or shared broadly, I've also moved
* from `mcp-prod-agents` to `mcp-agents/prod` and
* from `mcp-test-agents` to `mcp-agents/dev`.

Note TEST bexame dev, since its an environment and a `test/` folder carries a different meaning.

Action for Gemini agent: Please find all referrings to pre-refactoring in the READMEs and code, and help me fix it.

Simple Example (I'm sure you can do better):

`find . -name README.md |  grep -v site-packages | xargs grep adk/prod`
