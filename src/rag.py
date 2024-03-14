from typing import List, Optional
from termcolor import colored

from llama_index.core import (
    VectorStoreIndex,
    Settings,
    get_response_synthesizer,
    PromptTemplate,
    StorageContext,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.utils import truncate_text, infer_torch_device
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.llms import ChatMessage

from src.model_prompts import wrap_in_prompt
from src.utils import Timer
from src.config import AppConfig
from src.my_chat_engine import MyCondensePlusContextChatEngine


def init_verbose_logging(enabled=False):
    import logging
    import sys

    # https://docs.llamaindex.ai/en/stable/module_guides/observability/observability.html
    # https://docs.llamaindex.ai/en/stable/examples/callbacks/LlamaDebugHandler.html
    if enabled:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        return CallbackManager([llama_debug])
    return None


def init_llama_config(cfg: AppConfig):
    print(colored("Initializing llama_index config...", "blue"))
    # https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/settings.py
    Settings.context_window = cfg.llm.context_window
    Settings.num_output = cfg.llm.max_new_tokens
    Settings.chunk_size = cfg.vector_storage.chunk_size
    Settings.chunk_overlap = cfg.vector_storage.chunk_overlap

    # bge-m3 embedding model
    # https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/embeddings/llama-index-embeddings-huggingface/pyproject.toml
    # https://github.com/run-llama/llama_index/blob/0774d393be8116b7063367d613fde2e3bb11d26d/docs/examples/embeddings/huggingface.ipynb#L115
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=cfg.embeddings.model,
        cache_folder="./embeddings",
        query_instruction=cfg.llm.query_instruction,
        text_instruction=cfg.llm.text_instruction,
    )

    # ollama
    # https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/llms/llama-index-llms-ollama/llama_index/llms/ollama/base.py#L29
    # ollama API:
    # https://github.com/ollama/ollama-python/blob/main/ollama/_client.py
    # https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion - extra params
    Settings.llm = Ollama(
        base_url=cfg.ollama.api,
        model=cfg.llm.model,
        temperature=cfg.llm.temperature,
        context_window=cfg.llm.context_window,
        num_ctx=cfg.llm.context_window,
        request_timeout=cfg.llm.request_timeout,
        max_new_tokens=cfg.llm.max_new_tokens,
        top_k=cfg.llm.top_k,
        top_p=cfg.llm.top_p,
        # model_kwargs={"n_gpu_layers": -1, "offload_kqv": True},
        # model_kwargs={"n_gpu_layers": 4, "offload_kqv": True},
    )
    print(colored("llama_index config:", "blue"), Settings)
    print(
        colored("llama_index device:", "blue"),
        infer_torch_device(),
        "(this does not affect Ollama server)",
    )


def create_index_from_documents(cfg, chroma_collection, documents):
    chunk_size = cfg.vector_storage.chunk_size
    chunk_overlap = cfg.vector_storage.chunk_overlap

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # TODO [IGNORE] https://docs.llamaindex.ai/en/stable/module_guides/loading/ingestion_pipeline/root.html#parallel-processing - it's pararel by default
    return VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[
            SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                paragraph_separator="\n",
            )
        ],
        show_progress=True,
    )


def load_existing_index(db, chroma_collection_name):
    if db == None:
        return None

    chroma_collection = db.get_collection(chroma_collection_name)
    existing_docs = chroma_collection.count()
    if existing_docs == 0:
        return None

    # load the existing index
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        # show_progress=True,
        # use_async=True,
    )
    print(colored("RAG index loaded", "blue"))
    return index


def display_prompt_dict(prompts_dict, enabled=False):
    if not enabled:
        return
    for k, p in prompts_dict.items():
        print(colored(f"Prompt Key '{k}':", "yellow"))
        text = "<EMPTY>"
        if p != None:
            text = p if isinstance(p, str) else p.get_template()
        print(text)


def create_query_engine(
    cfg: AppConfig,
    index: VectorStoreIndex,
    callback_manager: Optional[CallbackManager] = None,
):
    query_mode_cfg = cfg.query_mode
    print(colored("Initializing query engine..", "blue"))
    # @see https://docs.llamaindex.ai/en/stable/module_guides/querying/retriever/retrievers.html
    # @see https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion
    # @see https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=query_mode_cfg.document_count_k,  # how many to retrieve
        verbose=cfg.verbose,
        callback_manager=callback_manager,
    )

    create_tmpl = lambda text: PromptTemplate(wrap_in_prompt(Settings.llm.model, text))

    # configure response synthesizer
    # https://docs.llamaindex.ai/en/stable/module_guides/querying/response_synthesizers/root.html
    response_synthesizer = get_response_synthesizer(
        verbose=cfg.verbose,
        response_mode=query_mode_cfg.response_mode,
        structured_answer_filtering=query_mode_cfg.structured_answer_filtering,
        summary_template=create_tmpl(query_mode_cfg.summary_template),
        text_qa_template=create_tmpl(query_mode_cfg.text_qa_template),
        refine_template=create_tmpl(query_mode_cfg.refine_template),
        use_async=False,
        streaming=False,
        callback_manager=callback_manager,
    )

    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        callback_manager=callback_manager,
    )
    display_prompt_dict(query_engine.get_prompts(), enabled=cfg.verbose)
    return query_engine


