Take the app from .crudo.wip and take functionality ONE piece at a time into crudo10/
Let's start with the retrieval of Cloud Run instances.

Note that ADK v1.0 (documented in: [https://github.com/google/adk/tree/main/adk](https://github.com/googlecloudplatform/advisory-digital-kit/tree/main/adk) desn't import files normally.

## fixing dupes

 the code in `crudo10/lib/` has plenty of duplication (under ). can u help me find what we're         │
calling and what not? *Im pretty sure adk-prod-agents/agents/crudo10/lib/ricc_cloud_run_v1.py and
adk-prod-agents/agents/crudo10/lib/ricc_cloud_run_v2.py are nearly identical and my main code is calling only one. Please:
1. tell me what's the difference between the 2 and help me dedupe them
2. lets delete the one we dont use (after having migrated some code which possibly might be useful another time).
3. I'm sure the diff is very small.

## Library errors:

Creating a `constants.py` file wuill yield this error:

## ERROR from constants.py

```bash
$ adk run .
To access latest log: tail -F /tmp/agents_log/agent.latest.log
Traceback (most recent call last):
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/bin/adk", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/click/core.py", line 1697, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/google/adk/cli/cli_tools_click.py", line 233, in cli_run
    asyncio.run(
  File "/usr/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/.venv/lib/python3.11/site-packages/google/adk/cli/cli.py", line 132, in run_cli
    agent_module = importlib.import_module(agent_folder_name)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/adk-prod-agents/agents/crudo10/__init__.py", line 1, in <module>
    from . import agent
  File "/usr/local/google/home/ricc/git/ai-friendly-agents/adk-prod-agents/agents/crudo10/agent.py", line 8, in <module>
    from constants import (
ModuleNotFoundError: No module named 'constants'
```
