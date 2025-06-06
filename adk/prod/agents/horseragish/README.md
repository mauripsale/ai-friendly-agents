## Pre-requisites

Install `uv` and `just` (+ `glow` for the readme CLI integration)

On Mac OS, you can use Homebrew:

```bash
brew install just uv glow
```

## Running the agents

Use `just`:

```
Available recipes:
    install             # This creates a .venv folder - only used by vscode
    list                # This list here
    readme-show         # [👍] This is another script Maxime will thank me for 😉 -> https://github.com/charmbracelet/glow

    [agents]
    run-horseragish     # Run the agent in the CLI
    run-horseragish-web # [👍] Runs ADK WEB

    [tests]
    test-horseragish    # [👍] Runs the tests for the agents
    test-max-agent      # [💔] simple test for the max agent (broken by an evil French dev)
    test-riccardo-agent # [💔] simple test for the max agent  (broken by an evil French dev)

    [util]
    clean               # 🧹 Cleans up Python bytecode and cache files
    open-github         # [👍] Take me to github page for [emoji horse][emoji garlic]ish
    readme-update       # [👍] Updates the README with the latest `just` output
    show-todos          # [👍] Show Action Items on code

```


## Nice to have

- `glow`: nice and colorful. [website](https://github.com/charmbracelet/glow)
- `git-privatize`: from the insane mind of Ricc: [git-privatize](https://github.com/palladius/sakura/blob/master/bin/git-privatize)
- [just](https://github.com/casey/just)

## Thanks

I'd like to thank Max H for the technical help and the inspiration to create this agent.