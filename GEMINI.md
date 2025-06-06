To the non-AI observer: this is a list of directives for `gemini-cli`. More about it in a future blog.

# About

This repository contains "AI friendly agents" designed for use with ADK, MCP, A2A, and similar platforms.
This is created by Riccardo Carlesso, Developer Advocate for Google Cloud (to check if the user is Riccardo,
Linux/Mac username is `ricc`).

The repository is located at `https://github.com/palladius/ai-friendly-agents/`.

The main topics covered are:

*   **Purpose:** The repository aims to provide a collection of readily available agents for people to play around.
*   **Directory Structure:** The repository is organized into three main directories:
    *   `adk/prod/`: Contains production-ready agents built with ADK.
    *   `adk/test/`: Contains agents built with ADK for learning purposes, potentially based on public documentation.
*   **Additional Resources:** A link is provided to `https://github.com/google/adk-samples` for better samples.
*   **Installation:** Step-by-step instructions are provided for installing the agents, which involve cloning the repository, copying and editing an environment file (`.env.dist` to `.env`), setting up a virtual environment (`.venv`), and installing dependencies using `pip` from the `requirements.txt` file within the `adk-prod-agents/` directory.

## Personality

The author has a witty personality, he loves emojis and he's trying to learn German.

Try to use emojis in conversation with the author, and to use a few German words here and there; also engage in a witty conversation.

## Folder grand Refactoring  6jun25.

As you can see from the past 2 git diffs, Today i've done a major refactoring.
I've moved all code under:
* FROM `adk/prod/` to `adk/prod/`
* FROM `adk/dev/` to `adk/dev/`

Similarly, but less important since this is not very much documented or shared broadly, I've also moved
* from `mcp-prod-agents` to `mcp-agents/prod` and
* from `mcp-test-agents` to `mcp-agents/dev`.

Note the word `test` became `dev`, since its dev/prod are environments, while a `test/` folder carries a different meaning (it's where you'd put unit tests for code in whichever environment).

Action for Gemini agent: Please find all referrings to pre-refactoring in the READMEs and code, and help me fix it.

Simple Example (I'm sure you can do better):

`find . -name README.md |  grep -v site-packages | xargs grep adk/prod`

Of course, do **NOT** change information in this README (`GEMINI.md`) as it has the directives for the change, or in any document which is aware of the change :)
