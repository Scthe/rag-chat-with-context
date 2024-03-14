import os
import sys
import click
import chromadb
from termcolor import colored
from llama_index.core.schema import Document
from datetime import datetime
from timeit import default_timer as timer

from src.socket_msg_handler import SocketMsgHandler
from src.utils import openFanbaseXml
from src.config import load_app_config
from src.server import create_server, set_socket_msg_handler, start_server
from src.rag import (
    create_index_from_documents,
    create_query_engine,
    init_llama_config,
    init_verbose_logging,
    load_existing_index,
    ask_question_sync,
)

STATIC_DIR = "./static"


def read_genshin_data(filepath):
    documents = []
    with openFanbaseXml(filepath) as xml_soup:
        for page in xml_soup.find_all("page"):
            title = page.title.get_text()
            text = page.find("text").text
            # print(title, "||", len(text))
            documents.append(
                Document(
                    text=text,
                    metadata={"filename": title},
                )
            )
    return documents


def strinfigy_chroma_collection(col, for_list=False):
    cnt = col.count()
    s = f"name='{colored(col.name,'blue')}' documents='{cnt}' id='{col.id}'"
    if for_list:
        s = "\t* " + s
    return s


def find_collections(db, name):
    return [x for x in db.list_collections() if x.name == name or x.id == name]


def get_collection_name_from_filepath(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]


def create_chroma_client(cfg):
    from chromadb.config import Settings

    db_dir = cfg.vector_storage.directory
    print(colored("Vector store path:", "blue"), f"'{db_dir}'")
    return chromadb.PersistentClient(
        path=db_dir, settings=Settings(anonymized_telemetry=False)
    )


def exit_invalid_store(cfg, name):
    db_dir = cfg.vector_storage.directory
    print(
        colored("No vector store found:", "blue"),
        f"directory='{db_dir}', vector_store='{name}'",
    )
    sys.exit(1)


@click.command()
def list():
    """List all vector stores"""
    cfg = load_app_config()
    db = create_chroma_client(cfg)

    print(colored("Available vector stores:", "yellow"))
    for col in db.list_collections():
        print(strinfigy_chroma_collection(col, for_list=True))


@click.command()
@click.argument("name", type=click.STRING)
def drop(name):
    """Delete vector store"""
    cfg = load_app_config()
    db = create_chroma_client(cfg)
    to_delete = find_collections(db, name)

    if len(to_delete) > 1:
        print(colored("Found multiple matching vector stores:", "blue"))
        for col in to_delete:
            print(strinfigy_chroma_collection(col, for_list=True))

    if len(to_delete) == 1:
        to_delete = to_delete[0]
        print(colored("Deleting:", "blue"))
        print(strinfigy_chroma_collection(to_delete, for_list=True))
        db.delete_collection(to_delete.name)
        print(colored("Deleted successfully", "green"))


@click.command()
@click.argument("filepath", type=click.Path(exists=True))
def add(filepath):
    """Load Genshin XML into vector store"""
    print(colored("Start:", "blue"), datetime.now())
    start = timer()

    cfg = load_app_config()
    db = create_chroma_client(cfg)
    init_llama_config(cfg)

    name = get_collection_name_from_filepath(filepath)
    existing = find_collections(db, name)

    if len(existing) > 0:
        print("Found already existing vector store:")
        for col in existing:
            print(strinfigy_chroma_collection(col, for_list=True))
        sys.exit(0)

    print(colored("Reading Genshin wiki XML from:", "blue"), f"'{filepath}'")
    documents = read_genshin_data(filepath)
    print(colored("Genshin wiki pages loaded:", "blue"), len(documents))

    # write
    db_dir = cfg.vector_storage.directory
    chroma_collection = db.get_or_create_collection(name)
    print(colored("Creating vector index store. This may take a while..", "blue"))
    index = create_index_from_documents(cfg, chroma_collection, documents)
    print(colored("Writing vector store as:", "blue"), f"'{name}'")
    index.storage_context.persist(persist_dir=db_dir)

    dt = timer() - start
    print(colored(f"Elapsed {dt :4.2f}s", "green"))


@click.command()
@click.argument("name", type=click.STRING, required=False)
@click.option("--input", "-i", help="Question to ask")
def query(name, input):
    """Test RAG with a few example queries

    NAME: Vector store name
    """
    cfg = load_app_config()
    callback_manager = init_verbose_logging(cfg.verbose)
    init_llama_config(cfg)

    vector_store = name or cfg.vector_storage.default_vector_store
    db = create_chroma_client(cfg)
    index = load_existing_index(db, vector_store)
    if index is None:
        exit_invalid_store(cfg, vector_store)

    query_engine = create_query_engine(
        cfg,
        index,
        callback_manager,
    )

    question = input or "Who are the Knights of Favonius?"
    ask_question_sync(query_engine, question)


@click.command()
@click.argument("name", type=click.STRING, required=False)
def serve(name):
    """Start the local server

    NAME: Vector store name
    """
    # https://docs.llamaindex.ai/en/stable/examples/customization/prompts/chat_prompts.html
    # https://docs.llamaindex.ai/en/stable/module_guides/deploying/chat_engines/root.html
    # https://docs.llamaindex.ai/en/stable/module_guides/deploying/query_engine/streaming.html
    cfg = load_app_config()
    callback_manager = init_verbose_logging(cfg.verbose)
    init_llama_config(cfg)

    vector_store = name or cfg.vector_storage.default_vector_store
    db = create_chroma_client(cfg)
    index = load_existing_index(db, vector_store)
    if index is None:
        exit_invalid_store(cfg, vector_store)

    app = create_server(STATIC_DIR)

    handler = SocketMsgHandler(
        cfg,
        index,
        callback_manager,
    )
    set_socket_msg_handler(app, handler)

    start_server(app)

    print("---DONE---")


@click.group()
def main():
    """Demo app for Retrieval-Augmented Generation"""


if __name__ == "__main__":
    main.add_command(list)
    main.add_command(drop)
    main.add_command(serve)
    main.add_command(add)
    main.add_command(query)
    main()
