"""Steps 3-4 of Module 1: embed each chunk and store it in the vector
index, plus the retrieval side (topic -> relevant chunks) that Module 2
(Question Factory) depends on.

ChromaDB is given a SentenceTransformer embedding function directly, so
`add_chunks` and `query_by_topic` never touch embeddings manually — Chroma
calls the model itself on write and on query.
"""

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL

_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_embedding_fn,
)


def add_chunks(document_id: str, chunks: list[str]) -> int:
    """Embeds and stores all chunks for one document. Returns how many
    were stored. Metadata carries the document_id and chunk_index so a
    retrieved chunk can always be traced back to its source and position."""
    if not chunks:
        return 0

    ids = [f"{document_id}-chunk{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]

    _collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def query_by_topic(topic_keywords: str, n_results: int = 5) -> list[dict]:
    """Returns the most relevant chunks for a topic/sub-topic query, each
    with its text and source metadata. This is what Module 2 calls to get
    grounding context before generating a question."""
    results = _collection.query(query_texts=[topic_keywords], n_results=n_results)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


def count_chunks() -> int:
    """Total chunks currently indexed, across all documents."""
    return _collection.count()
