"""Phase 1: Knowledge Base Ingestion Pipeline.

Receive source documents -> extract raw text -> chunk with overlap ->
embed -> store in the vector index.
"""

from pathlib import Path
from sqlalchemy.orm import Session

from core.config import settings
from core.models import DocumentStatus, SourceDocument


def extract_text(file_path: str) -> str:
    """Extracts raw text from a PDF, TXT, or MD file with resilient fallbacks."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext in [".txt", ".md", ".csv", ".json"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    text_parts: list[str] = []

    # 1. Try pypdf (standard, fast, robust)
    try:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
        if text_parts:
            return "\n\n".join(text_parts)
    except Exception as e:
        print(f"[Ingestion] pypdf extraction warning for {path.name}: {e}")

    # 2. Try pdfplumber if available
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text.strip())
        if text_parts:
            return "\n\n".join(text_parts)
    except Exception as e:
        print(f"[Ingestion] pdfplumber extraction warning for {path.name}: {e}")

    # 3. Fallback: raw binary read with text decode
    try:
        raw_bytes = path.read_bytes()
        import re
        ascii_strings = re.findall(rb"[\x20-\x7E\s]{4,}", raw_bytes)
        decoded = "\n".join(s.decode("latin-1", errors="ignore") for s in ascii_strings)
        if len(decoded.strip()) > 50:
            return decoded
    except Exception:
        pass

    extracted = "\n\n".join(text_parts).strip()
    if not extracted:
        raise ValueError(f"No extractable text found in {path.name}. Ensure it contains selectable text.")
    return extracted


def chunk_text(raw_text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Splits raw text into overlapping chunks using paragraph, sentence, and word boundaries."""
    if not raw_text or not raw_text.strip():
        return []

    # Try langchain text splitter if installed
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_text(raw_text)
        if chunks:
            return [c.strip() for c in chunks if c.strip()]
    except Exception:
        pass

    # Pure Python recursive splitter fallback
    paragraphs = raw_text.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current_chunk) + len(p) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{p}" if current_chunk else p
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Handle overlap
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = f"{overlap_text}\n\n{p}" if overlap_text else p
            else:
                # Paragraph itself exceeds chunk_size: split by sentences / words
                words = p.split()
                temp_chunk = ""
                for w in words:
                    if len(temp_chunk) + len(w) + 1 <= chunk_size:
                        temp_chunk = f"{temp_chunk} {w}" if temp_chunk else w
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = w
                if temp_chunk:
                    current_chunk = temp_chunk

    if current_chunk and current_chunk.strip():
        chunks.append(current_chunk.strip())

    return [c for c in chunks if len(c) > 20]


def ingest_document_file(document_id: int, file_path: str):
    """Background ingestion handler that creates its own SessionLocal to avoid closed-session race conditions."""
    from core.database import SessionLocal
    from services.vector_store import add_chunks

    db = SessionLocal()
    try:
        document = db.get(SourceDocument, document_id)
        if not document:
            return

        document.status = DocumentStatus.PROCESSING
        db.commit()

        raw_text = extract_text(file_path)
        chunks = chunk_text(
            raw_text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        stored_count = add_chunks(document.id, chunks)

        document.status = DocumentStatus.READY
        document.chunk_count = stored_count
        db.commit()
    except Exception as e:
        print(f"[Ingestion Error] Failed to ingest document {document_id}: {e}")
        try:
            document = db.get(SourceDocument, document_id)
            if document:
                document.status = DocumentStatus.FAILED
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

