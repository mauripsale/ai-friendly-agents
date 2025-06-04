#!/bin/bash

# TODO(Max): Max I like this, but maybe we should have some sort of INJECTION mechanism like a README.md in jinja or so where we
# can inject the `just -l` and so. I'd like to be able to b creative about readme without having to edit this script and regenerate
# - das stimmt? Meanwhile I'll change it to README2.md so that it doesn't overwrite the original README.md

cat << 'EOF' > README2.md

## Pre-requisites

Install `uv` and `just` (+ `glow` for the readme CLI integration)

On macos:

```
brew install just uv glow
```

## Running the agents

Just use `just`:

```
EOF

just -l >> README2.md

cat << 'EOF' >> README2.md
```


## Nice to have

- `glow`: useless but nice and colorful. [website](https://github.com/charmbracelet/glow)
- `git-privatize`: from the insane mind of Ricc: [git-privatize](https://github.com/palladius/sakura/blob/master/bin/git-privatize)

EOF
