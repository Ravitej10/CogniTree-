# Module 1 — Document Ingestion Pipeline

Standalone, runnable version of Phase 1 from the project pipeline:
**extract → chunk → embed → store**. It has no dependency on the rest of
the backend (no FastAPI, no Postgres) so it can be demoed, tested, and
graded on its own.

## Files

| File | Responsibility |
|---|---|
| `extractor.py` | Step 1 — pull raw text out of a PDF (PDFPlumber) |
| `chunker.py` | Step 2 — split text into 500-char chunks, 50-char overlap (LangChain) |
| `embedder_store.py` | Steps 3–4 — embed chunks (SentenceTransformers) and store/query them (ChromaDB) |
| `ingest.py` | Orchestrates the four steps for one document |
| `demo.py` | CLI script to run and sanity-check the whole pipeline |
| `config.py` | The knobs — chunk size/overlap, embedding model name, storage path |

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Try it

```bash
python demo.py path/to/some_chapter.pdf "photosynthesis"
```

This ingests the PDF, prints how many chunks were stored, then runs a
retrieval query and prints the top 3 matching chunks with their distance
scores — so you can eyeball whether retrieval is actually pulling
relevant material before Module 2 (question generation) depends on it.

## Verified

`chunker.py`'s overlap logic was tested directly: a 3-chunk sample text
confirmed each chunk is ≤500 chars and neighboring chunks share the
expected overlapping tail/head text.

`extractor.py`'s scanned-PDF case isn't auto-tested here (no OCR
fallback) — if a PDF comes back with no extractable text, `extract_text`
raises `ExtractionError` rather than silently indexing a blank document;
worth throwing a scanned PDF at it once to see that path fire.

## How this plugs into the full backend

This is the same logic as `app/services/ingestion_service.py` and
`app/services/vector_store.py` in the backend package — the difference is
this version takes a `document_id: str` directly instead of a SQLAlchemy
`SourceDocument` row, so it's not coupled to a database. If you want to
swap the backend's version out for this one, the only changes needed are
in `api/ingestion.py`, where the SQLAlchemy status updates happen around
the `ingest_document()` call.
