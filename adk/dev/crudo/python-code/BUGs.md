## P1 b/003


## P1 b/002 Project ids/region config is s***ed up rgiht now.

Before i run anything, I make sure `gcloud config` and `gcloud auth` are set and in sync with .env
Now I create a command to troubleshoot the two: `just env-troubleshoot`


## P3 making up a non-existing service

```
♊ [gemini-1.5-flash]: You have 10 Cloud Run services, Mr SREccardo25! 😲  Here they are in alpha order:

* `gemini-chat-dev`
* `gemini-chat-manhouse-dev`
* `gemini-chat-prod`
* `gemini-news-crawler-dev`
* `gemini-news-crawler-manhouse-dev`
* `gemini-news-crawler-manhouse-prod`
* `gemini-news-crawler-prod`
* `ricc-hotrails-v2-dev`
* `ricc-hotrails-v2-prod`
* `test-service-01`

Is there anything else I can help you with? 🤔
```

## logs are too big.

one log was 700MB (!!) Let's cap a log to max N lines, or M size (say 10MB)?
Maybe we could have a different file per log and split in smaller chunks so Gemini
can ingest one each?

According to an LLM: `6.5MB` is the sweet spot.

* A million (1M) tokens in an LLM, when converted to bytes, would be approximately 6.6 million bytes, based on the average 6.6 bytes per token.
