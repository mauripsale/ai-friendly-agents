



## History

On 3jun25, Riccardo talked to Maxime and we agreed on a new way fwd:
1. only 2 functions
2. use `uv` for pkg management.


I moved everything under `old_stuff/` to make sure wthere's no confict with uv.

## INSTALL

For my friend Max, to develop this, you *kinda* need to install these:

* `just`: nice and kind of useful. [Website](https://github.com/casey/just)
* `uv`: this is the only one you really do need. This needs pip, and i did install with virtualenv because
  pointless circles is what we love. Install with `pip install uv` (or `pip3 install uv`).

Then: `just install` (which will fail but point you to the next clue..)

Nice to have:

* `glow`: useless but nice and colorful. [website](https://github.com/charmbracelet/glow)
* `git-privatize`: from the insane mind of Ricc: [git-privatize](https://github.com/palladius/sakura/blob/master/bin/git-privatize)
