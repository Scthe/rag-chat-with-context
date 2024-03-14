from enum import Enum
from yaml import load, Loader
from termcolor import colored
from pydantic import BaseModel, PositiveFloat, PositiveInt, StrictBool


class VectorStorageCfg(BaseModel):
    directory: str = "./db"
    default_vector_store: str
    chunk_size: PositiveInt = 100
    chunk_overlap: PositiveInt = 20


class LlmCfg(BaseModel):
    model: str = "phi"
    temperature: PositiveFloat = 0.2
    request_timeout: PositiveFloat = 30.0
    max_new_tokens: PositiveInt = 256
    context_window: PositiveInt = 3900
    query_instruction: str
    text_instruction: str
    top_k: PositiveInt = 40
    top_p: PositiveFloat = 0.9


class EmbeddingsCfg(BaseModel):
    model: str = "BAAI/bge-small-en-v1.5"


class OllamaCfg(BaseModel):
    api: str = "http://localhost:11434"


class ResponseModeEnum(str, Enum):
    compact = "compact"
    refine = "refine"
    tree_summarize = "tree_summarize"


class QueryModeCfg(BaseModel):
    document_count_k: PositiveInt = 3
    response_mode: ResponseModeEnum = ResponseModeEnum.compact
    structured_answer_filtering: StrictBool = False
    summary_template: str
    text_qa_template: str
    refine_template: str


class QueryModeCfg(BaseModel):
    document_count_k: PositiveInt = 3
    response_mode: ResponseModeEnum = ResponseModeEnum.compact
    structured_answer_filtering: StrictBool = False
    summary_template: str
    text_qa_template: str
    refine_template: str


class ChatModeCfg(BaseModel):
    document_count_k: PositiveInt = 3
    memory: PositiveInt = 2048
    system_template: str
    context_template: str
    condense_template: str


class AppConfig(BaseModel):
    verbose: StrictBool = False
    vector_storage: VectorStorageCfg
    llm: LlmCfg
    embeddings: EmbeddingsCfg
    ollama: OllamaCfg
    query_mode: QueryModeCfg
    chat_mode: ChatModeCfg


def load_app_config(filepath="config.yaml"):
    with open(filepath, "r") as f:
        yaml_content = load(f.read(), Loader=Loader)
    cfg = AppConfig(**yaml_content)

    if cfg.llm.context_window <= cfg.chat_mode.memory:
        print(
            colored(
                f"chat_mode.memory ({cfg.chat_mode.memory}) is greater than llm.context_window({cfg.llm.context_window})!",
                "yellow",
            )
        )
    return cfg
