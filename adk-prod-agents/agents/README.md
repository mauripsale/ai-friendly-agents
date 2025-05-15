
## Agents NG

Refactoring test:

* 🟢 v2.0 Alfred. works but fails one trixie call
* 🟢 v2.0 Claudia. works!

* 🟢 v2.0 Larry
* 🟢 v2.0 Serpeverde
* 🟢 Cobie
* 🟢 Siculo
*
## Branch TMP commands

* `git push origin refactor-agent-structure`

## NG lib/ reboot

Gemini suggests to add these lines to all my agents:

```python

########################################################
# BEGIN Carlessian needed magical lines to import lib/ (God didn't write the world in Python, I tell you that! Perl or Ruby, but not Python).
# See `agents/README.md` for more info.
#
# --- MAGIC PATH FIXING START ---
import os, sys # if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
# --- MAGIC PATH FIXING END ---
########################################################

```

I said it's inelegant and I'd rather have it in the `__init__.py`, but he said that init is not guaranteed to be called.

* If you call explicitly python `path/to/main.py`, it will call also `path/to/__init____.py` if exists, but
* if you call an `agent.py` which in turn imports `path/to/lib/my_func.py` that will NOT import `path/to/lib/__init__.py`.

Seems a very un-debuggable issue, so I'm gonna use this pastie instead.
