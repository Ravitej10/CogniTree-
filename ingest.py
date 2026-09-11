"""Module 1 entrypoint: runs the full ingestion pipeline for one document.

extract -> chunk -> embed -> store, matching the "System Pipeline" slide.
Each stage is its own file (extractor.py, chunker.py, embedder_store.py)
so they can be tested, swapped, or reused independently — Module 2
(question generation) only ever imports `query_by_topic` from
embedder_store.py, for example, and doesn't care how the chunks got there.
"""

from dataclasses import dataclass

from chunker import chunk_text
from embedder_store import add_chunks
from extractor import ExtractionError, extract_text


@dataclass
class IngestionResult:
    document_id: str
    filename: str
    status: str  # "ready" or "failed"
    chunk_count: int
    error: str | None = None


def ingest_document(document_id: str, file_path: str) -> IngestionResult:
    """Runs the pipeline for one file. Never raises — failures are
    reported in the returned IngestionResult so a caller (e.g. the FastAPI
    background task in the full backend) can update a status column
    without needing a try/except at the call site."""
    filename = file_path.rsplit("/", 1)[-1]

    try:
        raw_text = extract_text(file_path)
    except ExtractionError as e:
        return IngestionResult(document_id, filename, status="failed", chunk_count=0, error=str(e))

    chunks = chunk_text(raw_text)
    if not chunks:
        return IngestionResult(
            document_id, filename, status="failed", chunk_count=0, error="Chunking produced no chunks."
        )

    stored_count = add_chunks(document_id, chunks)
    return IngestionResult(document_id, filename, status="ready", chunk_count=stored_count)
