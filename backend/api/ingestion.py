import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from core.models import DocumentStatus, Question, QuizSession, SkillType, SourceDocument, User
from core.schemas import DocumentResponse, QuestionWithAnswer, StartQuizResponse

router = APIRouter(prefix="/api/documents", tags=["ingestion"])

UPLOAD_DIR = Path("./uploaded_documents")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns list of all source documents and materials available."""
    return db.query(SourceDocument).order_by(SourceDocument.id.desc()).all()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accepts a document, saves it, and kicks off ingestion as an isolated background task."""
    document = SourceDocument(
        filename=file.filename,
        uploaded_by=current_user.id,
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    dest_path = UPLOAD_DIR / f"{document.id}_{file.filename}"
    with dest_path.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    from services.ingestion_service import ingest_document_file

    background_tasks.add_task(ingest_document_file, document.id, str(dest_path))

    return document


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.get(SourceDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("/{document_id}/reingest", response_model=DocumentResponse)
def reingest_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrigger ingestion for a pending or failed document."""
    document = db.get(SourceDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    dest_path = UPLOAD_DIR / f"{document.id}_{document.filename}"
    if not dest_path.exists():
        # Check backend subdirectory if running from different root
        dest_path = Path("backend/uploaded_documents") / f"{document.id}_{document.filename}"

    if not dest_path.exists():
        raise HTTPException(status_code=404, detail="Source file not found on server.")

    document.status = DocumentStatus.PENDING
    db.commit()

    from services.ingestion_service import ingest_document_file
    background_tasks.add_task(ingest_document_file, document.id, str(dest_path))

    return document


@router.post("/{document_id}/generate-questions", response_model=list[QuestionWithAnswer])
def generate_questions_from_doc(
    document_id: int,
    count: int = Query(12, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generates schema-validated questions directly grounded in this document's text."""
    document = db.get(SourceDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    from services.question_factory import QuestionGenerationError, generate_from_document_chunks

    try:
        generated = generate_from_document_chunks(db, document_id, count=count)
    except QuestionGenerationError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not generated:
        raise HTTPException(
            status_code=422,
            detail="Could not generate questions. Ensure the document has completed ingestion.",
        )
    return generated
