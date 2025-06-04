Note: this text is to be parsed by Gemini Code Assist and other tools which might arise sometime soon ;)

HorseRagish is a fun "RAG-ish" implementation of ADK with Gemini.

It's a Google ADK (`pip isntall google-adk`) agent which uses Gemini to answer questions about any generic RAG question.
The idea is to put RAG context in a folder (by default under `./etc/data`) and ask questions about it.
Instead of classical RAG retrieval, we use the sueperior Gemini context window to.
