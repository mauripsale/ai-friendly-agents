# Requirements

Run

```shell
./run.sh  # will install requirements if necessary
```

# Idea
=======
This folder is about 🐴🧄 *HorseRAGish*, a pun on this not being really RAG but achieving THIS through long-context what RAG normally does through Vector DBs and Embeddings.

Fun fact: I've been meaning to do this for months now, but I decided to do it when my buddy Maxime came to me with a real use case and we thought: let's do it!

## Image

**Prompt**: *A cute AI agent in the shape of a horse which is reading a lot of books, on their cover you can read "RAG", "PDF", "markdown". In front of him, some sushi with soy sauce and a huge quantity of wasabi. Wasabi everywhere. In the style of Pixar Cartoon.*

## Idea

The idea is to NOT do RAG, but to achieve RAG counting on Gemini long context window and injecting ALL content into it.

So I envision a few things:

1. Data is organized in folders (`etc/data/..`), each oflder being a corpus (Google financials, Maxime router, Riccardo kids school, ...)
2. The agent has a function call which, given folder name (and maybe some metadata in a yaml.. now that i think about it - see `folders_descriptions` in the etc yaml file).

Execution:
1. given a question, LLM finds the most approprtae data or refuse to do it (think of it of a concierge function).
2. calls the function which transfoms the folder in a big markdown
3. feeds the markdown with the user question.
4. returns to user.

Bonus point if the function has a limit comntext window size, eg 1M, and stops reading at that point. I know there are libraries in `rust` and `go` which DO THIS: take N info/files, prioritize them and fit into the given context window.

* https://github.com/zurawiki/tiktoken-rs
