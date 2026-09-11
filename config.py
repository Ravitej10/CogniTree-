"""Config for Module 1 (Document Ingestion). Kept as plain constants so
this module has zero dependency on the rest of the backend and can be
run, tested, and graded on its own."""

# Chunking — 500 chars with 50-char overlap, per the project spec. The
# overlap exists so a definition or formula split across a chunk boundary
# still appears whole in at least one chunk.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Embedding model (Hugging Face sentence-transformers)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Where Chroma persists its index to disk
CHROMA_PERSIST_DIR = "./chroma_data"
COLLECTION_NAME = "course_chunks"
