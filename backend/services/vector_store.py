"""Resilient Chunk & Vector Store.

Stores and queries document chunks for retrieval-augmented question generation
and diagnostic grounding. Falls back to a persistent SQLite/text similarity
index if ChromaDB/sentence-transformers are unavailable.
"""

import math
import re
import sqlite3
from pathlib import Path
from core.config import settings

_PERSIST_DIR = Path(settings.chroma_persist_dir)
_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _PERSIST_DIR / "chunks_store.db"

# Initialize local SQLite chunk store table
def _init_sqlite_store():
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id INTEGER,
            chunk_index INTEGER,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

_init_sqlite_store()

# Chroma and the embedding model are initialized only when semantic retrieval
# is actually needed. Document quiz generation reads already-stored chunks
# directly from SQLite and must not block on a Hugging Face model download.
_chroma_collection = None
_chroma_initialized = False


def _get_chroma_collection():
    global _chroma_collection, _chroma_initialized
    if _chroma_initialized:
        return _chroma_collection

    _chroma_initialized = True
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        client = chromadb.PersistentClient(path=str(_PERSIST_DIR))
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
        _chroma_collection = client.get_or_create_collection(
            name="course_chunks",
            embedding_function=embedding_fn,
        )
    except Exception as exc:
        print(f"[VectorStore] ChromaDB unavailable; using SQLite fallback: {exc}")
        _chroma_collection = None
    return _chroma_collection


def add_chunks(document_id: int, chunks: list[str]) -> int:
    """Embeds and stores chunks for one source document. Returns count stored."""
    if not chunks:
        return 0

    # 1. Store in SQLite fallback store
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    # Remove existing chunks for this document if re-ingesting
    cur.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    for i, c in enumerate(chunks):
        chunk_id = f"doc{document_id}-chunk{i}"
        cur.execute(
            "INSERT OR REPLACE INTO chunks (id, document_id, chunk_index, content) VALUES (?, ?, ?, ?)",
            (chunk_id, document_id, i, c),
        )
    conn.commit()
    conn.close()

    # 2. Store in ChromaDB if available
    chroma_collection = _get_chroma_collection()
    if chroma_collection is not None:
        try:
            ids = [f"doc{document_id}-chunk{i}" for i in range(len(chunks))]
            metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
            chroma_collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        except Exception as e:
            print(f"[VectorStore] ChromaDB add warning: {e}")

    return len(chunks)


def query_by_topic(topic_keywords: str, n_results: int = 5, document_id: int | None = None) -> list[str]:
    """Returns the most relevant chunks for a topic or keyword query."""
    chroma_collection = _get_chroma_collection()
    if chroma_collection is not None:
        try:
            where_clause = {"document_id": document_id} if document_id is not None else None
            results = chroma_collection.query(
                query_texts=[topic_keywords],
                n_results=n_results,
                where=where_clause,
            )
            docs = results.get("documents", [[]])
            if docs and docs[0]:
                return docs[0]
        except Exception as e:
            print(f"[VectorStore] ChromaDB query warning: {e}")

    # SQLite TF-IDF / BM25 style keyword ranking fallback
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    if document_id is not None:
        cur.execute("SELECT id, content FROM chunks WHERE document_id = ?", (document_id,))
    else:
        cur.execute("SELECT id, content FROM chunks")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    query_tokens = set(re.findall(r"\w+", topic_keywords.lower()))
    scored_chunks = []

    for _, content in rows:
        content_lower = content.lower()
        chunk_tokens = re.findall(r"\w+", content_lower)
        if not chunk_tokens:
            continue

        score = 0.0
        for token in query_tokens:
            tf = content_lower.count(token)
            if tf > 0:
                score += (1.0 + math.log(tf))

        if score > 0:
            scored_chunks.append((score, content))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    if scored_chunks:
        return [c[1] for c in scored_chunks[:n_results]]

    # If no exact token match, return first n chunks
    return [r[1] for r in rows[:n_results]]


def get_all_chunks_for_document(document_id: int) -> list[str]:
    """Retrieves all text chunks for a given document."""
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content FROM chunks WHERE document_id = ? ORDER BY chunk_index ASC", (document_id,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
