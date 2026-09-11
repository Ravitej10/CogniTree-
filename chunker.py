"""Step 2 of Module 1: split extracted text into overlapping chunks.

Uses LangChain's RecursiveCharacterTextSplitter, which tries to break on
paragraph/sentence boundaries first and only falls back to a hard
character cut when a section is too long to split cleanly.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def chunk_text(raw_text: str) -> list[str]:
    """Returns a list of overlapping text chunks, each up to CHUNK_SIZE
    characters, with CHUNK_OVERLAP characters shared between neighbors."""
    if not raw_text.strip():
        return []
    return _splitter.split_text(raw_text)
