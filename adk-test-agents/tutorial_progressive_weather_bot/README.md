This tutorial is taken by here:

* Tutorial: https://google.github.io/adk-docs/get-started/tutorial/
* Python notebook: https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/notebooks/adk_tutorial.ipynb
  from [here](https://github.com/google/adk-docs/tree/main/examples/python/notebooks).

## Notes on the code

Since the code is created from a Python notebook, it has a sort of "tridimensionality" to it. Code that works in step 1
needs to be working also in other steps.

I've tried my best to keep:

1. all the common/immutable code in single, testable files.
2. I've tried to keep all "e2e tests" in form of mains which import those lib files.

TODO(ricc): when it works, move all the (1) to `lib/` so all testable endpoints become obvious (in `.`).

In `justfile` I tried to keep a mapping between file invokation and title in python notebook.
