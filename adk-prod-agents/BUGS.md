# Bug on .env and common library
I've played with ADK for the past two weeks and I have a weird feeling I've tried to explain to Polong, and he asked me to put it in a bug.

So here's my sentiment on the othewrwise AWESOME work that's been odne on ADK.

TL;DR I think the folder structure as it is has some issues.

Say I have a code structure like this:

```bash
$ find  . -name \*py -or -name .env
./_common/lib/common_tools.py
./_common/lib/common_code.py
./larry/__init__.py
./larry/agent.py
./.env
./vicky/__init__.py
./vicky/agent.py
./vicky/wiki_fetcher.py
./codie/__init__.py
./codie/agent.py
./claudia/__init__.py
./claudia/.env
./claudia/agent.py
```
Some issues:

1. Where do I put the **common code** for agents 1,2,3? Most likely it should be in some 'common/lib/blah.py' file. But if I'm not mistaken, for a python script to be able to import a ../common/lib file, you need a single package, and a `__init__.py` also in the root folder. Currently I'm replicating code in
my agents but that's pure wrong, and I need guidance on how to fix that.

2. Where do I put my `.env`? Should be it be one for the whole execution, or one per agent?
   I think we should minimize the clutter and have a single .env, but what if both of my agents use DEBUG and I want different values?
   If I use only one, I need a naming convention (`AGENT1_DEBUG` vs `AGENT2_DEBUG`) which easy, but also I need the agent to be able to
   pull a load_env('../.env') and I know python and docker are reluctant to fetch info from upper folders.

3. The current agent listing in the UI (top left in `adk web`) [shows all folders](https://screenshot.googleplex.com/7MYC8UB3Kg7xeJY), again this is WRONG. _common doesn't contain an agent. The algorithm should be smarter.
   I personally believe the best way is to have some sort of blueprint `blueprint.yaml`  (like we do in Google!) or `agent'yaml`
   which contains the info. This is in line with Google blueprints and with [Ruby nanobots](https://github.com/icebaker/ruby-nano-bots).

How to solve this:

I think 1 and 2 can either be solved with pure docs (ie, Ricc is too stupid to figure it out, but some good docs can fix it).
If not, this should be fixed in code :)
3 is absolutely a code bug, but the blueprint is worth a discussion IMHO.

* Provide a golden path on how to solve (1) and (2).
* Fix (3) by either some eurithics (look for both `[__init__.py, agent.py]` - default over configuration), or solve the
  problem at the source with a blueprint file (probably a `agent'yaml` is more idiomatic). My blueprint proposal is in
  go/ricc-personal-agents .

Happy to jump on a call to explain this issue better.