def create_chat_engine(
    cfg: AppConfig,
    index: VectorStoreIndex,
    callback_manager: Optional[CallbackManager] = None,
):
    from llama_index.core.memory import ChatMemoryBuffer

    chat_mode_cfg = cfg.chat_mode
    print(colored("Initializing chat engine..", "blue"))

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=chat_mode_cfg.document_count_k,  # how many to retrieve
        verbose=cfg.verbose,
        callback_manager=callback_manager,
    )

    memory = ChatMemoryBuffer.from_defaults(token_limit=chat_mode_cfg.memory)

    # https://docs.llamaindex.ai/en/stable/examples/chat_engine/chat_engine_condense_plus_context.html
    chat_engine = MyCondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        verbose=cfg.verbose,
        memory=memory,
        # https://docs.llamaindex.ai/en/stable/examples/customization/prompts/chat_prompts.html
        system_prompt=chat_mode_cfg.system_template,
        context_prompt=chat_mode_cfg.context_template,
        condense_prompt=chat_mode_cfg.condense_template,
        # skip_condense=True,
    )

    prompts_dict = {
        "system_template": chat_engine._system_prompt,
        "context_template": chat_engine._context_prompt_template,
        "condense_template": chat_engine._condense_prompt_template,
    }
    display_prompt_dict(prompts_dict, enabled=cfg.verbose)
    return chat_engine


def parse_source(source, max_text_len=200):
    filename = source.node.metadata.get("filename", "<Unknown source>")
    text_chunk = source.node.get_content()

    tokenizer = Settings.embed_model._tokenizer
    tokens = tokenizer(
        [text_chunk],
        padding=True,
        truncation=True,
        return_tensors="pt",
    )
    token_counts = [list(x.shape)[0] for x in tokens["input_ids"]]
    token_count = sum(token_counts)

    if max_text_len > 0:
        text_chunk = truncate_text(text_chunk, max_text_len)
    text_chunk = text_chunk.replace("\n", "    ")

    return {
        "filename": filename,
        "url": f"https://genshin-impact.fandom.com/wiki/{filename}",
        "score": source.score,
        "content": text_chunk,
        "token_count": token_count,
    }


def ask_question_sync(query_engine: RetrieverQueryEngine, question: str):
    """https://github.com/run-llama/llama_index/blob/9d9e10bd4c2ad4f4cacfc6dab5ff20cc31c515e4/llama-index-core/llama_index/core/base/response/schema.py#L43"""
    with Timer() as timer:
        print(colored("Asking question:", "blue"), f"'{question}'")
        resp = query_engine.query(question)
        print(colored(f"Answer:", "green"), str(resp).rstrip())

    # array of:
    # https://github.com/run-llama/llama_index/blob/9d9e10bd4c2ad4f4cacfc6dab5ff20cc31c515e4/llama-index-core/llama_index/core/schema.py#L569
    print(colored("Sources:", "yellow"))
    for source in resp.source_nodes:
        s = parse_source(source)
        score, content, url = (
            s["score"],
            s["content"],
            s["url"],
        )
        print(colored(f"[{score :4.3f}] '{url}':", "blue"), content)

    print(colored(f"Elapsed {timer.delta :4.2f}s", "green"))


async def ask_question_in_chat_async(
    query_engine: CondensePlusContextChatEngine,
    question: str,
    message_history: List[ChatMessage],
    on_complete,
):
    """https://github.com/run-llama/llama_index/blob/9d9e10bd4c2ad4f4cacfc6dab5ff20cc31c515e4/llama-index-core/llama_index/core/base/response/schema.py#L85"""

    print(colored("[STREAMING] Asking question:", "blue"), f"'{question}'")

    with Timer() as timer:
        resp, inferred_question = await query_engine.astream_chat(
            question, message_history
        )

        async for token in resp.async_response_gen():
            # print(token, end="", flush=True)
            # print(datetime.utcnow(), token)
            # raise Exception("Mock error") # just for tests
            yield token
    print(colored(f"Elapsed {timer.delta :4.2f}s", "green"))

    sources = [parse_source(x, max_text_len=-1) for x in resp.source_nodes]
    await on_complete(timer.delta, sources, inferred_question)
