This contains old `gemini-cli` instructions for docs purposes. Not to be used anymore.

## Folder grand Refactoring  6jun25.

As you can see from the past 2 git diffs, Today i've done a major refactoring.
I've moved all code under:
* FROM `adk/prod/` to `adk/prod/`
* FROM `adk/dev/` to `adk/dev/`

Similarly, but less important since this is not very much documented or shared broadly, I've also moved
* from `mcp-prod-agents` to `mcp-agents/prod` and
* from `mcp-test-agents` to `mcp-agents/dev`.

Note the word `test` became `dev`, since its dev/prod are environments, while a `test/` folder carries a different meaning (it's where you'd put unit tests for code in whichever environment).

Action for Gemini agent:

1. Please find all referrings to pre-refactoring in the READMEs and code, and help me fix it.
2. Only look for *.md, `justfile`, and `*.py` files, and of course ignore installed packages.
3. Do **NOT** use `SearchText` tool for the whole repo, as its overkill and found 19k entries, which are clearly WRONG.

Simple Example (I'm sure you can do better):

`find . -name README.md |  grep -v site-packages | xargs grep adk/prod`

Of course, do **NOT** change information in this README (`GEMINI.md`) as it has the directives for the change, or in any document which is aware of the change :)

As of 09:24 on june 6th, the migration seems concluded.
