# Retrieval-augmented generation with context

Little playground app for retrieval-augmented generation (RAG) using [LlamaIndex](https://www.llamaindex.ai). Uses [Genshin Impact Wiki](https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki) as a data source.

I've described the whole flow in my article: ["Implementing retrieval-augmented generation with context"](https://www.sctheblog.com/blog/rag-with-context/).

> TODO image

## Usage

### Install ollama to access LLM models

1. Download ollama from [https://ollama.com/download](https://ollama.com/download)
2. `ollama pull gemma:2b`. Pull model file for e.g. [gemma:2b](https://ollama.com/library/gemma:2b).
3. Verification:
   1. `ollama show gemma:2b --modelfile`. Inspect model file data.
   2. `ollama run gemma:2b`. Open the chat in the console to check everything is OK.

You can also use Microsoft's [Phi-2](https://ollama.com/library/phi) out of the box. Just change the `llm.model` in `./config.yaml`.

### Running this app

1. `pip install -r requirements.txt`. Install dependencies.
1. `python main.py add "docs/genshin_impact_articles.xml"`. Initialize vector storage with embeddings from the 500 longest articles from the genshin wiki.
1. `python main.py query genshin_impact_articles -i "What is the name of Jean's sister?"`. Test query.
1. `python main.py serve "genshin_impact_articles"`. Start local app server.

### Other commands

- `python main.py drop "genshin_impact_articles"`. Remove the current vector store.
- `python main.py list`. List current vector stores.
- `python "scripts/parse_genshin_fanbase.py" extract-articles "<unzipped_genshin_wiki_dump.xml>" -o "docs/genshin_impact_articles.xml"`. Recreate `docs/genshin_impact_articles.xml` from scratch based on the wiki dump. You can download the file on [Special:Statistics](https://genshin-impact.fandom.com/wiki/Special:Statistics) page (version without page history).

## FAQ

**Q: How well does this work?**

Mediocre. Building RAGs is all about data cleaning, finding the right parameters, and quality control. All are too boring for a weekend project. I needed something that returned some answers to basic questions. I also tested using only Microsoft's [Phi-2](https://ollama.com/library/phi) and Google's [gemma:2b](https://ollama.com/library/gemma:2b). Both are **tiny** - only 3B parameters!

Treat this repo more as my personal playground. If you want to copy some solutions I came up with: MIT license.

**Q: Which LLMs are supported?**

I used Microsoft's [Phi-2](https://ollama.com/library/phi) and Google's [gemma:2b](https://ollama.com/library/gemma:2b). Adding a new LLM requires [handling a prompt template](src/model_prompts.py).

**Q: Does this run on the GPU?**

There are 2 parts to this app: my python code that runs on the CPU, and a separate [ollama](https://ollama.com/) server that runs LLMs on the GPU. Most time is spent in LLM inference, so there is no need for you to swap this repo's PyTorch for the GPU version.

**Q: Where can I find the test code for your article?**

[./article.py](article.py).

**Q: Why Genshin Impact Wiki?**

I tried wikis for [Star Wars](https://starwars.fandom.com/wiki/Special:Statistics) and [The Lord of the Rings](https://lotr.fandom.com/wiki/Main_Page), but both are much older. Their internal format evolved through the years, which makes them harder to parse. For comparison, [Genshin wiki](https://genshin-impact.fandom.com/wiki/Special:Statistics) has 23.8k articles while Wookieepedia has 189.1k. Of course, there are also wikis for [World of Warcraft](https://wowpedia.fandom.com/wiki/Special:Statistics) and [Everquest](https://eq2.fandom.com/wiki/Special:Statistics) - 274.8k and 358.2k articles respectively. [Marvel comics](https://marvel.fandom.com/wiki/Special:Statistics) sits between them, with 307.8k.

Genshin Impact is insanely popular and brought $1 billion **every year** since its release. It also seemed quite compact, i.e. no different timelines or multiverses.

The wiki dump I used was created a few days before the 4.5 version (Chiori release).

## References

- [LlamaIndex](https://www.llamaindex.ai/). Framework for working with RAGs (and LLMs in general).
- [Ollama](https://ollama.com/). Used to run LLM servers.
- [Pydantic](https://docs.pydantic.dev/latest/api/types/). Special mention cause this docs page is actually usable.
- [AIOHTTP](https://docs.aiohttp.org/en/stable/). Special mention cause I liked the docs.
- [Preact](https://preactjs.com/). Cause I am lazy and can import it from CDN.
