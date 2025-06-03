# Let's add here
# 1.  Enumerate sources() as Ricc did
# 2. BuildDocument(source) - but make sure to return a JSON:
#  { status: "ok", content: "..." } vs
#  { status: "error", message: "..." }
# Should habve some sort of error handling and optimize for 1M context window.

# Notes
# * NO Process documents with question - ERicc did but its wrong
# * local cache: local `.cache/buridone.md` and have a timestamp which expires in 1h.
