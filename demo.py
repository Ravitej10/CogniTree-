"""Demo/test script for Module 1. Run it against any PDF to see the full
pipeline work end to end and confirm retrieval quality before moving on
to Module 2.

Usage:
    python demo.py path/to/chapter.pdf "topic keywords to search for"

Example:
    python demo.py sample_docs/chapter3_thermodynamics.pdf "entropy"
"""

import sys

from embedder_store import count_chunks, query_by_topic
from ingest import ingest_document


def main():
    if len(sys.argv) < 2:
        print("Usage: python demo.py <path_to_pdf> [query]")
        sys.exit(1)

    file_path = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Ingesting: {file_path}")
    result = ingest_document(document_id="demo-doc-1", file_path=file_path)

    if result.status == "failed":
        print(f"FAILED: {result.error}")
        sys.exit(1)

    print(f"OK — stored {result.chunk_count} chunks. Total chunks in index: {count_chunks()}")

    if query:
        print(f"\nQuerying for: {query!r}")
        hits = query_by_topic(query, n_results=3)
        for i, hit in enumerate(hits, start=1):
            preview = hit["text"][:160].replace("\n", " ")
            print(f"\n[{i}] (distance={hit['distance']:.4f}) {preview}...")


if __name__ == "__main__":
    main()
