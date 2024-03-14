from termcolor import colored
import math

from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.utils import infer_torch_device


def init_llama_config():
    print(colored("Initializing llama_index config...", "blue"))
    Settings.context_window = 3900
    Settings.num_output = 256
    Settings.chunk_size = 200
    Settings.chunk_overlap = 10

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        cache_folder="./embeddings",
        query_instruction="",
        text_instruction="",
    )

    Settings.llm = Ollama(
        base_url="gemma:2b",
        model="gemma:2b",
        temperature=0.1,
        context_window=3900,
        num_ctx=3900,
        request_timeout=120,
        max_new_tokens=256,
        top_k=50,
        top_p=0.7,
    )
    print(colored("llama_index config:", "blue"), Settings)
    print(
        colored("llama_index device:", "blue"),
        infer_torch_device(),
        "(this does not affect Ollama server)",
    )


def tokenizer(text):
    return Settings.embed_model._tokenizer(
        text,
        padding=True,
        max_length=9999,
        truncation=True,
        return_tensors="pt",
    )


def embeddings(text):
    return Settings.embed_model._embed(text)


def print_tokens_and_embeddings(text):
    print(f'text="{text}"')
    t0 = tokenizer(text)
    print(f"tokenizer: (len={t0.input_ids.shape}):", t0.input_ids)
    e0 = embeddings(text)
    print("embeddings", [len(x) for x in e0], e0[0][0:10], "...")


def cosine_distance(a, b):
    dot = lambda v0, v1: sum([x * y for x, y in zip(v0, v1)])
    d_a = math.sqrt(dot(a, a))
    d_b = math.sqrt(dot(b, b))
    return dot(a, b) / (d_a * d_b)


def cmp_embeddings(text_a, text_b, silent=False):
    emb_a = embeddings(text_a)[0]
    emb_b = embeddings(text_b)[0]
    res = cosine_distance(emb_a, emb_b)
    if not silent:
        print(f"cosine_distance({text_a}, {text_b}) = {res}")
    return res


def print_cosine_simil_words():
    cmp_embeddings("hobby", "interests")
    cmp_embeddings("hobby", "clouds")
    cmp_embeddings("heaven", "hell")
    cmp_embeddings("order", "chaos")
    cmp_embeddings("hamster", "etheral")
    cmp_embeddings("hamster", "asdkmalsdmaskldmaklsmkl")
    cmp_embeddings("??!@?#!?@?#", "barbara")


def print_cosine_simil_sentences():
    question = "What are Barbara's hobbies aa?"
    answers = [
        "Barbara's hobbies are playing piano and singing.",
        "Barbara thinks clouds are white.",
        "Barbara likes to run.",
        "Sky is blue.",
    ]

    result = [(x, cmp_embeddings(question, x)) for x in answers]
    result.sort(key=lambda x: x[1], reverse=True)

    for ans, score in result:
        print(ans, score)


def torch_tests():
    import torch

    # 1,4,384
    x = torch.tensor(
        [
            [
                [1, 2, 3, 4, 11, 11, 11],
                [5, 6, 7, 8, 12, 12, 12],
                [9, 10, 11, 12, 13, 13, 13],
            ]
        ]
    )
    print(x.shape)
    y = x[:, 0]  # takes 0th value from each?
    print(y)
    # print(x[0])


def test_sentence_splitter_tok():
    chunk_size = 8
    chunk_overlap = 4
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator="\n",
    )

    text = "aa bb cc dd ee ff ii jj ll mm pp rr ss"
    res = splitter.split_text(text)
    print([(f"{x}", len(tokenizer(x).input_ids[0])) for x in text.split(" ")])
    print("tokenizer", tokenizer(text).input_ids[0])
    print("tokenizer", len(tokenizer(text).input_ids[0]))
    print("splitter", res)


def test_sentence_splitter_text():
    chunk_size = 10
    chunk_overlap = 0
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator="\n",
    )

    text = "aa bb cc dd ee.\nff ii jj ll mm.\npp rr ss"
    res = splitter.split_text(text)
    # print([(f"{x}", len(tokenizer(x).input_ids[0])) for x in text.split(" ")])
    # print("tokenizer", tokenizer(text).input_ids[0])
    # print("tokenizer", len(tokenizer(text).input_ids[0]))
    print("splitter", res)


if __name__ == "__main__":
    init_llama_config()
    embed_model = Settings.embed_model

    # print_tokens_and_embeddings("a")
    # print_tokens_and_embeddings("a b")

    # print_cosine_simil_words()

    # print(embed_model.pooling)

    # torch_tests()

    # print_cosine_simil_sentences()

    # test_sentence_splitter_tok()

    test_sentence_splitter_text()
