Note: this text is to be parsed by Gemini Code Assist and other tools which might arise sometime soon ;)

HorseRagish is a fun "RAG-ish" implementation of ADK with Gemini.

It's a Google ADK (`pip isntall google-adk`) agent which uses Gemini to answer questions about any generic RAG question.
The idea is to put RAG context in a folder (by default under `./etc/data`) and ask questions about it.
Instead of classical RAG retrieval, we use the sueperior Gemini context window to.


## Tasks 1

There are a lot of functions in `common_lib/` . Please check in the methods in all python files in commong_libs/ and
cross-correlate to the calling functions under `horseragish/agent.py`. Now, please find:

1. All functions which are NOT called at all.
2. All functions which ARE called, and create a tree of dependency , eg `main` calls `f1` which calls `f2`.
3. Find a way to make sure this tree is visualized or easily understandable on markdown, eg via mermaid. Also make sure the function name points directly to the file that calls it.
4. Write all of this in some sort of text, plus diagrams, plus bullet points in a new file called "gemini-functions-optimization.md". That file should contain a number of action items for me, like "delete f2() in lib/aaa.py" or "coalesce f1 and f2 into a single function" or "move this function to a differently named file which makes more sense". Use emojis to make my life happier.

We are moving to optimize the codebase and publish it in production so I want the files, the folders, and everything to LOOK GOOD.

