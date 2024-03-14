import multiprocessing
import multiprocessing.pool
import os
import threading

from llama_index.core.schema import Document
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import run_transformations


def get_sublists(original_list, number_of_sub_list_wanted):
    sublists = list()
    for sub_list_count in range(number_of_sub_list_wanted):
        sublists.append(original_list[sub_list_count::number_of_sub_list_wanted])
    return sublists


class ParallelIngest:
    """
    Code below works fine but there are no performance improvements above default
    version (which is already multithreaded).

    Based mostly on:
    - https://github.com/imartinez/privateGPT/blob/12f3a39e8aab94f1156adac7dcfbba29929840a9/private_gpt/components/ingest/ingest_component.py#L218

    To use:
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    pi = ParallelIngest(cfg, storage_context)
    pi.bulk_ingest(documents)
    """

    def __init__(
        self,
        cfg,
        storage_context: StorageContext,
    ) -> None:
        self.cfg = cfg
        self.storage_context = storage_context
        self.count_workers = 10

        # We are doing our own multiprocessing
        # To do not collide with the multiprocessing of huggingface, we disable it
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        self._ingest_work_pool = multiprocessing.pool.ThreadPool(
            processes=self.count_workers
        )

        # Thread lock! Not Multiprocessing lock
        self._index_thread_lock = threading.Lock()
        self._index = self._initialize_index()
        self._save_index()

    def _initialize_index(self):
        index = VectorStoreIndex.from_documents(
            [],
            storage_context=self.storage_context,
        )
        return index

    def _save_index(self) -> None:
        db_dir = self.cfg.vector_storage.directory
        self._index.storage_context.persist(persist_dir=db_dir)

    def bulk_ingest(self, documents) -> list[Document]:
        documents_nested = get_sublists(documents, self.count_workers)
        self._ingest_work_pool.map(self._save_docs, documents_nested)
        self._save_index()

    def _save_docs(self, documents):
        chunk_size = self.cfg.vector_storage.chunk_size
        chunk_overlap = self.cfg.vector_storage.chunk_overlap

        nodes = run_transformations(
            documents,
            [SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)],
        )
        # Locking the index to avoid concurrent writes
        with self._index_thread_lock:
            self._index.insert_nodes(nodes)
            for doc in documents:
                self._index.docstore.set_document_hash(doc.get_doc_id(), doc.hash)
        return documents
