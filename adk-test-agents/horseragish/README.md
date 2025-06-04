
## Pre-requisites

Install `uv` and `just` (+ `glow` for the readme CLI integration)

On macos:

```
brew install just uv glow
```

## Running the agents

Just use `just`:

```
Available recipes:
    clean               # 🧹 Cleans up Python bytecode and cache files
    list                # This list here
    readme              # [👍] This is another script Maxime will thank me for 😉 -> https://github.com/charmbracelet/glow
    readme-update       # [👍] Updates the README with the latest `just` output
    venv                # This creates a .venv folder - only used by vscode

    [after-meeting]
    github              # [👍] Take me to github
    run-horseragish     # Run the agent in the CLI
    run-horseragish-web # [👍] Runs ADK WEB

    [tests]
    show-todos          # [👍] Show Action Items on code
    test-max-agent      # [👍] simple test for the max agent
    test-riccardo-agent # [👍] simple test for the max agent
```


## Nice to have

- `glow`: useless but nice and colorful. [website](https://github.com/charmbracelet/glow)
- `git-privatize`: from the insane mind of Ricc: [git-privatize](https://github.com/palladius/sakura/blob/master/bin/git-privatize)

